print("ARQUIVO MAIN CARREGADO")

import requests
import os
from datetime import datetime, timedelta
from ai_comparison import groq_analysis
from telegram_bot import send_message
import time

CONFIG = {
    "MIN_PROBABILITY": 55.0,   # pode ajustar depois
    "MAX_GAMES_ANALYZED": 8,
}

# ================= API =================

def get_games_today():

    url = "https://odds-api1.p.rapidapi.com/odds"

    querystring = {
        "sport": "soccer",
        "region": "eu",
        "mkt": "h2h"
    }

    headers = {
        "X-RapidAPI-Key": os.getenv("ODDS_API_KEY"),
        "X-RapidAPI-Host": "odds-api1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        print("Erro na API:", response.text)
        return []

    data = response.json()

    games = []

    for match in data:
        try:
            home = match.get("home_team")
            away = match.get("away_team")
            commence_time = match.get("commence_time")

            bookmakers = match.get("bookmakers", [])
            if not bookmakers:
                continue

            markets = bookmakers[0].get("markets", [])
            if not markets:
                continue

            outcomes = markets[0].get("outcomes", [])
            if not outcomes:
                continue

            odd = outcomes[0].get("price")

            games.append({
                "home": home,
                "away": away,
                "league": match.get("sport_title"),
                "time": commence_time,
                "odd": odd
            })

        except Exception:
            continue

    return games

# ================= PROCESSAMENTO =================

def format_time(iso_time):
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        dt = dt - timedelta(hours=3)
        return dt.strftime("%d/%m %H:%M")
    except:
        return iso_time

def process_games(games):

    results = []

    games = games[:CONFIG["MAX_GAMES_ANALYZED"]]

    print(f"Jogos recebidos da API: {len(games)}")

    for game in games:

        print(f"Analisando {game['home']} vs {game['away']}")

        ai_result = groq_analysis(game)

        if not ai_result:
            print("IA retornou None")
            continue

        probability = ai_result.get("probability", 0)

        print(f"Probabilidade retornada: {probability}%")

        if probability < CONFIG["MIN_PROBABILITY"]:
            print("Abaixo do mínimo")
            continue

        results.append({
            "game": f"{game['home']} vs {game['away']}",
            "league": game["league"],
            "time": game["time"],
            "odd": game["odd"],
            "probability": round(probability, 2),
        })

        print("Jogo aprovado")

    ranked = sorted(results, key=lambda x: x["probability"], reverse=True)
    return ranked[:3]

# ================= MENSAGEM =================

def generate_message(games):

    message = "🔥 TOP PROBABILIDADE DO DIA\n"
    message += f"📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"

    for idx, game in enumerate(games, 1):

        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉"

        message += f"{medal} {game['game']}\n"
        message += f"Liga: {game['league']}\n"
        message += f"Horário: {format_time(game['time'])}\n"
        message += f"Prob IA: {game['probability']}%\n"
        message += f"Odd: {game['odd']}\n\n"

    return message

# ================= MAIN =================

def main():

    print("🚀 BOT INICIADO")

    start = time.time()

    games = get_games_today()

    if not games:
        print("Nenhum jogo retornado pela API")
        return

    top_games = process_games(games)

    if not top_games:
        print("Nenhum jogo passou no filtro")
        return

    message = generate_message(top_games)

    send_message(message)

    print("Mensagem enviada com sucesso")
    print(f"Tempo total: {round(time.time()-start,2)}s")

if __name__ == "__main__":
    main()
