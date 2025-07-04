from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str
    timestamp: datetime = datetime.now()

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseResponse):
    """Success response model"""
    success: bool = True
    data: Optional[Any] = None

class PaginatedResponse(SuccessResponse):
    """Paginated response model"""
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

class ChatResponse(SuccessResponse):
    """Chat response model"""
    session_id: str
    response: str
    confidence: float
    sources: Optional[List[Dict[str, Any]]] = None

class HTSSearchResponse(SuccessResponse):
    """HTS search response model"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float

class TariffCalculationResponse(SuccessResponse):
    """Tariff calculation response model"""
    hts_code: str
    country_origin: str
    material_cost: float
    tariff_rate: float
    tariff_amount: float
    total_landed_cost: float
    currency: str = "USD"

class MaterialAnalysisResponse(SuccessResponse):
    """Material analysis response model"""
    original_composition: Dict[str, float]
    suggested_composition: Dict[str, float]
    cost_savings: float
    quality_impact: str
    recommendations: List[str]

class ScenarioResponse(SuccessResponse):
    """Scenario simulation response model"""
    base_scenario: Dict[str, Any]
    modified_scenario: Dict[str, Any]
    savings: float
    percentage_change: float
    risk_assessment: str

class ReportResponse(SuccessResponse):
    """Report response model"""
    report_id: str
    report_type: str
    generated_at: datetime
    download_url: Optional[str] = None

class DataIngestionResponse(SuccessResponse):
    """Data ingestion response model"""
    file_name: str
    records_processed: int
    records_added: int
    records_updated: int
    errors: List[str] = []
