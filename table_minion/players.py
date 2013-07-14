# -*- test-case-name: table_minion.tests.test_players -*-


import re
import csv

import xlrd


SLOT_RE = re.compile(r'^[0-9]+[A-Za-z]?$')


class Player(object):
    def __init__(self, name, team, slots):
        self.name = name
        self.team = team or None
        self.slots = dict((k, v.upper()) for k, v in slots.iteritems())

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
    def _player_dict_from_row(cls, row):
        for field in row.keys():
            if field and field.lower() in ('name', 'team'):
                row[field.lower()] = row[field]
        return {
            'name': row['name'],
            'team': row['team'],
            'slots': dict((k, v) for k, v in row.iteritems()
                          if v and (SLOT_RE.match(k)))
        }

    @classmethod
    def from_csv(cls, csv_file):
        rows = [line for line in csv_file.readlines() if line.strip()]
        reader = csv.DictReader(rows)
        return cls.from_dicts(cls._player_dict_from_row(row) for row in reader)

    @classmethod
    def from_xls(cls, xls_data):
        book = xlrd.open_workbook(file_contents=xls_data)
        sheet = book.sheet_by_index(0)
        headers = None
        player_dicts = []
        for rowx in xrange(sheet.nrows):
            row = sheet.row_values(rowx)
            if not any(bool(v) for v in row):
                continue
            if headers is None:
                headers = row
                continue
            player_dicts.append(
                cls._player_dict_from_row(dict(zip(headers, row))))
        return cls.from_dicts(player_dicts)

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
