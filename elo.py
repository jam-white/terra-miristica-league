import numpy as np
from constants import C, MIN_K, MAX_K


def calculate_winloss_matrix(game_results):
    """Returns a win-loss matrix from a set of game results"""
    scores = np.array([entry.score for entry in game_results])
    score_delta_matrix = np.zeros((len(scores), len(scores)))
    for i, score in enumerate(scores):
        score_delta_matrix[i] = score - scores
    winloss_matrix = (np.sign(score_delta_matrix) + 1) / 2
    return winloss_matrix


def calculate_expected_matrix(game_results):
    """Returns the expected win probability matrix from a set of game results"""
    ratings = np.array([entry.old_rating for entry in game_results])
    expected_matrix = np.zeros((len(ratings), len(ratings)))
    q_list = 10 ** (ratings / C)
    for i, q in enumerate(q_list):
        expected_matrix[i] = q / (q + q_list)
    return expected_matrix


def calculate_new_elos(game_results, num_games, k_scale=1):
    """Returns game results with new ratings updated"""
    expected = calculate_expected_matrix(game_results)
    actual = calculate_winloss_matrix(game_results)
    num_games_array = np.array([num_games[entry.player.name]+1 for entry in game_results])
    k = np.minimum(np.maximum((800 / num_games_array[:, np.newaxis]), MIN_K), MAX_K)

    rating_change_matrix = (k * k_scale) * (actual - expected)
    player_rating_changes = rating_change_matrix.sum(axis=1)
    for i, entry in enumerate(game_results):
        entry.new_rating = int(entry.old_rating + int(player_rating_changes[i]))
    return game_results
