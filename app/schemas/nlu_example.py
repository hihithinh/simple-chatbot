from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NluExampleBase(BaseModel):
    intent_id: int
    text: str
    is_active: bool = True

class NluExampleCreate(NluExampleBase):
    pass

class NluExampleUpdate(BaseModel):
    text: Optional[str] = None
    is_active: Optional[bool] = None

class NluExampleInDBBase(NluExampleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NluExample(NluExampleInDBBase):
    pass
