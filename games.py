import pandas as pd
import numpy as np
from players import check_if_new_player, update_elo_ratings
from game_dicts import FACTIONS, GAME_BOARDS
from file_manager import get_games, get_player_stats, reset_player_data, generate_index_html, generate_results_html

GROUPS = ["A", "B", "C"]


class Game:

    def __init__(self, game_data):
        self.game_id = game_data["game_id"]
        self.round = game_data["round"]
        self.group = game_data["group"]
        self.board = game_data["board"]
        self.p1 = game_data["player1"]
        self.p2 = game_data["player2"]
        self.p3 = game_data["player3"]
        self.p4 = game_data["player4"]
        self.p5 = game_data["player5"]
        self.players = self.list_players()
        self.p1_faction = game_data["p1_faction"]
        self.p2_faction = game_data["p2_faction"]
        self.p3_faction = game_data["p3_faction"]
        self.p4_faction = game_data["p4_faction"]
        self.p5_faction = game_data["p5_faction"]
        self.p1_pts = game_data["p1_pts"]
        self.p2_pts = game_data["p2_pts"]
        self.p3_pts = game_data["p3_pts"]
        self.p4_pts = game_data["p4_pts"]
        self.p5_pts = game_data["p5_pts"]
        self.scores = np.array([x for x in [self.p1_pts, self.p2_pts, self.p3_pts, self.p4_pts, self.p5_pts]
                                if not np.isnan(x)])
        self.delta_matrix = self.calculate_delta_matrix()
        self.proportion_matrix = self.calculate_proportion_matrix()
        self.winloss_matrix = self.calculate_winloss_matrix()

    def list_players(self):
        players = [x for x in [self.p1, self.p2, self.p3, self.p4, self.p5] if x]
        return players

    def calculate_delta_matrix(self):
        delta_matrix = np.zeros((len(self.scores), len(self.scores)))
        for i, score in enumerate(self.scores):
            delta_matrix[i] = score - self.scores
        return delta_matrix

    def calculate_proportion_matrix(self):
        proportion_matrix = np.zeros((len(self.scores), len(self.scores)))
        for i, score in enumerate(self.scores):
            proportion_matrix[i] = score / (score + self.scores)
        return proportion_matrix

    def calculate_winloss_matrix(self):
        winloss_matrix = (np.sign(self.delta_matrix) + 1) / 2
        return winloss_matrix


def add_game():
    new_game = {}
    previous_games = get_games()

    new_game["game_id"] = len(previous_games.index) + 1
    if previous_games.empty:
        new_game["round"] = 1
    else:
        new_game["round"] = int(previous_games.loc[previous_games.index[-1], "round"])

    # Collect input
    num_players = 0
    while (num_players < 2) or (num_players > 5):
        try:
            num_players = int(input("Number of players (2-5): "))
        except ValueError:
            print("Must be an integer.")

    new_game["group"] = input(f"Group ({GROUPS}): ").lower()
    while new_game["group"].upper() not in GROUPS:
        new_game["group"] = input(f"Enter the group ({GROUPS}): ").lower()

    # Check if this is a new round and increase round number if so
    round_check = (previous_games["round"].astype(str) + previous_games["group"]).to_list()
    if str(new_game["round"]) + new_game["group"] in round_check:
        new_game["round"] += 1

    new_game["board"] = input("Game board: ").lower()
    while new_game["board"] not in GAME_BOARDS.keys():
        print(f"The game boards are {', '.join(GAME_BOARDS.keys())}.")
        new_game["board"] = input("Enter a game board: ")

    # Add players
    for i in range(num_players):
        player_num = i + 1
        while f"player{player_num}" not in new_game:
            new_game[f"player{player_num}"] = input(f"Player {player_num}: ")
            if check_if_new_player(new_game[f"player{player_num}"]) == "do not add":
                del new_game[f"player{player_num}"]
        new_game[f"p{player_num}_faction"] = input(f"Player {player_num} faction: ").lower()
        while new_game[f"p{player_num}_faction"] not in FACTIONS.keys():
            print("Faction not recognised.")
            new_game[f"p{player_num}_faction"] = input(f"Enter player {player_num} faction: ")
        new_game[f"p{player_num}_pts"] = 0
        while new_game[f"p{player_num}_pts"] == 0:
            try:
                new_game[f"p{player_num}_pts"] = int(input(f"Player {player_num} score: "))
            except ValueError:
                "Must be a number."

    if num_players < 3:
        new_game.update({"player3": "", "p3_faction": "", "p3_pts": np.nan})
    if num_players < 4:
        new_game.update({"player4": "", "p4_faction": "", "p4_pts": np.nan})
    if num_players < 5:
        new_game.update({"player5": "", "p5_faction": "", "p5_pts": np.nan})

    # Add game to database
    game_data = get_games()
    game_data = pd.concat([game_data, pd.DataFrame([new_game])], ignore_index=True)
    game_data.to_csv("game_stats.csv", index=False)

    # Update elo ratings
    print("Game added!")
    game = Game(new_game)
    update_elo_ratings(game)

    # Update webpages
    generate_index_html()
    generate_results_html()


def recalculate_ratings():
    reset_player_data()
    games = get_games()

    # Iterate through games and update elo
    print("Recalculating ratings based on game stats.")
    for game_data in games.to_dict(orient="records"):
        game = Game(game_data)
        update_elo_ratings(game)
        print(f"...Game {game.game_id}...")

    # Update webpages
    generate_index_html()
    generate_results_html()

    print("Recalculated player stats:")
    print(get_player_stats())
