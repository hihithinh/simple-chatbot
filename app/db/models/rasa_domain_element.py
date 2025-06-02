from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class RasaDomainElement(SQLModel, table=True):
    __tablename__ = "rasa_domain_elements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    element_type: str  # slot, action, form, etc.
    name: str = Field(index=True)
    configuration: str  # JSON string
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
