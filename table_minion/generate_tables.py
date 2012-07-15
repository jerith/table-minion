# -*- test-case-name: table_minion.tests.test_generate_tables -*-

import random

from table_minion.players import player_name


class GameTable(object):
    def __init__(self, slot, gm, players):
        self.slot = slot
        self.gm = gm
        self.players = players

    def __str__(self):
        return '<Table %s: %s\n%s\n>' % (
            self.slot, player_name(self.gm), '\n'.join([
                    '  %s' % player_name(player) for player in self.players]))

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
                    t.slot, player_name(t.gm), '\n'.join([
                            '  %s' % player_name(p) for p in t.players]))
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
            gms.extend([None] * (table_count - len(gms)))
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


class Con(object):
    def __init__(self):
        self.table_settings = {}

    def set_players(self, players):
        self.players = players

    def set_games(self, games):
        self.games = games

    def lay_tables(self, slots):
        pass
