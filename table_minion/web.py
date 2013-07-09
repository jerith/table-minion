from flask import Flask, request, url_for, redirect, flash, render_template

from table_minion import db
from table_minion.players import Players, player_name
from table_minion.games import Games
from table_minion.generate_tables import Tables


app = Flask(__name__)
app.secret_key = 'SEKRIT'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/')
def admin():
    return render_template('admin.html')


@app.route('/create_database', methods=['POST'])
def create_database():
    db.init_db(clear=request.form.get('delete', False))
    flash("Database created.")
    return redirect(url_for('admin'))


@app.route('/games/')
def games():
    games = sorted(db.get_games(), key=lambda g: g.slot)
    return render_template('games.html', games=games)


@app.route('/games/upload', methods=['POST'])
def games_upload():
    db.import_games(Games.from_csv(request.files['games.csv']), delete=True)
    flash("Games imported.")
    return redirect(url_for('games'))


@app.route('/games/<slot>/')
def game(slot):
    game = db.get_game(slot)
    tables = db.get_game_tables(slot)
    return render_template(
        'game.html', game=game, tables=tables, player_name=player_name)


@app.route('/games/<slot>/lay_tables', methods=['POST'])
def game_lay_tables(slot):
    players = db.get_players()
    games = db.get_games()
    tables = Tables(games, players, [slot])
    db.set_game_tables(slot, tables.game_tables[slot].tables)

    flash("Tables laid.")
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


@app.route('/players/upload', methods=['POST'])
def players_upload():
    db.import_players(
        Players.from_csv(request.files['players.csv']), delete=True)
    flash("Players imported.")
    return redirect(url_for('players'))


@app.route('/tables/')
def tables():
    slots = sorted(db.get_games().slots)
    tables = db.get_all_game_tables()
    max_tables = max(len(gt) for gt in tables.values()) if tables else 0
    return render_template(
        'tables.html', slots=slots, tables=tables, max_tables=max_tables,
        player_name=player_name)


@app.route('/tables/lay_tables', methods=['POST'])
def tables_lay_tables():
    players = db.get_players()
    games = db.get_games()
    tables = Tables(games, players, games.slots)
    db.set_all_game_tables(tables)

    flash("Tables laid.")
    return redirect(url_for('tables'))


@app.teardown_appcontext
def close_connection(exception):
    db.close_db()


if __name__ == '__main__':
    app.run(debug=True)
