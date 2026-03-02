import requests
import json
import hashlib
import os
import time
from datetime import datetime
from ai_comparison import groq_analysis
from telegram_bot import send_message

MIN_PROBABILITY = 60
MIN_CONFIDENCE = 0.6
MAX_GAMES_PER_RUN = 8
HISTORY_FILE = "history.json"


# ==============================
# HISTÓRICO
# ==============================

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def generate_game_id(game):
    raw = f"{game['home']}_{game['away']}_{game['date']}"
    return hashlib.md5(raw.encode()).hexdigest()


# ==============================
# BASE MATEMÁTICA
# ==============================

def calculate_base_probability(game):

    base = 33  # probabilidade neutra

    # vantagem casa
    base += 7

    # heurística simples: nome maior tende a time mais tradicional
    if len(game["home"]) > len(game["away"]):
        base += 3
    elif len(game["away"]) > len(game["home"]):
        base -= 3

    # limitar entre 40 e 65
    base = max(40, min(base, 65))

    return base


# ==============================
# BUSCAR JOGOS
# ==============================

def get_games_today():

    url = "https://www.scorebat.com/video-api/v3/"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    games = []

    for match in data.get("response", []):
        try:
            title = match.get("title", "")
            if " - " not in title:
                continue

            home, away = title.split(" - ")

            games.append({
                "home": home.strip(),
                "away": away.strip(),
                "date": match.get("date")
            })

        except:
            continue

    return games


# ==============================
# MAIN
# ==============================

def main():

    print("🚀 BOT HÍBRIDO INICIADO")

    history = load_history()
    games = get_games_today()

    print("Jogos encontrados:", len(games))

    alerts = 0
    analyzed = 0

    for game in games:

        if analyzed >= MAX_GAMES_PER_RUN:
            break

        game_id = generate_game_id(game)

        if game_id in history:
            continue

        base_prob = calculate_base_probability(game)

        ai_result = groq_analysis(game)

        if not isinstance(ai_result, dict):
            continue

        ai_prob = float(ai_result["probability"])
        confidence = float(ai_result["confidence"])

        # MODELO HÍBRIDO
        final_probability = (base_prob * 0.6) + (ai_prob * 0.4)

        analyzed += 1

        if final_probability >= MIN_PROBABILITY and confidence >= MIN_CONFIDENCE:

            message = f"""
🔥 OPORTUNIDADE HÍBRIDA

⚽ {game['home']} vs {game['away']}

📊 Base matemática: {base_prob}%
🤖 IA: {ai_prob}%
🎯 Final híbrido: {round(final_probability,1)}%
🔒 Confiança IA: {round(confidence*100,1)}%

Modelo: Matemática + IA
"""

            send_message(message)

            history[game_id] = {
                "prob": final_probability,
                "timestamp": datetime.now().isoformat()
            }

            alerts += 1

        time.sleep(1.3)

    save_history(history)

    print("Analisados:", analyzed)
    print("Alertas enviados:", alerts)


if __name__ == "__main__":
    main()
