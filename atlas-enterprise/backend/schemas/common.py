"""
Common Pydantic Schemas for ATLAS Enterprise
Standardized response models and base schemas.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )
    
    success: bool = Field(description="Whether the request was successful")
    message: str = Field(description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseResponse):
    """Error response model."""
    
    success: bool = Field(default=False, description="Always false for errors")
    error_code: Optional[str] = Field(None, description="Error code for client handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(BaseResponse, Generic[T]):
    """Generic success response model."""
    
    success: bool = Field(default=True, description="Always true for success")
    data: Optional[T] = Field(None, description="Response data")


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response model."""
    
    success: bool = Field(default=True, description="Always true for success")
    data: List[T] = Field(description="List of items")
    pagination: Dict[str, Any] = Field(description="Pagination metadata")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        page: int,
        page_size: int,
        total_count: int,
        message: str = "Success"
    ):
        """Create paginated response with metadata."""
        total_pages = (total_count + page_size - 1) // page_size
        
        return cls(
            message=message,
            data=items,
            pagination={
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        )


class HealthResponse(BaseModel):
    """Health check response model."""
    
    success: bool = Field(description="Overall health status")
    message: str = Field(description="Health message")
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment name")
    timestamp: float = Field(description="Unix timestamp")
    checks: Dict[str, str] = Field(description="Individual health checks")


class ValidationError(BaseModel):
    """Validation error detail."""
    
    field: str = Field(description="Field name with error")
    message: str = Field(description="Error message")
    value: Any = Field(description="Invalid value provided")


class BusinessMetrics(BaseModel):
    """Business metrics for calculation results."""
    
    cost_savings: Optional[float] = Field(None, description="Potential cost savings in USD")
    risk_score: Optional[float] = Field(None, description="Risk assessment score (0-100)")
    confidence_score: Optional[float] = Field(None, description="Confidence in result (0-1)")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")


class AuditInfo(BaseModel):
    """Audit information for tracking."""
    
    user_id: Optional[int] = Field(None, description="User who performed action")
    session_id: Optional[str] = Field(None, description="Session identifier")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Action timestamp") 