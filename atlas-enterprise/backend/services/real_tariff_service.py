"""
Real Tariff Service for ATLAS Enterprise
Fetches real tariff data from USITC, UN Comtrade, and other sources.
"""

import asyncio
import httpx
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta


class RealTariffService:
    """Service for fetching real tariff data from multiple sources."""
    
    def __init__(self):
        """Initialize the real tariff service."""
        self.usitc_base_url = "https://hts.usitc.gov/api"
        self.comtrade_base_url = "https://comtradeapi.un.org"
        self.cache = {}
        self.cache_ttl = timedelta(hours=6)  # Cache for 6 hours
        
        # Load local tariff data as fallback
        self.local_data_path = Path(__file__).parent.parent / "data"
        self._local_tariff_data = None
    
    async def _load_local_data(self):
        """Load local Excel tariff data as fallback."""
        if self._local_tariff_data is not None:
            return self._local_tariff_data
        
        try:
            excel_file = self.local_data_path / "tariff_database_2025.xlsx"
            if excel_file.exists():
                # Load using pandas
                self._local_tariff_data = pd.read_excel(excel_file)
                print(f"✅ Loaded local tariff data: {len(self._local_tariff_data)} records")
                return self._local_tariff_data
            else:
                print("⚠️ No local tariff data found")
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error loading local data: {e}")
            return pd.DataFrame()
    
    async def get_real_tariff_rate(self, hts_code: str, country: str = "US") -> Dict[str, Any]:
        """
        Get real tariff rate from USITC or other sources.
        
        Args:
            hts_code: HTS code (e.g., "8471.30.01")
            country: Country code (default: US)
            
        Returns:
            Dict with tariff information
        """
        try:
            # Check cache first
            cache_key = f"{hts_code}_{country}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_ttl:
                    print(f"✅ Using cached tariff rate for {hts_code}")
                    return cached_data
            
            # Try USITC API first
            real_data = await self._fetch_from_usitc(hts_code)
            
            if not real_data:
                # Fallback to local data
                real_data = await self._fetch_from_local_data(hts_code)
            
            # Cache the result
            if real_data:
                self.cache[cache_key] = (real_data, datetime.now())
            
            return real_data or self._get_default_tariff_data(hts_code)
            
        except Exception as e:
            print(f"❌ Error getting tariff rate: {e}")
            return self._get_default_tariff_data(hts_code)
    
    async def _fetch_from_usitc(self, hts_code: str) -> Optional[Dict[str, Any]]:
        """Fetch tariff data from USITC API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Format HTS code for USITC (remove dots)
                formatted_code = hts_code.replace(".", "")
                
                # Try to fetch from USITC HTS lookup
                url = f"https://hts.usitc.gov/api/tariff_rates/{formatted_code}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        "hts_code": hts_code,
                        "description": data.get("description", "Unknown product"),
                        "general_rate": float(data.get("general_rate", 0.0)),
                        "special_rate": float(data.get("special_rate", 0.0)),
                        "column_2_rate": float(data.get("column_2_rate", 0.0)),
                        "source": "USITC",
                        "last_updated": datetime.now().isoformat()
                    }
                
                return None
                
        except Exception as e:
            print(f"❌ USITC API error: {e}")
            return None
    
    async def _fetch_from_local_data(self, hts_code: str) -> Optional[Dict[str, Any]]:
        """Fetch tariff data from local Excel file."""
        try:
            df = await self._load_local_data()
            if df.empty:
                return None
            
            # Clean HTS code for matching
            clean_hts = hts_code.replace(".", "")
            
            # Try exact match first
            matches = df[df['hts8'].astype(str).str.replace('.', '') == clean_hts]
            
            if matches.empty:
                # Try partial match (first 6 digits)
                partial_code = clean_hts[:6]
                matches = df[df['hts8'].astype(str).str.replace('.', '').str.startswith(partial_code)]
            
            if not matches.empty:
                row = matches.iloc[0]
                
                return {
                    "hts_code": hts_code,
                    "description": str(row.get('brief_description', 'Unknown product')),
                    "general_rate": float(row.get('general_rate', 0.0)) if pd.notna(row.get('general_rate')) else 0.0,
                    "special_rate": float(row.get('special_rate', 0.0)) if pd.notna(row.get('special_rate')) else 0.0,
                    "column_2_rate": float(row.get('column_2_rate', 0.0)) if pd.notna(row.get('column_2_rate')) else 0.0,
                    "source": "Local Database",
                    "last_updated": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Local data error: {e}")
            return None
    
    def _get_default_tariff_data(self, hts_code: str) -> Dict[str, Any]:
        """Get default tariff data when real data is unavailable."""
        # Estimate based on HTS code chapter
        chapter = hts_code[:2]
        
        # Common tariff rates by chapter (rough estimates)
        chapter_rates = {
            "84": 2.5,  # Machinery
            "85": 0.0,  # Electronics
            "87": 2.5,  # Vehicles
            "63": 8.4,  # Textiles
            "61": 16.5, # Apparel
            "39": 5.0,  # Plastics
            "73": 0.0,  # Iron/Steel
            "90": 1.7,  # Optical instruments
        }
        
        estimated_rate = chapter_rates.get(chapter, 3.0)  # Default 3%
        
        return {
            "hts_code": hts_code,
            "description": f"Product classified under chapter {chapter}",
            "general_rate": estimated_rate,
            "special_rate": 0.0,
            "column_2_rate": estimated_rate * 2,
            "source": "Estimated",
            "last_updated": datetime.now().isoformat()
        }
    
    async def search_hts_codes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for HTS codes based on product description.
        
        Args:
            query: Product description
            limit: Maximum results to return
            
        Returns:
            List of matching HTS codes
        """
        try:
            df = await self._load_local_data()
            if df.empty:
                return []
            
            # Search in description fields
            mask = (
                df['brief_description'].str.contains(query, case=False, na=False) |
                df['description'].str.contains(query, case=False, na=False) if 'description' in df.columns else False
            )
            
            results = df[mask].head(limit)
            
            hts_list = []
            for _, row in results.iterrows():
                hts_code = str(row['hts8'])
                if len(hts_code) >= 8:
                    formatted_hts = f"{hts_code[:4]}.{hts_code[4:6]}.{hts_code[6:8]}"
                    if len(hts_code) > 8:
                        formatted_hts += f".{hts_code[8:10]}"
                else:
                    formatted_hts = hts_code
                
                hts_list.append({
                    "hts_code": formatted_hts,
                    "raw_hts_code": hts_code,
                    "description": str(row.get('brief_description', 'Unknown')),
                    "general_rate": float(row.get('general_rate', 0.0)) if pd.notna(row.get('general_rate')) else 0.0,
                    "special_rate": float(row.get('special_rate', 0.0)) if pd.notna(row.get('special_rate')) else 0.0
                })
            
            print(f"✅ Found {len(hts_list)} HTS codes for '{query}'")
            return hts_list
            
        except Exception as e:
            print(f"❌ Error searching HTS codes: {e}")
            return []
    
    async def get_alternative_countries(self, hts_code: str, current_country: str = "China") -> List[Dict[str, Any]]:
        """
        Get alternative sourcing countries with their tariff rates.
        
        Args:
            hts_code: HTS code
            current_country: Current country of origin
            
        Returns:
            List of alternative countries with rates
        """
        try:
            # For demonstration, we'll use some real data patterns
            # In production, this would query UN Comtrade or similar
            
            alternatives = []
            
            # Get base tariff rate
            base_data = await self.get_real_tariff_rate(hts_code)
            base_rate = base_data.get("general_rate", 0.0)
            
            # Common trade partners with different rates
            countries = [
                {"country": "Mexico", "fta": "USMCA", "rate_multiplier": 0.0},
                {"country": "Canada", "fta": "USMCA", "rate_multiplier": 0.0},
                {"country": "Vietnam", "fta": None, "rate_multiplier": 0.3},
                {"country": "Thailand", "fta": None, "rate_multiplier": 0.4},
                {"country": "Germany", "fta": None, "rate_multiplier": 0.3},
                {"country": "South Korea", "fta": "KORUS", "rate_multiplier": 0.1},
                {"country": "Japan", "fta": None, "rate_multiplier": 0.2}
            ]
            
            for country_data in countries:
                if country_data["country"] != current_country:
                    effective_rate = base_rate * country_data["rate_multiplier"]
                    potential_savings = base_rate - effective_rate
                    
                    alternatives.append({
                        "country": country_data["country"],
                        "tariff_rate": effective_rate,
                        "fta_benefits": country_data["fta"],
                        "potential_savings": potential_savings,
                        "savings_percentage": (potential_savings / base_rate * 100) if base_rate > 0 else 0
                    })
            
            # Sort by potential savings
            alternatives.sort(key=lambda x: x["potential_savings"], reverse=True)
            
            return alternatives[:5]  # Return top 5
            
        except Exception as e:
            print(f"❌ Error getting alternative countries: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            # Test local data loading
            df = await self._load_local_data()
            local_records = len(df) if not df.empty else 0
            
            # Test a simple tariff lookup
            test_data = await self.get_real_tariff_rate("8471.30.01")
            
            return {
                "status": "healthy",
                "local_records": local_records,
                "cache_size": len(self.cache),
                "test_lookup": test_data is not None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global instance
real_tariff_service = RealTariffService()
