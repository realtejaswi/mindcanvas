from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str 

    # Security
    secret_key: str = "77046b9c830c6525f812b1be75b2c5080fc4a7784517f2496376422321ad6d28"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: Optional[int] = 7

    # MCP Servers
    tavily_api_key: str
    replicate_api_token: str
    # Environment
    environment: str = "development"
    debug: bool = True

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # This will ignore extra fields instead of raising errors

settings = Settings()