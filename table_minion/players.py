# -*- test-case-name: table_minion.tests.test_players -*-


import re
import csv


SLOT_RE = re.compile(r'^[0-9]+[A-Z]$')


class Player(object):
    def __init__(self, name, team, slots):
        self.name = name
        self.team = team or None
        self.slots = slots

    def __str__(self):
        return '<Player %s (%s) %s>' % (
            self.name, self.team, self.slots)

    def __repr__(self):
        return str(self)


def player_name(player):
    if player is None:
        return '(None)'
    if player.team is not None:
        return '%s (%s)' % (player.name, player.team)
    return player.name


class Players(object):
    def __init__(self, players):
        self.players = players

    @classmethod
    def from_csv(cls, csv_file):
        reader = csv.DictReader(csv_file)
        players = []
        for player_dict in reader:
            slots = dict((k, v) for k, v in player_dict.iteritems()
                         if v and (SLOT_RE.match(k)))
            players.append(Player(
                    player_dict['name'],
                    player_dict['team'],
                    slots))
        return cls(players)

    def __str__(self):
        return '<Players:\n%s\n>' % '\n'.join([
                '  %s' % player for player in self.players])

    def __repr__(self):
        return str(self)
