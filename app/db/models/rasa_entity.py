from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class RasaEntity(SQLModel, table=True):
    __tablename__ = "rasa_entities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    entity_values: Optional[str] = None  # JSON string of possible values
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
