import os.path
from unittest import TestCase
from StringIO import StringIO

from table_minion.games import Game, Games


class TestGames(TestCase):
    def test_from_csv(self):
        games = Games.from_csv(StringIO('\n'.join([
            'slot,name,author,system,blurb,min_players,max_players',
            '1A,Aargh!,Alice Able,SillyDice,Camelot is a silly place.,,',
            '1B,Bouncing Babies,Brian May,nWoD,Not a very good idea.,5,7',
            '2A,Alien Attack,Axl Rose,Cthulhu,Giant robots!,,',
            '2B,Business,Bob Bobson,SrsBsns,Make some RoI.,,',
        ])))
        self.assertEqual(list(games), [
            Game('1A', 'Aargh!', 'Alice Able', 'SillyDice',
                 'Camelot is a silly place.', 4, 6),
            Game('1B', 'Bouncing Babies', 'Brian May', 'nWoD',
                 'Not a very good idea.', 5, 7),
            Game('2A', 'Alien Attack', 'Axl Rose', 'Cthulhu', 'Giant robots!'),
            Game('2B', 'Business', 'Bob Bobson', 'SrsBsns', 'Make some RoI.'),
        ])

    def test_from_xls(self):
        xls_file = open(os.path.join(os.path.dirname(__file__), 'games.xls'))
        games = Games.from_xls(xls_file.read())
        self.assertEqual(list(games), [
            Game('1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6),
            Game('1B', 'Game 1B', 'Author 1B', 'System 1B', 'Blurb 1B', 5, 5),
        ])

    def test_to_csv(self):
        games = Games({
            '1A': Game(
                '1A', 'Aargh!', 'Alice Able', 'SillyDice',
                'Camelot is a silly place.', 4, 6),
            '1B': Game(
                '1B', 'Bouncing Babies', 'Brian May', 'nWoD',
                'Not a very good idea.', 5, 7),
            '2A': Game(
                '2A', 'Alien Attack', 'Axl Rose', 'Cthulhu', 'Giant robots!'),
            '2B': Game(
                '2B', 'Business', 'Bob Bobson', 'SrsBsns', 'Make some RoI.'),
        })
        games_csv = StringIO()
        games.to_csv(games_csv)
        self.assertEqual(
            games_csv.getvalue(), '\r\n'.join([
                'slot,name,author,system,blurb,min_players,max_players',
                '1A,Aargh!,Alice Able,SillyDice,Camelot is a silly place.,4,6',
                '1B,Bouncing Babies,Brian May,nWoD,Not a very good idea.,5,7',
                '2A,Alien Attack,Axl Rose,Cthulhu,Giant robots!,4,6',
                '2B,Business,Bob Bobson,SrsBsns,Make some RoI.,4,6',
                '',
            ]))
