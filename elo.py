ratings = {}

def get_rating(team):
    if team not in ratings:
        ratings[team] = 1500
    return ratings[team]


def calculate_probability(home_rating, away_rating):
    return 1 / (1 + 10 ** ((away_rating - home_rating) / 400))


def update_elo(home, away, home_goals, away_goals, k=20):
    home_rating = get_rating(home)
    away_rating = get_rating(away)

    expected_home = calculate_probability(home_rating, away_rating)

    if home_goals > away_goals:
        score_home = 1
    elif home_goals == away_goals:
        score_home = 0.5
    else:
        score_home = 0

    new_home = home_rating + k * (score_home - expected_home)
    new_away = away_rating + k * ((1 - score_home) - (1 - expected_home))

    ratings[home] = new_home
    ratings[away] = new_away
