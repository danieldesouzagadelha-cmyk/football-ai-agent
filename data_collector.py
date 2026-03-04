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
        print("Erro ao buscar jogos:", response.text)
        return []

    data = response.json()
    events = data.get("events", [])

    games = []

    for event in events:
        try:
            games.append({
                "id": event["id"],
                "home": event["homeTeam"]["name"],
                "away": event["awayTeam"]["name"]
            })
        except:
            continue

    return games


def get_featured_odds(event_id):
    url = f"https://sportapi7.p.rapidapi.com/api/v1/event/{event_id}/featuredodds"

    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return None

    return response.json()


def fractional_to_decimal(fraction):
    num, den = fraction.split("/")
    return (float(num) / float(den)) + 1


def extract_home_odd(data):
    markets = data.get("markets", [])

    for market in markets:
        if market.get("marketGroup") == "1X2" and market.get("marketName") == "Full time":
            for choice in market.get("choices", []):
                if choice.get("name") == "1":
                    frac = choice.get("fractionalValue")
                    return fractional_to_decimal(frac)

    return None
