from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship


class CrawledContent(SQLModel, table=True):
    __tablename__ = "crawled_content"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    data_source_id: int = Field(foreign_key="data_sources.id")
    title: str
    content: str
    url: Optional[str] = None
    meta_data: Optional[str] = None  # JSON string
    is_processed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    data_source: "DataSource" = Relationship(back_populates="crawled_contents")
