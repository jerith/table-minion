# -*- test-case-name: table_minion.tests.test_games -*-

import csv


class Game(object):
    def __init__(self, slot, name, author, system, blurb,
                 max_players=6, min_players=4):
        self.slot = slot
        self.name = name
        self.author = author
        self.system = system
        self.blurb = blurb
        self.max_players = max_players
        self.min_players = min_players

    def __str__(self):
        return '<Game %s - %s (%s) - %s: %s (%s-%s)>' % (
            self.slot, self.name, self.system, self.author, self.blurb,
            self.min_players, self.max_players)

    def __repr__(self):
        return str(self)


class Games(object):
    def __init__(self, games):
        self.games = games

    def __iter__(self):
        return self.games.itervalues()

    def __getitem__(self, key):
        return self.games[key]

    @classmethod
    def from_dicts(cls, game_dicts):
        return cls(dict([
            (gdict['slot'], Game(**gdict)) for gdict in game_dicts]))

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

    def __str__(self):
        return '<Games:\n%s\n>' % '\n'.join([
                '  %s' % game for game in self.games])

    def __repr__(self):
        return str(self)
