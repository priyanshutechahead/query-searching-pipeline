from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import settings

def get_qdrant_client() -> QdrantClient:
    """Initialize and return the Qdrant client."""
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )
    # Enable FastEmbed native integration
    client.set_model(settings.embedding_model_name)
    return client

def init_qdrant_collection():
    """Ensure the Qdrant collection exists."""
    client = get_qdrant_client()
    collection_name = settings.collection_name
    
    if not client.collection_exists(collection_name):
        print(f"Creating Qdrant collection: {collection_name}")
        # When using set_model, we can get the required vector params directly
        client.create_collection(
            collection_name=collection_name,
            vectors_config=client.get_fastembed_vector_params()
        )
        
        # Create payload indices for fast deterministic filtering
        print("Creating payload indices...")
        client.create_payload_index(collection_name, "region", field_schema=models.PayloadSchemaType.KEYWORD)
        client.create_payload_index(collection_name, "subregion", field_schema=models.PayloadSchemaType.KEYWORD)
        client.create_payload_index(collection_name, "population", field_schema=models.PayloadSchemaType.INTEGER)
    else:
        print(f"Qdrant collection {collection_name} already exists.")

def is_collection_populated() -> bool:
    """Check if the collection exists and has at least one point."""
    client = get_qdrant_client()
    collection_name = settings.collection_name
    try:
        if not client.collection_exists(collection_name):
            return False
        
        info = client.get_collection(collection_name)
        return info.points_count > 0
    except Exception as e:
        print(f"Error checking collection status: {e}")
        return False

db_client = get_qdrant_client()
