import os
from datetime import datetime
from data_collector import get_games_today
from telegram_bot import send_message
from elo import load_ratings, save_ratings, get_rating, expected_score

# ==============================
# CONFIGURAÇÕES PROFISSIONAIS
# ==============================

MIN_PROBABILITY = 60  # só envia se Elo >= 60%
MAX_ALERTS = 3        # máximo de alertas por execução


def format_message(game, probability):
    return f"""
🔥 OPORTUNIDADE DETECTADA (ELO)

⚽ {game['home']} vs {game['away']}
📅 {game['time']}

📊 Probabilidade Modelo: {round(probability, 1)}%

🧠 Modelo: Elo Rating Matemático
"""


def main():
    print("🚀 BOT ELO INICIADO")
    print("🔎 Buscando jogos...")

    games = get_games_today()

    if not games:
        print("Nenhum jogo encontrado.")
        return

    print(f"Jogos encontrados: {len(games)}")

    ratings = load_ratings()

    alerts_sent = 0

    for game in games:

        if alerts_sent >= MAX_ALERTS:
            break

        home = game["home"]
        away = game["away"]

        home_rating = get_rating(home, ratings)
        away_rating = get_rating(away, ratings)

        probability = expected_score(home_rating, away_rating) * 100

        print(
            f"{home} vs {away} | "
            f"Rating: {round(home_rating)} x {round(away_rating)} | "
            f"Prob: {round(probability,1)}%"
        )

        if probability >= MIN_PROBABILITY:

            message = format_message(game, probability)
            send_message(message)

            alerts_sent += 1

    print(f"Alertas enviados: {alerts_sent}")


if __name__ == "__main__":
    main()
