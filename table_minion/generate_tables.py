# -*- test-case-name: table_minion.tests.test_generate_tables -*-

import csv
import random


class Player(object):
    def __init__(self, name, team, registration):
        self.name = name
        self.team = team or None
        self.registration = registration
        self.slots = dict(item for item in registration.items() if item[1])

    def get_name(self):
        name = self.name
        if self.team is not None:
            name = '%s (%s)' % (name, self.team)
        return name

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
        games = {}
        for game_dict in reader:
            if not game_dict.get('max_players', None):
                game_dict.pop('max_players', None)
            if not game_dict.get('min_players', None):
                game_dict.pop('min_players', None)
            games[game_dict['slot']] = Game(**game_dict)
        return cls(games)

    def __str__(self):
        return '<Games:\n%s\n>' % '\n'.join([
                '  %s' % game for game in self.games])

    def __repr__(self):
        return str(self)


class GameTable(object):
    def __init__(self, slot, gm, players):
        self.slot = slot
        self.gm = gm
        self.players = players

    def __str__(self):
        return '<Table %s: %s\n%s\n>' % (
            self.slot, self.gm.get_name(), '\n'.join([
                    '  %s' % player.get_name() for player in self.players]))

    def __repr__(self):
        return str(self)


class GameTables(object):
    def __init__(self, games, players, slots):
        self.games = games
        self.players = players
        self.slots = slots
        self.lay_tables()

    def __str__(self):
        return '<Tables:\n%s\n>' % '\n'.join([
                '  %s' % table for table in self.tables])

    def __repr__(self):
        return str(self)

    def make_list(self):
        return '\n'.join([
                '%s: %s\n%s\n' % (
                    t.slot, t.gm.get_name(), '\n'.join([
                            '  %s' % p.get_name() for p in t.players]))
                for t in self.tables])

    def validate_player(self, player):
        return sum(1 for slot in self.slots if slot in player.slots) <= 1

    def arrange_players(self):
        slotted_players = {}
        self.invalid_players = []
        for player in self.players.players:
            if not self.validate_player(player):
                self.invalid_players.append(player)
                print "WARNING: Invalid player:", player
                continue
            for slot in self.slots:
                if slot in player.slots:
                    slotted_players.setdefault(slot, []).append(player)
        return slotted_players

    def lay_tables(self):
        self.slotted_players = self.arrange_players()
        self.tables = []
        for slot in self.slots:
            self.tables.extend(self.lay_game_tables(slot))

    def calculate_table_data(self, game, players, gms, either):
        player_count = len(players + either)
        table_count, remainder = divmod(player_count, game.max_players)
        if remainder:
            table_count += 1

        while either and (len(gms) < table_count):
            gms.append(either.pop())
        if len(gms) < table_count:
            print "WARNING: Insufficient GMs."
            table_count = len(gms)

        players.extend(either)
        if len(players) > table_count * game.max_players:
            print "WARNING: Too many players."
            players = players[:table_count * game.max_players]
        if len(players) < table_count * game.min_players:
            print "WARNING: Insufficient players."

        return table_count, players, gms

    def lay_game_tables(self, slot):
        all_players = self.slotted_players[slot]
        table_count, players, gms = self.calculate_table_data(
            self.games.games[slot],
            [p for p in all_players if p.slots[slot] == 'P'],
            [p for p in all_players if p.slots[slot] == 'G'],
            [p for p in all_players if p.slots[slot] == 'X'])

        tables_players = [list() for i in range(table_count)]
        while players:
            for table_players in tables_players:
                if not players:
                    break
                player = random.choice(players)
                players.remove(player)
                table_players.append(player)

        game_tables = []
        for table_players in tables_players:
            game_table = GameTable(slot, random.choice(gms), table_players)
            gms.remove(game_table.gm)
            game_tables.append(game_table)
        return game_tables
