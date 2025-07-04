import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import HTSCode
from app.services.chroma_service import ChromaService
from app.core.config import settings
from loguru import logger
import asyncio
from datetime import datetime

class HTSService:
    """HTS Code service for tariff operations"""
    
    def __init__(self):
        self.chroma_service = ChromaService()
        
    async def load_tariff_data(self):
        """Load tariff data from Excel file into database and ChromaDB"""
        try:
            # Check if data already exists
            if await self._has_data():
                logger.info("HTS data already loaded, skipping...")
                return
            
            # Read Excel file
            df = pd.read_excel(settings.TARIFF_DATABASE_PATH)
            logger.info(f"Loaded {len(df)} records from Excel file")
            
            # Process and store data
            await self._process_tariff_data(df)
            
        except Exception as e:
            logger.error(f"Failed to load tariff data: {e}")
            raise
    
    async def _has_data(self) -> bool:
        """Check if HTS data already exists in database"""
        try:
            from app.db.base import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(HTSCode).limit(1))
                return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Failed to check data existence: {e}")
            return False
    
    async def _process_tariff_data(self, df: pd.DataFrame):
        """Process and store tariff data"""
        try:
            # Initialize ChromaDB
            await self.chroma_service.initialize()
            
            # Prepare data for database and ChromaDB
            hts_codes = []
            chroma_data = []
            
            for _, row in df.iterrows():
                # Extract data from Excel (adjust column names as needed)
                hts_code = str(row.get('HTS Code', '')).strip()
                description = str(row.get('Description', '')).strip()
                tariff_rate = float(row.get('Tariff Rate', 0.0))
                country_origin = str(row.get('Country', 'US')).strip()
                
                if hts_code and description:
                    # Database record
                    hts_codes.append({
                        'hts_code': hts_code,
                        'description': description,
                        'tariff_rate': tariff_rate,
                        'country_origin': country_origin,
                        'effective_date': datetime.now()
                    })
                    
                    # ChromaDB record
                    chroma_data.append({
                        'hts_code': hts_code,
                        'description': description,
                        'tariff_rate': tariff_rate,
                        'country_origin': country_origin
                    })
            
            # Store in database
            await self._store_in_database(hts_codes)
            
            # Store in ChromaDB
            await self.chroma_service.add_hts_codes(chroma_data)
            
            logger.info(f"Processed and stored {len(hts_codes)} HTS codes")
            
        except Exception as e:
            logger.error(f"Failed to process tariff data: {e}")
            raise
    
    async def _store_in_database(self, hts_codes: List[Dict[str, Any]]):
        """Store HTS codes in database"""
        try:
            from app.db.base import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                for hts_data in hts_codes:
                    hts_code = HTSCode(**hts_data)
                    session.add(hts_code)
                
                await session.commit()
                logger.info(f"Stored {len(hts_codes)} HTS codes in database")
                
        except Exception as e:
            logger.error(f"Failed to store in database: {e}")
            raise
    
    async def search_hts_codes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search HTS codes by description"""
        try:
            # Search in ChromaDB for semantic similarity
            chroma_results = await self.chroma_service.search_hts_codes(query, limit)
            
            # Also search in database for exact matches
            db_results = await self._search_database(query, limit)
            
            # Combine and deduplicate results
            combined_results = self._combine_search_results(chroma_results, db_results)
            
            return combined_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search HTS codes: {e}")
            return []
    
    async def _search_database(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search HTS codes in database"""
        try:
            from app.db.base import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                # Search for exact HTS code match
                if query.replace('.', '').replace('-', '').isdigit():
                    # Query looks like an HTS code
                    result = await session.execute(
                        select(HTSCode).where(HTSCode.hts_code.like(f"%{query}%")).limit(limit)
                    )
                else:
                    # Query looks like a description
                    result = await session.execute(
                        select(HTSCode).where(HTSCode.description.ilike(f"%{query}%")).limit(limit)
                    )
                
                hts_codes = result.scalars().all()
                
                return [
                    {
                        'hts_code': hts.hts_code,
                        'description': hts.description,
                        'tariff_rate': hts.tariff_rate,
                        'country_origin': hts.country_origin,
                        'similarity_score': 1.0  # Exact match
                    }
                    for hts in hts_codes
                ]
                
        except Exception as e:
            logger.error(f"Failed to search database: {e}")
            return []
    
    def _combine_search_results(self, chroma_results: List[Dict], db_results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate search results"""
        combined = {}
        
        # Add ChromaDB results
        for result in chroma_results:
            hts_code = result['hts_code']
            if hts_code not in combined or result['similarity_score'] > combined[hts_code]['similarity_score']:
                combined[hts_code] = result
        
        # Add database results
        for result in db_results:
            hts_code = result['hts_code']
            if hts_code not in combined or result['similarity_score'] > combined[hts_code]['similarity_score']:
                combined[hts_code] = result
        
        # Sort by similarity score
        sorted_results = sorted(combined.values(), key=lambda x: x['similarity_score'], reverse=True)
        
        return sorted_results
    
    async def get_hts_code(self, hts_code: str) -> Optional[Dict[str, Any]]:
        """Get specific HTS code details"""
        try:
            from app.db.base import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(HTSCode).where(HTSCode.hts_code == hts_code)
                )
                hts = result.scalar_one_or_none()
                
                if hts:
                    return {
                        'hts_code': hts.hts_code,
                        'description': hts.description,
                        'tariff_rate': hts.tariff_rate,
                        'country_origin': hts.country_origin,
                        'effective_date': hts.effective_date.isoformat()
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get HTS code: {e}")
            return None
    
    async def get_tariff_rate(self, hts_code: str, country_origin: str = "US") -> Optional[float]:
        """Get tariff rate for specific HTS code and country"""
        try:
            from app.db.base import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(HTSCode).where(
                        HTSCode.hts_code == hts_code,
                        HTSCode.country_origin == country_origin
                    )
                )
                hts = result.scalar_one_or_none()
                
                return hts.tariff_rate if hts else None
                
        except Exception as e:
            logger.error(f"Failed to get tariff rate: {e}")
            return None
    
    async def update_tariff_rate(self, hts_code: str, new_rate: float, country_origin: str = "US"):
        """Update tariff rate for specific HTS code"""
        try:
            from app.db.base import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                await session.execute(
                    update(HTSCode)
                    .where(HTSCode.hts_code == hts_code, HTSCode.country_origin == country_origin)
                    .values(tariff_rate=new_rate, updated_at=datetime.now())
                )
                await session.commit()
                
                logger.info(f"Updated tariff rate for HTS {hts_code} to {new_rate}")
                
        except Exception as e:
            logger.error(f"Failed to update tariff rate: {e}")
            raise
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get HTS code statistics"""
        try:
            from app.db.base import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                # Get total count
                total_result = await session.execute(select(HTSCode))
                total_count = len(total_result.scalars().all())
                
                # Get average tariff rate
                avg_result = await session.execute(
                    select(HTSCode.tariff_rate)
                )
                rates = [rate for rate in avg_result.scalars().all()]
                avg_rate = sum(rates) / len(rates) if rates else 0
                
                # Get unique countries
                countries_result = await session.execute(
                    select(HTSCode.country_origin.distinct())
                )
                countries = [country for country in countries_result.scalars().all()]
                
                return {
                    'total_hts_codes': total_count,
                    'average_tariff_rate': round(avg_rate, 2),
                    'countries': countries,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
