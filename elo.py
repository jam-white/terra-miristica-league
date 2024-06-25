import numpy as np

C = 400
MIN_K = 32
MAX_K = 200


def calculate_elo_changes(ratings, results, num_games, k_scale=1):
    expected = calculate_expected_matrix(ratings)
    k = np.minimum(np.maximum((800 / num_games[:, np.newaxis]), MIN_K), MAX_K)
    rating_change_matrix = (k * k_scale) * (results - expected)
    player_rating_changes = rating_change_matrix.sum(axis=1)
    return player_rating_changes


def calculate_expected_matrix(ratings):
    expected_matrix = np.zeros((len(ratings), len(ratings)))
    q_list = 10 ** (ratings / C)
    for i, q in enumerate(q_list):
        expected_matrix[i] = q / (q + q_list)
    return expected_matrix
