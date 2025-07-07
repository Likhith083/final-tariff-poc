"""
TariffDatabaseService for ATLAS Enterprise
HTS code lookup, duty rates, and tariff data management.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from models.tariff import HTSCode, TariffRate
from models.country import Country
from core.logging import get_logger

logger = get_logger(__name__)


class TariffDatabaseService:
    """Service for tariff database operations and HTS code management."""
    
    @staticmethod
    async def search_hts_codes(
        db: AsyncSession,
        query: str,
        limit: int = 20,
        chapter: Optional[str] = None
    ) -> List[HTSCode]:
        """
        Search HTS codes by description or code.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum results to return
            chapter: Optional chapter filter
            
        Returns:
            List of matching HTS codes
        """
        try:
            # Build the query
            stmt = select(HTSCode).where(HTSCode.is_active == True)
            
            # Add search conditions
            if query:
                search_conditions = or_(
                    HTSCode.hts_code.ilike(f"%{query}%"),
                    HTSCode.description.ilike(f"%{query}%"),
                    HTSCode.brief_description.ilike(f"%{query}%")
                )
                stmt = stmt.where(search_conditions)
            
            # Add chapter filter
            if chapter:
                stmt = stmt.where(HTSCode.hts_2 == chapter.zfill(2))
            
            # Order by relevance and limit
            stmt = stmt.order_by(
                # Exact code matches first
                func.case(
                    (HTSCode.hts_code == query, 1),
                    else_=2
                ),
                # Then by code length (more specific first)
                func.length(HTSCode.hts_code),
                HTSCode.hts_code
            ).limit(limit)
            
            result = await db.execute(stmt)
            hts_codes = result.scalars().all()
            
            logger.info(f"Found {len(hts_codes)} HTS codes for query: {query}")
            return list(hts_codes)
            
        except Exception as e:
            logger.error(f"Error searching HTS codes: {e}")
            raise
    
    @staticmethod
    async def get_hts_code_by_code(
        db: AsyncSession,
        hts_code: str
    ) -> Optional[HTSCode]:
        """
        Get HTS code by exact code match.
        
        Args:
            db: Database session
            hts_code: HTS code to find
            
        Returns:
            HTS code if found
        """
        try:
            # Clean the code (remove dots, ensure 10 digits)
            clean_code = hts_code.replace(".", "").zfill(10)
            
            stmt = select(HTSCode).where(
                and_(
                    HTSCode.hts_code == clean_code,
                    HTSCode.is_active == True
                )
            ).options(selectinload(HTSCode.tariff_rates))
            
            result = await db.execute(stmt)
            hts_code_obj = result.scalar_one_or_none()
            
            if hts_code_obj:
                logger.info(f"Found HTS code: {hts_code_obj.hts_code}")
            else:
                logger.warning(f"HTS code not found: {clean_code}")
                
            return hts_code_obj
            
        except Exception as e:
            logger.error(f"Error getting HTS code {hts_code}: {e}")
            raise
    
    @staticmethod
    async def get_tariff_rates(
        db: AsyncSession,
        hts_code_id: int,
        country_code: Optional[str] = None
    ) -> List[TariffRate]:
        """
        Get tariff rates for an HTS code.
        
        Args:
            db: Database session
            hts_code_id: HTS code ID
            country_code: Optional country filter
            
        Returns:
            List of tariff rates
        """
        try:
            stmt = select(TariffRate).where(
                and_(
                    TariffRate.hts_code_id == hts_code_id,
                    TariffRate.is_active == True
                )
            ).options(
                selectinload(TariffRate.country),
                selectinload(TariffRate.hts_code)
            )
            
            # Add country filter if specified
            if country_code:
                stmt = stmt.join(Country).where(Country.code == country_code.upper())
            
            # Order by effective rate (lowest first)
            stmt = stmt.order_by(TariffRate.mfn_rate)
            
            result = await db.execute(stmt)
            rates = result.scalars().all()
            
            logger.info(f"Found {len(rates)} tariff rates for HTS code ID: {hts_code_id}")
            return list(rates)
            
        except Exception as e:
            logger.error(f"Error getting tariff rates: {e}")
            raise
    
    @staticmethod
    async def get_chapters_summary(db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get summary of HTS chapters with counts.
        
        Args:
            db: Database session
            
        Returns:
            List of chapter summaries
        """
        try:
            stmt = select(
                HTSCode.hts_2,
                HTSCode.chapter_description,
                func.count(HTSCode.id).label('code_count')
            ).where(
                HTSCode.is_active == True
            ).group_by(
                HTSCode.hts_2,
                HTSCode.chapter_description
            ).order_by(HTSCode.hts_2)
            
            result = await db.execute(stmt)
            chapters = []
            
            for row in result:
                chapters.append({
                    "chapter": row.hts_2,
                    "description": row.chapter_description,
                    "code_count": row.code_count
                })
            
            logger.info(f"Retrieved {len(chapters)} HTS chapters")
            return chapters
            
        except Exception as e:
            logger.error(f"Error getting chapters summary: {e}")
            raise
    
    @staticmethod
    async def get_popular_hts_codes(
        db: AsyncSession,
        limit: int = 10
    ) -> List[HTSCode]:
        """
        Get most frequently used HTS codes based on calculation history.
        
        Args:
            db: Database session
            limit: Number of codes to return
            
        Returns:
            List of popular HTS codes
        """
        try:
            # This would join with calculation history to find most used codes
            # For now, return codes with lowest rates (most trade-friendly)
            stmt = select(HTSCode).join(TariffRate).where(
                and_(
                    HTSCode.is_active == True,
                    TariffRate.is_active == True
                )
            ).group_by(HTSCode.id).order_by(
                func.avg(TariffRate.mfn_rate)
            ).limit(limit)
            
            result = await db.execute(stmt)
            codes = result.scalars().all()
            
            logger.info(f"Retrieved {len(codes)} popular HTS codes")
            return list(codes)
            
        except Exception as e:
            logger.error(f"Error getting popular HTS codes: {e}")
            raise
    
    @staticmethod
    async def validate_hts_code(hts_code: str) -> Dict[str, Any]:
        """
        Validate HTS code format and structure.
        
        Args:
            hts_code: HTS code to validate
            
        Returns:
            Validation result with details
        """
        try:
            # Clean the code
            clean_code = hts_code.replace(".", "").replace(" ", "")
            
            validation = {
                "is_valid": False,
                "formatted_code": None,
                "errors": [],
                "warnings": []
            }
            
            # Check length
            if len(clean_code) < 4:
                validation["errors"].append("HTS code must be at least 4 digits")
            elif len(clean_code) > 10:
                validation["errors"].append("HTS code cannot exceed 10 digits")
            
            # Check if numeric
            if not clean_code.isdigit():
                validation["errors"].append("HTS code must contain only digits")
            
            # If no errors, format the code
            if not validation["errors"]:
                # Pad to 10 digits
                formatted = clean_code.zfill(10)
                validation["formatted_code"] = f"{formatted[:4]}.{formatted[4:6]}.{formatted[6:8]}.{formatted[8:]}"
                validation["is_valid"] = True
                
                # Add warnings for unusual patterns
                if formatted[:2] == "00":
                    validation["warnings"].append("Chapter 00 is reserved")
                
                if formatted[2:4] == "00" and len(clean_code) > 4:
                    validation["warnings"].append("Heading 00 within chapter is unusual")
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating HTS code {hts_code}: {e}")
            return {
                "is_valid": False,
                "formatted_code": None,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            } 