from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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

class HTSRecordResponse(BaseModel):
    hts_code: str
    description: str
    duty_rate: str
    category: str

class HTSSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class HTSSearchResponse(BaseModel):
    success: bool
    message: str
    query: str
    results: List[Dict[str, Any]]
    total_results: int

class HTSSuggestionResponse(BaseModel):
    success: bool
    message: str
    query: str
    suggestions: List[Dict[str, Any]]

class HTSRecord(BaseModel):
    hts_code: str
    description: str
    duty_rate: str
    category: str 