from unittest import TestCase

from utils import make_games, make_players
from table_minion.generate_tables import (
    GameTablesGenerator, AllTablesGenerator)


class TestGameTablesGenerator(TestCase):
    # TODO: These tests.

    def test_generate_two_full_tables(self):
        [game] = list(make_games(['1A']))
        players = make_players([
            (2, 'GM', None, {'1A': 'G'}),
            (12, 'Player', None, {'1A': 'P'}),
        ])
        generator = GameTablesGenerator(game, players)

        [table1, table2] = generator.generate_tables()

        self.assertNotEqual(table1, table2)
        self.assertNotEqual(table1.gm, table2.gm)
        self.assertNotEqual(table1.players, table2.players)

        self.assertEqual(game, table1.game)
        self.assertNotEqual(None, table1.gm)
        self.assertEqual(6, len(table1.players))
        self.assertEqual([], table1.warnings)
        self.assertEqual([], table1.info)

        self.assertEqual(game, table2.game)
        self.assertNotEqual(None, table2.gm)
        self.assertEqual(6, len(table2.players))
        self.assertEqual([], table2.warnings)
        self.assertEqual([], table2.info)
