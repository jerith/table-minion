from unittest import TestCase
from StringIO import StringIO

from table_minion.tests.utils import make_players, make_games
from table_minion.game_tables import GameTable, GameTables


def make_player_dict(name, team=None, slots=None):
    return {'name': name, 'team': team, 'slots': slots or {}}


class TestGameTable(TestCase):
    def test_warnings(self):
        [game] = list(make_games(['1A']))
        [gm] = list(make_players([(1, 'GM1A', None, {'1A': 'G'})]))
        [either] = list(make_players([(1, 'E1A', None, {'1A': 'X'})]))
        players = list(make_players([(5, 'P1A', None, {'1A': 'P'})]))

        self.assertEqual(GameTable(game, gm, players).warnings, [])
        self.assertEqual(GameTable(game, either, players).warnings, [])
        self.assertEqual(GameTable(game, gm, [either] + players).warnings, [])
        self.assertEqual(GameTable(game, None, players).warnings, [
            'No gm.',
        ])
        self.assertEqual(GameTable(game, players[0], players).warnings, [
            'P1A 0 not registered as a GM.',
        ])
        self.assertEqual(GameTable(game, gm, [gm] + players).warnings, [
            'GM1A 0 not registered as a player.',
        ])
        self.assertEqual(GameTable(game, gm, players + players).warnings, [
            '4 players too many.',
        ])
        self.assertEqual(GameTable(game, gm, players[:2]).warnings, [
            '2 players too few.',
        ])
        self.assertEqual(GameTable(game, None, [gm] + players[:2]).warnings, [
            'No gm.',
            '1 player too few.',
            'GM1A 0 not registered as a player.',
        ])


class TestGameTables(TestCase):
    def test_from_csv(self):
        games = make_games(['1A', '1B'])
        players = make_players([
            (1, 'GM1A', None, {'1A': 'G'}),
            (1, 'GM1B', None, {'1B': 'G'}),
            (5, 'P1A', None, {'1A': 'P'}),
            (5, 'P1B', None, {'1B': 'P'}),
        ])

        game_tables = GameTables.from_csv(
            games, players, StringIO('\n'.join([
                'slot,gm,players',
                '1A,GM1A 0,P1A 0,P1A 1,P1A 2,P1A 3,P1A 4',
                '1B,GM1B 0,P1B 0,P1B 1,P1B 2,P1B 3,P1B 4',
            ])))
        print game_tables

    def test_to_csv(self):
        games = make_games(['1A', '1B'])
        players = make_players([
            (1, 'GM1A', None, {'1A': 'G'}),
            (1, 'GM1B', None, {'1B': 'G'}),
            (5, 'P1A', None, {'1A': 'P'}),
            (5, 'P1B', None, {'1B': 'P'}),
        ])

        game_tables = GameTables(games, players, {
            '1A': [GameTable(
                games['1A'], players.get_player('GM1A 0'),
                [players.get_player('P1A %s' % (i,)) for i in xrange(5)])],
            '1B': [GameTable(
                games['1B'], players.get_player('GM1B 0'),
                [players.get_player('P1B %s' % (i,)) for i in xrange(5)])],
        })

        game_tables_csv = StringIO()
        game_tables.to_csv(game_tables_csv)
        self.assertEqual(game_tables_csv.getvalue(), '\r\n'.join([
            'slot,gm,players',
            '1A,GM1A 0,P1A 0,P1A 1,P1A 2,P1A 3,P1A 4',
            '1B,GM1B 0,P1B 0,P1B 1,P1B 2,P1B 3,P1B 4',
            '',
        ]))
