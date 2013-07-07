import json
import sqlite3

from flask import g

from table_minion.players import Player, Players
from table_minion.games import Game, Games
from table_minion.generate_tables import GameTable


# TODO: Something less horrible than this.

DATABASE = 'table-minion.db'

SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS players (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  team TEXT
);

CREATE TABLE IF NOT EXISTS games (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slot TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  author TEXT NOT NULL,
  system TEXT NOT NULL,
  blurb TEXT NOT NULL,
  min_players INTEGER NOT NULL,
  max_players INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS player_registrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  player INTEGER NOT NULL,
  slot TEXT NOT NULL,
  registration_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_tables (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slot TEXT NOT NULL,
  data TEXT NOT NULL
);
"""

CLEAR_SQL = r"""
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS player_registrations;
DROP TABLE IF EXISTS game_tables;
"""


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_db():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db(clear=False):
    db = get_db()
    if clear:
        db.cursor().executescript(CLEAR_SQL)
    db.cursor().executescript(SCHEMA_SQL)
    db.commit()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def commit_db():
    get_db().commit()


# The following should really be models of some kind.


def insert_player(player, commit=True):
    query_db(
        'INSERT INTO players (name, team) VALUES (?, ?);',
        (player.name, player.team))
    [player_id] = query_db('SELECT last_insert_rowid();', one=True)
    for slot, reg_type in player.slots.iteritems():
        query_db('''INSERT INTO player_registrations
                    (player, slot, registration_type)
                    VALUES (?, ?, ?);''',
                 (player_id, slot, reg_type))
    if commit:
        commit_db()
    return player_id


def import_players(players, delete=True):
    for player in players:
        insert_player(player, commit=False)
    commit_db()


def get_players():
    rows = query_db('''
        SELECT p.id AS id, name, team, slot, registration_type
        FROM players AS p
        LEFT JOIN player_registrations AS pr ON p.id=pr.player;
        ''')
    players = {}
    for row in rows:
        player_dict = players.setdefault(row['id'], {
            'name': row['name'],
            'team': row['team'],
            'slots': {},
        })
        if row['slot'] is not None:
            player_dict['slots'][row['slot']] = row['registration_type']
    return Players.from_dicts(players.values())


def get_player(name):
    rows = query_db('''
        SELECT p.id AS id, name, team, slot, registration_type
        FROM players AS p
        LEFT JOIN player_registrations AS pr ON p.id=pr.player
        WHERE p.name=?;
        ''', (name,))

    slots = dict([
        (row['slot'], row['registration_type']) for row in rows if row['slot']
    ])
    return Player(rows[0]['name'], rows[0]['team'], slots)


def insert_game(game, commit=True):
    query_db('''
        INSERT INTO games
        (slot, name, author, system, blurb, min_players, max_players)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        ''', (
            game.slot, game.name, game.author, game.system, game.blurb,
            game.min_players, game.max_players,
        ))
    [game_id] = query_db('SELECT last_insert_rowid();', one=True)
    if commit:
        commit_db()
    return game_id


def import_games(games, delete=True):
    for game in games:
        insert_game(game, commit=False)
    commit_db()


def get_games():
    rows = query_db('''
        SELECT slot, name, author, system, blurb, min_players, max_players
        FROM games;
        ''')
    return Games.from_dicts([dict(zip(row.keys(), row)) for row in rows])


def get_game(slot):
    row = query_db('''
        SELECT slot, name, author, system, blurb, min_players, max_players
        FROM games WHERE slot=?;
        ''', (slot,), one=True)
    return Game(**dict(zip(row.keys(), row)))


def set_game_tables(slot, game_tables):
    query_db('DELETE FROM game_tables WHERE slot=?;', (slot,))
    for game_table in game_tables:
        data = {
            'gm': game_table.gm.name if game_table.gm else None,
            'players': [p.name for p in game_table.players],
        }
        query_db(
            'INSERT INTO game_tables (slot, data) VALUES (?, ?);',
            (slot, json.dumps(data)))
    commit_db()


def get_game_tables(slot):
    rows = query_db('SELECT data FROM game_tables WHERE slot=?;', (slot,))
    game_tables = []
    for row in rows:
        data = json.loads(row['data'])
        gm = get_player(data['gm']) if data['gm'] else None
        players = [get_player(name) for name in data['players']]
        game_tables.append(GameTable(slot, gm, players))
    return game_tables
