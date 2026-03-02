from data_collector import get_games_today
from ai_comparison import groq_analysis
from telegram_bot import send_message
from datetime import datetime, timedelta
import time

CONFIG = {
    "MIN_ODDS": 1.3,
    "MAX_ODDS": 15.0,
    "MIN_PROBABILITY": 55.0,
    "MAX_GAMES_ANALYZED": 8,
}

def format_time(iso_time):
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        dt = dt - timedelta(hours=3)
        return dt.strftime("%d/%m %H:%M")
    except:
        return iso_time

def validate_game(game):
    return CONFIG["MIN_ODDS"] <= game["odd"] <= CONFIG["MAX_ODDS"]

def process_games(games):

    results = []

    games = games[:CONFIG["MAX_GAMES_ANALYZED"]]
    print(f"Analisando {len(games)} jogos")

    for game in games:

        print(f"➡️ {game['home']} vs {game['away']} | Odd: {game['odd']}")

        if not validate_game(game):
            print("❌ Odd inválida")
            continue

        try:
            ai_result = groq_analysis(game)

            if not ai_result:
                print("❌ IA retornou None")
                continue

            probability = ai_result.get("probability", 0)
            print(f"📊 Probabilidade: {probability}%")

            if probability < CONFIG["MIN_PROBABILITY"]:
                print("❌ Abaixo do mínimo")
                continue

            results.append({
                "game": f"{game['home']} vs {game['away']}",
                "league": game["league"],
                "time": game["time"],
                "odd": game["odd"],
                "probability": round(probability, 2),
            })

            print("✅ Aprovado")

        except Exception as e:
            print(f"Erro ao analisar jogo: {e}")
            continue

    ranked = sorted(results, key=lambda x: x["probability"], reverse=True)
    return ranked[:3]

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

def main():

    print("🚀 BOT INICIADO")

    start = time.time()

    games = get_games_today()

    if not games:
        print("⚠️ Nenhum jogo retornado pela API")
        return

    print(f"📥 Jogos recebidos: {len(games)}")

    top_games = process_games(games)

    if not top_games:
        print("⚠️ Nenhum jogo passou no filtro")
        return

    message = generate_message(top_games)

    send_message(message)

    print("📤 Mensagem enviada com sucesso")
    print(f"⏱ Tempo total: {round(time.time()-start,2)}s")

if __name__ == "__main__":
    main()
