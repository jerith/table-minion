# -*- test-case-name: table_minion.tests.test_players -*-


import csv


class Player(object):
    def __init__(self, name, team, registration):
        self.name = name
        self.team = team or None
        self.registration = registration
        self.slots = dict(item for item in registration.items() if item[1])

    def __str__(self):
        return '<Player %s (%s) %s>' % (
            self.name, self.team, self.slots)

    def __repr__(self):
        return str(self)


def get_name(player):
    if player is None:
        return '(None)'
    name = player.name
    if player.team is not None:
        name = '%s (%s)' % (name, player.team)
    return name


class Players(object):
    def __init__(self, players):
        self.players = players

    @classmethod
    def from_csv(cls, csv_file):
        reader = csv.DictReader(csv_file)
        players = []
        for player_dict in reader:
            players.append(Player(
                    player_dict.pop('name'),
                    player_dict.pop('team'),
                    player_dict))
        return cls(players)

    def __str__(self):
        return '<Players:\n%s\n>' % '\n'.join([
                '  %s' % player for player in self.players])

    def __repr__(self):
        return str(self)
