from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = True
    
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    collection_name: str = "country_intelligence"
    
    gemini_api_key: str
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    llm_model_name: str = "gemini-2.5-flash"  # Works perfectly on your tier!

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
