# -*- test-case-name: table_minion.tests.test_games -*-

import csv

import xlrd


class Game(object):
    def __init__(self, slot, name, author, system, blurb,
                 min_players=4, max_players=6):
        self.slot = slot
        self.name = name
        self.author = author
        self.system = system
        self.blurb = blurb
        self.min_players = min_players
        self.max_players = max_players

    def player_count(self):
        if self.min_players == self.max_players:
            return str(self.max_players)
        return "%s-%s" % (self.min_players, self.max_players)

    def __str__(self):
        return '<Game %s - %s (%s) - %s: %s (%s-%s)>' % (
            self.slot, self.name, self.system, self.author, self.blurb,
            self.min_players, self.max_players)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Game):
            return False
        return all([
            self.slot == other.slot,
            self.name == other.name,
            self.author == other.author,
            self.system == other.system,
            self.blurb == other.blurb,
            self.min_players == other.min_players,
            self.max_players == other.max_players,
        ])


class Games(object):
    def __init__(self, games):
        self.games = {}
        for game in games:
            self.games[game.slot] = game

    def __iter__(self):
        return self.games.itervalues()

    def __getitem__(self, key):
        return self.games[key]

    @property
    def slots(self):
        return self.games.keys()

    @classmethod
    def from_dicts(cls, game_dicts):
        return cls(Game(**game_dict) for game_dict in game_dicts)

    @classmethod
    def from_csv(cls, csv_file):
        reader = csv.DictReader(csv_file)
        games = []
        for game_dict in reader:
            max_players = game_dict.pop('max_players', None)
            if max_players:
                game_dict['max_players'] = int(max_players)
            min_players = game_dict.pop('min_players', None)
            if min_players:
                game_dict['min_players'] = int(min_players)
            games.append(game_dict)
        return cls.from_dicts(games)

    @classmethod
    def from_xls(cls, xls_data):
        book = xlrd.open_workbook(file_contents=xls_data)
        sheet = book.sheet_by_index(0)
        headers = sheet.row_values(0)
        return cls.from_dicts(
            dict(zip(headers, sheet.row_values(rowx)))
            for rowx in xrange(1, sheet.nrows))

    def to_csv(self, csv_file):
        fields = [
            'slot', 'name', 'author', 'system', 'blurb', 'min_players',
            'max_players']
        writer = csv.DictWriter(csv_file, fields)
        writer.writerow(dict(zip(fields, fields)))
        for slot, game in sorted(self.games.items()):
            writer.writerow({
                'slot': game.slot,
                'name': game.name,
                'author': game.author,
                'system': game.system,
                'blurb': game.blurb,
                'min_players': game.min_players,
                'max_players': game.max_players,
            })

    def __str__(self):
        return '<Games:\n%s\n>' % '\n'.join([
            '  %s' % game for game in self.games])

    def __repr__(self):
        return str(self)
