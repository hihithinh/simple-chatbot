from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.schemas.crawled_content import CrawledContentRead

class DataSourceBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    source_type: str = "web"
    is_active: bool = True

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceRead(DataSourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DataSourceWithContent(BaseModel):
    data_source: DataSourceRead
    crawled_content: "CrawledContentRead"

    class Config:
        orm_mode = True
