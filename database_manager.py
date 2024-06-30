import datetime as dt
import pandas as pd
from typing import List
from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy


# Create database
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)


# Database tables
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
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    current_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    games: Mapped[List["GameHistory"]] = relationship(back_populates="faction")


class Game(db.Model):
    __tablename__ = "game"
    bga_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    group: Mapped[str] = mapped_column(String(10), nullable=False)
    map: Mapped[str] = mapped_column(String(50), nullable=False)
    num_players: Mapped[int] = mapped_column(Integer, nullable=False)
    included: Mapped[List["GameHistory"]] = relationship(back_populates="game")


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
    player_ratings = result.scalars().all()
    return player_ratings


def get_num_games(db, players):
    """Return the number of games each player has played as a dict {player_name(str):num_games(int)}"""
    num_games_dict = {}
    for player in players:
        num_games_dict[player.name] = db.session.query(GameHistory).filter(GameHistory.player == player).count()
    return num_games_dict


def split_results(results, rounds, groups):
    """Returns a dictionary with the format of {round: {group:[results], ..}}"""
    split_results_dict = {}
    for round_ in rounds:
        round_dict = {}
        for group in groups:
            round_dict[group] = [entry for entry in results if
                                 entry.game.round == int(round_) and entry.game.group == group]
        split_results_dict[round_] = round_dict
    return split_results_dict


def get_latest_results(db):
    """Returns results from the latest round's games, split by group, a sorted list of groups, and the round (str)"""
    latest_round = db.session.execute(func.max(Game.round)).scalar()
    result = db.session.execute(db.select(GameHistory).join(Game).where(Game.round == latest_round))
    latest_game_data = result.scalars().all()
    groups = sorted(list(set([entry.game.group for entry in latest_game_data])))
    latest_results = split_results(latest_game_data, rounds=[str(latest_round)], groups=groups)
    return latest_results, groups, str(latest_round)


def get_all_games(db):
    """Returns results from all games, split by round and group, and a sorted list of rounds and groups"""
    result = db.session.execute(db.select(GameHistory).join(Game))
    all_games_data = result.scalars().all()
    rounds = sorted(list(set([str(entry.game.round) for entry in all_games_data])))
    groups = sorted(list(set([entry.game.group for entry in all_games_data])))
    all_games_results =  split_results(all_games_data, rounds=rounds, groups=groups)
    return all_games_results, rounds, groups
