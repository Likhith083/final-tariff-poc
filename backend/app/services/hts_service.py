import pandas as pd
import os
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.hts import HTSRecord
from app.core.config import settings
from app.services.ai_service import AIService

class HTSService:
    def __init__(self):
        self.ai_service = AIService()
        self.excel_file_path = "./data/tariff_database_2025.xlsx"
        self.knowledge_base_path = "./data/adcvd_faq.json"
        
    async def import_from_excel(self, db: Session) -> int:
        """Import HTS data from Excel file"""
        
        if not os.path.exists(self.excel_file_path):
            raise FileNotFoundError(f"Excel file not found: {self.excel_file_path}")
        
        try:
            # Read Excel file
            df = pd.read_excel(self.excel_file_path)
            
            imported_count = 0
            
            for _, row in df.iterrows():
                # Check if record already exists
                existing = db.query(HTSRecord).filter(
                    HTSRecord.hts_code == str(row.get('HTS_Code', ''))
                ).first()
                
                if not existing:
                    # Create new record
                    record = HTSRecord(
                        hts_code=str(row.get('HTS_Code', '')),
                        description=str(row.get('Description', '')),
                        duty_rate=float(row.get('Duty_Rate', 0)) if pd.notna(row.get('Duty_Rate')) else None,
                        category=str(row.get('Category', '')) if pd.notna(row.get('Category')) else None,
                        subcategory=str(row.get('Subcategory', '')) if pd.notna(row.get('Subcategory')) else None,
                        notes=str(row.get('Notes', '')) if pd.notna(row.get('Notes')) else None
                    )
                    db.add(record)
                    imported_count += 1
            
            db.commit()
            return imported_count
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Import failed: {str(e)}")
    
    async def ai_search(self, query: str, limit: int = 10) -> List[HTSRecord]:
        """Use AI to search for HTS codes when database search fails"""
        
        try:
            # Use AI to classify the product
            classification = await self.ai_service.classify_product(query)
            
            # Create a mock HTS record from AI classification
            if classification.get("hts_code") and classification.get("hts_code") != "Unknown":
                record = HTSRecord(
                    hts_code=classification["hts_code"],
                    description=classification.get("explanation", query),
                    duty_rate=None,  # AI doesn't provide exact rates
                    category="AI Suggested",
                    subcategory=None,
                    notes=f"AI classification based on: {query}. {classification.get('considerations', '')}"
                )
                return [record]
            
            return []
            
        except Exception as e:
            print(f"AI Search Error: {str(e)}")
            return []
    
    async def get_hts_details(self, hts_code: str) -> Optional[HTSRecord]:
        """Get detailed information about an HTS code using AI if not in database"""
        
        try:
            # Try AI classification for the HTS code
            classification = await self.ai_service.classify_product(f"HTS Code: {hts_code}")
            
            if classification.get("hts_code") and classification.get("hts_code") != "Unknown":
                record = HTSRecord(
                    hts_code=hts_code,
                    description=classification.get("explanation", f"Details for HTS code {hts_code}"),
                    duty_rate=None,
                    category="AI Generated",
                    subcategory=None,
                    notes=f"AI-generated information. {classification.get('considerations', '')}"
                )
                return record
            
            return None
            
        except Exception as e:
            print(f"Get HTS Details Error: {str(e)}")
            return None
    
    def search_by_code(self, db: Session, code: str, limit: int = 10) -> List[HTSRecord]:
        """Search HTS codes by exact or partial code match"""
        
        return db.query(HTSRecord).filter(
            HTSRecord.hts_code.contains(code)
        ).limit(limit).all()
    
    def search_by_description(self, db: Session, description: str, limit: int = 10) -> List[HTSRecord]:
        """Search HTS codes by description keywords"""
        
        return db.query(HTSRecord).filter(
            HTSRecord.description.contains(description)
        ).limit(limit).all()
    
    def get_categories(self, db: Session) -> List[str]:
        """Get all available HTS categories"""
        
        categories = db.query(HTSRecord.category).distinct().filter(
            HTSRecord.category.isnot(None)
        ).all()
        
        return [cat[0] for cat in categories if cat[0]]
    
    def get_by_category(self, db: Session, category: str, limit: int = 50) -> List[HTSRecord]:
        """Get HTS codes by category"""
        
        return db.query(HTSRecord).filter(
            HTSRecord.category == category
        ).limit(limit).all()
    
    def get_suggestions(self, db: Session, query: str, limit: int = 5) -> List[str]:
        """Get HTS code suggestions for autocomplete"""
        
        if len(query.strip()) < 2:
            return []
        
        # Get code-based suggestions
        code_suggestions = db.query(HTSRecord.hts_code).filter(
            HTSRecord.hts_code.startswith(query)
        ).limit(limit).all()
        
        suggestions = [s[0] for s in code_suggestions]
        
        # If not enough suggestions, add description-based ones
        if len(suggestions) < limit:
            desc_suggestions = db.query(HTSRecord.hts_code).filter(
                HTSRecord.description.contains(query)
            ).limit(limit - len(suggestions)).all()
            suggestions.extend([s[0] for s in desc_suggestions])
        
        return suggestions
    
    def validate_hts_code(self, hts_code: str) -> bool:
        """Validate HTS code format"""
        
        # Basic validation: should be 6-10 digits
        if not hts_code or not hts_code.replace('.', '').isdigit():
            return False
        
        # Check length (6-10 digits)
        digits_only = hts_code.replace('.', '')
        if len(digits_only) < 6 or len(digits_only) > 10:
            return False
        
        return True
    
    def format_hts_code(self, hts_code: str) -> str:
        """Format HTS code with proper separators"""
        
        # Remove any existing separators
        digits_only = hts_code.replace('.', '').replace('-', '').replace(' ', '')
        
        if len(digits_only) >= 6:
            # Format as XX.XX.XX or XX.XX.XX.XX
            if len(digits_only) <= 8:
                return f"{digits_only[:2]}.{digits_only[2:4]}.{digits_only[4:]}"
            else:
                return f"{digits_only[:2]}.{digits_only[2:4]}.{digits_only[4:6]}.{digits_only[6:]}"
        
        return hts_code 