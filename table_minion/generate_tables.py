# -*- test-case-name: table_minion.tests.test_generate_tables -*-

import random

from table_minion.game_tables import GameTable, GameTables


class GameTablesGenerator(object):
    def __init__(self, game, players, game_tables=None):
        self.game = game
        self.all_players = players

    @property
    def slot(self):
        return self.game.slot

    def generate_tables(self):
        game_tables = []
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
            game_tables.append(GameTable(self.game, gms.pop(0)))

        while players:
            for table in game_tables:
                if players:
                    table.add_player(players.pop())
        return game_tables

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

    def team_penalty_variances(self, game_tables):
        teams = set()
        for player in self.all_players:
            if player.team is not None:
                teams.add(player.team)
        if not teams:
            return {}
        team_penalties = dict((team, 0) for team in teams)
        for table in game_tables:
            table_penalties = table.team_penalties()
            for team in teams:
                team_penalties[team] += table_penalties.get(team, 0)
        min_penalty = min(team_penalties.values()) if len(teams) > 1 else 0
        for team in teams:
            team_penalties[team] = team_penalties[team] - min_penalty
        return sorted(
            [(p, t) for t, p in team_penalties.items()], reverse=True)

    def team_penalty_variance_total(self, game_tables):
        print self.team_penalty_variances(game_tables)
        return sum(p for p, t in self.team_penalty_variances(game_tables))

    def generate_lowest_penalty_tables(self, tries=100):
        table_sets = []
        for _ in xrange(tries):
            tables = self.generate_tables()
            table_sets.append(
                (self.team_penalty_variance_total(tables), tables))
        print sorted([p for p, _ in table_sets])
        return sorted(table_sets)[0][1]


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

    def generate_lowest_penalty_game_tables(self, slot, tries=100):
        generator = GameTablesGenerator(
            self.games[slot], self.slotted_players[slot])
        self.game_tables.set_tables_for_slot(
            slot, generator.generate_lowest_penalty_tables(tries))

    def generate_tables(self):
        self.game_tables = GameTables(self.games, self.players)
        self.arrange_players()
        for slot in self.slots:
            self.generate_game_tables(slot)
        return self.game_tables

    def generate_lowest_penalty_tables(self, tries=100):
        self.game_tables = GameTables(self.games, self.players)
        self.arrange_players()
        for slot in self.slots:
            self.generate_lowest_penalty_game_tables(slot, tries)
        return self.game_tables
