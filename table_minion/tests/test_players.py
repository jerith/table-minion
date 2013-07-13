import os.path
from unittest import TestCase
from StringIO import StringIO

from table_minion.players import Player, Players, player_name


class TestPlayer(TestCase):
    def test_equality(self):
        player = Player('Gary Gygax', 'TSR', {'1A': 'G'})
        self.assertEqual(player, player)
        self.assertEqual(player, Player('Gary Gygax', 'TSR', {'1A': 'G'}))
        self.assertNotEqual(player, None)
        self.assertNotEqual(player, 'Gary Gygax')
        self.assertFalse(player == 'Gary Gygax')  # To hit `==` instead of `!=`
        self.assertNotEqual(player, Player('Gary Glitter', 'TSR', {'1A': 'G'}))
        self.assertNotEqual(player, Player('Gary Gygax', None, {'1A': 'G'}))
        self.assertNotEqual(player, Player('Gary Gygax', 'WotC', {'1A': 'G'}))
        self.assertNotEqual(player, Player('Gary Gygax', 'TSR', {}))
        self.assertNotEqual(player, Player('Gary Gygax', 'TSR', {'1A': 'P'}))

    def test_repr(self):
        player = Player('Gary Gygax', 'TSR', {'1A': 'G'})
        self.assertEqual(str(player), repr(player))
        self.assertTrue('Gary Gygax' in repr(player))
        self.assertTrue('TSR' in repr(player))
        self.assertTrue('1A:G' in repr(player))

    def test_player_name(self):
        player1 = Player('Gary Gygax', 'TSR', {'1A': 'G'})
        player2 = Player('Gary Gygax', None, {'1A': 'G'})
        self.assertEqual('Gary Gygax (TSR)', player_name(player1))
        self.assertEqual('Gary Gygax', player_name(player2))
        self.assertEqual('(None)', player_name(None))


class TestPlayers(TestCase):
    def test_from_csv(self):
        players = Players.from_csv(StringIO('\n'.join([
            'name,team,1A,1B,2A,2B',
            'Gary Gygax,TSR,G,,G,',
            'Dave Arneson,TSR,P,,P,',
            'Jane Bloggs,,,X,,X',
        ])))
        self.assertEqual(list(players), [
            Player('Gary Gygax', 'TSR', {'1A': 'G', '2A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1A': 'P', '2A': 'P'}),
            Player('Jane Bloggs', None, {'1B': 'X', '2B': 'X'}),
        ])

    def test_from_imperfect_csv(self):
        players = Players.from_csv(StringIO('\n'.join([
            '',
            'Name,Team,First,Last,1a,1b,2a,2b',
            'Gary Gygax,TSR,Gary,Gygax,G,,g,',
            'Dave Arneson,TSR,Dave,Arneson,P,,p,',
            'Jane Bloggs,,Jane,Bloggs,,X,,x',
        ])))
        self.assertEqual(list(players), [
            Player('Gary Gygax', 'TSR', {'1a': 'G', '2a': 'G'}),
            Player('Dave Arneson', 'TSR', {'1a': 'P', '2a': 'P'}),
            Player('Jane Bloggs', None, {'1b': 'X', '2b': 'X'}),
        ])

    def test_from_xls(self):
        xls_file = open(os.path.join(os.path.dirname(__file__), 'players.xls'))
        players = Players.from_xls(xls_file.read())
        self.assertEqual(list(players), [
            Player('Gary Gygax', 'TSR', {'1A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1B': 'G'}),
        ])

    def test_to_csv(self):
        players = Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G', '2A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1A': 'P', '2A': 'P'}),
            Player('Jane Bloggs', None, {'1B': 'X', '2B': 'X'}),
        ])

        players_csv = StringIO()
        players.to_csv(['1A', '1B', '2A', '2B'], players_csv)
        self.assertEqual(players_csv.getvalue(), '\r\n'.join([
            'name,team,1A,1B,2A,2B',
            'Gary Gygax,TSR,G,,G,',
            'Dave Arneson,TSR,P,,P,',
            'Jane Bloggs,,,X,,X',
            '',
        ]))

    def test_get_slots(self):
        players = Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G', '2A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1A': 'P', '2A': 'P'}),
            Player('Jane Bloggs', None, {'1B': 'X'}),
        ])
        self.assertEqual(['1A', '1B', '2A'], players.get_slots())

    def test_get_player(self):
        players = Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G', '2A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1A': 'P', '2A': 'P'}),
            Player('Jane Bloggs', None, {'1B': 'X'}),
        ])
        self.assertEqual(None, players.get_player(None))
        self.assertEqual(None, players.get_player(''))
        self.assertEqual(list(players)[0], players.get_player('Gary Gygax'))
        self.assertRaises(ValueError, players.get_player, 'foo')

    def test_repr(self):
        player1 = Player('Gary Gygax', 'TSR', {'1A': 'G'})
        player2 = Player('Dave Arneson', 'TSR', {'1B': 'G'})
        players = Players([player1, player2])
        self.assertEqual(str(players), repr(players))
        self.assertTrue(repr(player1) in repr(players))
        self.assertTrue(repr(player2) in repr(players))
