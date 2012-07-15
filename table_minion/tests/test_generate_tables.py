from unittest import TestCase

from table_minion.players import Player, Players
from table_minion.games import Game, Games
from table_minion.generate_tables import GameTables


def make_players(count, name_prefix, team='', **reg):
    return [Player('%s %s' % (name_prefix, i), team, reg)
            for i in range(count)]


def make_games(slots):
    return Games(dict(
            (s, Game(s, 'Game %s' % s, 'Author', 'System', 'Blurb'))
            for s in slots))


class TestGameTables(TestCase):
    def test_lay_tables(self):
        games = make_games(['1A', '1B'])
        players = []
        players.extend(make_players(10, 'Alpha', **{'1A': 'P', '1B': ''}))
        players.extend(make_players(1, 'Able', **{'1A': 'X', '1B': ''}))
        players.extend(make_players(2, 'Ares', 'Olympians',
                                    **{'1A': 'P', '1B': ''}))
        players.extend(make_players(9, 'Bravo', **{'1A': '', '1B': 'P'}))
        players.extend(make_players(2, 'Baker', **{'1A': '', '1B': 'X'}))

        players = Players(players)
        game_tables = GameTables(games, players, ['1A', '1B'])
        game_tables.lay_game_tables('1A')
        print ''
        print game_tables.make_list()
