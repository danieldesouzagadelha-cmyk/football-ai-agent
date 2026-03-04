from data_collector import get_games_today, get_featured_odds, extract_home_odd
from elo import get_rating, calculate_probability
from telegram_bot import send_message

EDGE_THRESHOLD = -1


def run():
    print("🚀 BOT ELO INICIADO")

    games = get_games_today()

    print(f"Jogos encontrados: {len(games)}")

    for game in games:
        home = game["home"]
        away = game["away"]

        odds_data = get_featured_odds(game["id"])

        if not odds_data:
            continue

        odd_home = extract_home_odd(odds_data)

        if not odd_home:
            continue

        home_rating = get_rating(home)
        away_rating = get_rating(away)

        prob_model = calculate_probability(home_rating, away_rating)
        prob_market = 1 / odd_home

        edge = prob_model - prob_market

        print(f"{home} vs {away} | Edge: {round(edge,4)}")

        if edge >= EDGE_THRESHOLD:
            message = (
                f"📊 <b>ALERTA QUANTITATIVO</b>\n\n"
                f"{home} vs {away}\n\n"
                f"Modelo: {round(prob_model*100,2)}%\n"
                f"Mercado: {round(prob_market*100,2)}%\n"
                f"Odd: {round(odd_home,2)}\n"
                f"Edge: {round(edge*100,2)}%"
            )

            send_message(message)


if __name__ == "__main__":
    run()
