import json
import uuid
from typing import List

from app.config import settings
from app.database.qdrant_client import db_client, init_qdrant_collection

DATA_FILE = "app/data/countries.json"

def create_country_profile(country_data: dict) -> str:
    """Creates a concise textual profile for a country to be used for semantic embedding."""
    name = country_data.get("country_name", "")
    capital = country_data.get("capital", "Unknown capital")
    region = country_data.get("region", "")
    subregion = country_data.get("subregion", "")
    gov = country_data.get("government_type", "")
    flag_desc = country_data.get("flag", {}).get("description", "")
    
    profile = f"{name} is a country located in {subregion}, {region}. Its capital is {capital}. The government type is {gov}. {flag_desc}"
    return profile

def ingest_data() -> dict:
    """Reads the JSON file and ingests it into Qdrant using native FastEmbed."""
    
    # Ensure collection exists
    init_qdrant_collection()
    
    # Read data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"Failed to read data file: {str(e)}"}
    
    countries = data.get("results", [])
    if not countries:
        return {"status": "error", "message": "No countries found in the dataset."}
    
    print(f"Found {len(countries)} countries to ingest. Starting ingestion...")
    
    documents = []
    metadata = []
    ids = []
    
    for country in countries:
        country_name = country.get("country_name")
        if not country_name:
            continue
            
        profile = create_country_profile(country)
        documents.append(profile)
        metadata.append(country)
        
        # Generate a deterministic UUID based on country name
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, country_name))
        ids.append(point_id)
        
    # Upload to Qdrant using FastEmbed natively
    if documents:
        db_client.add(
            collection_name=settings.collection_name,
            documents=documents,
            metadata=metadata,
            ids=ids
        )
        print("Ingestion complete.")
        return {"status": "success", "message": f"Successfully ingested {len(documents)} countries."}
    else:
        return {"status": "error", "message": "No valid points to ingest."}
