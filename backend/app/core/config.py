from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "Signal Lab"
    app_version: str = "1.0.0"
    debug: bool = False
    
    database_url: str = "sqlite:///./signal_lab.db"
    
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "signal-lab"
    keycloak_client_id: str = "signal-lab-backend"
    keycloak_client_secret: Optional[str] = None
    
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()