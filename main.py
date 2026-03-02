import requests
import json
import hashlib
import os
from datetime import datetime
from ai_comparison import groq_analysis
from telegram_bot import send_message

MIN_PROBABILITY = 65
MIN_CONFIDENCE = 0.6
HISTORY_FILE = "history.json"


# ==============================
# HISTÓRICO (ANTI-REPETIÇÃO)
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
# BUSCAR JOGOS (Scorebat - grátis)
# ==============================

def get_games_today():
    print("🔎 Buscando jogos...")

    url = "https://www.scorebat.com/video-api/v3/"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Erro ao buscar jogos:", response.text)
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

            except Exception:
                continue

        return games

    except Exception as e:
        print("Erro geral ao buscar jogos:", e)
        return []


# ==============================
# FORMATAR MENSAGEM
# ==============================

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


# ==============================
# MAIN
# ==============================

def main():

    print("🚀 BOT INICIADO")

    history = load_history()
    games = get_games_today()

    print(f"Jogos encontrados: {len(games)}")

    if not games:
        print("Nenhum jogo retornado pela API.")
        return

    alerts_sent = 0

    for game in games:

        game_id = generate_game_id(game)

        # Evita repetição
        if game_id in history:
            continue

        result = groq_analysis(game)

        if not result:
            continue

        probability = float(result.get("probability", 0))
        confidence = float(result.get("confidence", 0))

        if probability >= MIN_PROBABILITY and confidence >= MIN_CONFIDENCE:

            message = format_message(game, result)
            send_message(message)

            history[game_id] = {
                "home": game["home"],
                "away": game["away"],
                "probability": probability,
                "timestamp": datetime.now().isoformat()
            }

            alerts_sent += 1
            print("✅ Alerta enviado:", game["home"], "vs", game["away"])

    save_history(history)

    print(f"🔔 Total de alertas enviados: {alerts_sent}")


if __name__ == "__main__":
    main()
