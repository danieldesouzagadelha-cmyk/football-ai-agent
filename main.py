from data_collector import get_games_today
from probability_engine import calculate_probability
from ai_comparison import groq_analysis
from telegram_bot import send_message

def main():
    games = get_games_today()

    results = []

    for game in games:
        stat_prob = calculate_probability(game)
        ai_prob = groq_analysis(game)

        final_score = (stat_prob + ai_prob) / 2

        results.append({
            "game": f"{game['home']} vs {game['away']}",
            "probability": final_score
        })

    # Ordenar top 3
    top_games = sorted(results, key=lambda x: x["probability"], reverse=True)[:3]

    message = "🔥 *Top 3 Análises Estatísticas do Dia*\n\n"

    for idx, game in enumerate(top_games, 1):
        message += f"{idx}️⃣ {game['game']}\n"
        message += f"Probabilidade estimada: {round(game['probability'],2)}%\n\n"

    send_message(message)

if __name__ == "__main__":
    main()
