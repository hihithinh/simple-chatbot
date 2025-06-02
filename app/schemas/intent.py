from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class IntentBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class IntentCreate(IntentBase):
    pass

class IntentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class IntentInDBBase(IntentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Intent(IntentInDBBase):
    pass

class IntentWithExamples(IntentInDBBase):
    nlu_examples: List["NluExample"] = []
    responses: List["Response"] = []
