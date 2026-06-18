from fastapi import APIRouter, HTTPException
from app.services.ingestion_service import ingest_data

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/")
def trigger_ingestion():
    """Trigger the parsing of the countries dataset and ingestion into Qdrant."""
    result = ingest_data()
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result
