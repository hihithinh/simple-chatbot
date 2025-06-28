import os
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseSettings, AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Chatbot CMS"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "54320")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "vaadinstart")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "vaadinstart")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chatbot")
    
    DATABASE_URI: Optional[str] = None
    
    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000", "http://localhost:5006", "http://localhost:8001", "http://localhost:8002", "http://localhost:5175"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Rasa Configuration
    RASA_SERVER: str = os.getenv("RASA_SERVER", "http://localhost:5005")
    RASA_ACTION_SERVER: str = os.getenv("RASA_ACTION_SERVER", "http://localhost:5055")
    
    # Together AI API key
    TOGETHER_API_KEY: str = "0e22219e5d412fb12ae4c4a3fd7e611210834b75703de2697c6640179554583a"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    USE_GPT4: bool = os.getenv("USE_GPT4", "false").lower() == "true"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
