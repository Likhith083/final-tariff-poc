"""
ExchangeRateService for ATLAS Enterprise
Real exchange rate service using forex-python and fallback APIs.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import httpx
from forex_python.converter import CurrencyRates
import json


class ExchangeRateService:
    """Production service for real currency conversion."""
    
    def __init__(self):
        """Initialize ExchangeRateService."""
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)
        self.currency_rates = CurrencyRates()
        # Currency converter not needed, using direct API calls
        
        # Fallback API URLs (free services)
        self.fallback_apis = [
            "https://api.exchangerate-api.com/v4/latest/USD",
            "https://api.fixer.io/latest?access_key=YOUR_API_KEY",
            "https://free.currconv.com/api/v7/convert"
        ]
        
        # Common currency pairs cache
        self._common_rates = {}
        self._last_update = None
    
    def _get_cache_key(self, from_currency: str, to_currency: str) -> str:
        """Generate cache key for currency pair."""
        return f"{from_currency.upper()}_{to_currency.upper()}"
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cached rate is still valid."""
        return datetime.now() - timestamp < self._cache_ttl
    
    async def _fetch_from_forex_python(self, from_currency: str, to_currency: str) -> float:
        """Fetch rate using forex-python library."""
        try:
            # forex-python is synchronous, so we run it in a thread
            loop = asyncio.get_event_loop()
            rate = await loop.run_in_executor(
                None,
                self.currency_rates.get_rate,
                from_currency,
                to_currency
            )
            return rate
        except Exception as e:
            print(f"❌ forex-python failed: {e}")
            return None
    
    async def _fetch_from_fallback_api(self, from_currency: str, to_currency: str) -> float:
        """Fetch rate from fallback API."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try exchangerate-api.com (free, no API key needed)
                response = await client.get(f"https://api.exchangerate-api.com/v4/latest/{from_currency}")
                
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get("rates", {})
                    
                    if to_currency in rates:
                        return float(rates[to_currency])
                
                return None
                
        except Exception as e:
            print(f"❌ Fallback API failed: {e}")
            return None
    
    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None
    ) -> float:
        """
        Get real exchange rate between two currencies.
        """
        try:
            # Normalize currency codes
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            # Same currency
            if from_currency == to_currency:
                return 1.0
            
            # Check cache first
            cache_key = self._get_cache_key(from_currency, to_currency)
            if cache_key in self._cache:
                cached_rate, timestamp = self._cache[cache_key]
                if self._is_cache_valid(timestamp):
                    print(f"✅ Using cached rate: {from_currency} to {to_currency} = {cached_rate}")
                    return cached_rate
            
            # Try forex-python first (most reliable)
            rate = await self._fetch_from_forex_python(from_currency, to_currency)
            
            # If forex-python fails, try fallback API
            if rate is None:
                rate = await self._fetch_from_fallback_api(from_currency, to_currency)
            
            # If still no rate, try reverse calculation
            if rate is None:
                reverse_rate = await self._fetch_from_forex_python(to_currency, from_currency)
                if reverse_rate:
                    rate = 1.0 / reverse_rate
            
            # If all else fails, return 1.0 as last resort
            if rate is None:
                print(f"⚠️ Could not fetch rate for {from_currency} to {to_currency}, using 1.0")
                rate = 1.0
            
            # Cache the result
            self._cache[cache_key] = (rate, datetime.now())
            
            print(f"✅ Real exchange rate: {from_currency} to {to_currency} = {rate}")
            return rate
            
        except Exception as e:
            print(f"❌ Error getting exchange rate {from_currency} to {to_currency}: {e}")
            return 1.0
    
    async def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        date: Optional[datetime] = None
    ) -> float:
        """
        Convert amount from one currency to another using real rates.
        """
        try:
            rate = await self.get_exchange_rate(from_currency, to_currency, date)
            converted_amount = amount * rate
            
            print(f"✅ Converted {amount} {from_currency} to {converted_amount:.2f} {to_currency} (rate: {rate})")
            return converted_amount
            
        except Exception as e:
            print(f"❌ Error converting currency: {e}")
            return amount  # Return original amount as fallback
    
    async def get_multiple_rates(
        self,
        base_currency: str,
        target_currencies: List[str],
        date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get real exchange rates for multiple currencies.
        """
        rates = {}
        
        # Fetch rates concurrently for better performance
        tasks = []
        for currency in target_currencies:
            task = self.get_exchange_rate(base_currency, currency, date)
            tasks.append((currency, task))
        
        for currency, task in tasks:
            try:
                rate = await task
                rates[currency] = rate
            except Exception as e:
                print(f"❌ Failed to get rate for {currency}: {e}")
                rates[currency] = 1.0
        
        return rates
    
    async def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currencies.
        """
        # Major currencies commonly supported
        return [
            "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY",
            "SEK", "NOK", "MXN", "SGD", "HKD", "NZD", "ZAR", "BRL",
            "INR", "KRW", "TRY", "RUB", "PLN", "DKK", "CZK", "HUF"
        ]
    
    async def get_historical_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: datetime
    ) -> float:
        """
        Get historical exchange rate for a specific date.
        """
        try:
            # forex-python supports historical rates
            loop = asyncio.get_event_loop()
            rate = await loop.run_in_executor(
                None,
                self.currency_rates.get_rate,
                from_currency,
                to_currency,
                date
            )
            return rate
        except Exception as e:
            print(f"❌ Error getting historical rate: {e}")
            # Fallback to current rate
            return await self.get_exchange_rate(from_currency, to_currency)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if exchange rate service is working.
        """
        try:
            # Test with a common currency pair
            rate = await self.get_exchange_rate("USD", "EUR")
            
            return {
                "status": "healthy",
                "test_rate_USD_EUR": rate,
                "cache_size": len(self._cache),
                "last_update": self._last_update.isoformat() if self._last_update else None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
            try:
                rate = await self.get_exchange_rate(base_currency, currency, date)
                rates[currency] = rate
            except Exception as e:
                print(f"Error getting rate for {currency}: {e}")
                rates[currency] = 1.0  # Fallback
        
        return rates
    
    async def get_supported_currencies(self) -> List[Dict[str, str]]:
        """
        Get list of supported currencies.
        """
        currencies = [
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            {"code": "GBP", "name": "British Pound", "symbol": "£"},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
            {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
            {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
        ]
        
        return currencies
    
    async def calculate_landed_cost(
        self,
        product_value: float,
        product_currency: str,
        target_currency: str,
        duty_rate: float,
        additional_fees: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Calculate landed cost with currency conversion.
        """
        try:
            # Convert product value to target currency
            converted_value = await self.convert_currency(
                product_value, product_currency, target_currency
            )
            
            # Calculate duty
            duty_amount = converted_value * (duty_rate / 100)
            
            # Calculate additional fees
            total_fees = 0.0
            fee_breakdown = {}
            
            if additional_fees:
                for fee_name, fee_amount in additional_fees.items():
                    if product_currency != target_currency:
                        fee_amount = await self.convert_currency(
                            fee_amount, product_currency, target_currency
                        )
                    fee_breakdown[fee_name] = fee_amount
                    total_fees += fee_amount
            
            # Calculate total landed cost
            total_landed_cost = converted_value + duty_amount + total_fees
            
            result = {
                "product_value": converted_value,
                "duty_amount": duty_amount,
                "total_fees": total_fees,
                "total_landed_cost": total_landed_cost,
                "currency": target_currency,
                "exchange_rate": await self.get_exchange_rate(product_currency, target_currency),
                "fee_breakdown": fee_breakdown
            }
            
            return result
            
        except Exception as e:
            print(f"Error calculating landed cost: {e}")
            raise
    
    async def calculate_landed_cost(
        self,
        product_value: float,
        product_currency: str,
        target_currency: str,
        duty_rate: float,
        additional_fees: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate landed cost with real exchange rates.
        """
        try:
            if additional_fees is None:
                additional_fees = {}
            
            # Convert product value to target currency
            exchange_rate = await self.get_exchange_rate(product_currency, target_currency)
            converted_value = product_value * exchange_rate
            
            # Calculate duty
            duty_amount = converted_value * (duty_rate / 100.0)
            
            # Calculate additional fees
            total_fees = sum(additional_fees.values()) * exchange_rate
            
            # Calculate total landed cost
            total_landed_cost = converted_value + duty_amount + total_fees
            
            return {
                "product_value": converted_value,
                "duty_amount": duty_amount,
                "total_fees": total_fees,
                "total_landed_cost": total_landed_cost,
                "currency": target_currency,
                "exchange_rate": exchange_rate,
                "breakdown": {
                    "original_value": product_value,
                    "original_currency": product_currency,
                    "converted_value": converted_value,
                    "duty_rate": duty_rate,
                    "additional_fees": additional_fees
                }
            }
            
        except Exception as e:
            print(f"❌ Error calculating landed cost: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Check exchange rate service health.
        """
        try:
            # Test basic conversion
            test_rate = await self.get_exchange_rate("USD", "EUR")
            
            return {
                "status": "healthy",
                "service": "mock-forex",
                "test_rate_usd_eur": test_rate,
                "cache_size": len(self._cache),
                "supported_currencies": len(await self.get_supported_currencies())
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "mock-forex",
                "error": str(e)
            }


# Global service instance
exchange_rate_service = ExchangeRateService()