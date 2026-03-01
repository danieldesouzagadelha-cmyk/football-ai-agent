from data_collector import get_games_today
from ai_comparison import groq_analysis
from telegram_bot import send_message
from datetime import datetime, timedelta
import logging
import time
import json

# ================= CONFIG =================

CONFIG = {
    'MIN_ODDS': 1.3,
    'MAX_ODDS': 15.0,
    'MIN_PROBABILITY': 5.0,
    'VALUE_THRESHOLD': 0.02,   # 2% mais realista
    'MAX_GAMES_ANALYZED': 8,   # limitar chamadas Groq
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= FUNÇÕES =================

def calculate_value(probability, odd):
    return (probability / 100 * odd) - 1

def calculate_kelly(probability, odd):
    implied_prob = 1 / odd
    edge = (probability / 100) - implied_prob
    if edge <= 0:
        return 0
    kelly = edge / (odd - 1)
    return min(kelly, 0.05)  # máximo 5%

def format_time(iso_time):
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        dt = dt - timedelta(hours=3)
        return dt.strftime("%d/%m %H:%M")
    except:
        return iso_time

def validate_game(game):
    if not (CONFIG['MIN_ODDS'] <= game['odd'] <= CONFIG['MAX_ODDS']):
        return False
    return True

# ================= PROCESSAMENTO =================

def process_games(games):

    results = []

    # Limitar número de jogos para economizar Groq
    games = games[:CONFIG['MAX_GAMES_ANALYZED']]

    for game in games:

        if not validate_game(game):
            continue

        try:
            ai_result = groq_analysis(game)
            if not ai_result:
                continue

            probability = ai_result.get("probability", 0)

            if probability < CONFIG['MIN_PROBABILITY']:
                continue

            value = calculate_value(probability, game['odd'])

            if value <= CONFIG['VALUE_THRESHOLD']:
                continue

            stake_fraction = calculate_kelly(probability, game['odd'])

            results.append({
                "game": f"{game['home']} vs {game['away']}",
                "league": game["league"],
                "time": game["time"],
                "odd": game["odd"],
                "probability": round(probability, 2),
                "value": round(value, 4),
                "stake_fraction": round(stake_fraction * 100, 2)
            })

        except Exception as e:
            logger.error(f"Erro no jogo {game.get('home')}: {e}")
            continue

    # Ranking por maior value
    ranked = sorted(results, key=lambda x: x["value"], reverse=True)

    return ranked[:3]

# ================= MENSAGEM =================

def generate_message(games):

    if not games:
        return "⚠️ Nenhuma oportunidade estatística encontrada hoje."

    message = "🔥 *TOP 3 VALUE DO DIA*\n"
    message += f"📅 {datetime.now().strftime('%d/%m/%Y')}\n"
    message += "═══════════════════════\n\n"

    for idx, game in enumerate(games, 1):

        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉"

        message += f"{medal} *{game['game']}*\n"
        message += f"🏆 Liga: {game['league']}\n"
        message += f"⏰ Horário: {format_time(game['time'])}\n"
        message += f"📊 Prob IA: {game['probability']}%\n"
        message += f"💰 Odd: {game['odd']}\n"
        message += f"📈 Value: {game['value']*100:.2f}%\n"
        message += f"💵 Stake sugerida: {game['stake_fraction']}% banca\n\n"

    message += "⚠️ Gestão de risco sempre.\n"
    return message

# ================= MAIN =================

def main():

    start = time.time()

    games = get_games_today()

    if not games:
        send_message("⚠️ Nenhum jogo encontrado hoje.")
        return

    top_games = process_games(games)

    message = generate_message(top_games)

    send_message(message)

    logger.info(f"Finalizado em {round(time.time()-start,2)}s")

if __name__ == "__main__":
    main()
