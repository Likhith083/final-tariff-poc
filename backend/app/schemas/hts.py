from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class HTSRecordBase(BaseModel):
    hts_code: str
    description: str
    duty_rate: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    notes: Optional[str] = None

class HTSRecordCreate(HTSRecordBase):
    effective_date: Optional[datetime] = None

class HTSRecordResponse(HTSRecordBase):
    id: int
    effective_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class HTSSearchRequest(BaseModel):
    query: str
    limit: int = 10

class HTSSearchResponse(BaseModel):
    results: List[HTSRecordResponse]
    total_count: int
    query: str 