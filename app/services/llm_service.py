import json
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import ollama

from app.config import settings
from app.models.schemas import SearchIntent


def _build_ollama_client() -> ollama.Client:
    return ollama.Client(host=settings.ollama_base_url)


# Build the JSON schema once from the Pydantic model
_INTENT_SCHEMA = SearchIntent.model_json_schema()


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(4))
def _extract_search_intent_with_retry(query: str) -> SearchIntent:
    """Internal retryable call to Ollama for intent extraction."""
    client = _build_ollama_client()

    prompt = f"""You are an expert intent extractor for a country database search engine.
Extract the core semantic search intent and any specific metadata filters from the user's query.
Return a JSON object matching the schema exactly — do not include extra fields.

Query: "{query}"
"""

    response = client.chat(
        model=settings.llm_model_name,
        messages=[{"role": "user", "content": prompt}],
        format=_INTENT_SCHEMA,   # Ollama structured output (JSON schema)
        options={"temperature": 0},
    )

    raw = response.message.content
    intent_dict = json.loads(raw)
    return SearchIntent.model_validate(intent_dict)


def extract_search_intent(query: str) -> SearchIntent:
    """Extracts search intent, unwrapping RetryError to surface the real exception."""
    try:
        return _extract_search_intent_with_retry(query)
    except RetryError as e:
        raise e.last_attempt.exception() from e


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(4))
def _generate_final_answer_with_retry(query: str, context_countries: list[dict]) -> str:
    """Internal retryable call to Ollama for answer generation."""
    client = _build_ollama_client()
    context_str = json.dumps(context_countries, indent=2)

    prompt = f"""You are a highly intelligent, concise, and helpful general chatbot.
You have been provided with some JSON data retrieved from a country database. This data was fetched via semantic vector search, which means it may be INCOMPLETE — it finds similar countries, not necessarily ALL relevant ones.

Rules:
1. **Be Extremely Brief:** Do NOT write full sentences. Use short bullet points, single words, or raw lists.
2. **For geographic/relational queries** (e.g. "neighboring countries", "countries that border X"):
   - The context data may be missing some countries.
   - Use your OWN geographic knowledge to give a COMPLETE answer.
3. **For factual lookups**:
   - Prioritize the context data if the country is present.
   - Fall back to your own knowledge if the country is missing.
4. **Format:** Only output the data requested. Do not say "Here are the countries" or provide conversational filler.

Context Countries (may be incomplete):
{context_str}

User Question: {query}
"""

    response = client.chat(
        model=settings.llm_model_name,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.4},
    )

    return response.message.content


def generate_final_answer(query: str, context_countries: list[dict]) -> str:
    """Generates the final answer, unwrapping RetryError to surface the real exception."""
    try:
        return _generate_final_answer_with_retry(query, context_countries)
    except RetryError as e:
        raise e.last_attempt.exception() from e


def generate_final_answer_stream(query: str, context_countries: list[dict]):
    """Streams the final answer chunk by chunk directly from Ollama."""
    client = _build_ollama_client()
    context_str = json.dumps(context_countries, indent=2)

    prompt = f"""You are a highly intelligent, concise, and helpful general chatbot.
You have been provided with some JSON data retrieved from a country database. This data was fetched via semantic vector search, which means it may be INCOMPLETE — it finds similar countries, not necessarily ALL relevant ones.

Rules:
1. **Be Extremely Brief:** Do NOT write full sentences. Use short bullet points, single words, or raw lists.
2. **For geographic/relational queries** (e.g. "neighboring countries", "countries that border X"):
   - The context data may be missing some countries.
   - Use your OWN geographic knowledge to give a COMPLETE answer.
3. **For factual lookups**:
   - Prioritize the context data if the country is present.
   - Fall back to your own knowledge if the country is missing.
4. **Format:** Only output the data requested. Do not say "Here are the countries" or provide conversational filler.

Context Countries (may be incomplete):
{context_str}

User Question: {query}
"""

    stream = client.chat(
        model=settings.llm_model_name,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.4},
        stream=True,
    )

    for chunk in stream:
        yield chunk['message']['content']
