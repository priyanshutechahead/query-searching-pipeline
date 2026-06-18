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
    """Ensure the Qdrant collection exists with compatible vector config."""
    client = get_qdrant_client()
    collection_name = settings.collection_name

    if client.collection_exists(collection_name):
        # Check whether the existing collection uses named vectors (dict),
        # which is what FastEmbed's `add()` method requires. If the collection
        # was created with an anonymous single-vector config, it is incompatible
        # and must be recreated.
        collection_info = client.get_collection(collection_name)
        vectors_config = collection_info.config.params.vectors
        if not isinstance(vectors_config, dict):
            print(
                f"Collection '{collection_name}' has incompatible vector params "
                f"(anonymous single vector). Deleting and recreating..."
            )
            client.delete_collection(collection_name)
        else:
            print(f"Qdrant collection '{collection_name}' already exists and is compatible.")
            return

    print(f"Creating Qdrant collection: {collection_name}")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=client.get_fastembed_vector_params()
    )

    # Create payload indices for fast deterministic filtering
    print("Creating payload indices...")
    client.create_payload_index(collection_name, "region", field_schema=models.PayloadSchemaType.KEYWORD)
    client.create_payload_index(collection_name, "subregion", field_schema=models.PayloadSchemaType.KEYWORD)
    client.create_payload_index(collection_name, "population", field_schema=models.PayloadSchemaType.INTEGER)

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
