import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import ingest, search
from app.database.qdrant_client import is_collection_populated
from app.services.ingestion_service import ingest_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check if DB is populated, if not, ingest data automatically
    print("Checking Qdrant database status...")
    if not is_collection_populated():
        print("Database is empty. Starting automatic data ingestion...")
        result = ingest_data()
        if result.get("status") == "success":
            print(f"Automatic ingestion successful: {result.get('message')}")
        else:
            print(f"Automatic ingestion failed: {result.get('message')}")
    else:
        print("Database is already populated. Ready for search!")
    
    yield
    # Shutdown logic goes here (if any)

app = FastAPI(
    title="Country Intelligence RAG API",
    description="Deterministic RAG Backend using FastAPI, Qdrant, and Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ingest.router)
app.include_router(search.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Country Intelligence RAG API"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.debug
    )
