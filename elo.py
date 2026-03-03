import json
import os
import math

RATINGS_FILE = "data/ratings.json"
INITIAL_RATING = 1500
K_FACTOR = 20


def load_ratings():
    if not os.path.exists(RATINGS_FILE):
        return {}
    with open(RATINGS_FILE, "r") as f:
        return json.load(f)


def save_ratings(ratings):
    os.makedirs("data", exist_ok=True)
    with open(RATINGS_FILE, "w") as f:
        json.dump(ratings, f, indent=2)


def get_rating(team, ratings):
    return ratings.get(team, INITIAL_RATING)


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(home, away, result, ratings):
    """
    result:
    1 = home win
    0.5 = draw
    0 = away win
    """

    rating_home = get_rating(home, ratings)
    rating_away = get_rating(away, ratings)

    expected_home = expected_score(rating_home, rating_away)
    expected_away = expected_score(rating_away, rating_home)

    rating_home += K_FACTOR * (result - expected_home)
    rating_away += K_FACTOR * ((1 - result) - expected_away)

    ratings[home] = rating_home
    ratings[away] = rating_away

    return ratings
