import datetime as dt
from io import BytesIO
import os

from flask import Flask, render_template, redirect, url_for, flash, Response
from flask_bootstrap import Bootstrap5
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

from constants import STARTING_RATING, RATING_FIG_YRANGE, HIGH_RATING_THRESHOLD, EMOJIS
from database_manager import db, Player, Faction, Game, GameHistory, User
from database_manager import (get_player_data, get_latest_round, get_latest_results, get_all_games, get_num_games,
                              split_results, get_player_rating, update_player_rating, get_player,
                              get_player_game_history, get_rating_history, get_high_rating, get_most_played_faction,
                              get_results_highlights, get_faction_bg_color, get_score_stats, get_head_to_head,
                              get_col_spans)
from decorators import admin_required
from elo import calculate_new_elos, recalculate_elos
from forms import AddPlayerForm, AddFactionForm, AddGameForm, RegisterForm, LoginForm


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///tm_data.db")
register_code = os.environ.get("REGISTER_CODE")
Bootstrap5(app)

# Configure Flask login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return user


# Prepare database
db.init_app(app)
with app.app_context():
    db.create_all()


# Routes
@app.route('/')
def home():
    player_data = get_player_data(db)
    latest_results = get_latest_results(db)
    num_games = get_num_games(db, player_data)
    return render_template('index.html', player_data=player_data,
                           latest_results=latest_results, num_games=num_games, emojis=EMOJIS)


@app.route('/results')
def get_all_results():
    all_games_data = get_all_games(db)
    all_results = split_results(all_games_data)
    return render_template('results.html', results=all_results, emojis=EMOJIS)


@app.route('/profile/<player_name>')
def get_profile(player_name):
    player = get_player(db, player_name)
    game_history = get_player_game_history(db, player_name)
    col_spans = get_col_spans(game_history)
    most_played_faction = get_most_played_faction(db, player_name)
    profile_data = {
        "player_name": player_name,
        "current_rating": player.current_rating,
        "num_games": get_num_games(db, [player])[player.name],
        "high_rating": get_high_rating(db, player_name, HIGH_RATING_THRESHOLD),
        "results_highlights": get_results_highlights(db, player_name, game_history),
        "most_played_faction": most_played_faction,
        "faction_bg_color": get_faction_bg_color(db, most_played_faction),
        "score_stats": get_score_stats(db, player_name, game_history),
        "head_to_head": get_head_to_head(db, player_name)
    }
    return render_template('profile.html',
                           profile_data=profile_data, game_history=game_history, col_spans=col_spans)


@app.route('/get-rating-plot/<player_name>')
def get_rating_fig(player_name):
    rating_history = get_rating_history(db, player_name)
    round_nums, ratings = zip(*rating_history)


    # Create figure
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(*zip(*rating_history), color="black")
    axis.set_xticks(np.arange(0, get_latest_round(db) + 1))
    axis.set_yticks(np.arange(*RATING_FIG_YRANGE))
    axis.set_xlabel("Round")
    axis.set_ylabel("Rating")
    axis.axhline(1000, ls="--", color="gray", linewidth=1)

    # Output figure
    output = BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


