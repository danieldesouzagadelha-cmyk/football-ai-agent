import os
import requests

def get_games_today():
    api_key = os.getenv("ODDS_API_KEY")

    url = "https://odds-api1.p.rapidapi.com/v5/odds"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "odds-api1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Erro na API:", response.text)
        return []

    data = response.json()

    games = []

    # dependendo do formato, pode ser lista direta ou dentro de "data"
    matches = data if isinstance(data, list) else data.get("data", [])

    for match in matches[:10]:
        games.append({
            "home": match.get("home_team"),
            "away": match.get("away_team"),
            "league": match.get("sport_title"),
            "time": match.get("commence_time")
        })

    return games
