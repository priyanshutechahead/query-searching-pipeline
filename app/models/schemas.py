from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class PopulationFilter(BaseModel):
    min_population: Optional[int] = Field(None, description="Minimum population boundary")
    max_population: Optional[int] = Field(None, description="Maximum population boundary")

class SearchIntent(BaseModel):
    search_query: str = Field(..., description="The main intent or keyword text to search for semantically.")
    region: Optional[str] = Field(None, description="The continent or region to filter by (e.g., 'Asia', 'Europe', 'Africa').")
    subregion: Optional[str] = Field(None, description="The specific subregion to filter by.")
    population: Optional[PopulationFilter] = Field(None, description="Numeric bounds for population.")
    language: Optional[str] = Field(None, description="The language spoken in the country.")
    currency: Optional[str] = Field(None, description="The currency used in the country.")

class SearchRequest(BaseModel):
    query: str = Field(..., description="The user's query.")

class SearchResponse(BaseModel):
    answer: str
