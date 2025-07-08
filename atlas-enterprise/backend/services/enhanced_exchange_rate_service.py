"""
Enhanced ExchangeRateService for ATLAS Enterprise
Advanced exchange rate service with multiple sources, auto-updates, and predictive capabilities.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import httpx
from forex_python.converter import CurrencyRates, CurrencyConverter
import json
import sqlite3
import pandas as pd
from pathlib import Path
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import logging
import schedule
import time
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedExchangeRateService:
    """
    Enhanced production service for real currency conversion with:
    - Multiple data sources and validation
    - Daily auto-updates
    - Historical data storage and analysis
    - Predictive modeling
    - Risk assessment
    """
    
    def __init__(self, db_path: str = "exchange_rates.db"):
        """Initialize Enhanced ExchangeRateService."""
        self.db_path = db_path
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)
        self.currency_rates = CurrencyRates()
        self.currency_converter = CurrencyConverter()
        
        # Initialize database
        self._init_database()
        
        # Free API sources (no API key required)
        self.data_sources = {
            "exchangerate_api": "https://api.exchangerate-api.com/v4/latest/{base}",
            "fixer_free": "http://data.fixer.io/api/latest?access_key=FREE_TIER",
            "currencylayer_free": "http://api.currencylayer.com/live?access_key=FREE_TIER",
            "openexchangerates_free": "https://openexchangerates.org/api/latest.json?app_id=FREE_TIER"
        }
        
        # Backup sources
        self.backup_sources = [
            "https://api.exchangerate.host/latest",
            "https://api.vatcomply.com/rates",
            "https://api.ratesapi.io/api/latest"
        ]
        
        # Common currency pairs for enhanced caching
        self.major_pairs = [
            ("USD", "EUR"), ("USD", "GBP"), ("USD", "JPY"), ("USD", "AUD"),
            ("USD", "CAD"), ("USD", "CHF"), ("EUR", "GBP"), ("EUR", "JPY"),
            ("GBP", "JPY"), ("USD", "CNY"), ("USD", "INR"), ("USD", "KRW")
        ]
        
        # Predictive models
        self.prediction_models = {}
        self.scalers = {}
        
        # Start background update scheduler
        self._start_background_updates()
    
    def _init_database(self):
        """Initialize SQLite database for historical data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_currency TEXT NOT NULL,
                    to_currency TEXT NOT NULL,
                    rate REAL NOT NULL,
                    source TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(from_currency, to_currency, source, date(timestamp))
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_currency TEXT NOT NULL,
                    to_currency TEXT NOT NULL,
                    predicted_rate REAL NOT NULL,
                    confidence REAL NOT NULL,
                    prediction_date DATETIME NOT NULL,
                    for_date DATETIME NOT NULL,
                    model_version TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS volatility_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency_pair TEXT NOT NULL,
                    volatility_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    def _start_background_updates(self):
        """Start background thread for scheduled updates."""
        def run_scheduler():
            # Schedule daily updates at 6 AM UTC
            schedule.every().day.at("06:00").do(self._daily_update_job)
            # Schedule major pairs update every 4 hours
            schedule.every(4).hours.do(self._update_major_pairs)
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("✅ Background scheduler started")
    
    async def _daily_update_job(self):
        """Daily job to update all currency data."""
        logger.info("🔄 Starting daily currency update job")
        
        try:
            # Update major currency pairs
            await self._update_major_pairs()
            
            # Clean old cache
            self._clean_old_cache()
            
            # Update prediction models
            await self._update_prediction_models()
            
            # Analyze volatility
            await self._analyze_volatility()
            
            logger.info("✅ Daily update job completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Daily update job failed: {e}")
    
    async def _update_major_pairs(self):
        """Update major currency pairs from multiple sources."""
        logger.info("🔄 Updating major currency pairs")
        
        for from_curr, to_curr in self.major_pairs:
            try:
                # Get rates from multiple sources
                rates = await self._fetch_from_multiple_sources(from_curr, to_curr)
                
                if rates:
                    # Calculate weighted average
                    validated_rate = self._validate_and_average_rates(rates)
                    
                    # Store in database
                    await self._store_rate_in_db(from_curr, to_curr, validated_rate, "validated_average")
                    
                    # Update cache
                    cache_key = self._get_cache_key(from_curr, to_curr)
                    self._cache[cache_key] = (validated_rate, datetime.now())
                    
            except Exception as e:
                logger.error(f"❌ Failed to update {from_curr}/{to_curr}: {e}")
    
    async def _fetch_from_multiple_sources(self, from_currency: str, to_currency: str) -> List[Tuple[float, str]]:
        """Fetch rates from multiple sources for validation."""
        rates = []
        
        # Try forex-python
        try:
            rate = await self._fetch_from_forex_python(from_currency, to_currency)
            if rate:
                rates.append((rate, "forex_python"))
        except Exception as e:
            logger.warning(f"forex-python failed: {e}")
        
        # Try free APIs
        for source_name, url_template in self.data_sources.items():
            try:
                rate = await self._fetch_from_api_source(source_name, from_currency, to_currency)
                if rate:
                    rates.append((rate, source_name))
            except Exception as e:
                logger.warning(f"{source_name} failed: {e}")
        
        # Try backup sources
        for backup_url in self.backup_sources:
            try:
                rate = await self._fetch_from_backup_source(backup_url, from_currency, to_currency)
                if rate:
                    rates.append((rate, f"backup_{backup_url.split('//')[1].split('/')[0]}"))
            except Exception as e:
                logger.warning(f"Backup source {backup_url} failed: {e}")
        
        return rates
    
    def _validate_and_average_rates(self, rates: List[Tuple[float, str]]) -> float:
        """Validate rates and calculate weighted average."""
        if not rates:
            return 1.0
        
        # Remove outliers (rates that are more than 5% different from median)
        rate_values = [r[0] for r in rates]
        median_rate = np.median(rate_values)
        
        filtered_rates = []
        for rate, source in rates:
            if abs(rate - median_rate) / median_rate <= 0.05:  # Within 5%
                filtered_rates.append((rate, source))
            else:
                logger.warning(f"Outlier rate detected from {source}: {rate} (median: {median_rate})")
        
        if not filtered_rates:
            # If all rates are outliers, use the one closest to median
            closest_rate = min(rates, key=lambda x: abs(x[0] - median_rate))
            return closest_rate[0]
        
        # Calculate weighted average (forex-python gets higher weight)
        total_weight = 0
        weighted_sum = 0
        
        for rate, source in filtered_rates:
            weight = 3 if source == "forex_python" else 2 if "api" in source else 1
            weighted_sum += rate * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 1.0
    
    async def _fetch_from_forex_python(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch rate using forex-python library."""
        try:
            loop = asyncio.get_event_loop()
            rate = await loop.run_in_executor(
                None,
                self.currency_rates.get_rate,
                from_currency,
                to_currency
            )
            return rate
        except Exception as e:
            logger.warning(f"forex-python failed: {e}")
            return None
    
    async def _fetch_from_api_source(self, source_name: str, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch rate from a specific API source."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if source_name == "exchangerate_api":
                    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        rates = data.get("rates", {})
                        return float(rates.get(to_currency, 0)) if to_currency in rates else None
                
                # Add more API source implementations here
                return None
                
        except Exception as e:
            logger.warning(f"API source {source_name} failed: {e}")
            return None
    
    async def _fetch_from_backup_source(self, url: str, from_currency: str, to_currency: str) -> Optional[float]:
        """Fetch rate from backup source."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response formats
                    if "rates" in data:
                        rates = data["rates"]
                        base = data.get("base", "EUR")
                        
                        if base == from_currency and to_currency in rates:
                            return float(rates[to_currency])
                        elif base == to_currency and from_currency in rates:
                            return 1.0 / float(rates[from_currency])
                
                return None
                
        except Exception as e:
            logger.warning(f"Backup source failed: {e}")
            return None
    
    async def _store_rate_in_db(self, from_currency: str, to_currency: str, rate: float, source: str):
        """Store exchange rate in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO exchange_rates 
                (from_currency, to_currency, rate, source, timestamp) 
                VALUES (?, ?, ?, ?, ?)
            """, (from_currency, to_currency, rate, source, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store rate in DB: {e}")
    
    async def get_historical_data(self, from_currency: str, to_currency: str, days: int = 30) -> pd.DataFrame:
        """Get historical exchange rate data."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT rate, timestamp 
                FROM exchange_rates 
                WHERE from_currency = ? AND to_currency = ? 
                AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp
            """.format(days)
            
            df = pd.read_sql_query(query, conn, params=(from_currency, to_currency))
            conn.close()
            
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return pd.DataFrame()
    
    async def _update_prediction_models(self):
        """Update ML models for rate prediction."""
        logger.info("🔄 Updating prediction models")
        
        for from_curr, to_curr in self.major_pairs:
            try:
                # Get historical data
                df = await self.get_historical_data(from_curr, to_curr, days=90)
                
                if len(df) < 10:  # Need minimum data points
                    continue
                
                # Prepare features
                df['rate_change'] = df['rate'].pct_change()
                df['ma_7'] = df['rate'].rolling(window=7).mean()
                df['ma_30'] = df['rate'].rolling(window=30).mean()
                df['volatility'] = df['rate'].rolling(window=7).std()
                
                # Drop NaN values
                df = df.dropna()
                
                if len(df) < 5:
                    continue
                
                # Prepare training data
                features = ['rate_change', 'ma_7', 'ma_30', 'volatility']
                X = df[features].values
                y = df['rate'].values
                
                # Train model
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                model = LinearRegression()
                model.fit(X_scaled[:-1], y[1:])  # Predict next rate
                
                # Store model and scaler
                pair_key = f"{from_curr}_{to_curr}"
                self.prediction_models[pair_key] = model
                self.scalers[pair_key] = scaler
                
                logger.info(f"✅ Updated prediction model for {from_curr}/{to_curr}")
                
            except Exception as e:
                logger.error(f"Failed to update model for {from_curr}/{to_curr}: {e}")
    
    async def predict_exchange_rate(self, from_currency: str, to_currency: str, days_ahead: int = 1) -> Dict[str, Any]:
        """Predict future exchange rate using ML model."""
        try:
            pair_key = f"{from_currency}_{to_currency}"
            
            if pair_key not in self.prediction_models:
                return {
                    "predicted_rate": None,
                    "confidence": 0.0,
                    "error": "No prediction model available for this currency pair"
                }
            
            # Get recent data for prediction
            df = await self.get_historical_data(from_currency, to_currency, days=30)
            
            if len(df) < 5:
                return {
                    "predicted_rate": None,
                    "confidence": 0.0,
                    "error": "Insufficient historical data for prediction"
                }
            
            # Prepare features
            df['rate_change'] = df['rate'].pct_change()
            df['ma_7'] = df['rate'].rolling(window=7).mean()
            df['ma_30'] = df['rate'].rolling(window=30).mean()
            df['volatility'] = df['rate'].rolling(window=7).std()
            df = df.dropna()
            
            # Get latest features
            features = ['rate_change', 'ma_7', 'ma_30', 'volatility']
            latest_features = df[features].iloc[-1].values.reshape(1, -1)
            
            # Scale features
            scaler = self.scalers[pair_key]
            latest_features_scaled = scaler.transform(latest_features)
            
            # Make prediction
            model = self.prediction_models[pair_key]
            predicted_rate = model.predict(latest_features_scaled)[0]
            
            # Calculate confidence (simplified)
            recent_volatility = df['volatility'].iloc[-1]
            confidence = max(0.1, min(0.9, 1.0 - (recent_volatility * 10)))
            
            return {
                "predicted_rate": float(predicted_rate),
                "confidence": float(confidence),
                "current_rate": float(df['rate'].iloc[-1]),
                "volatility": float(recent_volatility),
                "prediction_date": datetime.now().isoformat(),
                "for_date": (datetime.now() + timedelta(days=days_ahead)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed for {from_currency}/{to_currency}: {e}")
            return {
                "predicted_rate": None,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _analyze_volatility(self):
        """Analyze currency volatility and risk levels."""
        logger.info("🔄 Analyzing currency volatility")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for from_curr, to_curr in self.major_pairs:
                df = await self.get_historical_data(from_curr, to_curr, days=30)
                
                if len(df) < 10:
                    continue
                
                # Calculate volatility metrics
                daily_returns = df['rate'].pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252)  # Annualized volatility
                
                # Determine risk level
                if volatility < 0.1:
                    risk_level = "LOW"
                elif volatility < 0.2:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "HIGH"
                
                # Store analysis
                cursor.execute("""
                    INSERT OR REPLACE INTO volatility_analysis 
                    (currency_pair, volatility_score, risk_level, analysis_date) 
                    VALUES (?, ?, ?, ?)
                """, (f"{from_curr}/{to_curr}", volatility, risk_level, datetime.now()))
            
            conn.commit()
            conn.close()
            logger.info("✅ Volatility analysis completed")
            
        except Exception as e:
            logger.error(f"Volatility analysis failed: {e}")
    
    def _clean_old_cache(self):
        """Clean old cache entries."""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (rate, timestamp) in self._cache.items():
            if current_time - timestamp > self._cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        logger.info(f"🧹 Cleaned {len(expired_keys)} expired cache entries")
    
    def _get_cache_key(self, from_currency: str, to_currency: str) -> str:
        """Generate cache key for currency pair."""
        return f"{from_currency.upper()}_{to_currency.upper()}"
    
    async def get_exchange_rate_with_confidence(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get exchange rate with confidence metrics and validation."""
        try:
            # Get rates from multiple sources
            rates = await self._fetch_from_multiple_sources(from_currency, to_currency)
            
            if not rates:
                return {
                    "rate": 1.0,
                    "confidence": 0.0,
                    "sources_count": 0,
                    "validation": "FAILED",
                    "error": "No sources available"
                }
            
            # Validate and get final rate
            final_rate = self._validate_and_average_rates(rates)
            
            # Calculate confidence based on source agreement
            rate_values = [r[0] for r in rates]
            std_dev = np.std(rate_values)
            mean_rate = np.mean(rate_values)
            
            # Confidence decreases with higher standard deviation
            confidence = max(0.1, min(0.95, 1.0 - (std_dev / mean_rate)))
            
            # Validation status
            validation = "HIGH" if confidence > 0.8 else "MEDIUM" if confidence > 0.5 else "LOW"
            
            return {
                "rate": final_rate,
                "confidence": confidence,
                "sources_count": len(rates),
                "validation": validation,
                "source_rates": [{"rate": r[0], "source": r[1]} for r in rates],
                "std_deviation": std_dev,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get rate with confidence: {e}")
            return {
                "rate": 1.0,
                "confidence": 0.0,
                "sources_count": 0,
                "validation": "ERROR",
                "error": str(e)
            }
    
    async def get_currency_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive currency service health report."""
        try:
            # Check database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count recent rates
            cursor.execute("""
                SELECT COUNT(*) FROM exchange_rates 
                WHERE timestamp >= datetime('now', '-1 day')
            """)
            recent_rates = cursor.fetchone()[0]
            
            # Get model count
            model_count = len(self.prediction_models)
            
            # Get cache statistics
            cache_count = len(self._cache)
            
            conn.close()
            
            return {
                "status": "HEALTHY",
                "database_status": "CONNECTED",
                "recent_rates_count": recent_rates,
                "prediction_models_count": model_count,
                "cache_entries": cache_count,
                "supported_pairs": len(self.major_pairs),
                "data_sources": len(self.data_sources) + len(self.backup_sources),
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "UNHEALTHY",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 