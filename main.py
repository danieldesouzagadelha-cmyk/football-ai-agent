import os
import requests
from datetime import datetime
from ai_comparison import groq_analysis
from telegram_bot import send_message

MIN_PROBABILITY = 65
MIN_CONFIDENCE = 0.6


def get_games_today():
    """
    Busca jogos públicos do dia (API gratuita)
    """
    url = "https://free-api-live-football-data.p.rapidapi.com/football-live-list"

    headers = {
        "X-RapidAPI-Key": os.getenv("ODDS_API_KEY"),
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Erro ao buscar jogos:", response.text)
        return []

    data = response.json()

    games = []

    # Ajuste conforme estrutura real da API
    for match in data.get("response", []):
        games.append({
            "home": match.get("home_name"),
            "away": match.get("away_name"),
            "time": match.get("match_time")
        })

    return games


def format_message(game, result):
    return f"""
🔥 *OPORTUNIDADE DETECTADA*

⚽ {game['home']} vs {game['away']}
📅 {datetime.now().strftime('%d/%m/%Y')}

📊 Probabilidade: {result['probability']}%
🎯 Confiança: {round(result['confidence'] * 100, 1)}%
📌 Previsão: {result['prediction'].upper()}

🤖 Análise via IA (Groq)
"""


def main():
    print("🚀 BOT INICIADO")

    games = get_games_today()

    print(f"Jogos encontrados: {len(games)}")

    for game in games:

        result = groq_analysis(game)

        if not result:
            continue

        if (
            result["probability"] >= MIN_PROBABILITY and
            result["confidence"] >= MIN_CONFIDENCE
        ):
            message = format_message(game, result)
            send_message(message)
            print("Alerta enviado:", game["home"], "vs", game["away"])


if __name__ == "__main__":
    main()
