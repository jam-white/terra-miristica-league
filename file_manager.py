import numpy as np
import pandas as pd
from game_dicts import FACTIONS, GAME_BOARDS


HTML_HEADER = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Terra Miristica</title>
    <link rel="stylesheet" href="./assets/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville&display=swap" rel="stylesheet">
  </head>
  <body>
"""

HTML_FOOTER = """
  </body>
</html>
"""

TITLE = """
    <div>
      <h1>Terra Miristica League</h1>
    </div>
"""

RATING_EXPLANATION_LINK = """
    <div>
      <p>
        <a href="./rating_system.html">Explanation of the rating system</a>
      </p>
    </div>
"""

LATEST_RESULTS_HEADER = """
    <div>
      <h2>Latest Results</h2>
"""

RESULTS_FOOTER = """
    </div>

    <div>
      <p>
        <a href="./results.html">All previous results</a>
      </p>
    </div>
"""

RESULTS_PAGE_HEADER = """
    <div>
      <p>
        <a href="./index.html">Back to main page</a>
      </p>
    </div>

    <div>
      <h2>Previous results</h2>
      <p>(reverse chronological order)</p>
    </div>
"""


def get_player_stats():
    with open("player_stats.csv") as f:
        player_stats = pd.read_csv(f)
    player_stats.sort_values(by=["elo_win_loss"], ascending=False, inplace=True)
    return player_stats


def record_player_stats(stats):
    stats.to_csv("player_stats.csv", index=False)


def record_elo_changes(game_id, players, wl_ratings, pts_ratings, new_wl_ratings, new_pts_ratings,
                       wl_changes, pts_changes):
    new_row = f"{game_id}"
    for i, player in enumerate(players):
        new_row += f",{player},{wl_ratings[i]},{new_wl_ratings[i]},{wl_changes[i]}," \
                   f"{pts_ratings[i]},{new_pts_ratings[i]},{pts_changes[i]}"

    blanks = ""
    blanks += (",,," * (5 - len(players)))
    new_row += blanks + "\n"

    with open("rating_changes.csv", "a") as f:
        f.write(new_row)


def reset_elo_changes_data():
    with open("rating_changes.csv", "r+") as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        f.write(lines[0])


def reset_player_data():
    reset_elo_changes_data()
    stats = get_player_stats()
    for player in stats.player:
        stats.loc[stats.player == player, "games"] = 0
        stats.loc[stats.player == player, "elo_win_loss"] = 1000
        stats.loc[stats.player == player, "elo_points"] = 1000
    record_player_stats(stats)
    print("Player stats reset!")


def get_games():
    with open("game_stats.csv") as f:
        game_stats = pd.read_csv(f)
    game_stats.astype({"player3": "str", "p3_faction": "str", "player4": "str", "p4_faction": "str",
                       "player5": "str", "p5_faction": "str"})
    game_stats.fillna(value={"player3": "", "p3_faction": "",
                             "player4": "", "p4_faction": "",
                             "player5": "", "p5_faction": ""}, inplace=True)
    return game_stats


def get_rating_changes(game_id):
    with open("rating_changes.csv") as f:
        rating_changes = pd.read_csv(f)
    return rating_changes[rating_changes["game_id"] == game_id]


def make_rating_table(stats):
    html_text = """
    <div>
      <h2>Current Ratings</h2>
      <table class="ratings">
        <tr>
          <th>Player</th>
          <th>Rating</th>
          <th>Games</th>
        </tr>
    """

    for player in stats["player"].to_list():
        player_text = f"""<tr>
          <td>{player}</td>
          <td>{stats[stats["player"]==player].elo_win_loss.item()}</td>
          <td>{stats[stats["player"]==player].games.item()}</td>
        </tr>
        """
        html_text += player_text

    html_text += """
    </table>
    </div>
    """

    return html_text


def make_result_table(game):
    html_text = """
    <table class="results">
        <tr>
          <th>Player</th>
          <th>Faction</th>
          <th>Score</th>
          <th>New Rating</th>
        </tr>
    """
    elo_changes = get_rating_changes(game["game_id"])
    table = pd.DataFrame({
        "Player": [game["player1"], game["player2"], game["player3"], game["player4"], game["player5"]],
        "Faction": [game["p1_faction"], game["p2_faction"], game["p3_faction"], game["p4_faction"], game["p5_faction"]],
        "Score": [game["p1_pts"], game["p2_pts"], game["p3_pts"], game["p4_pts"], game["p5_pts"]],
        "New rating": [elo_changes["p1_wl_new"].item(), elo_changes["p2_wl_new"].item(),
                          elo_changes["p3_wl_new"].item(), elo_changes["p4_wl_new"].item(),
                          elo_changes["p5_wl_new"].item()],
        "Rating change": [elo_changes["p1_wl_change"].item(), elo_changes["p2_wl_change"].item(),
                          elo_changes["p3_wl_change"].item(), elo_changes["p4_wl_change"].item(),
                          elo_changes["p5_wl_change"].item()]
    })
    table.sort_values(by=["Score"], ascending=False, inplace=True)

    for player in list(filter(None, table["Player"].to_list())):
        faction = table[table["Player"] == player]["Faction"].item()
        score = int(table[table["Player"] == player]["Score"].item())
        new_rating = int(table[table["Player"] == player]["New rating"].item())
        rating_change = int(table[table["Player"] == player]["Rating change"].item())
        if not np.isnan(rating_change):
            if rating_change > 0:
                rating_change = f"+{rating_change}"
        player_text = f"""<tr>
          <td>{player}</td>
          <td style="color:{FACTIONS[faction]}">{faction.replace("_", " ")}</td>
          <td>{score}</td>
          <td>{new_rating} ({rating_change})</td>
        </tr>
        """
        html_text += player_text

    html_text += """
    </table>
    """

    return html_text


def generate_index_html():
    # Ratings table
    rating_table_text = make_rating_table(get_player_stats())

    # Most recent results
    recent_results_text = ""
    game_data = get_games()
    last_round = np.max(game_data["round"])
    last_round_games = game_data[game_data["round"] == last_round]
    for game in last_round_games.sort_values(by=["group"]).to_dict(orient="records"):
        recent_results_text += f"""
        <h3>{game["group"].upper()}</h3>
        """
        game_text = make_result_table(game)
        recent_results_text += game_text

    # Combine text for file
    with open("templates/index.html", "w") as f:
        f.write(HTML_HEADER +
                TITLE + rating_table_text + RATING_EXPLANATION_LINK +
                LATEST_RESULTS_HEADER + recent_results_text + RESULTS_FOOTER +
                HTML_FOOTER)


def generate_results_html():
    # Results tables
    all_results_text = ""
    all_games = get_games()
    all_games.sort_values(by=["round", "group"], ascending=[False, True], inplace=True)
    all_games = all_games.to_dict(orient="records")
    for i, game in enumerate(all_games):
        all_results_text += f"<div>"
        if i == 0:
            all_results_text += f"""
                    <h3>Round {game["round"]}</h3>
                    <p>Board: {GAME_BOARDS[game["board"]]}</p>
            """
        elif all_games[i]["round"] < all_games[i-1]["round"]:
            all_results_text += f"""
                    <h3>Round {game["round"]}</h3>
                    <p>Board: {GAME_BOARDS[game["board"]]}</p>
            """

        if int(game["round"]) > 8:
            all_results_text += f"<h3>{game['group'].upper()}</h3>"
        game_text = make_result_table(game)
        all_results_text += game_text + "\n</div>"

    # Combine text for file
    with open("results.html", "w") as f:
        f.write(HTML_HEADER + TITLE + RESULTS_PAGE_HEADER +
                all_results_text +
                HTML_FOOTER)
