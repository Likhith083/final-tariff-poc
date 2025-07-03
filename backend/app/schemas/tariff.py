from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TariffCalculationBase(BaseModel):
    hts_code: str
    description: Optional[str] = None
    quantity: float
    unit_price: float
    duty_rate: Optional[float] = None

class TariffCalculationCreate(TariffCalculationBase):
    user_id: int

class TariffCalculationResponse(TariffCalculationBase):
    id: int
    user_id: int
    total_value: float
    duty_amount: float
    total_with_duty: float
    calculation_details: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CalculationRequest(BaseModel):
    hts_code: str
    quantity: float
    unit_price: float
    description: Optional[str] = None

class CalculationResponse(BaseModel):
    hts_code: str
    description: str
    quantity: float
    unit_price: float
    total_value: float
    duty_rate: float
    duty_amount: float
    total_with_duty: float
    calculation_id: int 