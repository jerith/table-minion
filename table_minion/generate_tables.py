# -*- test-case-name: table_minion.tests.test_generate_tables -*-

import random

from table_minion.players import player_name


class GameTable(object):
    def __init__(self, slot, gm, players=None):
        self.slot = slot
        self.gm = gm
        if players is None:
            players = []
        self.players = players

    def __str__(self):
        return '<Table %s: %s\n%s\n>' % (
            self.slot, player_name(self.gm), '\n'.join([
                    '  %s' % player_name(player) for player in self.players]))

    def __repr__(self):
        return str(self)


class GameTables(object):
    def __init__(self, slot, game, players):
        self.slot = slot
        self.game = game
        self.all_players = players

        self.warnings = []
        self.players = [p for p in players if p.slots[slot] == 'P']
        self.gms = [p for p in players if p.slots[slot] == 'G']
        self.allocate_either([p for p in players if p.slots[slot] == 'X'])
        self.lay_tables()

    def num_tables_needed(self):
        table_count, remainder = divmod(
            len(self.players), self.game.max_players)
        if remainder:
            table_count += 1
        return table_count

    def allocate_either(self, either):
        while either:
            if len(self.gms) < self.num_tables_needed():
                self.gms.append(either.pop())
            else:
                self.players.append(either.pop())

    def check_participant_counts(self):
        table_count = self.num_tables_needed()

        if len(self.gms) > table_count:
            self.warnings.append("Too many GMs.")
            self.gms[table_count:] = []
        elif len(self.gms) < table_count:
            self.warnings.append("Not enough GMs.")
            self.gms.extend([None] * (table_count - len(self.gms)))

        if len(self.players) > table_count * self.game.max_players:
            self.warnings.append("Too many players.")
            self.players[table_count * self.game.max_players:] = []
        elif len(self.players) < table_count * self.game.min_players:
            self.warnings.append("Not enough players.")

    def lay_tables(self):
        self.check_participant_counts()

        # Taking a sample equal to the population size is equivalent to copying
        # and then shuffling.
        players = random.sample(self.players, len(self.players))
        gms = random.sample(self.gms, len(self.gms))

        self.tables = []
        for _ in xrange(self.num_tables_needed()):
            self.tables.append(GameTable(self.slot, gms.pop()))

        while players:
            for table in self.tables:
                if players:
                    table.players.append(players.pop())


class Tables(object):
    def __init__(self, games, players, slots):
        self.games = games
        self.players = players
        self.slots = slots
        self.lay_tables()

    @property
    def tables(self):
        tables = []
        for game_tables in self.game_tables:
            tables.extend(game_tables.tables)
        return tables

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

    def lay_game_tables(self, slot):
        self.game_tables.append(GameTables(
            slot, self.games.games[slot], self.slotted_players[slot]))

    def lay_tables(self):
        self.game_tables = []
        self.slotted_players = self.arrange_players()
        for slot in self.slots:
            self.lay_game_tables(slot)


class Con(object):
    def __init__(self):
        self.table_settings = {}

    def set_players(self, players):
        self.players = players

    def set_games(self, games):
        self.games = games

    def lay_tables(self, slots):
        pass
