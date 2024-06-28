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


def get_player_num_games(db, player):
    """Return the number of games a player has played (int)"""
    pass
    # num_games = db.session.query(GameHistory).filter(GameHistory.player == player).count()
    # return num_games


def split_results_by_groups(results, groups):
    """Returns a dictionary with the format of group:list of results for that group"""
    results_by_groups = {}
    for group in groups:
        results_by_groups[group] = [entry for entry in results if entry.game.group == group]
    return results_by_groups


def get_latest_results(db):
    """Returns results from the latest round's games, split by group, and a sorted list of groups"""
    latest_round = db.session.execute(func.max(Game.round)).scalar()
    result = db.session.execute(db.select(GameHistory).join(Game).where(Game.round == latest_round))
    latest_game_data = result.scalars().all()
    groups = sorted(list(set([entry.game.group for entry in latest_game_data])))
    latest_results = split_results_by_groups(latest_game_data, groups)
    return latest_results, groups


def get_all_games(db):
    pass
