"""
Risk Assessment API endpoints for TariffAI
Provides compliance and risk assessment functionality.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.responses import create_success_response, create_error_response

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


class RiskAssessmentRequest(BaseModel):
    """Risk assessment request model."""
    input: str = Field(..., description="HTS code or product description")


@router.post("/assess", response_model=dict)
async def assess_risk(request: RiskAssessmentRequest):
    """
    Assess compliance risk for a given HTS code or product.
    """
    try:
        logger.info(f"⚠️ Risk assessment request: {request.input}")
        
        # Extract HTS code if present
        hts_code = extract_hts_code(request.input)
        
        # Perform risk assessment
        risk_assessment = perform_risk_assessment(hts_code or request.input)
        
        return create_success_response(
            data={"risk_assessment": risk_assessment},
            message="Risk assessment completed successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Risk assessment error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Risk assessment failed: {str(e)}"
        )


def extract_hts_code(text: str) -> str:
    """Extract HTS code from text using regex patterns."""
    import re
    
    # Common HTS code patterns
    patterns = [
        r'\b\d{4}\.\d{2}\.\d{2}\b',  # 4.2.2 format
        r'\b\d{6}\.\d{2}\b',         # 6.2 format
        r'\b\d{8}\b',                # 8 digits
        r'\b\d{10}\b'                # 10 digits
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None


def perform_risk_assessment(identifier: str) -> dict:
    """
    Perform risk assessment for a given identifier.
    
    Args:
        identifier: HTS code or product description
        
    Returns:
        Risk assessment results
    """
    # Determine risk level
    risk_level = determine_risk_level(identifier)
    
    # Check restrictions
    restrictions = check_restrictions(identifier)
    
    # Get requirements
    requirements = get_requirements(identifier)
    
    # Generate recommendations
    recommendations = get_recommendations(risk_level, restrictions)
    
    return {
        "risk_level": risk_level,
        "restrictions": restrictions,
        "requirements": requirements,
        "recommendations": recommendations
    }


def determine_risk_level(identifier: str) -> str:
    """Determine risk level based on identifier."""
    # Simplified risk assessment
    if identifier.startswith("93"):  # Arms and ammunition
        return "HIGH"
    elif identifier.startswith("29"):  # Organic chemicals
        return "MEDIUM"
    elif identifier.startswith("30"):  # Pharmaceutical products
        return "MEDIUM"
    elif identifier.startswith("97"):  # Works of art
        return "LOW"
    else:
        return "LOW"


def check_restrictions(identifier: str) -> dict:
    """Check for any restrictions on the identifier."""
    restrictions = {
        "is_restricted": False,
        "restriction_type": None,
        "description": "No restrictions found"
    }
    
    # Simplified restriction check
    if identifier.startswith("93"):
        restrictions.update({
            "is_restricted": True,
            "restriction_type": "weapons",
            "description": "Firearms and ammunition require special permits"
        })
    elif identifier.startswith("29"):
        restrictions.update({
            "is_restricted": True,
            "restriction_type": "chemicals",
            "description": "Chemical products may require safety data sheets"
        })
    
    return restrictions


def get_requirements(identifier: str) -> dict:
    """Get import requirements for the identifier."""
    requirements = {
        "licenses_required": False,
        "certificates_required": False,
        "inspections_required": False,
        "documentation": []
    }
    
    # Simplified requirements check
    if identifier.startswith("93"):
        requirements.update({
            "licenses_required": True,
            "certificates_required": True,
            "inspections_required": True,
            "documentation": ["Import license", "End-user certificate", "Safety inspection"]
        })
    elif identifier.startswith("29"):
        requirements.update({
            "certificates_required": True,
            "documentation": ["Safety data sheet", "Chemical composition certificate"]
        })
    
    return requirements


def get_recommendations(risk_level: str, restrictions: dict) -> List[str]:
    """Get recommendations based on risk level and restrictions."""
    recommendations = []
    
    if risk_level == "HIGH":
        recommendations.append("Consult with customs broker before import")
        recommendations.append("Ensure all required permits are obtained")
        recommendations.append("Consider alternative sourcing options")
    
    if restrictions["is_restricted"]:
        recommendations.append(f"Special handling required for {restrictions['restriction_type']} items")
        recommendations.append("Verify compliance with all regulations")
    
    if not recommendations:
        recommendations.append("Standard import procedures apply")
    
    return recommendations 