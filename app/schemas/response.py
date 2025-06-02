from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ResponseBase(BaseModel):
    intent_id: int
    response_text: str
    response_type: str = "text"
    meta_data: Optional[str] = None
    is_active: bool = True

class ResponseCreate(ResponseBase):
    pass

class ResponseUpdate(BaseModel):
    response_text: Optional[str] = None
    response_type: Optional[str] = None
    meta_data: Optional[str] = None
    is_active: Optional[bool] = None

class ResponseInDBBase(ResponseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Response(ResponseInDBBase):
    pass
