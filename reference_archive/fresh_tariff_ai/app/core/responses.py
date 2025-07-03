"""
Standardized response models for TariffAI API
Provides consistent response formats across all endpoints.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool = Field(description="Whether the request was successful")
    message: str = Field(description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = Field(None, description="Error code for client handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(BaseResponse):
    """Success response model."""
    success: bool = True
    data: Optional[Any] = Field(None, description="Response data")


class HTSResult(BaseModel):
    """HTS search result model."""
    hts_code: str = Field(description="HTS code")
    description: str = Field(description="Product description")
    tariff_rate: float = Field(description="Tariff rate percentage")
    confidence: float = Field(description="Search confidence score (0-1)")
    specific_rate: float = Field(0.0, description="Specific rate if applicable")
    other_rate: float = Field(0.0, description="Other rate if applicable")


class HTSearchResponse(SuccessResponse):
    """HTS search response model."""
    data: List[HTSResult] = Field(description="List of HTS search results")
    total_results: int = Field(description="Total number of results found")
    search_time: float = Field(description="Search execution time in seconds")


class TariffCalculationResult(BaseModel):
    """Tariff calculation result model."""
    hts_code: str = Field(description="HTS code")
    description: str = Field(description="Product description")
    material_cost: float = Field(description="Material cost")
    tariff_rate: float = Field(description="Tariff rate percentage")
    duty_amount: float = Field(description="Calculated duty amount")
    mpf_amount: float = Field(description="Merchandise processing fee")
    total_cost: float = Field(description="Total landed cost")
    currency: str = Field(description="Currency used for calculations")


class TariffCalculationResponse(SuccessResponse):
    """Tariff calculation response model."""
    data: TariffCalculationResult = Field(description="Tariff calculation result")


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(description="Message role (user/assistant)")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class ChatResponse(SuccessResponse):
    """Chat response model."""
    data: Dict[str, Any] = Field(description="Chat response data")
    session_id: Optional[str] = Field(None, description="Chat session ID")


class ScenarioResult(BaseModel):
    """Scenario analysis result model."""
    scenario_type: str = Field(description="Type of scenario analyzed")
    current_cost: float = Field(description="Current total cost")
    alternative_cost: float = Field(description="Alternative scenario cost")
    savings: float = Field(description="Potential savings")
    recommendations: List[str] = Field(description="Recommendations")


class ScenarioResponse(SuccessResponse):
    """Scenario analysis response model."""
    data: ScenarioResult = Field(description="Scenario analysis result")


class SourcingSuggestion(BaseModel):
    """Sourcing suggestion model."""
    country: str = Field(description="Suggested country")
    tariff_rate: float = Field(description="Tariff rate for this country")
    total_cost: float = Field(description="Total cost including tariffs")
    savings: float = Field(description="Potential savings vs current")
    risk_level: str = Field(description="Risk level (low/medium/high)")


class SourcingResponse(SuccessResponse):
    """Sourcing suggestions response model."""
    data: List[SourcingSuggestion] = Field(description="List of sourcing suggestions")


class RiskAssessmentResult(BaseModel):
    """Risk assessment result model."""
    hts_code: str = Field(description="HTS code")
    risk_level: str = Field(description="Overall risk level")
    compliance_issues: List[str] = Field(description="Compliance issues found")
    recommendations: List[str] = Field(description="Risk mitigation recommendations")
    restrictions: List[str] = Field(description="Import restrictions if any")


class RiskAssessmentResponse(SuccessResponse):
    """Risk assessment response model."""
    data: RiskAssessmentResult = Field(description="Risk assessment result")


class CurrencyConversionResult(BaseModel):
    """Currency conversion result model."""
    amount: float = Field(description="Original amount")
    from_currency: str = Field(description="Source currency")
    to_currency: str = Field(description="Target currency")
    converted_amount: float = Field(description="Converted amount")
    exchange_rate: float = Field(description="Exchange rate used")
    timestamp: datetime = Field(description="Conversion timestamp")


class CurrencyConversionResponse(SuccessResponse):
    """Currency conversion response model."""
    data: CurrencyConversionResult = Field(description="Currency conversion result")


# Response factory functions
def create_success_response(
    data: Any = None,
    message: str = "Success",
    **kwargs
) -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }


def create_error_response(
    message: str = "An error occurred",
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }


def create_hts_search_response(
    results: List[HTSResult],
    total_results: int,
    search_time: float,
    message: str = "HTS search completed successfully"
) -> Dict[str, Any]:
    """Create a standardized HTS search response."""
    return create_success_response(
        data=[result.dict() for result in results],
        message=message,
        total_results=total_results,
        search_time=search_time
    )


def create_tariff_calculation_response(
    result: TariffCalculationResult,
    message: str = "Tariff calculation completed successfully"
) -> Dict[str, Any]:
    """Create a standardized tariff calculation response."""
    return create_success_response(
        data=result.dict(),
        message=message
    )


def create_chat_response(
    response_data: Dict[str, Any],
    session_id: Optional[str] = None,
    message: str = "Chat response generated successfully"
) -> Dict[str, Any]:
    """Create a standardized chat response."""
    return create_success_response(
        data=response_data,
        message=message,
        session_id=session_id
    ) 