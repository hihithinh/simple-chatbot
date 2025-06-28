from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class RasaResponse(SQLModel, table=True):
    __tablename__ = "rasa_responses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    intent_id: int = Field(foreign_key="rasa_intents.id")
    response_text: str
    response_type: str = Field(default="text")  # text, image, button, etc.
    meta_data: Optional[str] = None  # JSON string for additional data
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    intent: "RasaIntent" = Relationship(back_populates="responses")
