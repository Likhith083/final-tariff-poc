"""
Free API Integration Service for ATLAS Enterprise
Comprehensive integration with free APIs and open-source services.
"""

import asyncio
import httpx
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import logging
from pathlib import Path
import time
import random

# Hugging Face and ML libraries
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FreeAPIIntegrationService:
    """
    Service for integrating with free APIs and open-source resources:
    - UN Comtrade API (trade data)
    - World Bank Open Data API
    - OECD Trade Data API
    - Hugging Face models for AI classification
    - OpenStreetMap Nominatim for location data
    - Open Exchange Rates (free tier)
    - REST Countries API
    """
    
    def __init__(self, db_path: str = "free_api_data.db", cache_ttl_hours: int = 24):
        """Initialize Free API Integration Service."""
        self.db_path = db_path
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self._cache = {}
        
        # Initialize database
        self._init_database()
        
        # API configurations (all free)
        self.api_configs = {
            "un_comtrade": {
                "base_url": "https://comtrade.un.org/api/get",
                "rate_limit": 1.0,  # 1 request per second (free tier)
                "max_requests_per_hour": 100
            },
            "world_bank": {
                "base_url": "https://api.worldbank.org/v2",
                "rate_limit": 0.5,
                "format": "json"
            },
            "oecd": {
                "base_url": "https://stats.oecd.org/SDMX-JSON/data",
                "rate_limit": 1.0
            },
            "rest_countries": {
                "base_url": "https://restcountries.com/v3.1",
                "rate_limit": 0.1
            },
            "openstreetmap": {
                "base_url": "https://nominatim.openstreetmap.org",
                "rate_limit": 1.0
            },
            "exchange_rates_free": {
                "base_url": "https://api.exchangerate-api.com/v4",
                "rate_limit": 0.5
            }
        }
        
        # Initialize AI models
        self._init_ai_models()
        
        # Request tracking for rate limiting
        self.request_counts = {}
        self.last_request_time = {}
    
    def _init_database(self):
        """Initialize database for caching API data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # API cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT NOT NULL,
                    cache_key TEXT NOT NULL,
                    data TEXT NOT NULL,
                    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    UNIQUE(api_name, cache_key)
                )
            """)
            
            # Trade data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reporter_country TEXT,
                    partner_country TEXT,
                    commodity_code TEXT,
                    trade_flow TEXT,
                    trade_value REAL,
                    year INTEGER,
                    source TEXT,
                    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Country data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS country_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    country_code TEXT NOT NULL,
                    country_name TEXT,
                    region TEXT,
                    currency_code TEXT,
                    currency_name TEXT,
                    capital TEXT,
                    population INTEGER,
                    gdp REAL,
                    trade_agreements TEXT,
                    source TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # AI classification results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT NOT NULL,
                    classification_type TEXT NOT NULL,
                    result TEXT NOT NULL,
                    confidence REAL,
                    model_name TEXT,
                    classified_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Free API database initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def _init_ai_models(self):
        """Initialize free AI models from Hugging Face."""
        try:
            # Text classification model for product classification
            self.text_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
            
            # Sentence embedding model for similarity search
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Named Entity Recognition for extracting product names
            self.ner_model = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            
            logger.info("✅ AI models initialized")
            
        except Exception as e:
            logger.error(f"❌ AI model initialization failed: {e}")
            # Fallback to None if models can't be loaded
            self.text_classifier = None
            self.sentence_model = None
            self.ner_model = None
    
    async def _rate_limit_check(self, api_name: str) -> bool:
        """Check if we can make a request to the API without hitting rate limits."""
        current_time = time.time()
        config = self.api_configs.get(api_name, {})
        rate_limit = config.get("rate_limit", 1.0)
        
        # Check time-based rate limit
        last_request = self.last_request_time.get(api_name, 0)
        if current_time - last_request < rate_limit:
            return False
        
        # Check hourly limits for UN Comtrade
        if api_name == "un_comtrade":
            hour_key = f"{api_name}_{int(current_time // 3600)}"
            hourly_count = self.request_counts.get(hour_key, 0)
            if hourly_count >= config.get("max_requests_per_hour", 100):
                return False
        
        return True
    
    async def _make_api_request(self, api_name: str, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """Make rate-limited API request with caching."""
        try:
            # Check rate limits
            if not await self._rate_limit_check(api_name):
                logger.warning(f"Rate limit hit for {api_name}")
                return None
            
            # Check cache first
            cache_key = f"{url}_{json.dumps(params or {}, sort_keys=True)}"
            cached_data = await self._get_from_cache(api_name, cache_key)
            if cached_data:
                return cached_data
            
            # Make request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Cache the result
                    await self._store_in_cache(api_name, cache_key, data)
                    
                    # Update request tracking
                    current_time = time.time()
                    self.last_request_time[api_name] = current_time
                    
                    if api_name == "un_comtrade":
                        hour_key = f"{api_name}_{int(current_time // 3600)}"
                        self.request_counts[hour_key] = self.request_counts.get(hour_key, 0) + 1
                    
                    return data
                else:
                    logger.error(f"API request failed: {api_name} returned {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"API request error for {api_name}: {e}")
            return None
    
    async def _get_from_cache(self, api_name: str, cache_key: str) -> Optional[Dict]:
        """Get data from cache if still valid."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data, expires_at FROM api_cache 
                WHERE api_name = ? AND cache_key = ? AND expires_at > datetime('now')
            """, (api_name, cache_key))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    async def _store_in_cache(self, api_name: str, cache_key: str, data: Dict):
        """Store data in cache."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + self.cache_ttl
            
            cursor.execute("""
                INSERT OR REPLACE INTO api_cache (api_name, cache_key, data, expires_at) 
                VALUES (?, ?, ?, ?)
            """, (api_name, cache_key, json.dumps(data), expires_at))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    async def get_un_comtrade_data(self, reporter: str, partner: str = "0", 
                                  commodity: str = "TOTAL", year: str = "2023") -> Dict[str, Any]:
        """
        Get trade data from UN Comtrade API.
        
        Args:
            reporter: Reporter country code (e.g., "842" for USA)
            partner: Partner country code ("0" for world)
            commodity: Commodity code ("TOTAL" for all)
            year: Year for data
        """
        try:
            url = self.api_configs["un_comtrade"]["base_url"]
            params = {
                "max": "50000",
                "type": "C",  # Commodities
                "freq": "A",  # Annual
                "px": "HS",   # HS classification
                "ps": year,
                "r": reporter,
                "p": partner,
                "rg": "all",  # All trade flows
                "cc": commodity,
                "fmt": "json"
            }
            
            data = await self._make_api_request("un_comtrade", url, params)
            
            if data and "dataset" in data:
                # Store in database
                await self._store_trade_data(data["dataset"], "un_comtrade")
                
                return {
                    "status": "success",
                    "source": "UN Comtrade",
                    "records_count": len(data["dataset"]),
                    "data": data["dataset"],
                    "metadata": {
                        "reporter": reporter,
                        "partner": partner,
                        "commodity": commodity,
                        "year": year
                    }
                }
            else:
                return {"status": "error", "message": "No data received from UN Comtrade"}
                
        except Exception as e:
            logger.error(f"UN Comtrade data fetch failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_world_bank_data(self, indicator: str, country: str = "all", 
                                 start_year: str = "2020", end_year: str = "2023") -> Dict[str, Any]:
        """
        Get economic data from World Bank API.
        
        Args:
            indicator: World Bank indicator code (e.g., "NY.GDP.MKTP.CD" for GDP)
            country: Country code or "all"
            start_year: Start year
            end_year: End year
        """
        try:
            url = f"{self.api_configs['world_bank']['base_url']}/country/{country}/indicator/{indicator}"
            params = {
                "date": f"{start_year}:{end_year}",
                "format": "json",
                "per_page": "1000"
            }
            
            data = await self._make_api_request("world_bank", url, params)
            
            if data and len(data) > 1:
                return {
                    "status": "success",
                    "source": "World Bank",
                    "records_count": len(data[1]) if len(data) > 1 else 0,
                    "data": data[1] if len(data) > 1 else [],
                    "metadata": data[0] if len(data) > 0 else {}
                }
            else:
                return {"status": "error", "message": "No data received from World Bank"}
                
        except Exception as e:
            logger.error(f"World Bank data fetch failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_oecd_trade_data(self, dataset: str = "TRADE_GOODS", 
                                 country: str = "USA", measure: str = "VALUE") -> Dict[str, Any]:
        """
        Get trade data from OECD API.
        
        Args:
            dataset: OECD dataset name
            country: Country code
            measure: Measure type (VALUE, QUANTITY, etc.)
        """
        try:
            url = f"{self.api_configs['oecd']['base_url']}/{dataset}"
            params = {
                "startTime": "2020",
                "endTime": "2023",
                "dimensionAtObservation": "allDimensions"
            }
            
            data = await self._make_api_request("oecd", url, params)
            
            if data:
                return {
                    "status": "success",
                    "source": "OECD",
                    "data": data,
                    "metadata": {
                        "dataset": dataset,
                        "country": country,
                        "measure": measure
                    }
                }
            else:
                return {"status": "error", "message": "No data received from OECD"}
                
        except Exception as e:
            logger.error(f"OECD data fetch failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_country_information(self, country_code: str) -> Dict[str, Any]:
        """Get comprehensive country information from REST Countries API."""
        try:
            url = f"{self.api_configs['rest_countries']['base_url']}/alpha/{country_code}"
            
            data = await self._make_api_request("rest_countries", url)
            
            if data and len(data) > 0:
                country_info = data[0]
                
                # Extract relevant information
                result = {
                    "status": "success",
                    "country_code": country_code,
                    "name": country_info.get("name", {}).get("common", ""),
                    "official_name": country_info.get("name", {}).get("official", ""),
                    "region": country_info.get("region", ""),
                    "subregion": country_info.get("subregion", ""),
                    "capital": country_info.get("capital", []),
                    "currencies": country_info.get("currencies", {}),
                    "languages": country_info.get("languages", {}),
                    "borders": country_info.get("borders", []),
                    "trade_agreements": [],  # Would need additional API for this
                    "population": country_info.get("population", 0),
                    "area": country_info.get("area", 0)
                }
                
                # Store in database
                await self._store_country_data(result)
                
                return result
            else:
                return {"status": "error", "message": "Country not found"}
                
        except Exception as e:
            logger.error(f"Country information fetch failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def classify_product_text(self, product_description: str) -> Dict[str, Any]:
        """Use Hugging Face models to classify product descriptions."""
        try:
            if not self.text_classifier:
                return {"status": "error", "message": "Text classifier not available"}
            
            # Extract entities first
            entities = []
            if self.ner_model:
                ner_results = self.ner_model(product_description)
                entities = [{"text": entity["word"], "label": entity["entity_group"], 
                           "confidence": entity["score"]} for entity in ner_results]
            
            # Get sentence embedding for similarity search
            embedding = None
            if self.sentence_model:
                embedding = self.sentence_model.encode(product_description).tolist()
            
            # Classify the text (this would be enhanced with a proper product classification model)
            classification_result = {
                "status": "success",
                "input_text": product_description,
                "entities": entities,
                "embedding": embedding,
                "suggested_categories": self._suggest_product_categories(product_description),
                "confidence": 0.8,  # Placeholder
                "model_info": {
                    "ner_model": "bert-large-cased-finetuned-conll03-english",
                    "embedding_model": "all-MiniLM-L6-v2"
                }
            }
            
            # Store result in database
            await self._store_ai_classification(product_description, "product_classification", 
                                              classification_result, 0.8, "huggingface_ensemble")
            
            return classification_result
            
        except Exception as e:
            logger.error(f"Product classification failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _suggest_product_categories(self, description: str) -> List[Dict[str, Any]]:
        """Suggest product categories based on keywords."""
        # Simple keyword-based categorization (would be enhanced with proper ML)
        categories = []
        description_lower = description.lower()
        
        category_keywords = {
            "electronics": ["computer", "phone", "electronic", "device", "battery", "circuit"],
            "textiles": ["cotton", "fabric", "clothing", "textile", "yarn", "fiber"],
            "machinery": ["machine", "engine", "motor", "equipment", "tool", "mechanical"],
            "chemicals": ["chemical", "acid", "polymer", "compound", "solution"],
            "food": ["food", "beverage", "grain", "meat", "dairy", "fruit", "vegetable"],
            "automotive": ["car", "vehicle", "auto", "tire", "engine", "brake"],
            "medical": ["medical", "pharmaceutical", "drug", "medicine", "surgical"],
            "metals": ["steel", "aluminum", "copper", "iron", "metal", "alloy"]
        }
        
        for category, keywords in category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            if matches > 0:
                confidence = min(0.9, matches / len(keywords) + 0.1)
                categories.append({
                    "category": category,
                    "confidence": confidence,
                    "matching_keywords": [kw for kw in keywords if kw in description_lower]
                })
        
        return sorted(categories, key=lambda x: x["confidence"], reverse=True)[:3]
    
    async def _store_trade_data(self, trade_records: List[Dict], source: str):
        """Store trade data in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for record in trade_records:
                cursor.execute("""
                    INSERT OR REPLACE INTO trade_data 
                    (reporter_country, partner_country, commodity_code, trade_flow, trade_value, year, source) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.get("rtTitle", ""),
                    record.get("ptTitle", ""),
                    record.get("cmdCode", ""),
                    record.get("rgDesc", ""),
                    record.get("TradeValue", 0),
                    record.get("yr", 0),
                    source
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store trade data: {e}")
    
    async def _store_country_data(self, country_info: Dict):
        """Store country data in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract currency info
            currencies = country_info.get("currencies", {})
            currency_code = list(currencies.keys())[0] if currencies else ""
            currency_name = currencies.get(currency_code, {}).get("name", "") if currency_code else ""
            
            cursor.execute("""
                INSERT OR REPLACE INTO country_data 
                (country_code, country_name, region, currency_code, currency_name, capital, population, source) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                country_info.get("country_code", ""),
                country_info.get("name", ""),
                country_info.get("region", ""),
                currency_code,
                currency_name,
                ",".join(country_info.get("capital", [])),
                country_info.get("population", 0),
                "rest_countries"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store country data: {e}")
    
    async def _store_ai_classification(self, input_text: str, classification_type: str, 
                                     result: Dict, confidence: float, model_name: str):
        """Store AI classification result in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ai_classifications 
                (input_text, classification_type, result, confidence, model_name) 
                VALUES (?, ?, ?, ?, ?)
            """, (input_text, classification_type, json.dumps(result), confidence, model_name))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store AI classification: {e}")
    
    async def get_comprehensive_trade_analysis(self, country_code: str, hts_code: str = None) -> Dict[str, Any]:
        """Get comprehensive trade analysis using multiple free APIs."""
        try:
            analysis = {
                "country_code": country_code,
                "hts_code": hts_code,
                "analysis_timestamp": datetime.now().isoformat(),
                "data_sources": []
            }
            
            # Get country information
            country_info = await self.get_country_information(country_code)
            if country_info["status"] == "success":
                analysis["country_info"] = country_info
                analysis["data_sources"].append("REST Countries API")
            
            # Get trade data from UN Comtrade
            un_data = await self.get_un_comtrade_data(
                reporter=self._get_un_country_code(country_code),
                commodity=hts_code[:4] if hts_code else "TOTAL"
            )
            if un_data["status"] == "success":
                analysis["trade_data"] = un_data
                analysis["data_sources"].append("UN Comtrade")
            
            # Get World Bank economic indicators
            wb_gdp = await self.get_world_bank_data("NY.GDP.MKTP.CD", country_code.lower())
            if wb_gdp["status"] == "success":
                analysis["economic_data"] = wb_gdp
                analysis["data_sources"].append("World Bank")
            
            # Generate insights
            analysis["insights"] = self._generate_trade_insights(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Comprehensive trade analysis failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_un_country_code(self, iso_code: str) -> str:
        """Convert ISO country code to UN Comtrade country code."""
        # This is a simplified mapping - in production, use a complete mapping table
        mapping = {
            "US": "842", "CN": "156", "DE": "276", "JP": "392",
            "GB": "826", "FR": "250", "IT": "380", "CA": "124"
        }
        return mapping.get(iso_code.upper(), "842")  # Default to US
    
    def _generate_trade_insights(self, analysis_data: Dict) -> List[Dict[str, Any]]:
        """Generate insights from the collected trade data."""
        insights = []
        
        # Analyze trade volume
        if "trade_data" in analysis_data:
            trade_records = analysis_data["trade_data"].get("data", [])
            if trade_records:
                total_trade = sum(record.get("TradeValue", 0) for record in trade_records)
                insights.append({
                    "type": "trade_volume",
                    "message": f"Total trade value: ${total_trade:,.0f}",
                    "impact": "info",
                    "data": {"total_trade_value": total_trade}
                })
        
        # Analyze economic indicators
        if "economic_data" in analysis_data:
            gdp_data = analysis_data["economic_data"].get("data", [])
            if gdp_data:
                latest_gdp = gdp_data[0].get("value") if gdp_data else 0
                if latest_gdp:
                    insights.append({
                        "type": "economic_indicator",
                        "message": f"GDP: ${latest_gdp:,.0f}",
                        "impact": "info",
                        "data": {"gdp": latest_gdp}
                    })
        
        return insights
    
    async def get_service_health_report(self) -> Dict[str, Any]:
        """Generate health report for the free API integration service."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Count cached entries
            cache_stats = pd.read_sql_query("""
                SELECT api_name, COUNT(*) as cached_entries, 
                       MAX(cached_at) as last_cache_update
                FROM api_cache 
                WHERE expires_at > datetime('now')
                GROUP BY api_name
            """, conn)
            
            # Count AI classifications
            ai_stats = pd.read_sql_query("""
                SELECT classification_type, COUNT(*) as count,
                       AVG(confidence) as avg_confidence
                FROM ai_classifications 
                WHERE classified_at >= datetime('now', '-7 days')
                GROUP BY classification_type
            """, conn)
            
            conn.close()
            
            return {
                "status": "healthy",
                "available_apis": list(self.api_configs.keys()),
                "ai_models_loaded": {
                    "text_classifier": self.text_classifier is not None,
                    "sentence_model": self.sentence_model is not None,
                    "ner_model": self.ner_model is not None
                },
                "cache_statistics": cache_stats.to_dict('records'),
                "ai_classification_stats": ai_stats.to_dict('records'),
                "request_limits": {
                    "un_comtrade_hourly": 100,
                    "current_hour_usage": sum(1 for k in self.request_counts.keys() if "un_comtrade" in k)
                },
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health report failed: {e}")
            return {"status": "unhealthy", "error": str(e)} 