import datetime as dt
from typing import List
from sqlalchemy import Integer, String, DateTime, ForeignKey
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
