from data_collector import get_games_today
from ai_comparison import groq_analysis
from telegram_bot import send_message
from datetime import datetime

def calculate_value(probability, odd):
    return (probability / 100 * odd) - 1

def format_time(iso_time):
    dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
    return dt.strftime("%d/%m %H:%M")

def main():
    games = get_games_today()

    results = []

    for game in games:
        ai_prob = groq_analysis(game)

        value = calculate_value(ai_prob, game["odd"])

        if value > 0:
            results.append({
                "game": f"{game['home']} vs {game['away']}",
                "league": game["league"],
                "time": game["time"],
                "odd": game["odd"],
                "probability": ai_prob,
                "value": value
            })

    # Ranking por maior VALUE
    top_games = sorted(results, key=lambda x: x["value"], reverse=True)[:3]

    if not top_games:
        send_message("⚠️ Nenhuma oportunidade estatística encontrada hoje.")
        return

    message = "🔥 *Top 3 Análises Estatísticas do Dia*\n\n"

    for idx, game in enumerate(top_games, 1):
        message += f"{idx}️⃣ *{game['game']}*\n"
        message += f"🏆 Liga: {game['league']}\n"
        message += f"⏰ Horário: {format_time(game['time'])}\n"
        message += f"📊 Probabilidade IA: {round(game['probability'],2)}%\n"
        message += f"💰 Melhor Odd: {game['odd']}\n"
        message += f"📈 Value: {round(game['value'],4)}\n\n"

    send_message(message)

if __name__ == "__main__":
    main()
