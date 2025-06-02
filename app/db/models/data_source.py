from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class DataSource(SQLModel, table=True):
    __tablename__ = "data_sources"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url: str
    description: Optional[str] = None
    source_type: str  # web, document, api, etc.
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    crawled_contents: List["CrawledContent"] = Relationship(back_populates="data_source")
