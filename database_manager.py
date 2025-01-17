import datetime as dt
from statistics import mean
from typing import List

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


# Create database
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)


# Database tables
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(250), unique=True)
    password: Mapped[str] = mapped_column(String(250))


class Player(db.Model):
    __tablename__ = "player"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    current_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    games: Mapped[List["GameHistory"]] = relationship(back_populates="player")


class Faction(db.Model):
    __tablename__ = "faction"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)  # RGB values without (), e.g. 160, 82, 45
    current_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    games: Mapped[List["GameHistory"]] = relationship(back_populates="faction")


class Game(db.Model):
    __tablename__ = "game"
    bga_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    group: Mapped[str] = mapped_column(String(10), nullable=False)
    map: Mapped[str] = mapped_column(String(50), nullable=False)
    num_players: Mapped[int] = mapped_column(Integer, nullable=False)
    included: Mapped[List["GameHistory"]] = relationship(back_populates="game", order_by="desc(GameHistory.score)")


# Association table
class GameHistory(db.Model):
    __tablename__ = "game_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(db.ForeignKey("player.id"))
    faction_id: Mapped[int] = mapped_column(db.ForeignKey("faction.id"))
    game_id: Mapped[int] = mapped_column(db.ForeignKey("game.bga_id"))
    player: Mapped["Player"] = relationship(back_populates="games")
    faction: Mapped["Faction"] = relationship(back_populates="games")
    game: Mapped["Game"] = relationship(back_populates="included")
    bid: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    old_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    new_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)


# Functions for interacting with database
def get_player_data(db):
    """Returns player data from the database sorted by rating"""
    result = db.session.execute(db.select(Player).order_by(Player.current_rating.desc()))
    player_data = result.scalars().all()
    return player_data


def get_num_games(db, players):
    """Return the number of games each player has played as a dict {player_name(str):num_games(int)}"""
    num_games_dict = {}
    for player in players:
        num_games_dict[player.name] = db.session.query(GameHistory).filter(GameHistory.player == player).count()
    return num_games_dict


def get_latest_round(db):
    """Returns the round number of the latest round"""
    latest_round = db.session.execute(func.max(Game.round)).scalar()
    return latest_round


def get_latest_results(db):
    """Returns results from the latest round's game results as a dict {group:[results]}"""
    latest_round = get_latest_round(db)
    latest_round_games = db.session.execute(db.select(Game).where(Game.round == latest_round)
                                            .order_by(Game.group)).scalars().all()
    latest_results = {game.group: game.included for game in latest_round_games}
    return latest_results


def get_all_games(db):
    """Returns a list of all games sorted by round (oldest first) and group"""
    all_games_data = db.session.execute(db.select(Game).order_by(Game.round, Game.group)).scalars().all()
    return all_games_data


def split_results(game_data):
    """Returns a nest dictionary from a list of games with the format {round_num: {group: entries}}"""
    results_dict = {}
    for game in game_data:
        if game.round in results_dict:
            results_dict[game.round][game.group] = game.included
        else:
            results_dict[game.round] = {game.group: game.included}
    return results_dict


def get_player(db, player_name):
    """Returns a player object given a player name"""
    player = db.session.execute(db.select(Player).where(Player.name == player_name)).scalar()
    return player


def get_player_rating(db, player_name):
    player = get_player(db, player_name)
    return player.current_rating


def update_player_rating(db, player_name, new_rating):
    """Updates a player's rating in the players table"""
    player = get_player(db, player_name)
    player.current_rating = new_rating
    db.session.commit()


def get_player_games(db, player_name):
    """Returns a list of game IDs that a player was in, sorted by round (reverse play order)"""
    player = get_player(db, player_name)
    query_result = db.session.execute(db.select(GameHistory).join(Game).where(GameHistory.player_id == player.id)
                    .order_by(Game.round.desc(), GameHistory.score.desc()))
    player_games = query_result.scalars().all()
    player_game_ids = [game.game_id for game in player_games]
    return player_game_ids


def get_player_game_history(db, player_name):
    """Returns the game history dict for a player, sorted by round (reverse play order)"""
    game_history = {}
    game_ids = get_player_games(db, player_name)
    for game_id in game_ids:
        game = db.get_or_404(Game, game_id)
        game_details = {
            "round": game.round,
            "group": game.group,
            "map": game.map,
            "num_players": game.num_players,
            "entries": game.included
        }
        game_history[game_id] = game_details
    return game_history


def get_rating_history(db, player_name):
    """Returns a list of tuples, (round_num, rating), for named player, sorted by round num"""
    player = get_player(db, player_name)
    player_entries = db.session.execute(db.select(GameHistory)
                                        .where(GameHistory.player_id == player.id)).scalars().all()
    rating_history = sorted([(entry.game.round, entry.new_rating) for entry in player_entries])
    rating_history = [(rating_history[0][0]-1, 1000)] + rating_history
    return rating_history


