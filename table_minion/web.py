from flask import Flask, url_for, redirect, flash, render_template

from table_minion import db
from table_minion.players import player_name


app = Flask(__name__)
app.secret_key = 'SEKRIT'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/')
def admin():
    return render_template('admin.html')


@app.route('/create_database', methods=['POST'])
def reset_data():
    db.init_db(clear=True)
    from table_minion.tests.utils import make_games, make_players

    db.import_games(make_games(['1A', '1B']))

    db.import_players(make_players([
        (10, 'Alpha', None, {'1A': 'P'}),
        (1, 'Able', None, {'1A': 'X'}),
        (2, 'Ares', 'Olympians', {'1A': 'P'}),
        (10, 'Bravo', None, {'1B': 'P'}),
        (2, 'Baker', None, {'1B': 'X'}),
    ]))

    flash("Database created.")
    return redirect(url_for('admin'))


@app.route('/games/')
def games():
    return render_template('games.html', games=db.get_games())


@app.route('/games/<slot>/')
def game(slot):
    game = db.get_game(slot)
    tables = db.get_game_tables(slot)
    return render_template(
        'game.html', game=game, tables=tables, player_name=player_name)


@app.route('/games/<slot>/lay_tables', methods=['POST'])
def game_lay_tables(slot):
    from table_minion.generate_tables import Tables
    players = db.get_players()
    games = db.get_games()
    tables = Tables(games, players, [slot])
    db.set_game_tables(slot, tables.game_tables[slot].tables)

    flash("Tables laid.")
    return redirect(url_for('game', slot=slot))


@app.route('/players/')
def players():
    return render_template('players.html', players=db.get_players())


@app.teardown_appcontext
def close_connection(exception):
    db.close_db()


if __name__ == '__main__':
    app.run(debug=True)
