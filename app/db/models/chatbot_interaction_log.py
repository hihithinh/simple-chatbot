from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class ChatbotInteractionLog(SQLModel, table=True):
    __tablename__ = "chatbot_interactions_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    user_message: str
    bot_response: str
    intent_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    entities_detected: Optional[str] = None  # JSON string
    timestamp: datetime = Field(default_factory=datetime.now)
    meta_data: Optional[str] = None  # JSON string for additional data
