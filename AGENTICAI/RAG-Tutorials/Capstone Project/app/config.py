from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # LLMs
    gemini_api_key: str = ""
    groq_api_key: str = ""
    primary_model: str = "gemini-2.5-flash"
    fallback_model: str = "llama3-8b-8192"
    
    # LangSmith Tracing
    langchain_tracing_v2: str = "true"
    langchain_api_key: str = ""
    langchain_project: str = "production-rag "
    
    # Application Settings
    app_env: str = "development"
    log_level: str = "INFO"
    rate_limit: str = "20/minute"
    cache_ttl_seconds: int = 300
    max_retries: int = 3
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    use_redis: bool = True

    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

@lru_cache
def get_settings() -> Settings:
    return Settings()