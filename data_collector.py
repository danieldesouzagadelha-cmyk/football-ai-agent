import os
import requests
from datetime import datetime, timezone

def get_games_today():
    api_key = os.getenv("ODDS_API_KEY")

    url = "https://odds-api1.p.rapidapi.com/odds"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "odds-api1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Erro na API:", response.text)
        return []

    data = response.json()

    matches = data if isinstance(data, list) else data.get("data", [])

    today = datetime.now(timezone.utc).date()

    games = []

    for match in matches:

        commence = match.get("commence_time")
        if not commence:
            continue

        game_date = datetime.fromisoformat(commence.replace("Z", "+00:00")).date()

        if game_date != today:
            continue

        # Pegando a melhor odd disponível
        best_odd = None

        bookmakers = match.get("bookmakers", [])
        for book in bookmakers:
            markets = book.get("markets", [])
            for market in markets:
                if market.get("key") == "h2h":
                    for outcome in market.get("outcomes", []):
                        if outcome.get("name") == match.get("home_team"):
                            odd = outcome.get("price")
                            if best_odd is None or odd > best_odd:
                                best_odd = odd

        if best_odd is None:
            continue

        games.append({
            "home": match.get("home_team"),
            "away": match.get("away_team"),
            "league": match.get("sport_title"),
            "time": commence,
            "odd": best_odd
        })

    return games
