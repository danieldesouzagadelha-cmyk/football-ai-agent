import requests
import os
from datetime import datetime

API_KEY = os.getenv("RAPIDAPI_KEY")

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"
}

def get_games_today():
    today = datetime.now().strftime("%Y-%m-%d")

    url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{today}"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Erro API:", response.text)
        return []

    data = response.json()
    events = data.get("events", [])

    games = []

    for event in events:
        try:
            home = event["homeTeam"]["name"]
            away = event["awayTeam"]["name"]
            event_id = event["id"]

            games.append({
                "id": event_id,
                "home": home,
                "away": away
            })

        except KeyError:
            continue

    print(f"Jogos encontrados: {len(games)}")
    return games
