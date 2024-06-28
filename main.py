import datetime as dt
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from database_manager import db, Player, Faction, Game, GameHistory, get_player_data, get_latest_results
from forms import AddPlayerForm, AddFactionForm, AddGameForm
from constants import STARTING_RATING
from players import add_player
from file_manager import get_player_stats
from games import add_game, recalculate_ratings


app = Flask(__name__)
app.config["SECRET_KEY"] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tm_data.db'
Bootstrap5(app)


# Prepare database
db.init_app(app)
with app.app_context():
    db.create_all()


# Routes
@app.route('/')
def home():
    player_data = get_player_data(db)
    latest_results, groups = get_latest_results(db)
    return render_template('index.html',
                           player_data=player_data, latest_results=latest_results, groups=groups)


@app.route('/results')
def get_all_results():
    return render_template('results.html')


@app.route('/add-player', methods=["GET", "POST"])
def add_player():
    form = AddPlayerForm()
    if form.validate_on_submit():
        new_name = form.name.data

        if db.session.execute(db.select(Player).where(Player.name == new_name)).scalar():
            flash("Player already exists.")

        else:
            new_player = Player(name=new_name, current_rating=STARTING_RATING)
            db.session.add(new_player)
            db.session.commit()

    return render_template('add-player.html', form=form)


@app.route('/add-faction', methods=["GET", "POST"])
def add_faction():
    form = AddFactionForm()
    if form.validate_on_submit():
        new_name = form.name.data

        if db.session.execute(db.select(Faction).where(Faction.name == new_name)).scalar():
            flash("Faction already exists.")

        else:
            new_faction = Faction(name=new_name, color=form.color.data, current_rating=STARTING_RATING)
            db.session.add(new_faction)
            db.session.commit()

    return render_template('add-faction.html', form=form)


@app.route('/add-game', methods=["GET", "POST"])
def add_game():
    form = AddGameForm()
    if form.validate_on_submit():
        new_game_id = form.bga_id.data

        if db.session.execute(db.select(Game).where(Game.bga_id == new_game_id)).scalar():
            flash("Game ID already exists.")

        else:
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

            for i in range(num_players):
                player_details = GameHistory(
                    player=db.session.execute(db.select(Player).where(Player.name == form[f"p{i+1}"].data)).scalar(),
                    faction=db.session.execute(db.select(Faction)
                                               .where(Faction.name == form[f"p{i+1}_faction"].data)).scalar(),
                    game=new_game,
                    bid=form[f"p{i+1}_bid"].data,
                    score=form[f"p{i+1}_score"].data,
                    old_rating=STARTING_RATING,  # TODO: FIX
                    new_rating=STARTING_RATING,  # TODO: FIX
                    created_at=dt.datetime.now()
                )
                db.session.add(player_details)
                db.session.commit()

    return render_template('add-game.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)


# OLD

# HEADER = "==============================================\n" \
#          "** Welcome to the Terra Mystica League tracker! **\n"
#
# PROMPT = "What would you like to do?\n"\
#          "-- Type 'stats' to get a list of players and their stats.\n"\
#          "-- Type 'player' to add a new player.\n"\
#          "-- Type 'game' to add a new game.\n"\
#          "-- Type 'recalculate' to recalculate player stats based on games in the database.\n"
#
#
# def run():
#     # Prompt user for command
#     response = input(PROMPT).lower()
#     while response not in ["stats", "game", "player", "recalculate"]:
#         print("Invalid command.")
#         response = input(PROMPT).lower()
#
#     # Run according to response
#     if response == "stats":
#         print(get_player_stats())
#     elif response == "game":
#         add_game()
#     elif response == "player":
#         new_player = input("Which player do you want to add? ")
#         add_player(new_player)
#     elif response == "recalculate":
#         recalculate_ratings()
#
#     # Ask if user wants to do something else
#     again = input("Do you want to do something else (Y or N)? ").upper()
#     if (again == "Y") or (again == "YES"):
#         run()
#
#
# print(HEADER)
# run()