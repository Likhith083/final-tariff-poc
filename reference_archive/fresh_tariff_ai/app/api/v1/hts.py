"""
HTS Lookup API endpoints for TariffAI
Provides direct Excel-based HTS code search functionality.
"""

import logging
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.database import get_tariff_data
from app.core.responses import create_success_response, create_error_response

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class HTSearchRequest(BaseModel):
    """HTS search request model."""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    category: Optional[str] = Field(None, description="Category filter")
    rate_filter: Optional[str] = Field(None, description="Rate filter")


class HTSResult(BaseModel):
    """HTS search result model."""
    hts_code: str = Field(..., description="HTS code")
    description: str = Field(..., description="Product description")
    tariff_rate: float = Field(..., description="Tariff rate percentage")
    confidence: float = Field(..., description="Search confidence score (0-1)")
    specific_rate: float = Field(0.0, description="Specific rate if applicable")
    other_rate: float = Field(0.0, description="Other rate if applicable")


@router.post("/search", response_model=dict)
async def search_hts(request: HTSearchRequest):
    """
    Search for HTS codes using direct Excel database lookup.
    
    This endpoint performs fast, direct search through the tariff database
    without relying on LLM, providing instant results like Ctrl+F functionality.
    """
    try:
        logger.info(f"🔍 HTS search request: {request.query}")
        
        # Get tariff data from database
        tariff_data = get_tariff_data()
        if tariff_data is None:
            raise HTTPException(
                status_code=500,
                detail="Tariff database not available"
            )
        
        # Perform direct search
        results = await perform_hts_search(
            query=request.query,
            tariff_data=tariff_data,
            category=request.category,
            rate_filter=request.rate_filter
        )
        
        return create_success_response(
            data={
                "results": results,
                "total_results": len(results),
                "query": request.query
            },
            message=f"Found {len(results)} HTS codes"
        )
        
    except Exception as e:
        logger.error(f"❌ HTS search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


async def perform_hts_search(
    query: str, 
    tariff_data, 
    category: Optional[str] = None,
    rate_filter: Optional[str] = None
) -> List[dict]:
    """
    Perform simple keyword search through Excel data (like Ctrl+F).
    
    Args:
        query: Search query
        tariff_data: Pandas DataFrame with tariff data
        category: Optional category filter
        rate_filter: Optional rate filter
        
    Returns:
        List of matching HTS results
    """
    try:
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower().strip()
        
        if not query_lower:
            return []
        
        # Simple keyword search in description column
        # This is like doing Ctrl+F in Excel
        matches = tariff_data[
            tariff_data['brief_description'].str.lower().str.contains(query_lower, na=False)
        ]
        
        # Also search in HTS code if query looks like a code
        if query.replace('.', '').replace('-', '').isdigit():
            hts_matches = tariff_data[
                tariff_data['hts8'].astype(str).str.contains(query, na=False)
            ]
            # Combine results
            matches = pd.concat([matches, hts_matches]).drop_duplicates()
        
        # Apply rate filter if specified
        if rate_filter:
            matches = apply_rate_filter(matches, rate_filter)
        
        # Convert to result format with all details
        results = []
        for _, row in matches.head(20).iterrows():  # Show up to 20 results
            # Get all available rate information
            general_rate = row.get('mfn_ad_val_rate this is the general tariff rate', 0)
            specific_rate = row.get('mfn_specific_rate', 0)
            other_rate = row.get('mfn_other_rate', 0)
            
            # Format HTS code properly (add dots)
            hts_code = str(row['hts8'])
            if len(hts_code) >= 8:
                formatted_hts = f"{hts_code[:4]}.{hts_code[4:6]}.{hts_code[6:8]}"
                if len(hts_code) > 8:
                    formatted_hts += f".{hts_code[8:10]}"
            else:
                formatted_hts = hts_code
            
            result = {
                "hts_code": formatted_hts,
                "raw_hts_code": hts_code,
                "description": str(row['brief_description']),
                "general_rate": float(general_rate) if pd.notna(general_rate) else 0.0,
                "specific_rate": float(specific_rate) if pd.notna(specific_rate) else 0.0,
                "other_rate": float(other_rate) if pd.notna(other_rate) else 0.0,
                "rate_type": "Ad Valorem" if general_rate > 0 else "Specific" if specific_rate > 0 else "Other" if other_rate > 0 else "Free",
                "rate_display": f"{general_rate:.1f}%" if general_rate > 0 else f"${specific_rate:.2f}" if specific_rate > 0 else f"${other_rate:.2f}" if other_rate > 0 else "Free",
                "confidence": 1.0  # Simple search always has high confidence
            }
            results.append(result)
        
        logger.info(f"✅ Found {len(results)} HTS matches for query: '{query}'")
        return results
        
    except Exception as e:
        logger.error(f"❌ Error in HTS search: {e}")
        return []


def apply_rate_filter(data, rate_filter: str):
    """Apply rate filter to the data."""
    try:
        if rate_filter == "0":
            return data[data['mfn_ad_val_rate this is the general tariff rate'] == 0]
        elif rate_filter == "low":
            return data[
                (data['mfn_ad_val_rate this is the general tariff rate'] > 0) &
                (data['mfn_ad_val_rate this is the general tariff rate'] <= 0.05)
            ]
        elif rate_filter == "medium":
            return data[
                (data['mfn_ad_val_rate this is the general tariff rate'] > 0.05) &
                (data['mfn_ad_val_rate this is the general tariff rate'] <= 0.15)
            ]
        elif rate_filter == "high":
            return data[data['mfn_ad_val_rate this is the general tariff rate'] > 0.15]
        else:
            return data
    except:
        return data


def calculate_confidence(query: str, description: str) -> float:
    """
    Calculate confidence score based on query match quality.
    
    Args:
        query: Search query
        description: Product description
        
    Returns:
        Confidence score between 0 and 1
    """
    try:
        desc_lower = description.lower()
        
        # Exact phrase match
        if query in desc_lower:
            return 1.0
        
        # Word matches
        query_words = query.split()
        desc_words = desc_lower.split()
        
        matches = sum(1 for word in query_words if word in desc_words)
        if matches == 0:
            return 0.0
        
        # Calculate confidence based on word match ratio
        confidence = matches / len(query_words)
        
        # Boost confidence for longer descriptions (more context)
        if len(desc_words) > 10:
            confidence *= 1.1
        
        return min(confidence, 1.0)
        
    except:
        return 0.5


@router.get("/categories")
async def get_categories():
    """Get available HTS categories."""
    try:
        # This would return categories from your database
        # For now, return sample categories
        categories = [
            "Textiles",
            "Electronics", 
            "Machinery",
            "Chemicals",
            "Metals",
            "Food & Agriculture",
            "Vehicles",
            "Pharmaceuticals"
        ]
        
        return create_success_response(
            data=categories,
            message="Categories retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting categories: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve categories"
        ) 