@app.route('/rating-system')
def rating_system():
    return render_template('rating-system.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_username = form.username.data

        if db.session.execute(db.select(User).where(User.username == new_username)).scalar():
            flash("Username already exists. Please login.")
            return redirect(url_for('login'))

        if form.code.data != register_code:
            flash("Incorrect register code. You must know this to register.")
            return render_template("register.html", form=form)

        else:
            password_hashed_and_salted = generate_password_hash(form.password.data, method="pbkdf2", salt_length=8)
            new_user = User(username=new_username, password=password_hashed_and_salted)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("Registration successful!")
            return redirect(url_for('admin'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    login_username = form.username.data
    login_password = form.password.data

    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.username == login_username)).scalar()
        if not user:
            flash("Username not found. Please try again.", "error")
            return render_template("login.html", form=form)
        elif check_password_hash(user.password, login_password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash("Password incorrect. Please try again.", "error")
            return render_template('login.html', form=form)

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')


@app.route('/recalculate')
@admin_required
def recalculate():
    recalculate_elos(db)
    flash("Ratings recalculated!", "notice")
    return redirect(url_for('admin'))


@app.route('/add-player', methods=["GET", "POST"])
@admin_required
def add_player():
    form = AddPlayerForm()
    if form.validate_on_submit():
        new_name = form.name.data

        if db.session.execute(db.select(Player).where(Player.name == new_name)).scalar():
            flash("Player already exists!", "error")
            return redirect(url_for("admin"))

        else:
            new_player = Player(name=new_name, current_rating=STARTING_RATING)
            db.session.add(new_player)
            db.session.commit()
            flash("Player added!", "notice")
            return redirect(url_for("admin"))

    return render_template('add-player.html', form=form)


@app.route('/add-faction', methods=["GET", "POST"])
@admin_required
def add_faction():
    form = AddFactionForm()
    if form.validate_on_submit():
        new_name = form.name.data

        if db.session.execute(db.select(Faction).where(Faction.name == new_name)).scalar():
            flash("Faction already exists!", "error")
            return redirect(url_for("admin"))

        else:
            new_faction = Faction(name=new_name, color=form.color.data, current_rating=STARTING_RATING)
            db.session.add(new_faction)
            db.session.commit()
            flash("Faction added!", "notice")
            return redirect(url_for("admin"))

    return render_template('add-faction.html', form=form)


@app.route('/add-game', methods=["GET", "POST"])
@admin_required
def add_game():
    form = AddGameForm()

    # Pass dynamic choices for player names
    player_choices = sorted([(player.name, player.name) for player in get_player_data(db)])
    form.p1.choices = player_choices
    form.p2.choices = player_choices
    form.p3.choices = [("", "")] + player_choices  # Can be null
    form.p4.choices = [("", "")] + player_choices  # Can be null
    form.p5.choices = [("", "")] + player_choices  # Can be null

    if form.validate_on_submit():
        new_game_id = form.bga_id.data

        # Check if game ID exists
        if db.session.execute(db.select(Game).where(Game.bga_id == new_game_id)).scalar():
            flash("Game ID already exists!", "error")
            return redirect(url_for("admin"))

        else:
            # Add to games table
            num_players = form.num_players.data
            new_game = Game(
                bga_id=new_game_id,
                round=form.round.data,
                group=form.group.data,
                map=form.map.data,
                num_players = num_players
            )
            db.session.add(new_game)
            db.session.commit()

            # Add to game_history table
            game_results = []
            for i in range(num_players):
                player = db.session.execute(db.select(Player).where(Player.name == form[f"p{i+1}"].data)).scalar()
                entry = GameHistory(
                    player=player,
                    faction=db.session.execute(db.select(Faction)
                                               .where(Faction.name == form[f"p{i+1}_faction"].data)).scalar(),
                    game=new_game,
                    bid=form[f"p{i+1}_bid"].data,
                    score=form[f"p{i+1}_score"].data,
                    old_rating=get_player_rating(db, player.name),
                    new_rating=STARTING_RATING,  # This is just a placeholder.
                    created_at=dt.datetime.now()
                )
                game_results.append(entry)

            # Compute new ratings and update game results
                num_games = get_num_games(db, [entry.player for entry in game_results])
                game_results = calculate_new_elos(game_results, num_games)

            # Add updated entries to game_history table and update ratings in players table
            for entry in game_results:
                update_player_rating(db, player_name=entry.player.name, new_rating=entry.new_rating)
                db.session.add(entry)
                db.session.commit()

            flash("Game added!", "notice")
            return redirect(url_for("admin"))

    return render_template('add-game.html', form=form)


if __name__ == "__main__":
    app.run(debug=False)
