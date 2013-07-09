from unittest import TestCase
from StringIO import StringIO

from table_minion.games import Game, Games


GAMES_CSV = '\r\n'.join([
    'slot,name,author,system,blurb,min_players,max_players',
    '1A,Aargh!,Alice Able,SillyDice,Camelot is a silly place.,,',
    '1B,Bouncing Babies,Brian May,nWoD,Not a very good idea.,5,7',
    '2A,Alien Attack,Axl Rose,Cthulhu,Giant robots!,,',
    '2B,Business,Bob Bobson,SrsBsns,Make some RoI.,,',
    '',
])


class TestGames(TestCase):
    def test_from_csv(self):
        games = Games.from_csv(StringIO(GAMES_CSV))

        self.assertEqual('1A', games['1A'].slot)
        self.assertEqual('Aargh!', games['1A'].name)
        self.assertEqual('Alice Able', games['1A'].author)
        self.assertEqual('SillyDice', games['1A'].system)
        self.assertEqual('Camelot is a silly place.', games['1A'].blurb)
        self.assertEqual(4, games['1A'].min_players)
        self.assertEqual(6, games['1A'].max_players)

        self.assertEqual(5, games['1B'].min_players)
        self.assertEqual(7, games['1B'].max_players)

    def test_to_csv(self):
        games = Games({
            '1A': Game(
                '1A', 'Aargh!', 'Alice Able', 'SillyDice',
                'Camelot is a silly place.'),
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
            games_csv.getvalue(), GAMES_CSV.replace(',,\r', ',4,6\r'))
