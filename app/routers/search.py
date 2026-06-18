from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import SearchRequest, SearchResponse
from app.services.search_service import process_search_query, process_search_query_stream

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/", response_model=SearchResponse)
def search(request: SearchRequest):
    """Process a user search query, perform deterministic vector search, and return the LLM response."""
    try:
        result = process_search_query(request.query)
        return SearchResponse(
            answer=result["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream/")
def search_stream(request: SearchRequest):
    """Process a query and stream the text answer back to the client word-by-word."""
    try:
        generator = process_search_query_stream(request.query)
        return StreamingResponse(generator, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
