from unittest import TestCase
from StringIO import StringIO

from table_minion.games import Games


def get_games():
    games_file = StringIO('\n'.join([
                'slot,name,author,system,blurb',
                '1A,Aargh!,Alice Able,SillyDice,Camelot is a silly place.',
                '1B,Business,Bob Bobson,SrsBsns,Make some RoI.',
                '2A,Alien Attack,Axl Rose,Cthulhu,Giant robots!',
                '2B,Bouncing Babies,Brian May,nWoD,Not a very good idea.',
                ]))
    return Games.from_csv(games_file)


class TestGames(TestCase):
    def test_from_csv(self):
        games = get_games()

        self.assertEqual('1A', games.games['1A'].slot)
        self.assertEqual('Aargh!', games.games['1A'].name)
        self.assertEqual('Alice Able', games.games['1A'].author)
        self.assertEqual('SillyDice', games.games['1A'].system)
        self.assertEqual('Camelot is a silly place.', games.games['1A'].blurb)
        self.assertEqual('Camelot is a silly place.', games.games['1A'].blurb)
        self.assertEqual('Camelot is a silly place.', games.games['1A'].blurb)

        # TODO: Finish this.
