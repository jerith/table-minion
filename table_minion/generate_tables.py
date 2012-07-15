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

    def __repr__(self):
        return str(self)


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

    @classmethod
    def from_csv(cls, csv_file):
        reader = csv.DictReader(csv_file)
        games = []
        for game_dict in reader:
            if not game_dict.get('max_players', None):
                game_dict.pop('max_players', None)
            if not game_dict.get('min_players', None):
                game_dict.pop('min_players', None)
            games.append(Game(**game_dict))
        return cls(games)

    def __str__(self):
        return '<Ganes:\n%s\n>' % '\n'.join([
                '  %s' % game for game in self.games])

    def __repr__(self):
        return str(self)


class GameTable(object):
    def __init__(self, slot, gm, players):
        self.slot = slot
        self.gm = gm
        self.players = players


class GameTables(object):
    def __init__(self, games, players, slots):
        self.games = games
        self.players = players
        self.slots = slots
        self.lay_tables()

    def validate_player(self, player):
        return sum(1 for slot in self.slots if slot in player.slots) <= 1

    def arrange_players(self):
        slotted_players = {}
        self.invalid_players = []
        for player in self.players.players:
            if not self.validate_player(player):
                self.invalid_players.append(player)
                print player
                continue
            for slot in self.slots:
                if slot in player.slots:
                    slotted_players.setdefault(slot, []).append(player)
        return slotted_players

    def lay_tables(self):
        self.slotted_players = self.arrange_players()
