# -*- test-case-name: table_minion.tests.test_web -*-

from StringIO import StringIO

from flask import (
    Flask, request, abort, url_for, redirect, flash, render_template,
    make_response)

from table_minion import db
from table_minion.players import Players, player_name
from table_minion.games import Games
from table_minion.game_tables import GameTables
from table_minion.generate_tables import (
    GameTablesGenerator, AllTablesGenerator)


app = Flask('table_minion')
app.config.from_object('table_minion.settings')
app.config.from_envvar('TABLE_MINION_SETTINGS', silent=True)


@app.before_request
def before_request():
    db.open_db(app)


@app.teardown_request
def teardown_request(exception):
    db.close_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/')
def admin():
    return render_template('admin.html')


@app.route('/create_database', methods=['POST'])
def create_database():
    db.init_db(app, clear=request.form.get('delete', False))
    flash("Database created.")
    return redirect(url_for('admin'))


@app.route('/games/')
def games():
    games = sorted(db.get_games(), key=lambda g: g.slot)
    return render_template('games.html', games=games)


@app.route('/games/games.csv')
def games_csv():
    games_csv = StringIO()
    db.get_games().to_csv(games_csv)
    resp = make_response(games_csv.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    return resp


@app.route('/games/upload', methods=['POST'])
def games_upload():
    f = request.files['games_file']
    if f.filename.endswith('.csv'):
        games = Games.from_csv(f)
    else:
        games = Games.from_xls(f.read())
    db.import_games(games, delete=True)
    flash("Games imported.")
    return redirect(url_for('games'))


@app.route('/games/<slot>/')
def game(slot):
    try:
        game = db.get_game(slot)
    except db.NotFound:
        abort(404)
    game_tables = db.get_game_tables(slot)
    return render_template(
        'game.html', game=game, game_tables=game_tables,
        player_name=player_name, len=len)


@app.route('/games/<slot>/table_list.csv')
def game_table_list_csv(slot):
    try:
        game = db.get_game(slot)
    except db.NotFound:
        abort(404)
    players = db.get_players_for_game(slot)
    game_tables = GameTables([game], players, {slot: db.get_game_tables(slot)})
    table_list_csv = StringIO()
    game_tables.to_list_csv(table_list_csv)
    resp = make_response(table_list_csv.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    return resp


@app.route('/games/<slot>/generate_tables', methods=['POST'])
def game_generate_tables(slot):
    game = db.get_game(slot)
    players = db.get_players_for_game(slot)
    generator = GameTablesGenerator(game, players)
    game_tables = generator.generate_lowest_penalty_tables()
    db.set_game_tables(slot, game_tables)

    flash("Tables generated.")
    return redirect(url_for('game', slot=slot))


@app.route('/players/')
def players():
    slots = sorted(db.get_games().slots)
    players = db.get_players()
    player_only_slots = set(
        s for p in players for s in p.slots.keys() if s not in slots)
    if player_only_slots:
        flash("Warning: Players are registered for unknown slots: %s" % (
            ', '.join(sorted(player_only_slots)),), 'error')
        slots = sorted(slots + list(player_only_slots))
    return render_template('players.html', slots=slots, players=players)


@app.route('/players/players.csv')
def players_csv():
    players = db.get_players()
    slots = players.get_slots()
    players_csv = StringIO()
    players.to_csv(slots, players_csv)
    resp = make_response(players_csv.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    return resp


@app.route('/players/upload', methods=['POST'])
def players_upload():
    f = request.files['players_file']
    if f.filename.endswith('.csv'):
        players = Players.from_csv(f)
    else:
        players = Players.from_xls(f.read())
    db.import_players(players, delete=True)
    flash("Players imported.")
    return redirect(url_for('players'))


@app.route('/tables/')
def tables():
    game_tables = db.get_all_game_tables()
    return render_template(
        'tables.html', game_tables=game_tables, player_name=player_name)


@app.route('/tables/tables.csv')
def tables_csv():
    game_tables = db.get_all_game_tables()
    tables_csv = StringIO()
    game_tables.to_csv(tables_csv)
    resp = make_response(tables_csv.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    return resp


@app.route('/tables/table_list.csv')
def table_list_csv():
    game_tables = db.get_all_game_tables()
    table_list_csv = StringIO()
    game_tables.to_list_csv(table_list_csv)
    resp = make_response(table_list_csv.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    return resp


@app.route('/tables/upload', methods=['POST'])
def tables_upload():
    games = db.get_games()
    players = db.get_players()
    game_tables = GameTables.from_csv(
        games, players, request.files['tables.csv'])
    db.set_all_game_tables(game_tables)
    flash("Tables imported.")
    return redirect(url_for('tables'))


@app.route('/tables/generate_tables', methods=['POST'])
def tables_generate_tables():
    players = db.get_players()
    games = db.get_games()
    generator = AllTablesGenerator(games, players)
    game_tables = generator.generate_lowest_penalty_tables()
    db.set_all_game_tables(game_tables)

    flash("Tables generated.")
    return redirect(url_for('tables'))


if __name__ == '__main__':
    app.run(debug=True)
