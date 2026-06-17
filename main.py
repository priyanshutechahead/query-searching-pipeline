from router import classify_query
from app.services.query_service import handle_structured_query, generate_final_answer
from llm_service import generate_answer as semantic_generate_answer

def run_pipeline(question):
    print(f"--- Processing: {question} ---")
    
    # 1. Classify the query
    category = classify_query(question)
    print(f"Category: {category}")
    
    if category == "API_ONLY":
        # Use structured query engine to get ALL relevant data
        data = handle_structured_query(question)
        if not data:
            return "No matching countries found in the database."
        
        # Generate answer using the full context of matching countries
        answer = generate_final_answer(question, data)
        return answer
    
    elif category == "WEB_SEARCH":
        # Placeholder for web search logic
        return "This query requires web search which is not implemented yet."
    
    elif category == "API_AND_WEB":
        # Hybrid approach
        data = handle_structured_query(question)
        # Combine with web search results...
        return "Hybrid query results (partial): " + str([c.get('country_name') for c in data])
    
    else:
        # Default to standard RAG (semantic search)
        # Note: In a real system, you'd perform vector search here and get top-k chunks.
        # But we know that's what failed for the user's specific query.
        print("Falling back to semantic search (RAG)...")
        # mock context for now as we don't have the vector search logic
        context = "Top 5 chunks would go here..." 
        return semantic_generate_answer(question, context)

if __name__ == "__main__":
    test_queries = [
        "tell me the countries whose population is above 50 cr in asia",
        "Which countries in Europe have mountains in their landscape?",
        "List countries in Asia that speak English.",
        "What are the seasons in India?",
        "recommend some places to visit in Japan"
    ]
    
    for q in test_queries:
        result = run_pipeline(q)
        print(f"Result: {result}\n")
