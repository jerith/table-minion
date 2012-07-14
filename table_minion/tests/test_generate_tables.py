from unittest import TestCase
from StringIO import StringIO

from table_minion.generate_tables import Players


class TestPlayerList(TestCase):
    def test_from_csv(self):
        players_file = StringIO('\n'.join([
                    'name,team,1A,1B,2A,2B',
                    'Gary Gygax,TSR,G,,G,',
                    'Joe Bloggs,TSR,P,,P,',
                    'Jane Bloggs,,,X,,X',
                    ]))
        players = Players.from_csv(players_file)

        self.assertEqual('Gary Gygax', players.players[0].name)
        self.assertEqual('TSR', players.players[0].team)
        self.assertEqual({'1A': 'G', '2A': 'G'}, players.players[0].slots)

        self.assertEqual('Joe Bloggs', players.players[1].name)
        self.assertEqual('TSR', players.players[1].team)
        self.assertEqual({'1A': 'P', '2A': 'P'}, players.players[1].slots)

        self.assertEqual('Jane Bloggs', players.players[2].name)
        self.assertEqual(None, players.players[2].team)
        self.assertEqual({'1B': 'X', '2B': 'X'}, players.players[2].slots)
