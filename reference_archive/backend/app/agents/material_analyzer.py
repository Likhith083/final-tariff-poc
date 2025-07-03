"""
Material Analyzer Agent - Material composition and optimization specialist
"""
import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any
import requests

from ..core.config import settings
from ..core.responses import MaterialCompositionResponse, MaterialSuggestionResponse

logger = logging.getLogger(__name__)


class MaterialAnalyzerAgent:
    """
    Material Analysis Specialist Agent
    """
    
    def __init__(self):
        self.material_database = self._load_material_database()
        self._initialized = False
    
    async def initialize(self):
        """Initialize the material analyzer agent"""
        if self._initialized:
            return
        
        try:
            # Initialize any required services
            self._initialized = True
            logger.info("✅ Material analyzer agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing material analyzer: {e}")
    
    def _load_material_database(self) -> Dict[str, Any]:
        """Load material properties database"""
        return {
            "nitrile": {
                "properties": {"strength": 0.9, "durability": 0.8, "flexibility": 0.7},
                "tariff_rate": 3.0,
                "alternatives": ["latex", "vinyl", "polyethylene"],
                "quality_impact": "High strength and chemical resistance"
            },
            "latex": {
                "properties": {"strength": 0.8, "durability": 0.7, "flexibility": 0.9},
                "tariff_rate": 2.5,
                "alternatives": ["nitrile", "vinyl", "polyethylene"],
                "quality_impact": "Excellent flexibility and comfort"
            },
            "steel": {
                "properties": {"strength": 1.0, "durability": 0.9, "flexibility": 0.3},
                "tariff_rate": 2.9,
                "alternatives": ["aluminum", "titanium", "carbon_fiber"],
                "quality_impact": "Maximum strength and durability"
            },
            "aluminum": {
                "properties": {"strength": 0.7, "durability": 0.8, "flexibility": 0.6},
                "tariff_rate": 2.1,
                "alternatives": ["steel", "titanium", "magnesium"],
                "quality_impact": "Good strength-to-weight ratio"
            },
            "cotton": {
                "properties": {"strength": 0.6, "durability": 0.5, "flexibility": 0.8},
                "tariff_rate": 8.5,
                "alternatives": ["polyester", "bamboo", "hemp"],
                "quality_impact": "Natural and breathable"
            },
            "polyester": {
                "properties": {"strength": 0.8, "durability": 0.9, "flexibility": 0.7},
                "tariff_rate": 5.3,
                "alternatives": ["cotton", "nylon", "acrylic"],
                "quality_impact": "Durable and wrinkle-resistant"
            },
            "plastic": {
                "properties": {"strength": 0.5, "durability": 0.7, "flexibility": 0.6},
                "tariff_rate": 5.3,
                "alternatives": ["bioplastic", "recycled_plastic", "composite"],
                "quality_impact": "Versatile and cost-effective"
            },
            "electronics": {
                "properties": {"strength": 0.3, "durability": 0.6, "flexibility": 0.4},
                "tariff_rate": 2.6,
                "alternatives": ["modular_electronics", "integrated_circuits"],
                "quality_impact": "Essential for functionality"
            }
        }
    
    async def analyze_materials(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze material composition from product description
        """
        await self.initialize()
        
        try:
            # Extract product information
            product_info = self._extract_product_info(message, entities)
            
            if not product_info.get("product_name"):
                return {
                    "message": "I need a product description to analyze materials. Please provide more details.",
                    "data": None
                }
            
            # Infer material composition
            composition = await self._infer_material_composition(product_info)
            
            if not composition:
                return {
                    "message": f"I couldn't determine the material composition for '{product_info['product_name']}'. Please provide more specific details.",
                    "data": None
                }
            
            # Get HTS code suggestion
            hts_suggestion = await self._suggest_hts_code(composition, product_info)
            
            # Create response message
            message = f"Material analysis for {product_info['product_name']}:\n\n"
            for material, percentage in composition.items():
                material_info = self.material_database.get(material, {})
                tariff_rate = material_info.get("tariff_rate", 5.0)
                message += f"• {material.title()}: {percentage}% (tariff: {tariff_rate}%)\n"
            
            if hts_suggestion:
                message += f"\nSuggested HTS Code: {hts_suggestion}"
            
            return {
                "message": message,
                "data": {
                    "product_name": product_info["product_name"],
                    "company_name": product_info.get("company_name"),
                    "material_composition": composition,
                    "inferred_hts_code": hts_suggestion,
                    "confidence_score": 0.8,
                    "source_url": None
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in material analysis: {e}")
            return {
                "message": "I encountered an error while analyzing materials. Please try again.",
                "data": None
            }
    
    def _extract_product_info(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product information from message and entities"""
        info = {}
        
        # Extract product name
        if entities.get("products"):
            info["product_name"] = entities["products"][0]
        else:
            # Try to extract from message
            product_keywords = ["gloves", "shirt", "phone", "computer", "toy", "drill", "furniture"]
            for keyword in product_keywords:
                if keyword in message.lower():
                    info["product_name"] = keyword
                    break
        
        # Extract company name
        company_pattern = r'(?:from|by|manufactured by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        company_match = re.search(company_pattern, message, re.IGNORECASE)
        if company_match:
            info["company_name"] = company_match.group(1)
        
        return info
    
    async def _infer_material_composition(self, product_info: Dict[str, Any]) -> Dict[str, float]:
        """Infer material composition based on product type"""
        product_name = product_info["product_name"].lower()
        
        # Define material compositions for different product types
        compositions = {
            "gloves": {
                "nitrile": 100.0
            },
            "shirt": {
                "cotton": 80.0,
                "polyester": 20.0
            },
            "phone": {
                "plastic": 60.0,
                "electronics": 30.0,
                "aluminum": 10.0
            },
            "computer": {
                "plastic": 50.0,
                "electronics": 40.0,
                "aluminum": 10.0
            },
            "toy": {
                "plastic": 90.0,
                "electronics": 10.0
            },
            "drill": {
                "steel": 60.0,
                "plastic": 30.0,
                "electronics": 10.0
            },
            "furniture": {
                "wood": 80.0,
                "metal": 15.0,
                "fabric": 5.0
            }
        }
        
        return compositions.get(product_name, {"plastic": 100.0})
    
    async def _suggest_hts_code(self, composition: Dict[str, float], product_info: Dict[str, Any]) -> Optional[str]:
        """Suggest HTS code based on material composition"""
        product_name = product_info["product_name"].lower()
        
        # Simplified HTS code mapping
        hts_mapping = {
            "gloves": "4015.19.05",
            "shirt": "6104.43.20",
            "phone": "8517.13.00",
            "computer": "8471.30.01",
            "toy": "9503.00.00",
            "drill": "8467.21.00",
            "furniture": "9401.61.00"
        }
        
        return hts_mapping.get(product_name)
    
    async def suggest_material_alternatives(self, current_materials: Dict[str, float], quality_priority: str = "balanced") -> Dict[str, Any]:
        """
        Suggest alternative material compositions
        """
        await self.initialize()
        
        try:
            if not current_materials:
                return {
                    "message": "I need current material composition to suggest alternatives.",
                    "data": None
                }
            
            # Calculate current tariff cost
            current_tariff_cost = self._calculate_tariff_cost(current_materials)
            
            # Generate alternative compositions
            alternatives = await self._generate_alternatives(current_materials, quality_priority)
            
            if not alternatives:
                return {
                    "message": "I couldn't find suitable alternative materials for your current composition.",
                    "data": None
                }
            
            # Select best alternative
            best_alternative = alternatives[0]
            new_tariff_cost = self._calculate_tariff_cost(best_alternative["composition"])
            tariff_savings = current_tariff_cost - new_tariff_cost
            
            # Create response message
            message = f"Material alternative suggestions:\n\n"
            message += f"Current composition:\n"
            for material, percentage in current_materials.items():
                message += f"• {material.title()}: {percentage}%\n"
            
            message += f"\nSuggested alternative:\n"
            for material, percentage in best_alternative["composition"].items():
                message += f"• {material.title()}: {percentage}%\n"
            
            message += f"\nTariff savings: ${tariff_savings:.2f}"
            message += f"\nQuality impact: {best_alternative['quality_impact']}"
            
            return {
                "message": message,
                "data": {
                    "current_materials": current_materials,
                    "suggested_materials": best_alternative["composition"],
                    "tariff_savings": tariff_savings,
                    "quality_impact": best_alternative["quality_impact"],
                    "reasoning": best_alternative["reasoning"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in material alternatives: {e}")
            return {
                "message": "I encountered an error while suggesting alternatives. Please try again.",
                "data": None
            }
    
    def _calculate_tariff_cost(self, composition: Dict[str, float], base_cost: float = 100.0) -> float:
        """Calculate total tariff cost for material composition"""
        total_cost = 0.0
        
        for material, percentage in composition.items():
            material_info = self.material_database.get(material, {})
            tariff_rate = material_info.get("tariff_rate", 5.0)
            material_cost = base_cost * (percentage / 100.0)
            tariff_cost = material_cost * (tariff_rate / 100.0)
            total_cost += tariff_cost
        
        return total_cost
    
    async def _generate_alternatives(self, current_materials: Dict[str, float], quality_priority: str) -> List[Dict[str, Any]]:
        """Generate alternative material compositions"""
        alternatives = []
        
        for material, percentage in current_materials.items():
            material_info = self.material_database.get(material, {})
            alternative_materials = material_info.get("alternatives", [])
            
            for alt_material in alternative_materials:
                if alt_material in self.material_database:
                    # Create alternative composition
                    alt_composition = current_materials.copy()
                    alt_composition[alt_material] = percentage
                    del alt_composition[material]
                    
                    # Calculate quality impact
                    quality_impact = self._assess_quality_impact(material, alt_material, quality_priority)
                    
                    alternatives.append({
                        "composition": alt_composition,
                        "quality_impact": quality_impact,
                        "reasoning": f"Replaced {material} with {alt_material} for potential cost savings"
                    })
        
        # Sort by tariff savings (descending)
        alternatives.sort(key=lambda x: self._calculate_tariff_cost(x["composition"]), reverse=False)
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def _assess_quality_impact(self, original_material: str, new_material: str, priority: str) -> str:
        """Assess the quality impact of material substitution"""
        original_info = self.material_database.get(original_material, {})
        new_info = self.material_database.get(new_material, {})
        
        original_props = original_info.get("properties", {})
        new_props = new_info.get("properties", {})
        
        # Calculate overall quality score
        original_score = sum(original_props.values()) / len(original_props) if original_props else 0.5
        new_score = sum(new_props.values()) / len(new_props) if new_props else 0.5
        
        quality_change = ((new_score - original_score) / original_score) * 100
        
        if quality_change > 10:
            return "Quality improvement expected"
        elif quality_change > -5:
            return "Minimal quality impact"
        elif quality_change > -15:
            return "Moderate quality reduction"
        else:
            return "Significant quality reduction"
    
    async def search_product_details(self, product_description: str, company_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for product details using external APIs (simplified)
        """
        await self.initialize()
        
        try:
            # This would integrate with SERP APIs in a real implementation
            # For now, return simulated data
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # Extract basic information
            product_name = product_description.split()[0] if product_description else "product"
            
            # Simulate product details
            details = {
                "product_name": f"{company_name} {product_name}" if company_name else product_name,
                "material_composition": await self._infer_material_composition({"product_name": product_name}),
                "suggested_hts_code": await self._suggest_hts_code(
                    await self._infer_material_composition({"product_name": product_name}),
                    {"product_name": product_name}
                ),
                "source_url": f"https://example.com/products/{product_name.lower()}",
                "confidence_score": 0.75
            }
            
            return {
                "message": f"Found product details for {details['product_name']}",
                "data": details
            }
            
        except Exception as e:
            logger.error(f"❌ Error in product search: {e}")
            return {
                "message": "I couldn't find product details. Please try a different search.",
                "data": None
            } 