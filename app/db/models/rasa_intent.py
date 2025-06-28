from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class RasaIntent(SQLModel, table=True):
    __tablename__ = "rasa_intents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    data_source_id: Optional[int] = Field(foreign_key="data_sources.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    data_source: "DataSource" = Relationship(back_populates="intents")
    nlu_examples: List["RasaNluExample"] = Relationship(back_populates="intent")
    responses: List["RasaResponse"] = Relationship(back_populates="intent")
