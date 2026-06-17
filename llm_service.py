import os
import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv("app/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_answer(question, context):

    prompt = f"""
Answer using the context.
Context:{context}
Question: {question}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_json = response.json()

    return response_json["choices"][0]["message"]["content"].strip()