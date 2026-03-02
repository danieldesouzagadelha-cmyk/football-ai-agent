import os
import requests
import json
import hashlib
from datetime import datetime
from ai_comparison import groq_analysis
from telegram_bot import send_message

MIN_PROBABILITY = 65
MIN_CONFIDENCE = 0.6

HISTORY_FILE = "history.json"


# --------------------------
# HISTÓRICO
# --------------------------

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def generate_game_id(game):
    raw = f"{game['home']}_{game['away']}_{game['time']}"
    return hashlib.md5(raw.encode()).hexdigest()


# --------------------------
# BUSCAR JOGOS
# --------------------------

def get_games_today():

    url = "https://free-api-live-football-data.p.rapidapi.com/football-live-list"

    headers = {
        "X-RapidAPI-Key": os.getenv("ODDS_API_KEY"),
        "X-RapidAPI-Host": "free-api-live-football-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Erro API:", response.text)
        return []

    data = response.json()

    games = []

    for match in data.get("response", []):
        games.append({
            "home": match.get("home_name"),
            "away": match.get("away_name"),
            "time": match.get("match_time")
        })

    return games


# --------------------------
# FORMATAÇÃO
# --------------------------

def format_message(game, result):

    return f"""
🔥 *OPORTUNIDADE DETECTADA*

⚽ {game['home']} vs {game['away']}
📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 Probabilidade: {result['probability']}%
🎯 Confiança: {round(result['confidence'] * 100, 1)}%
📌 Previsão: {result['prediction'].upper()}

🤖 Análise via Groq AI
"""


# --------------------------
# EXECUÇÃO PRINCIPAL
# --------------------------

def main():

    print("🚀 BOT INICIADO")

    history = load_history()
    games = get_games_today()

    print(f"Jogos encontrados: {len(games)}")

    for game in games:

        game_id = generate_game_id(game)

        # 🔒 Anti repetição
        if game_id in history:
            continue

        result = groq_analysis(game)

        if not result:
            continue

        if (
            result["probability"] >= MIN_PROBABILITY and
            result["confidence"] >= MIN_CONFIDENCE
        ):

            message = format_message(game, result)
            send_message(message)

            history[game_id] = {
                "home": game["home"],
                "away": game["away"],
                "time": game["time"],
                "probability": result["probability"],
                "timestamp": datetime.now().isoformat()
            }

            print("Alerta enviado:", game["home"], "vs", game["away"])

    save_history(history)


if __name__ == "__main__":
    main()
