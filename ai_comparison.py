from groq import Groq
import os
import json
import re

def groq_analysis(game):

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
Analise o jogo:

{game['home']} vs {game['away']}

Responda APENAS com JSON válido no formato:

{{
  "probability": 70.5,
  "confidence": 0.75,
  "prediction": "home"
}}

Sem texto adicional.
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

        content = completion.choices[0].message.content

        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match:
            return None

        data = json.loads(match.group())

        if not all(k in data for k in ["probability", "confidence", "prediction"]):
            return None

        return {
            "probability": float(data["probability"]),
            "confidence": float(data["confidence"]),
            "prediction": data["prediction"]
        }

    except Exception as e:
        print("Erro na Groq:", e)
        return None
