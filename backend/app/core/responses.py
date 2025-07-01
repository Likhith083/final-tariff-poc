"""
Response models for API endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HTSCodeResponse(BaseModel):
    """HTS Code response model"""
    id: int
    code: str
    description: str
    chapter: Optional[str] = None
    heading: Optional[str] = None
    subheading: Optional[str] = None
    level: Optional[int] = None
    tariff_rate: float = 0.0
    confidence_score: Optional[float] = None


class TariffCalculationResponse(BaseModel):
    """Tariff calculation response model"""
    hts_code: str
    hts_description: str
    material_cost: float
    tariff_rate: float
    tariff_amount: float
    shipping_cost: float = 0.0
    mpf_amount: float = 0.0
    total_landed_cost: float
    country_of_origin: str
    currency: str = "USD"
    calculation_breakdown: Dict[str, float]


class MaterialCompositionResponse(BaseModel):
    """Material composition response model"""
    product_name: str
    company_name: Optional[str] = None
    material_composition: Dict[str, float]
    inferred_hts_code: Optional[str] = None
    confidence_score: Optional[float] = None
    source_url: Optional[str] = None


class MaterialSuggestionResponse(BaseModel):
    """Material suggestion response model"""
    current_materials: Dict[str, float]
    suggested_materials: Dict[str, float]
    tariff_savings: float
    quality_impact: str
    reasoning: str


class ScenarioSimulationResponse(BaseModel):
    """Scenario simulation response model"""
    original_scenario: TariffCalculationResponse
    new_scenario: TariffCalculationResponse
    cost_difference: float
    percentage_change: float
    recommendations: List[str]


class AlternativeSourcingResponse(BaseModel):
    """Alternative sourcing response model"""
    current_country: str
    alternatives: List[Dict[str, Any]]
    recommendations: List[str]


class ChatMessageResponse(BaseModel):
    """Chat message response model"""
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseResponse):
    """Chat response model"""
    message: str
    session_id: str
    suggestions: Optional[List[str]] = None
    data: Optional[Dict[str, Any]] = None


class SearchResponse(BaseResponse):
    """Search response model"""
    query: str
    results: List[HTSCodeResponse]
    total_count: int
    search_time: float


class AlertSubscriptionResponse(BaseResponse):
    """Alert subscription response model"""
    subscription_id: int
    hts_codes: List[str]
    email: str
    frequency: str


class ReportResponse(BaseResponse):
    """Report response model"""
    report_id: str
    report_url: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    format: str


class HealthResponse(BaseResponse):
    """Health check response model"""
    status: str = "healthy"
    version: str
    database_status: str
    ollama_status: str
    chroma_status: str
    uptime: float 