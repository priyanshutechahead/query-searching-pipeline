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
    result_limit: int = Field(
        default=10,
        description=(
            "How many results to retrieve. Use a high number (20-50) when the user asks for ALL items "
            "or uses open-ended language ('list all', 'name every', 'which countries'). "
            "Use the exact number when the user specifies one (e.g. 'top 5', '3 countries'). "
            "Default to 10 for general queries."
        )
    )

class SearchRequest(BaseModel):
    query: str = Field(..., description="The user's query.")

class SearchResponse(BaseModel):
    answer: str
