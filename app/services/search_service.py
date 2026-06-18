from qdrant_client.http import models

from app.config import settings
from app.config import settings
from app.database.qdrant_client import db_client
from app.services.llm_service import extract_search_intent, generate_final_answer, generate_final_answer_stream

def build_qdrant_filter(intent) -> models.Filter:
    """Builds a Qdrant filter based on the extracted search intent."""
    must_conditions = []
    
    if intent.region:
        must_conditions.append(
            models.FieldCondition(
                key="region",
                match=models.MatchValue(value=intent.region)
            )
        )
        
    if intent.subregion:
        must_conditions.append(
            models.FieldCondition(
                key="subregion",
                match=models.MatchValue(value=intent.subregion)
            )
        )
        
    if intent.population:
        range_params = {}
        if intent.population.min_population is not None:
            range_params["gte"] = intent.population.min_population
        if intent.population.max_population is not None:
            range_params["lte"] = intent.population.max_population
            
        if range_params:
            must_conditions.append(
                models.FieldCondition(
                    key="population",
                    range=models.Range(**range_params)
                )
            )
            
    # For nested attributes or lists, Qdrant can match values
    if intent.language:
        # Note: language filtering depends on the JSON structure.
        # This assumes a flat match is possible or it's just a text match.
        pass
        
    if intent.currency:
        pass

    if must_conditions:
        return models.Filter(must=must_conditions)
    return None

def process_search_query(query: str) -> dict:
    """End-to-end processing of a user search query using Native FastEmbed."""
    
    # 1. Extract Intent and Filters using Gemini
    print(f"Extracting intent for query: '{query}'")
    intent = extract_search_intent(query)
    print(f"Extracted Intent: {intent}")
    
    # 2. Build Filter
    qdrant_filter = build_qdrant_filter(intent)
    
    # 3. Search Qdrant via FastEmbed
    print(f"Searching Qdrant (limit={intent.result_limit})...")
    search_results = db_client.query(
        collection_name=settings.collection_name,
        query_text=intent.search_query,
        query_filter=qdrant_filter,
        limit=intent.result_limit
    )
    
    # Extract matching country payloads (db_client.query returns QueryResponse where we get metadata)
    context_countries = [hit.metadata for hit in search_results if hit.metadata]
    
    # --- DEBUG: Print the context being sent to the LLM ---
    print("\n" + "="*60)
    print(f"CONTEXT SENT TO LLM ({len(context_countries)} countries):")
    print("="*60)
    for i, country in enumerate(context_countries, 1):
        country_name = country.get('country_name', 'Unknown')
        region = country.get('region', 'N/A')
        population = country.get('population', 'N/A')
        print(f"  [{i}] {country_name} | Region: {region} | Population: {population:,}" if isinstance(population, int) else f"  [{i}] {country_name} | Region: {region} | Population: {population}")
    print("="*60 + "\n")
    # -------------------------------------------------------

    # 4. Generate Final Answer
    print(f"Generating final answer using {len(context_countries)} matching countries as context...")
    answer = generate_final_answer(query, context_countries)
        
    return {
        "answer": answer,
        "context_countries": context_countries
    }

def process_search_query_stream(query: str):
    """End-to-end processing that yields answer chunks for streaming."""
    print(f"Extracting intent for query: '{query}'")
    intent = extract_search_intent(query)
    qdrant_filter = build_qdrant_filter(intent)
    
    print(f"Searching Qdrant (limit={intent.result_limit})...")
    search_results = db_client.query(
        collection_name=settings.collection_name,
        query_text=intent.search_query,
        query_filter=qdrant_filter,
        limit=intent.result_limit
    )
    
    context_countries = [hit.metadata for hit in search_results if hit.metadata]
    print(f"Generating streaming answer using {len(context_countries)} matching countries...")
    
    return generate_final_answer_stream(query, context_countries)

