import requests
import os
from datetime import datetime

def get_games_today():

    url = "https://odds-api1.p.rapidapi.com/odds"

    querystring = {
        "sport": "soccer",
        "region": "eu",   # pode testar: eu, uk, us
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

            # pegar primeira odd disponível
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
