import os
import re
import tempfile
from StringIO import StringIO
from contextlib import contextmanager
from unittest import TestCase

from table_minion import web, db
from table_minion.games import Game
from table_minion.players import Player


def make_tag_re(tag):
    return re.compile(r'<(%s)(| [^>]*)>(.*?)</\1>' % (tag,), re.DOTALL)


class BaseWebTestCase(TestCase):

    def setUp(self):
        self.db_fd, web.app.config['DATABASE'] = tempfile.mkstemp()
        web.app.config['TESTING'] = True
        self.client = web.app.test_client()
        db.init_db(web.app)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(web.app.config['DATABASE'])

    def parse_tables(self, response):
        # This is horrible, but it works because we know what the HTML looks
        # like. It assumes there are no nested tables.
        table_re = make_tag_re('table')
        row_re = make_tag_re('tr')
        cell_re = make_tag_re('t[dh]')

        tables = []
        for table_match in table_re.finditer(response.data):
            table = {'attrs': table_match.group(2), 'rows': []}
            tables.append(table)
            for row_match in row_re.finditer(table_match.group(3)):
                row = {'attrs': row_match.group(2), 'cells': []}
                table['rows'].append(row)
                for cell_match in cell_re.finditer(row_match.group(3)):
                    row['cells'].append({
                        'tag': cell_match.group(1),
                        'attrs': cell_match.group(2),
                        'value': cell_match.group(3),
                    })
        return tables

    @contextmanager
    def db_context(self):
        with web.app.test_request_context():
            db.open_db(web.app)
            yield
            db.close_db()

    def post_file(self, url, filename, fileobj, extra_data=None):
        data = {filename: (fileobj, filename)}
        if extra_data:
            data.update(extra_data)
        return self.client.post(url, data=data)


class TestWebPlayers(BaseWebTestCase):
    def make_game(self, slot):
        return Game(slot, 'name', 'author', 'system', 'blurb', 4, 6)

    def upload_players(self, csv_data):
        response = self.post_file(
            '/players/upload', 'players.csv', StringIO(csv_data))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/players/')
        return response

    def assert_table_values(self, table, expected):
        self.assertEqual(expected, [
            [cell['value'].strip() for cell in row['cells']]
            for row in table['rows']
        ])

    def assert_db_players(self, expected):
        with self.db_context():
            self.assertEqual(expected, list(db.get_players()))

    def test_no_players(self):
        [player_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(player_table, [
            ['name', 'team'],
        ])

    def test_no_players_one_game_slot(self):
        with self.db_context():
            db.insert_game(self.make_game('1A'))
        [player_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(player_table, [
            ['name', 'team', '1A'],
        ])

    def test_one_player_no_slots(self):
        with self.db_context():
            db.insert_player(Player('Gary Gygax', 'TSR', {}))
        [player_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(player_table, [
            ['name', 'team'],
            ['Gary Gygax', 'TSR'],
        ])

    def test_one_player_one_game_slot(self):
        with self.db_context():
            db.insert_game(self.make_game('1A'))
            db.insert_player(Player('Gary Gygax', 'TSR', {}))
        [player_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(player_table, [
            ['name', 'team', '1A'],
            ['Gary Gygax', 'TSR', ''],
        ])

    def test_one_player_one_slot(self):
        with self.db_context():
            db.insert_player(Player('Gary Gygax', 'TSR', {'1A': 'G'}))
        [player_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(player_table, [
            ['name', 'team', '1A'],
            ['Gary Gygax', 'TSR', 'G'],
        ])

    def test_two_players_one_slot_each(self):
        with self.db_context():
            db.insert_player(Player('Gary Gygax', 'TSR', {'1A': 'G'}))
            db.insert_player(Player('Dave Arneson', 'TSR', {'1B': 'G'}))
        [player_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(player_table, [
            ['name', 'team', '1A', '1B'],
            ['Gary Gygax', 'TSR', 'G', ''],
            ['Dave Arneson', 'TSR', '', 'G'],
        ])

    def test_import_one_player_no_slots(self):
        self.assert_db_players([])
        self.upload_players('\n'.join([
            'name,team',
            'Gary Gygax,TSR',
        ]))
        self.assert_db_players([Player('Gary Gygax', 'TSR', {})])

    def test_import_two_players_one_slot_each(self):
        self.assert_db_players([])
        self.upload_players('\n'.join([
            'name,team,1A,1B',
            'Gary Gygax,TSR,G,',
            'Dave Arneson,TSR,,G',
        ]))
        self.assert_db_players([
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1B': 'G'}),
        ])
