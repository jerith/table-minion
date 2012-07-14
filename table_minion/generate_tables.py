# -*- test-case-name: table_minion.tests.test_generate_tables -*-

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


class Game(object):
    def __init__(self, slot, name, author, system, blurb):
        self.slot = slot
        self.name = name
        self.author = author
        self.system = system
        self.blurb = blurb

    def __str__(self):
        return '<Game %s - %s (%s) - %s: %s>' % (
            self.slot, self.name, self.system, self.author, self.blurb)


class Games(object):
    def __init__(self, games):
        self.games = games


    @classmethod
    def from_csv(cls, csv_file):
        reader = csv.DictReader(csv_file)
        games = []
        for game_dict in reader:
            games.append(Game(
                    game_dict['slot'],
                    game_dict['name'],
                    game_dict['author'],
                    game_dict['system'],
                    game_dict['blurb']))
        return cls(games)

    def __str__(self):
        return '<Ganes:\n%s\n>' % '\n'.join([
                '  %s' % game for games in self.games])


class GameTable(object):
    def __init__(self, slot, gm, players):
        self.slot = slot
        self.gm = gm
        self.players = players


class GameTables(object):
    def __init__(self, slots):
        self.slots = slots

    def lay_tables(self, player_list):
        raise NotImplementedError()

