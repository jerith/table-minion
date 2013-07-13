import os.path
from unittest import TestCase
from StringIO import StringIO

from table_minion.games import Game, Games


class TestGame(TestCase):
    def test_equality(self):
        game = Game(
            '1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6)
        self.assertEqual(game, game)
        self.assertEqual(game, Game(
            '1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6))
        self.assertNotEqual(game, None)
        self.assertNotEqual(game, '1A')
        self.assertFalse(game == '1A')  # To hit `==` instead of `!=`
        self.assertNotEqual(game, Game(
            '2B', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6))
        self.assertNotEqual(game, Game(
            '1A', 'Game 2B', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 6))
        self.assertNotEqual(game, Game(
            '1A', 'Game 1A', 'Author 2B', 'System 1A', 'Blurb 1A', 4, 6))
        self.assertNotEqual(game, Game(
            '1A', 'Game 1A', 'Author 1A', 'System 2B', 'Blurb 1A', 4, 6))
        self.assertNotEqual(game, Game(
            '1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 2B', 4, 6))
        self.assertNotEqual(game, Game(
            '1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 5, 6))
        self.assertNotEqual(game, Game(
            '1A', 'Game 1A', 'Author 1A', 'System 1A', 'Blurb 1A', 4, 5))

    def test_repr(self):
        game = Game(
            '1A', 'Game A1', 'Author A1', 'System A1', 'Blurb A1', 4, 6)
        self.assertEqual(str(game), repr(game))
        self.assertTrue('1A' in repr(game))
        self.assertTrue('Game A1' in repr(game))
        self.assertTrue('4-6' in repr(game))


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
        games = Games([
            Game('1A', 'Aargh!', 'Alice Able', 'SillyDice',
                 'Camelot is a silly place.', 4, 6),
            Game('1B', 'Bouncing Babies', 'Brian May', 'nWoD',
                 'Not a very good idea.', 5, 7),
            Game('2A', 'Alien Attack', 'Axl Rose', 'Cthulhu', 'Giant robots!'),
            Game('2B', 'Business', 'Bob Bobson', 'SrsBsns', 'Make some RoI.'),
        ])
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

    def test_repr(self):
        game1a = Game(
            '1A', 'Game A1', 'Author A1', 'System A1', 'Blurb A1', 4, 6)
        game1b = Game(
            '1B', 'Game B1', 'Author B1', 'System B1', 'Blurb B1', 5, 5)
        games = Games([game1a, game1b])
        self.assertEqual(str(games), repr(games))
        self.assertTrue(repr(game1a) in repr(games))
        self.assertTrue(repr(game1b) in repr(games))
