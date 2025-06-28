from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class RasaNluExample(SQLModel, table=True):
    __tablename__ = "rasa_nlu_examples"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    intent_id: int = Field(foreign_key="rasa_intents.id")
    text: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    intent: "RasaIntent" = Relationship(back_populates="nlu_examples")
