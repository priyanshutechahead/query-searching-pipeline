import os
import json
import requests
import re
from dotenv import load_dotenv
from app.utils.data_utils import search_countries, get_country_by_name

load_dotenv()
load_dotenv("app/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def extract_query_params(question):
    prompt = f"""
Extract search criteria from the user's question about countries to help filter a JSON dataset.
Fields in the dataset include: country_name, capital, region, subregion, population, area, currencies, languages, etc.

Return a JSON object with:
- "query_text": A string for keyword search (e.g., "island", "landlocked"). Use null if not applicable.
- "filters": A dictionary of exact field matches (e.g., {{"region": "Asia"}}). Use null if not applicable.
- "logic": A brief description of any complex logic needed (e.g., "population > 500000000").

Question: {question}
JSON:
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
        ],
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()

    try:
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {}

def handle_structured_query(question):
    criteria = extract_query_params(question)
    print(f"Extracted criteria: {criteria}")

    # Use the new search_countries for flexible matching
    results = search_countries(
        query_text=criteria.get("query_text"),
        filters=criteria.get("filters")
    )

    # Apply additional logic from the LLM criteria
    logic = criteria.get("logic", "").lower()
    if logic:
        # Population logic
        if "population" in logic:
            import re
            match = re.search(r'(>|<|above|below|more than|less than)\s*(\d+)', logic)
            if match:
                op_str, val_str = match.groups()
                val = int(val_str)
                if "cr" in logic or "crore" in logic:
                    val *= 10000000
                if op_str in [">", "above", "more than"]:
                    results = [c for c in results if c.get("population", 0) > val]
                elif op_str in ["<", "below", "less than"]:
                    results = [c for c in results if c.get("population", 0) < val]
        
        # Language logic
        if "language" in logic:
            # Check if any specific language is mentioned in logic
            langs_to_check = ["english", "french", "spanish", "hindi", "chinese", "arabic"]
            for lang in langs_to_check:
                if lang in logic:
                    results = [c for c in results if any(lang in str(l).lower() for l in c.get("official_languages", []))]
                    break

        # Landscape logic
        if "landscape" in logic or "mountain" in logic or "beach" in logic:
            if "mountain" in logic:
                results = [c for c in results if "Mountains" in c.get("Landscape", [])]
            if "beach" in logic:
                results = [c for c in results if "Beaches" in c.get("Landscape", [])]

    return results

def generate_final_answer(question, data):
    # Summarize data to avoid Payload Too Large (413)
    # Strip heavy fields like flag, links, coordinates
    summarized_data = []
    for c in data:
        summary = {
            "name": c.get("country_name"),
            "capital": c.get("capital"),
            "region": c.get("region"),
            "population": c.get("population"),
            "languages": c.get("official_languages"),
            "landscape": c.get("Landscape"),
            "seasons": c.get("seasons"),
            "flora_fauna": c.get("FloraFauna")
        }
        # Remove null values
        summary = {k: v for k, v in summary.items() if v is not None}
        summarized_data.append(summary)
    
    # Limit to top 20 results if it's still too large
    if len(summarized_data) > 20:
        summarized_data = summarized_data[:20]
        question += " (Note: Only showing top 20 results due to context limits)"

    context = json.dumps(summarized_data, indent=2)
    
    prompt = f"""
You are a helpful assistant. Use the following data to answer the user's question accurately.
Data:
{context}

Question: {question}
Answer:
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

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    
    return result["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    q = "tell me the countries whose population is above 50 cr in asia"
    data = handle_structured_query(q)
    answer = generate_final_answer(q, data)
    print(f"Question: {q}")
    print(f"Answer: {answer}")
