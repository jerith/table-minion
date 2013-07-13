# -*- test-case-name: table_minion.tests.test_game_tables -*-

import csv

from table_minion.players import player_name


class GameTable(object):
    def __init__(self, game, gm, players=None):
        self.game = game
        self.gm = gm
        self.players = players if players is not None else []
        self.update_warnings()

    @property
    def slot(self):
        return self.game.slot

    def update_warnings(self):
        self.warnings = []
        self.info = []
        if self.gm is None:
            self.warnings.append('No gm.')
        elif self.gm.slots.get(self.slot, None) not in 'XG':
            self.warnings.append('%s not registered as a GM.' % (
                player_name(self.gm)))

        if len(self.players) > self.game.max_players:
            num = len(self.players) - self.game.max_players
            self.warnings.append('%s player%s too many.' % (
                num, 's' if num > 1 else ''))
        elif len(self.players) < self.game.min_players:
            num = self.game.min_players - len(self.players)
            self.warnings.append('%s player%s too few.' % (
                num, 's' if num > 1 else ''))

        for player in self.players:
            if player.slots.get(self.slot, None) not in 'XP':
                self.warnings.append('%s not registered as a player.' % (
                    player_name(player)))

        if self.game.min_players <= len(self.players) < self.game.max_players:
            num = self.game.max_players - len(self.players)
            self.info.append('%s slot%s available.' % (
                num, 's' if num > 1 else ''))

    def set_game(self, game):
        self.game = game
        self.update_warnings()

    def set_gm(self, gm):
        self.gm = gm
        self.update_warnings()

    def set_players(self, players):
        self.players = players
        self.update_warnings()

    def add_player(self, player):
        self.players.append(player)
        self.update_warnings()

    def table_teams(self):
        teams = set()
        for player in self.players + [self.gm]:
            if player and player.team is not None:
                teams.add(player.team)
        return teams

    def team_penalties(self):
        teams = self.table_teams()
        if not teams:
            return {}
        team_players = dict((team, []) for team in teams)
        for player in self.players:
            if player.team is not None:
                team_players[player.team].append(player)
        team_penalties = {}
        for team in teams:
            penalty = sum(2 * i for i in xrange(len(team_players[team])))
            if penalty and self.gm and self.gm.team == team:
                penalty += 1
            team_penalties[team] = penalty
        return team_penalties

    def __str__(self):
        return '<Table %s: %s\n%s\n>' % (
            self.slot, player_name(self.gm), '\n'.join([
                '  %s' % player_name(player) for player in self.players]))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, GameTable):
            return False
        return all([
            self.game == other.game,
            self.gm == other.gm,
            self.players == other.players,
            self.warnings == other.warnings,
        ])


class GameTables(object):
    def __init__(self, games, players, game_tables=None):
        self.games = games
        self.players = players
        self.game_tables = game_tables if game_tables is not None else {}

    @property
    def slots(self):
        return sorted(self.games.slots)

    def __getitem__(self, slot):
        self.games[slot]  # To make sure the game exists.
        return self.game_tables.get(slot, [])

    def all_tables(self):
        for slot, game_tables in sorted(self.game_tables.items()):
            for game_table in game_tables:
                yield game_table

    def max_tables_per_slot(self):
        if not self.game_tables:
            return 1
        return max(len(gt) for gt in self.game_tables.values())

    def set_tables_for_slot(self, slot, game_tables):
        self.game_tables[slot] = game_tables

    @classmethod
    def from_dicts(cls, games, players, game_table_dicts):
        game_tables = {}
        for game_table_dict in game_table_dicts:
            slot = game_table_dict['slot']
            game_tables.setdefault(slot, []).append(GameTable(
                games[slot], players.get_player(game_table_dict['gm']),
                [players.get_player(p) for p in game_table_dict['players']]))
        return cls(games, players, game_tables)

    @classmethod
    def from_csv(cls, games, players, csv_file):
        reader = csv.DictReader(csv_file, restkey='extra_players')
        return cls.from_dicts(games, players, [{
            'slot': row['slot'],
            'gm': row['gm'],
            'players': [row['players']] + row.get('extra_players', []),
        } for row in list(reader)])

    def to_csv(self, csv_file):
        writer = csv.writer(csv_file)
        writer.writerow(['slot', 'gm', 'players'])
        for game_table in self.all_tables():
            gm = game_table.gm.name if game_table.gm is not None else None
            writer.writerow(
                [game_table.slot, gm] + [p.name for p in game_table.players])

    def to_list_csv(self, csv_file):
        writer = csv.writer(csv_file)
        for slot, tables in sorted(self.game_tables.items()):
            for num, game_table in enumerate(tables):
                writer.writerow(['Table %s (%s: %s)' % (
                    num + 1, slot, game_table.game.name)])
                writer.writerow(['GM: %s' % (player_name(game_table.gm),)])
                for player in game_table.players:
                    writer.writerow([player_name(player)])
                writer.writerow([])

    def __str__(self):
        return '<GameTables:\n%s\n>' % '\n'.join([
            '  %s' % game_table for game_table in self.all_tables()])

    def __repr__(self):
        return str(self)
