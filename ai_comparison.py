import os
from groq import Groq

def groq_analysis(game):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
    Analise estatisticamente o jogo {game['home']} vs {game['away']}.
    Retorne apenas um número percentual estimado de probabilidade.
    """

    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant"

    response = completion.choices[0].message.content
    try:
        value = float(response.strip().replace("%", ""))
    except:
        value = 50.0

    return value
