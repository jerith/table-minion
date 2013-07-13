import os
import tempfile
from unittest import TestCase

from table_minion import web, db
from table_minion.games import Game, Games
from table_minion.players import Player, Players


PLAYER_WITH_REG_QUERY = '''
SELECT name, team, slot, registration_type
FROM players AS p LEFT JOIN player_registrations AS pr ON p.id=pr.player
ORDER BY p.id, slot;
'''

GAME_QUERY = '''
SELECT slot, name, author, system, blurb, min_players, max_players FROM games;
'''


class TestDB(TestCase):
    def setUp(self):
        self.db_fd, web.app.config['DATABASE'] = tempfile.mkstemp()
        web.app.config['TESTING'] = True
        self.client = web.app.test_client()
        db.init_db(web.app)
        self.rctx = web.app.test_request_context()
        self.rctx.push()
        db.open_db(web.app)

    def tearDown(self):
        db.close_db()
        self.rctx.pop()
        os.close(self.db_fd)
        os.unlink(web.app.config['DATABASE'])

    def assert_query(self, expected, query, args=()):
        rows = db.query_db(query, args)
        self.assertEqual(expected, map(tuple, rows))
            # row_dicts, [dict(zip(row.keys(), row)) for row in rows])

    def test_init_db(self):
        db.query_db('INSERT INTO players (name) VALUES ("foo");')
        db.commit_db()
        self.assertNotEqual([], db.query_db('SELECT * FROM players;'))

        db.init_db(web.app)
        self.assertNotEqual([], db.query_db('SELECT * FROM players;'))

        db.init_db(web.app, clear=True)
        self.assertEqual([], db.query_db('SELECT * FROM players;'))

    def test_insert_player(self):
        self.assert_query([], 'SELECT * FROM players;')
        self.assert_query([], 'SELECT * FROM player_registrations;')
        db.insert_player(Player('Gary Gygax', 'TSR', {'1A': 'G'}))
        self.assert_query(
            [('Gary Gygax', 'TSR', '1A', 'G')], PLAYER_WITH_REG_QUERY)

    def test_import_players(self):
        db.query_db('INSERT INTO players (name) VALUES ("foo");')
        db.commit_db()
        self.assert_query([('foo', None, None, None)], PLAYER_WITH_REG_QUERY)

        db.import_players(Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', None, {'1B': 'P'}),
        ]))
        self.assert_query([
            ('Gary Gygax', 'TSR', '1A', 'G'),
            ('Dave Arneson', None, '1B', 'P'),
        ], PLAYER_WITH_REG_QUERY)

    def test_get_players(self):
        self.assertEqual([], list(db.get_players()))
        db.import_players(Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', None, {'1B': 'P'}),
        ]))
        players = db.get_players()
        self.assertTrue(isinstance(players, Players))
        self.assertEqual(list(players), [
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', None, {'1B': 'P'}),
        ])

    def test_get_players_for_game(self):
        db.import_players(Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', None, {'1A': 'P', '2A': 'X'}),
            Player('Jane Bloggs', None, {'2A': 'P'}),
        ]))
        players = db.get_players_for_game('1A')
        self.assertTrue(isinstance(players, Players))
        self.assertEqual(list(players), [
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', None, {'1A': 'P'}),
        ])

    def test_get_player(self):
        db.import_players(Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G', '2A': 'G'}),
            Player('Dave Arneson', None, {'1A': 'P'}),
        ]))
        self.assertRaises(db.NotFound, db.get_player, 'foo')
        self.assertEqual(
            db.get_player('Gary Gygax'),
            Player('Gary Gygax', 'TSR', {'1A': 'G', '2A': 'G'}))

    def test_insert_game(self):
        self.assert_query([], 'SELECT * FROM games;')
        db.insert_game(Game(
            '1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6))
        self.assert_query(
            [('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6)],
            GAME_QUERY)

    def test_import_games(self):
        db.insert_game(Game(
            '1X', 'Game 1X', 'Author 1X', 'System 1X', 'Blurb 1X', 4, 6))
        db.commit_db()
        self.assert_query(
            [('1X', 'Game 1X', 'Author 1X', 'System 1X', 'Blurb 1X', 4, 6)],
            GAME_QUERY)

        db.import_games(Games([
            Game('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6),
            Game('1B', 'Game 1B', 'Author 1B', 'System 1B', 'Blurb 1B', 4, 6),
        ]))
        self.assert_query([
            ('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6),
            ('1B', 'Game 1B', 'Author 1B', 'System 1B', 'Blurb 1B', 4, 6),
        ], GAME_QUERY)

    def test_get_games(self):
        self.assertEqual([], list(db.get_games()))
        db.import_games(Games([
            Game('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6),
            Game('1B', 'Game 1B', 'Author 1B', 'System 1B', 'Blurb 1B', 4, 6),
        ]))
        games = db.get_games()
        self.assertTrue(isinstance(games, Games))
        self.assertEqual(list(games), [
            Game('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6),
            Game('1B', 'Game 1B', 'Author 1B', 'System 1B', 'Blurb 1B', 4, 6),
        ])

    def test_get_game(self):
        db.import_games(Games([
            Game('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6),
            Game('1B', 'Game 1B', 'Author 1B', 'System 1B', 'Blurb 1B', 4, 6),
        ]))
        self.assertRaises(db.NotFound, db.get_game, '9X')
        self.assertEqual(
            Game('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6),
            db.get_game('1A'))
