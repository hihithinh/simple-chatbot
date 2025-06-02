from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class RasaRule(SQLModel, table=True):
    __tablename__ = "rasa_rules"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    rule_content: str  # YAML format
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
