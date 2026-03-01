import logging
import json
import re
import time
import os
from groq import Groq

logger = logging.getLogger(__name__)

_analysis_cache = {}
_cache_time = {}

def groq_analysis(game):

    cache_key = f"{game['home']}_{game['away']}"

    if cache_key in _analysis_cache:
        cache_age = time.time() - _cache_time.get(cache_key, 0)
        if cache_age < 300:
            logger.info(f"Usando cache para {cache_key}")
            return _analysis_cache[cache_key]

    try:
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        prompt = f"""Analise este jogo de futebol e retorne APENAS UM JSON:

Jogo: {game['home']} vs {game['away']}
Odd: {game['odd']}

Formato obrigatório:
{{
    "probability": 75.5,
    "confidence": 0.8,
    "prediction": "home"
}}
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Responda apenas JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=120
        )

        response_text = completion.choices[0].message.content

        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)

        if json_match:
            result = json.loads(json_match.group())

            result['probability'] = min(max(float(result['probability']), 0), 100)
            result['confidence'] = min(max(float(result['confidence']), 0), 1)

            _analysis_cache[cache_key] = result
            _cache_time[cache_key] = time.time()

            return result

        return groq_analysis_fallback(game)

    except Exception as e:
        logger.error(f"Erro na API Groq: {e}")
        return groq_analysis_fallback(game)


def groq_analysis_fallback(game):

    odd = game.get('odd', 2.0)
    implied_prob = (1 / odd) * 100
    safe_prob = min(implied_prob * 1.05, 95)

    return {
        "probability": round(safe_prob, 2),
        "confidence": 0.5,
        "prediction": "home"
    }
