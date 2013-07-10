from unittest import TestCase

from utils import make_games, make_players
from table_minion.generate_tables import (
    GameTablesGenerator, AllTablesGenerator)


class TestGameTablesGenerator(TestCase):
    # TODO: These tests.
    def test_generate_tables(self):
        [game] = list(make_games(['1A']))
        players = make_players([
                (10, 'Alpha', None, {'1A': 'P'}),
                (2, 'Able', None, {'1A': 'X'}),
                (2, 'Ares', 'Olympians', {'1A': 'P'}),
                ])

        print game
        generator = GameTablesGenerator(game, players)
        print generator.generate_tables()
