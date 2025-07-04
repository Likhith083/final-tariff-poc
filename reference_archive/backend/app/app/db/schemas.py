from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import datetime

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    company: Optional[str]
    material_composition: Optional[Dict[str, Any]]
    hts_code: Optional[str]

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class TariffBase(BaseModel):
    hts_code: str
    country: str
    rate: float
    effective_date: Optional[datetime.datetime]

class TariffCreate(TariffBase):
    pass

class Tariff(TariffBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    hts_code: str
    email: EmailStr
    is_active: Optional[bool] = True

class AlertCreate(AlertBase):
    user_id: int

class Alert(AlertBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class ScenarioBase(BaseModel):
    name: str
    data: Dict[str, Any]

class ScenarioCreate(ScenarioBase):
    user_id: int

class Scenario(ScenarioBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    name: str
    file_path: str

class ReportCreate(ReportBase):
    user_id: int

class Report(ReportBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True 