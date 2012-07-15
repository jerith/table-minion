from StringIO import StringIO

from table_minion.players import Player, Players
from table_minion.games import Game, Games


def make_csv(lines):
    return StringIO('\n'.join(lines))


def make_players(player_definitions):
    players = []
    for count, prefix, team, reg in player_definitions:
        players.extend([Player('%s %s' % (prefix, i), team, reg)
                        for i in range(count)])
    return Players(players)


def make_games(slots):
    return Games(dict(
            (s, Game(s, 'Game %s' % s, 'Author', 'System', 'Blurb'))
            for s in slots))
