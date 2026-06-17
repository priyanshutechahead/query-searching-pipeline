import os
import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv("app/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def classify_query(question: str):
    prompt = f"""
You are a routing assistant.

Classify the query into exactly one category:

API_ONLY
WEB_SEARCH
API_AND_WEB

Rules:

API_ONLY:
- population, capital, currency, language
- region, subregion, timezone
- weather, humidity (real-time)
- landscape, mountains, beaches, deserts
- seasons, flora, fauna
- general facts about specific countries found in a database

WEB_SEARCH:
- recommendations
- work
- study
- relocation
- tourism
- hidden places
- culture
- comparisons

API_AND_WEB:
- needs both real-time country data and recommendations

Question:
{question}

Return only category name.
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    result = response.json()

    category = result["choices"][0]["message"]["content"].strip()
    return category.replace("`", "").strip()
