# -*- test-case-name: table_minion.tests.test_generate_tables -*-

import random

from table_minion.game_tables import GameTable, GameTables


class GameTablesGenerator(object):
    def __init__(self, game, players, game_tables=None):
        self.game = game
        print game
        self.all_players = players
        self.game_tables = game_tables if game_tables is not None else []

    @property
    def slot(self):
        return self.game.slot

    def generate_tables(self):
        self.game_tables = []
        self.gms = [p for p in self.all_players if p.slots[self.slot] == 'G']
        self.players = [
            p for p in self.all_players if p.slots[self.slot] == 'P']
        self.allocate_either(
            [p for p in self.all_players if p.slots[self.slot] == 'X'])

        # Taking a sample equal to the population size is equivalent to copying
        # and then shuffling.
        players = random.sample(self.players, len(self.players))
        gms = random.sample(self.gms, len(self.gms))
        gms.extend([None] * self.num_tables_needed())

        for _ in xrange(self.num_tables_needed()):
            self.game_tables.append(GameTable(self.game, gms.pop(0)))

        while players:
            for table in self.game_tables:
                if players:
                    table.add_player(players.pop())
        return self.game_tables

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


class AllTablesGenerator(object):
    def __init__(self, games, players):
        self.games = games
        self.players = players

    @property
    def slots(self):
        return self.games.slots

    def __str__(self):
        return '<Tables:\n%s\n>' % '\n'.join([
                '  %s' % table for table in self.tables])

    def __repr__(self):
        return str(self)

    def arrange_players(self):
        self.slotted_players = {}
        self.invalid_players = []
        for player in self.players:
            valid = True
            if not player.slots:
                valid = False
            for slot in player.slots:
                if slot not in self.slots:
                    valid = False
            if not valid:
                self.invalid_players.append(player)
                continue

            for slot in player.slots:
                self.slotted_players.setdefault(slot, []).append(player)
        return self.slotted_players

    def generate_game_tables(self, slot):
        generator = GameTablesGenerator(
            self.games[slot], self.slotted_players[slot])
        self.game_tables.set_tables_for_slot(slot, generator.generate_tables())

    def generate_tables(self):
        self.game_tables = GameTables(self.games, self.players)
        self.arrange_players()
        for slot in self.slots:
            self.generate_game_tables(slot)
        return self.game_tables
