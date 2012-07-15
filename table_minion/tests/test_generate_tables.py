from unittest import TestCase
from StringIO import StringIO

from table_minion.generate_tables import Players, Games, GameTables


def get_players():
    players_file = StringIO('\n'.join([
                'name,team,1A,1B,2A,2B',
                'Gary Gygax,TSR,G,,G,',
                'Joe Bloggs,TSR,P,,P,',
                'Jane Bloggs,,,X,,X',
                ]))
    return Players.from_csv(players_file)


def get_games():
    games_file = StringIO('\n'.join([
                'slot,name,author,system,blurb',
                '1A,Aargh!,Alice Able,SillyDice,Camelot is a silly place.',
                '1B,Business,Bob Bobson,SrsBsns,Make some RoI.',
                '2A,Alien Attack,Axl Rose,Cthulhu,Giant robots!',
                '2B,Bouncing Babies,Brian May,nWoD,Not a very good idea.',
                ]))
    return Games.from_csv(games_file)


class TestPlayers(TestCase):
    def test_from_csv(self):
        players = get_players()

        self.assertEqual('Gary Gygax', players.players[0].name)
        self.assertEqual('TSR', players.players[0].team)
        self.assertEqual({'1A': 'G', '2A': 'G'}, players.players[0].slots)

        self.assertEqual('Joe Bloggs', players.players[1].name)
        self.assertEqual('TSR', players.players[1].team)
        self.assertEqual({'1A': 'P', '2A': 'P'}, players.players[1].slots)

        self.assertEqual('Jane Bloggs', players.players[2].name)
        self.assertEqual(None, players.players[2].team)
        self.assertEqual({'1B': 'X', '2B': 'X'}, players.players[2].slots)


class TestGames(TestCase):
    def test_from_csv(self):
        games = get_games()

        self.assertEqual('1A', games.games[0].slot)
        self.assertEqual('Aargh!', games.games[0].name)
        self.assertEqual('Alice Able', games.games[0].author)
        self.assertEqual('SillyDice', games.games[0].system)
        self.assertEqual('Camelot is a silly place.', games.games[0].blurb)
        self.assertEqual('Camelot is a silly place.', games.games[0].blurb)
        self.assertEqual('Camelot is a silly place.', games.games[0].blurb)

        # TODO: Finish this.


class TestGameTables(TestCase):
    def test_lay_tables(self):
        games = get_games()
        players = get_players()

        game_tables = GameTables(games, players, ['1A', '1B'])
        print game_tables.slotted_players
