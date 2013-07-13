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

    def assert_table_values(self, table, expected):
        self.assertEqual(expected, [
            [cell['value'].strip() for cell in row['cells']]
            for row in table['rows']
        ])

    @contextmanager
    def db_context(self):
        with web.app.test_request_context():
            db.open_db(web.app)
            yield
            db.close_db()

    def post_file(self, url, fieldname, filename, fileobj):
        return self.client.post(url, data={fieldname: (fileobj, filename)})

    def make_game(self, slot, **kw):
        kw.setdefault('name', 'Game %s' % (slot,))
        kw.setdefault('author', 'Author %s' % (slot,))
        kw.setdefault('system', 'System %s' % (slot,))
        kw.setdefault('blurb', 'Blurb %s' % (slot,))
        return Game(slot, **kw)


class TestWebPlayers(BaseWebTestCase):
    def make_game(self, slot):
        return Game(slot, 'name', 'author', 'system', 'blurb', 4, 6)

    def upload_players_csv(self, csv_data):
        response = self.post_file(
            '/players/upload', 'players_file', 'players.csv',
            StringIO(csv_data))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/players/')
        return response

    def upload_players_xls(self, xls_filename):
        response = self.post_file(
            '/players/upload', 'players_file', 'players.xls',
            open(xls_filename))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/players/')
        return response

    def assert_db_players(self, expected):
        with self.db_context():
            self.assertEqual(expected, list(db.get_players()))

    def test_no_players(self):
        self.assert_db_players([])
        [players_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(players_table, [
            ['name', 'team'],
        ])

    def test_no_players_one_game_slot(self):
        with self.db_context():
            db.insert_game(self.make_game('1A'))
        [players_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(players_table, [
            ['name', 'team', '1A'],
        ])

    def test_one_player_no_slots(self):
        with self.db_context():
            db.insert_player(Player('Gary Gygax', 'TSR', {}))
        [players_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(players_table, [
            ['name', 'team'],
            ['Gary Gygax', 'TSR'],
        ])

    def test_one_player_one_game_slot(self):
        with self.db_context():
            db.insert_game(self.make_game('1A'))
            db.insert_player(Player('Gary Gygax', 'TSR', {}))
        [players_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(players_table, [
            ['name', 'team', '1A'],
            ['Gary Gygax', 'TSR', ''],
        ])

    def test_one_player_one_slot(self):
        with self.db_context():
            db.insert_player(Player('Gary Gygax', 'TSR', {'1A': 'G'}))
        [players_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(players_table, [
            ['name', 'team', '1A'],
            ['Gary Gygax', 'TSR', 'G'],
        ])

    def test_two_players_one_slot_each(self):
        with self.db_context():
            db.insert_player(Player('Gary Gygax', 'TSR', {'1A': 'G'}))
            db.insert_player(Player('Dave Arneson', 'TSR', {'1B': 'G'}))
        [players_table] = self.parse_tables(self.client.get('/players/'))
        self.assert_table_values(players_table, [
            ['name', 'team', '1A', '1B'],
            ['Gary Gygax', 'TSR', 'G', ''],
            ['Dave Arneson', 'TSR', '', 'G'],
        ])

    def test_import_one_player_no_slots(self):
        self.assert_db_players([])
        self.upload_players_csv('\n'.join([
            'name,team',
            'Gary Gygax,TSR',
        ]))
        self.assert_db_players([Player('Gary Gygax', 'TSR', {})])

    def test_import_two_players_one_slot_each(self):
        self.assert_db_players([])
        self.upload_players_csv('\n'.join([
            'name,team,1A,1B',
            'Gary Gygax,TSR,G,',
            'Dave Arneson,TSR,,G',
        ]))
        self.assert_db_players([
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1B': 'G'}),
        ])

    def test_import_two_players_one_slot_each_xls(self):
        self.assert_db_players([])
        self.upload_players_xls(os.path.join(
            os.path.dirname(__file__), 'players.xls'))
        self.assert_db_players([
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1B': 'G'}),
        ])


class TestWebGames(BaseWebTestCase):
    def slot_link(self, slot):
        return '<a href="/games/%s/">%s</a>' % (slot, slot)

    def upload_games_csv(self, csv_data):
        response = self.post_file(
            '/games/upload', 'games_file', 'games.csv', StringIO(csv_data))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/games/')
        return response

    def upload_games_xls(self, xls_filename):
        response = self.post_file(
            '/games/upload', 'games_file', 'games.xls', open(xls_filename))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/games/')
        return response

    def assert_db_games(self, expected):
        with self.db_context():
            self.assertEqual(expected, list(db.get_games()))

    def test_no_games(self):
        self.assert_db_games([])
        [games_table] = self.parse_tables(self.client.get('/games/'))
        self.assert_table_values(games_table, [
            ['slot', 'name', 'author', 'system', 'players'],
        ])

    def test_one_game_4_to_6_players(self):
        with self.db_context():
            db.insert_game(self.make_game('1A'))
        [games_table] = self.parse_tables(self.client.get('/games/'))
        self.assert_table_values(games_table, [
            ['slot', 'name', 'author', 'system', 'players'],
            [self.slot_link('1A'), 'Game 1A', 'Author 1A', 'System 1A', '4-6'],
        ])

    def test_one_game_5_players(self):
        with self.db_context():
            db.insert_game(self.make_game('1A', min_players=5, max_players=5))
        [games_table] = self.parse_tables(self.client.get('/games/'))
        self.assert_table_values(games_table, [
            ['slot', 'name', 'author', 'system', 'players'],
            [self.slot_link('1A'), 'Game 1A', 'Author 1A', 'System 1A', '5'],
        ])

    def test_two_games(self):
        with self.db_context():
            db.insert_game(self.make_game('1A'))
            db.insert_game(self.make_game('1B', min_players=5, max_players=5))
        [games_table] = self.parse_tables(self.client.get('/games/'))
        self.assert_table_values(games_table, [
            ['slot', 'name', 'author', 'system', 'players'],
            [self.slot_link('1A'), 'Game 1A', 'Author 1A', 'System 1A', '4-6'],
            [self.slot_link('1B'), 'Game 1B', 'Author 1B', 'System 1B', '5'],
        ])

    def test_import_one_game(self):
        self.assert_db_games([])
        self.upload_games_csv('\n'.join([
            'slot,name,author,system,blurb,min_players,max_players',
            '1A,Game 1A,Author 1A,System 1A,Blurb 1A,4,6',
        ]))
        self.assert_db_games([self.make_game('1A')])

    def test_import_two_games(self):
        self.assert_db_games([])
        self.upload_games_csv('\n'.join([
            'slot,name,author,system,blurb,min_players,max_players',
            '1A,Game 1A,Author 1A,System 1A,Blurb 1A,4,6',
            '1B,Game 1B,Author 1B,System 1B,Blurb 1B,5,5',
        ]))
        self.assert_db_games([
            self.make_game('1A'),
            self.make_game('1B', min_players=5, max_players=5),
        ])

    def test_import_two_games_xls(self):
        self.assert_db_games([])
        self.upload_games_xls(os.path.join(
            os.path.dirname(__file__), 'games.xls'))
        self.assert_db_games([
            self.make_game('1A'),
            self.make_game('1B', min_players=5, max_players=5),
        ])


class TestWebGame(BaseWebTestCase):
    def assert_response_contains(self, response, text):
        self.assertTrue(
            text in response.data, '%r not found in response.' % (text,))

    def test_no_game(self):
        response = self.client.get('/games/1A/')
        self.assertEqual(response.status_code, 404)

    def test_game_4_to_6_players_no_tables(self):
        with self.db_context():
            db.insert_game(self.make_game('1A'))
        response = self.client.get('/games/1A/')
        self.assertEqual(response.status_code, 200)
        self.assert_response_contains(response, '1A: Game 1A')
        self.assert_response_contains(response, 'Author: Author 1A')
        self.assert_response_contains(response, 'System: System 1A')
        self.assert_response_contains(response, 'Blurb: Blurb 1A')
        self.assert_response_contains(response, 'Players: 4-6')
        [tables_table] = self.parse_tables(response)
        self.assert_table_values(tables_table, [['tables'], []])

    def test_game_5_players_no_tables(self):
        with self.db_context():
            db.insert_game(self.make_game('1A', min_players=5, max_players=5))
        response = self.client.get('/games/1A/')
        self.assertEqual(response.status_code, 200)
        self.assert_response_contains(response, '1A: Game 1A')
        self.assert_response_contains(response, 'Author: Author 1A')
        self.assert_response_contains(response, 'System: System 1A')
        self.assert_response_contains(response, 'Blurb: Blurb 1A')
        self.assert_response_contains(response, 'Players: 5')
        [tables_table] = self.parse_tables(response)
        self.assert_table_values(tables_table, [['tables'], []])

    # TODO: Games with tables.
