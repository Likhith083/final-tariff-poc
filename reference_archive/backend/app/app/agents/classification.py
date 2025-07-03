"""
Classification Agent for TariffAI
Handles product classification and HTS code identification.
"""

import logging
from typing import Dict, Any, Optional
import re

from app.services.search_service import search_service
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class ClassificationAgent:
    """Agent for product classification and HTS code identification."""
    
    def __init__(self):
        self.name = "ClassificationAgent"
    
    async def classify_product(self, description: str, session_id: str = None) -> Dict[str, Any]:
        """
        Classify a product and find relevant HTS codes.
        
        Args:
            description: Product description
            session_id: Session ID for context
            
        Returns:
            Dict containing classification results
        """
        try:
            logger.info(f"🔍 Classifying product: {description}")
            
            # Search for similar products in the database
            search_results = await search_service.search_tariffs(description, limit=5)
            
            # Use AI to enhance classification
            ai_analysis = await ai_service.analyze_material(description)
            
            # Extract potential HTS codes from search results
            hts_codes = []
            for result in search_results:
                if "hs_code" in result.get("metadata", {}):
                    hts_codes.append({
                        "code": result["metadata"]["hs_code"],
                        "description": result["metadata"].get("description", ""),
                        "confidence": 1.0 - result.get("distance", 0.0)
                    })
            
            # If no HTS codes found, create a generic response
            if not hts_codes:
                hts_codes = [{
                    "code": "Unknown",
                    "description": "Product classification not found",
                    "confidence": 0.0
                }]
            
            return {
                "success": True,
                "product_description": description,
                "hts_codes": hts_codes,
                "ai_analysis": ai_analysis,
                "search_results": search_results,
                "confidence": max([code["confidence"] for code in hts_codes], default=0.0)
            }
            
        except Exception as e:
            logger.error(f"❌ Classification error: {e}")
            return {
                "success": False,
                "error": str(e),
                "product_description": description,
                "hts_codes": []
            }
    
    def extract_hts_code(self, text: str) -> Optional[str]:
        """
        Extract HTS code from text using regex patterns.
        
        Args:
            text: Text containing potential HTS code
            
        Returns:
            Extracted HTS code or None
        """
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