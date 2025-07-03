import pandas as pd
from typing import List, Dict, Any, Optional
from loguru import logger
import os
import asyncio
from .chroma_service import ChromaService

class HTSService:
    """HTS Code service for tariff operations with vector and substring search"""
    
    def __init__(self):
        self.chroma_service = ChromaService()
        self.excel_file = os.path.join(os.path.dirname(__file__), '../../data/tariff_database_2025.xlsx')
        self._df = None
        
    async def initialize(self):
        """Initialize the service and load data"""
        try:
            # Initialize ChromaDB
            await self.chroma_service.initialize()
            
            # Load Excel data
            await self._load_excel_data()
            
            # Check if ChromaDB has data, if not, populate it
            stats = await self.chroma_service.get_collection_stats("hts_codes")
            if stats.get("total_documents", 0) == 0:
                await self._populate_chroma_db()
                
            logger.info("HTS Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize HTS Service: {e}")
            raise
    
    async def _load_excel_data(self):
        """Load Excel data into memory"""
        try:
            if not os.path.exists(self.excel_file):
                raise FileNotFoundError(f"Excel file not found: {self.excel_file}")
            
            self._df = pd.read_excel(self.excel_file)
            logger.info(f"Loaded {len(self._df)} records from Excel file")
            
        except Exception as e:
            logger.error(f"Failed to load Excel data: {e}")
            raise
    
    async def _populate_chroma_db(self):
        """Populate ChromaDB with HTS codes from Excel"""
        try:
            if self._df is None:
                await self._load_excel_data()
            
            hts_data = []
            for _, row in self._df.iterrows():
                hts_code = str(row.get('hts8', '')).strip()
                description = str(row.get('brief_description', '')).strip()
                duty_rate = str(row.get('mfn_ad_val_rate this is the general tariff rate', '')).strip()
                
                if hts_code and description:
                    hts_data.append({
                        'hts_code': hts_code,
                        'description': description,
                        'duty_rate': duty_rate,
                        'category': ''  # No category column in current Excel
                    })
            
            await self.chroma_service.add_hts_codes(hts_data)
            logger.info(f"Populated ChromaDB with {len(hts_data)} HTS codes")
            
        except Exception as e:
            logger.error(f"Failed to populate ChromaDB: {e}")
            raise
    
    async def search_hts_codes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search HTS codes using both vector similarity and substring matching"""
        try:
            if not query.strip():
                return []
            
            # Get vector search results from ChromaDB
            vector_results = await self.chroma_service.search_hts_codes(query, limit)
            
            # Get substring search results from pandas
            substring_results = await self._search_excel_substring(query, limit)
            
            # Combine and deduplicate results
            combined_results = self._combine_search_results(vector_results, substring_results)
            
            return combined_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search HTS codes: {e}")
            return []
    
    async def _search_excel_substring(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search HTS codes in Excel using substring matching"""
        try:
            if self._df is None:
                await self._load_excel_data()
            
            query_lower = query.lower()
            results = []
            
            # Search in hts8 column (exact or partial match)
            hts_matches = self._df[
                self._df['hts8'].astype(str).str.contains(query_lower, case=False, na=False)
            ].head(limit)
            
            for _, row in hts_matches.iterrows():
                results.append({
                    'hts_code': str(row.get('hts8', '')).strip(),
                    'description': str(row.get('brief_description', '')).strip(),
                    'duty_rate': str(row.get('mfn_ad_val_rate this is the general tariff rate', '')).strip(),
                    'category': '',
                    'similarity_score': 1.0  # Exact match
                })
            
            # Search in brief_description column
            desc_matches = self._df[
                self._df['brief_description'].astype(str).str.contains(query_lower, case=False, na=False)
            ].head(limit)
            
            for _, row in desc_matches.iterrows():
                hts_code = str(row.get('hts8', '')).strip()
                # Avoid duplicates
                if not any(r['hts_code'] == hts_code for r in results):
                    results.append({
                        'hts_code': hts_code,
                        'description': str(row.get('brief_description', '')).strip(),
                        'duty_rate': str(row.get('mfn_ad_val_rate this is the general tariff rate', '')).strip(),
                        'category': '',
                        'similarity_score': 0.8  # Substring match
                    })
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search Excel substring: {e}")
            return []
    
    def _combine_search_results(self, vector_results: List[Dict], substring_results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate search results"""
        combined = {}
        
        # Add vector results
        for result in vector_results:
            hts_code = result['hts_code']
            if hts_code not in combined or result['similarity_score'] > combined[hts_code]['similarity_score']:
                combined[hts_code] = result
        
        # Add substring results
        for result in substring_results:
            hts_code = result['hts_code']
            if hts_code not in combined or result['similarity_score'] > combined[hts_code]['similarity_score']:
                combined[hts_code] = result
        
        # Sort by similarity score
        sorted_results = sorted(combined.values(), key=lambda x: x['similarity_score'], reverse=True)
        
        return sorted_results
    
    async def get_suggestions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get HTS code suggestions for autocomplete"""
        try:
            if not query.strip():
                return []
            
            # Get suggestions from ChromaDB
            suggestions = await self.chroma_service.get_suggestions(query, limit)
            
            # Also get substring suggestions from Excel
            if len(suggestions) < limit:
                substring_suggestions = await self._search_excel_substring(query, limit - len(suggestions))
                for result in substring_suggestions:
                    suggestions.append({
                        'hts_code': result['hts_code'],
                        'description': result['description'],
                        'display_text': f"{result['hts_code']} - {result['description']}",
                        'similarity_score': result['similarity_score']
                    })
            
            # Remove duplicates and sort
            unique_suggestions = []
            seen_codes = set()
            for suggestion in suggestions:
                if suggestion['hts_code'] not in seen_codes:
                    unique_suggestions.append(suggestion)
                    seen_codes.add(suggestion['hts_code'])
            
            return sorted(unique_suggestions, key=lambda x: x['similarity_score'], reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []
    
    async def get_hts_code(self, hts_code: str) -> Optional[Dict[str, Any]]:
        """Get specific HTS code details"""
        try:
            if self._df is None:
                await self._load_excel_data()
            
            # Search in Excel
            matches = self._df[self._df['hts8'].astype(str) == hts_code]
            
            if not matches.empty:
                row = matches.iloc[0]
                return {
                    'hts_code': str(row.get('hts8', '')).strip(),
                    'description': str(row.get('brief_description', '')).strip(),
                    'duty_rate': str(row.get('mfn_ad_val_rate this is the general tariff rate', '')).strip(),
                    'category': ''
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get HTS code: {e}")
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get HTS code statistics"""
        try:
            if self._df is None:
                await self._load_excel_data()
            
            stats = await self.chroma_service.get_collection_stats("hts_codes")
            
            return {
                'total_hts_codes': len(self._df),
                'vector_store_documents': stats.get('total_documents', 0),
                'last_updated': pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {} 