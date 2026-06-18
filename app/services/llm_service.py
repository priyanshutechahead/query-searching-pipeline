import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

from app.config import settings
from app.models.schemas import SearchIntent

client = genai.Client(api_key=settings.gemini_api_key)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(4))
def _extract_search_intent_with_retry(query: str) -> SearchIntent:
    """Internal retryable call to Gemini for intent extraction."""
    prompt = f"""
    You are an expert intent extractor for a country database search engine.
    Extract the core semantic search intent and any specific metadata filters from the user's query.
    
    Query: "{query}"
    """
    
    response = client.models.generate_content(
        model=settings.llm_model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SearchIntent,
            temperature=0.0
        ),
    )
    
    intent_dict = json.loads(response.text)
    return SearchIntent.model_validate(intent_dict)

def extract_search_intent(query: str) -> SearchIntent:
    """Extracts search intent, unwrapping RetryError to surface the real exception."""
    try:
        return _extract_search_intent_with_retry(query)
    except RetryError as e:
        # Unwrap the last real exception so callers see the actual error
        raise e.last_attempt.exception() from e

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(4))
def _generate_final_answer_with_retry(query: str, context_countries: list[dict]) -> str:
    """Internal retryable call to Gemini for answer generation."""
    context_str = json.dumps(context_countries, indent=2)
    
    prompt = f"""
    You are a highly intelligent, concise, and helpful general chatbot.
    You have been provided with some JSON data retrieved from a database that might be relevant to the user's question.
    
    Instructions:
    1. If the user's question can be answered using the 'Context Countries' JSON data (e.g. they ask about population, region, capital, etc. of specific countries), prioritize that data to give a very concise answer (e.g. just naming the countries).
    2. If the user's question requires general knowledge NOT present in the JSON (e.g. "which countries have cold weather and mountains?"), answer the question natively using your own internal knowledge.
    3. Keep your answers brief and conversational. Never dump raw JSON or statistical text unless explicitly requested.
    
    Context Countries (may be irrelevant or empty):
    {context_str}
    
    User Question: {query}
    """
    
    response = client.models.generate_content(
        model=settings.llm_model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4
        ),
    )
    
    return response.text

def generate_final_answer(query: str, context_countries: list[dict]) -> str:
    """Generates the final answer, unwrapping RetryError to surface the real exception."""
    try:
        return _generate_final_answer_with_retry(query, context_countries)
    except RetryError as e:
        raise e.last_attempt.exception() from e
