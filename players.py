import pandas as pd
import numpy as np
from elo import calculate_elo_changes
from file_manager import get_player_stats, record_player_stats, record_elo_changes

STARTING_ELO = 1000


def add_player(new_player):
    with open("player_stats.csv", "a") as f:
        f.write(f"\n{new_player},0,{STARTING_ELO},{STARTING_ELO}")
    print("Player added!")


def check_if_new_player(name):
    player_list = list(get_player_stats()["player"])
    if name not in player_list:
        add_response = input("This player isn't in the database; do you want to add them (Y or N)? ").upper()
        while add_response not in ["Y", "N", "YES", "NO"]:
            add_response = input("This player isn't in the database; do you want to add them (Y or N)? ").upper()
        if (add_response == "Y") or (add_response == "YES"):
            add_player(name)
            return "added"
        else:
            print("Enter a player in the database.")
            print(f"Existing players: {', '.join(player_list)}")
            return "do not add"
    else:
        return "not a new player"


def update_elo_ratings(game):
    # Get current player information
    all_stats = get_player_stats()
    wl_ratings = []
    pts_ratings = []
    num_games = []
    for player in game.players:
        player_stats = all_stats.loc[all_stats["player"] == player]
        wl_ratings.append(player_stats.iloc[0]["elo_win_loss"])
        pts_ratings.append(player_stats.iloc[0]["elo_points"])
        num_games.append(player_stats.iloc[0]["games"])

    # Calculate changes
    num_games = np.array(num_games) + 1
    wl_changes = calculate_elo_changes(np.array(wl_ratings), game.winloss_matrix, num_games).astype(int)
    pts_changes = calculate_elo_changes(np.array(pts_ratings), game.proportion_matrix, num_games, k_scale=2).astype(int)

    # Make updates
    new_wl_ratings = wl_ratings + wl_changes
    new_pts_ratings = pts_ratings + pts_changes
    for i, player in enumerate(game.players):
        new_wl_rating = new_wl_ratings[i]
        new_pts_rating = new_pts_ratings[i]
        all_stats.loc[all_stats["player"] == player, "elo_win_loss"] = new_wl_rating
        all_stats.loc[all_stats["player"] == player, "elo_points"] = new_pts_rating
        all_stats.loc[all_stats["player"] == player, "games"] = num_games[i]
        print(f"{player}'s new ratings: win/loss {new_wl_rating} (change of {wl_changes[i]}), "
              f"points {new_pts_rating} (change of {pts_changes[i]}).")

    # Record to data files
    record_player_stats(all_stats)
    record_elo_changes(game.game_id, game.players, wl_ratings, pts_ratings, new_wl_ratings, new_pts_ratings,
                       wl_changes, pts_changes)
