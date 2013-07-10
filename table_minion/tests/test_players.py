from unittest import TestCase
from StringIO import StringIO

from table_minion.players import Player, Players


PLAYERS_CSV = '\r\n'.join([
    'name,team,1A,1B,2A,2B',
    'Gary Gygax,TSR,G,,G,',
    'Dave Arneson,TSR,P,,P,',
    'Jane Bloggs,,,X,,X',
    '',
])


class TestPlayers(TestCase):
    def test_player_equality(self):
        player = Player('Gary Gygax', 'TSR', {'1A': 'G'})
        self.assertEqual(player, player)
        self.assertEqual(player, Player('Gary Gygax', 'TSR', {'1A': 'G'}))
        self.assertNotEqual(player, 'Gary Gygax')
        self.assertNotEqual(player, Player('Gary Glitter', 'TSR', {'1A': 'G'}))
        self.assertNotEqual(player, Player('Gary Gygax', None, {'1A': 'G'}))
        self.assertNotEqual(player, Player('Gary Gygax', 'WotC', {'1A': 'G'}))
        self.assertNotEqual(player, Player('Gary Gygax', 'TSR', {}))
        self.assertNotEqual(player, Player('Gary Gygax', 'TSR', {'1A': 'P'}))

    def test_from_csv(self):
        players = Players.from_csv(StringIO(PLAYERS_CSV))

        self.assertEqual('Gary Gygax', players.players[0].name)
        self.assertEqual('TSR', players.players[0].team)
        self.assertEqual({'1A': 'G', '2A': 'G'}, players.players[0].slots)

        self.assertEqual('Dave Arneson', players.players[1].name)
        self.assertEqual('TSR', players.players[1].team)
        self.assertEqual({'1A': 'P', '2A': 'P'}, players.players[1].slots)

        self.assertEqual('Jane Bloggs', players.players[2].name)
        self.assertEqual(None, players.players[2].team)
        self.assertEqual({'1B': 'X', '2B': 'X'}, players.players[2].slots)

    def test_to_csv(self):
        players = Players([
            Player('Gary Gygax', 'TSR', {'1A': 'G', '2A': 'G'}),
            Player('Dave Arneson', 'TSR', {'1A': 'P', '2A': 'P'}),
            Player('Jane Bloggs', None, {'1B': 'X', '2B': 'X'}),
        ])

        players_csv = StringIO()
        players.to_csv(['1A', '1B', '2A', '2B'], players_csv)
        self.assertEqual(players_csv.getvalue(), PLAYERS_CSV)
