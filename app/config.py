from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = True
    
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    collection_name: str = "country_intelligence"
    
    # Gemini API key is now optional (only needed if using Gemini models)
    gemini_api_key: str | None = None
    
    # Local Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    llm_model_name: str = "llama3.2:1b"  # Local Ollama model
    
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