def get_high_rating(db, player_name, threshold):
    """Returns highest rating with at least <threshold> games, else '--' if below <threshold> total games"""
    rating_history = get_rating_history(db, player_name)
    if len(rating_history)-1 < threshold:  # -1 because the first is the starting rating at game 0
        return "--"
    else:
        high_rating = max([rating for round_num, rating in rating_history[threshold:]])
        return high_rating


def get_player_records(db, player_name):
    player = get_player(db, player_name)
    player_records = (db.session.execute(db.select(GameHistory).where(GameHistory.player_id == player.id))
                      .scalars().all())
    return player_records


def get_most_played_faction(db, player_name):
    """Returns a dict with the most played faction and number of times played (multiple if tied)"""
    faction_tally = {}
    player_records = get_player_records(db, player_name)
    for record in player_records:
        faction = record.faction.name.replace(" ", "")
        if faction in faction_tally:
            faction_tally[faction] += 1
        else:
            faction_tally[faction] = 1
    max_value = max(faction_tally.values())
    max_factions = {faction:faction_tally[faction] for faction in faction_tally if faction_tally[faction] == max_value}
    return max_factions


def get_results_highlights(db, player_name, game_history):
    """Returns a dict with player's 1st, 2nd, 3rd placements and total games by group"""
    groups = db.session.execute(db.select(Game.group).distinct()).scalars().all()
    result_highlights = {group: {1: 0, 2: 0, 3: 0, "Total": 0} for group in groups}
    # Loop through games in their history
    for game_id in list(game_history.keys()):
        entries = game_history[game_id]["entries"]
        for entry in entries:
            if entry.player.name == player_name:
                # Check if the player was 1st, 2nd, or 3rd
                if entries.index(entry) < 3:
                    # Iterate the appropriate total based on the index of the entry and round
                    result_highlights[entry.game.group][entries.index(entry)+1] += 1
                # Iterate the round total regardless of placement
                result_highlights[entry.game.group]["Total"] += 1
    return result_highlights


def get_faction_color(db, faction_name):
    faction = db.session.execute(db.select(Faction).where(Faction.name == faction_name)).scalar()
    return faction.color


def get_faction_bg_color(db, most_played_dict):
    if len(list(most_played_dict.keys())) == 1:
        faction = list(most_played_dict.keys())[0]
        # TODO: Rework this so the following adjustment isn't necessary
        if faction in ["ChaosMagicians", "IceMaidens"]:
            faction = faction.replace("M", " M")
        return get_faction_color(db, faction)
    else:
        return "220, 226, 230"


def get_score_stats(db, player_name, game_history):
    player = get_player(db, player_name)
    player_scores = []
    player_bids = []
    game_avg_scores = []
    for game_id in list(game_history.keys()):
        entries = game_history[game_id]["entries"]
        game_avg_scores.append(mean([entry.score for entry in entries]))
        for entry in entries:
            if entry.player_id == player.id:
                player_scores.append(entry.score)
                player_bids.append(entry.bid)
    score_stats = {
        "avg_final_score": round(mean(player_scores), 1),
        "avg_starting_score": round(mean(player_bids), 1),
        "avg_net_gained": round(mean([score - bid for score, bid in zip(player_scores, player_bids)]), 1),
        "relative_to_game_avg": round(mean([score - avg for score, avg in zip(player_scores, game_avg_scores)]), 1)
    }
    return score_stats


def get_head_to_head(db, player_name):
    """Returns a dict with results vs each other player as a tuple, (W, L, D)"""
    head_to_head = {}
    this_player = get_player(db, player_name)
    for player in get_player_data(db):
        if player != this_player:
            head_to_head[player.name] = [0, 0, 0]
    for game_id in get_player_games(db, player_name):
        game = db.session.execute(db.select(Game).where(Game.bga_id == game_id)).scalar()
        player_score = [entry.score for entry in game.included if entry.player_id == this_player.id][0]
        other_players = [entry for entry in game.included if entry.player_id != this_player.id]
        for player_entry in other_players:
            if player_score > player_entry.score:
                head_to_head[player_entry.player.name][0] += 1
            elif player_score < player_entry.score:
                head_to_head[player_entry.player.name][1] += 1
            else:
                head_to_head[player_entry.player.name][2] += 1
    return head_to_head


def get_col_spans(game_history):
    """Returns a dict of {game_id:col_spans} for the player game history table taking into account ties"""
    col_spans_dict = {}
    for game_id in game_history:
        game = game_history[game_id]
        col_spans = [1] * game["num_players"]
        for i in reversed(range(game["num_players"])):
            if i > 0:
                if game["entries"][i].score == game["entries"][i-1].score:
                    col_spans[i-1] += col_spans[i]
                    col_spans[i] = 0
        col_spans_dict[game_id] = col_spans
    return col_spans_dict
