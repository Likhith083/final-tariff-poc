"""
Tariff Pydantic Schemas for ATLAS Enterprise
Request/response models for tariff calculations and HTS operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, ConfigDict

from .common import BaseResponse, BusinessMetrics


class HTSCodeBase(BaseModel):
    """Base HTS code schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    hts_code: str = Field(description="10-digit HTS code")
    description: str = Field(description="Full product description")
    brief_description: Optional[str] = Field(None, description="Brief product description")
    chapter_description: Optional[str] = Field(None, description="Chapter description")
    unit_of_quantity: Optional[str] = Field(None, description="Unit of measurement")


class HTSCodeResponse(HTSCodeBase):
    """HTS code response schema."""
    
    id: int = Field(description="Database ID")
    hts_8: str = Field(description="8-digit HTS code")
    hts_6: str = Field(description="6-digit harmonized code")
    hts_4: str = Field(description="4-digit heading")
    hts_2: str = Field(description="2-digit chapter")
    effective_date: datetime = Field(description="Effective date")
    is_active: bool = Field(description="Whether code is active")


class TariffRateResponse(BaseModel):
    """Tariff rate response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="Database ID")
    mfn_rate: float = Field(description="Most Favored Nation rate (%)")
    specific_rate: float = Field(description="Specific rate ($/unit)")
    fta_rate: Optional[float] = Field(None, description="Free Trade Agreement rate (%)")
    gsp_rate: Optional[float] = Field(None, description="GSP rate (%)")
    antidumping_duty: float = Field(description="Antidumping duty (%)")
    countervailing_duty: float = Field(description="Countervailing duty (%)")
    effective_rate: float = Field(description="Effective rate after preferences (%)")
    total_duty_rate: float = Field(description="Total duty rate including AD/CVD (%)")
    country_code: str = Field(description="Country code")
    country_name: str = Field(description="Country name")


class TariffCalculationRequest(BaseModel):
    """Tariff calculation request schema."""
    
    hts_code: str = Field(description="HTS code for the product", min_length=4, max_length=10)
    country_code: str = Field(description="Country of origin (ISO 2-letter code)", min_length=2, max_length=2)
    product_value: float = Field(description="FOB value of goods", gt=0)
    quantity: float = Field(default=1.0, description="Quantity of items", gt=0)
    freight_cost: float = Field(default=0.0, description="Shipping/freight cost", ge=0)
    insurance_cost: float = Field(default=0.0, description="Insurance cost", ge=0)
    other_costs: float = Field(default=0.0, description="Other additional costs", ge=0)
    currency: str = Field(default="USD", description="Currency of values", min_length=3, max_length=3)
    
    @validator('hts_code')
    def validate_hts_code(cls, v):
        # Remove dots and validate format
        clean_code = v.replace('.', '').replace(' ', '')
        if not clean_code.isdigit():
            raise ValueError('HTS code must contain only digits')
        if len(clean_code) < 4 or len(clean_code) > 10:
            raise ValueError('HTS code must be 4-10 digits')
        return clean_code
    
    @validator('country_code')
    def validate_country_code(cls, v):
        return v.upper()
    
    @validator('currency')
    def validate_currency(cls, v):
        return v.upper()


class TariffCalculationResponse(BaseResponse):
    """Tariff calculation response schema."""
    
    data: Dict[str, Any] = Field(description="Calculation results")
    
    class CalculationData(BaseModel):
        """Nested calculation data structure."""
        
        hts_code: str = Field(description="HTS code used")
        country_code: str = Field(description="Country code")
        country_name: str = Field(description="Country name")
        
        input_values: Dict[str, Any] = Field(description="Input parameters")
        calculated_values: Dict[str, Any] = Field(description="Calculated amounts")
        unit_costs: Dict[str, Any] = Field(description="Per-unit costs")
        rates_applied: Dict[str, Any] = Field(description="Rates used in calculation")
        percentages: Dict[str, Any] = Field(description="Percentage breakdowns")
        trade_preferences: List[str] = Field(description="Applicable trade preferences")
        calculation_metadata: Dict[str, Any] = Field(description="Additional metadata")


class SourcingComparisonRequest(BaseModel):
    """Sourcing comparison request schema."""
    
    hts_code: str = Field(description="HTS code for the product", min_length=4, max_length=10)
    countries: List[str] = Field(description="List of country codes to compare", min_items=2, max_items=10)
    product_value: float = Field(description="FOB value of goods", gt=0)
    quantity: float = Field(default=1.0, description="Quantity of items", gt=0)
    freight_cost: float = Field(default=0.0, description="Shipping/freight cost", ge=0)
    insurance_cost: float = Field(default=0.0, description="Insurance cost", ge=0)
    other_costs: float = Field(default=0.0, description="Other additional costs", ge=0)
    currency: str = Field(default="USD", description="Currency of values", min_length=3, max_length=3)
    
    @validator('countries')
    def validate_countries(cls, v):
        # Convert to uppercase and remove duplicates
        return list(set(country.upper() for country in v))
    
    @validator('hts_code')
    def validate_hts_code(cls, v):
        clean_code = v.replace('.', '').replace(' ', '')
        if not clean_code.isdigit():
            raise ValueError('HTS code must contain only digits')
        return clean_code


class SourcingOption(BaseModel):
    """Individual sourcing option result."""
    
    country_code: str = Field(description="Country code")
    country_name: str = Field(description="Country name")
    total_cost: float = Field(description="Total landed cost")
    duty_rate: float = Field(description="Total duty rate (%)")
    trade_preferences: List[str] = Field(description="Applicable trade preferences")
    risk_level: str = Field(description="Risk level (low/medium/high)")
    rank: int = Field(description="Ranking (1 = best)")
    savings_vs_best: float = Field(description="Additional cost vs best option")
    savings_percentage: float = Field(description="Additional cost percentage vs best option")
    details: Dict[str, Any] = Field(description="Full calculation details")


class SourcingComparisonResponse(BaseResponse):
    """Sourcing comparison response schema."""
    
    data: Dict[str, Any] = Field(description="Comparison results")
    
    class ComparisonData(BaseModel):
        """Nested comparison data structure."""
        
        hts_code: str = Field(description="HTS code analyzed")
        comparison_results: List[SourcingOption] = Field(description="Sourcing options ranked by cost")
        best_option: Optional[SourcingOption] = Field(None, description="Best sourcing option")
        total_countries_compared: int = Field(description="Number of countries successfully compared")


class HTSSearchRequest(BaseModel):
    """HTS code search request schema."""
    
    query: str = Field(description="Search query (code or description)", min_length=1, max_length=200)
    chapter: Optional[str] = Field(None, description="Filter by chapter (2 digits)", min_length=2, max_length=2)
    limit: int = Field(default=20, description="Maximum results to return", ge=1, le=100)
    
    @validator('chapter')
    def validate_chapter(cls, v):
        if v is not None:
            if not v.isdigit():
                raise ValueError('Chapter must be numeric')
            return v.zfill(2)
        return v


class HTSSearchResponse(BaseResponse):
    """HTS code search response schema."""
    
    data: List[HTSCodeResponse] = Field(description="List of matching HTS codes")
    total_results: int = Field(description="Total number of results found")
    search_query: str = Field(description="Original search query")
    search_time_ms: int = Field(description="Search execution time in milliseconds")


class ChapterSummary(BaseModel):
    """HTS chapter summary."""
    
    chapter: str = Field(description="2-digit chapter code")
    description: str = Field(description="Chapter description")
    code_count: int = Field(description="Number of HTS codes in chapter")


class ChapterSummaryResponse(BaseResponse):
    """HTS chapters summary response."""
    
    data: List[ChapterSummary] = Field(description="List of HTS chapters with counts") 