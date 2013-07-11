# -*- test-case-name: table_minion.tests.test_players -*-


import re
import csv


SLOT_RE = re.compile(r'^[0-9]+[A-Z]?$')


class Player(object):
    def __init__(self, name, team, slots):
        self.name = name
        self.team = team or None
        self.slots = slots

    def _format_slots(self):
        return ', '.join(sorted(
            '%s:%s' % item for item in self.slots.iteritems()))

    def __str__(self):
        return '<Player %s (%s) %s>' % (
            self.name, self.team, self._format_slots())

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return all([
            self.name == other.name,
            self.team == other.team,
            self.slots == other.slots,
        ])


def player_name(player):
    if player is None:
        return '(None)'
    if player.team is not None:
        return '%s (%s)' % (player.name, player.team)
    return player.name


class Players(object):
    def __init__(self, players):
        self.players = players

    def __iter__(self):
        return iter(self.players)

    def get_slots(self):
        slots = set()
        for player in self.players:
            slots.update(player.slots.keys())
        return sorted(slots)

    def get_player(self, name):
        if not name:
            # This catches '' and None.
            return None
        for player in self.players:
            if player.name == name:
                return player
        raise ValueError('No player named %r' % (name,))

    @classmethod
    def from_dicts(cls, player_dicts):
        return cls([Player(**pdict) for pdict in player_dicts])

    @classmethod
    def from_csv(cls, csv_file):
        reader = csv.DictReader(csv_file)
        return cls.from_dicts([{
            'name': player_dict['name'],
            'team': player_dict['team'],
            'slots': dict((k, v) for k, v in player_dict.iteritems()
                          if v and (SLOT_RE.match(k)))
        } for player_dict in reader])

    def to_csv(self, slots, csv_file):
        fields = ['name', 'team'] + list(slots)
        writer = csv.DictWriter(csv_file, fields)
        writer.writerow(dict(zip(fields, fields)))
        for player in self.players:
            player_dict = {'name': player.name, 'team': player.team}
            player_dict.update(player.slots)
            writer.writerow(player_dict)

    def __str__(self):
        return '<Players:\n%s\n>' % '\n'.join([
                '  %s' % player for player in self.players])

    def __repr__(self):
        return str(self)
