from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CrawledContentBase(BaseModel):
    title: str
    content: str
    url: Optional[str] = None
    meta_data: Optional[str] = None
    is_processed: bool = False

class CrawledContentCreate(CrawledContentBase):
    data_source_id: int

class CrawledContentRead(CrawledContentBase):
    id: int
    data_source_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
