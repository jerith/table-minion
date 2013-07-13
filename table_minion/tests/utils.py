from table_minion.players import Player, Players
from table_minion.games import Game, Games


def make_players(player_definitions):
    players = []
    for count, prefix, team, reg in player_definitions:
        players.extend(
            Player('%s %s' % (prefix, i), team, reg) for i in xrange(count))
    return Players(players)


def make_game(slot, **kw):
    kw.setdefault('name', 'Game %s' % (slot,))
    kw.setdefault('author', 'Author %s' % (slot,))
    kw.setdefault('system', 'System %s' % (slot,))
    kw.setdefault('blurb', 'Blurb %s' % (slot,))
    return Game(slot, **kw)


def make_games(slots, games_extras=None):
    if games_extras is None:
        games_extras = {}
    return Games(make_game(s, **games_extras.get(s, {})) for s in slots)
