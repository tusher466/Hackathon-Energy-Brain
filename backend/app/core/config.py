from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Energy Brain"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True

    # DB
    database_url: str = "sqlite:///./energy_brain.db"

    # External keys optional
    nrel_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    electricitymaps_api_key: Optional[str] = None

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Model cache dir
    model_cache_dir: str = "./model_cache"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def cors_origins_list(self):
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

@lru_cache()
def get_settings():
    return Settings()
