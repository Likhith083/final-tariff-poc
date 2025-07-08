"""
TariffCalculationEngine for ATLAS Enterprise
Real-time cost simulation using tariffs, MPF, VAT, and other fees.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.tariff import HTSCode, TariffRate, TariffCalculation
from models.country import Country
from models.exchange_rate import ExchangeRate
from core.logging import get_logger, log_business_event
from services.exchange_rate_service import ExchangeRateService

logger = get_logger(__name__)


class TariffCalculationEngine:
    """Engine for comprehensive tariff and landed cost calculations."""
    
    # MPF rates (Merchandise Processing Fee)
    MPF_RATE_FORMAL = Decimal("0.003464")  # 0.3464% for formal entries
    MPF_MIN_FORMAL = Decimal("27.23")      # Minimum MPF for formal entries
    MPF_MAX_FORMAL = Decimal("528.33")     # Maximum MPF for formal entries
    MPF_INFORMAL = Decimal("2.22")         # Fixed MPF for informal entries
    
    # Harbor Maintenance Fee
    HMF_RATE = Decimal("0.00125")          # 0.125% of cargo value
    
    @classmethod
    async def calculate_landed_cost(
        cls,
        db: AsyncSession,
        hts_code: str,
        country_code: str,
        product_value: float,
        quantity: float = 1.0,
        freight_cost: float = 0.0,
        insurance_cost: float = 0.0,
        other_costs: float = 0.0,
        currency: str = "USD",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive landed cost including all duties and fees.
        
        Args:
            db: Database session
            hts_code: HTS code for the product
            country_code: Country of origin
            product_value: FOB value of goods
            quantity: Quantity of items
            freight_cost: Shipping/freight cost
            insurance_cost: Insurance cost
            other_costs: Other additional costs
            currency: Currency of values
            user_id: User performing calculation
            
        Returns:
            Comprehensive calculation results
        """
        try:
            start_time = datetime.utcnow()
            
            # Get HTS code and tariff rate
            from .tariff_database_service import TariffDatabaseService
            
            hts_obj = await TariffDatabaseService.get_hts_code_by_code(db, hts_code)
            if not hts_obj:
                raise ValueError(f"HTS code not found: {hts_code}")
            
            # Get country
            country = await cls._get_country(db, country_code)
            if not country:
                raise ValueError(f"Country not found: {country_code}")
            
            # Get tariff rate
            tariff_rate = await cls._get_tariff_rate(db, hts_obj.id, country.id)
            if not tariff_rate:
                # Use default MFN rate of 0 if no specific rate found
                effective_rate = 0.0
                ad_rate = 0.0
                cvd_rate = 0.0
            else:
                effective_rate = tariff_rate.effective_rate
                ad_rate = tariff_rate.antidumping_duty
                cvd_rate = tariff_rate.countervailing_duty
            
            # Convert to USD if needed
            exchange_rate = 1.0
            if currency != "USD":
                exchange_rate = await ExchangeRateService.get_exchange_rate(
                    db, currency, "USD"
                )
                product_value *= exchange_rate
                freight_cost *= exchange_rate
                insurance_cost *= exchange_rate
                other_costs *= exchange_rate
            
            # Calculate using Decimal for precision
            product_val = Decimal(str(product_value))
            freight_val = Decimal(str(freight_cost))
            insurance_val = Decimal(str(insurance_cost))
            other_val = Decimal(str(other_costs))
            
            # Calculate CIF value (Cost, Insurance, Freight)
            cif_value = product_val + freight_val + insurance_val
            
            # Calculate duty
            duty_rate = Decimal(str(effective_rate / 100))  # Convert percentage to decimal
            duty_amount = cif_value * duty_rate
            
            # Calculate AD/CVD
            ad_amount = cif_value * Decimal(str(ad_rate / 100))
            cvd_amount = cif_value * Decimal(str(cvd_rate / 100))
            
            # Calculate MPF (Merchandise Processing Fee)
            mpf_amount = cls._calculate_mpf(cif_value)
            
            # Calculate HMF (Harbor Maintenance Fee) - only for seaports
            hmf_amount = cif_value * cls.HMF_RATE
            
            # Total landed cost
            total_landed_cost = (
                product_val + freight_val + insurance_val + other_val +
                duty_amount + ad_amount + cvd_amount + mpf_amount + hmf_amount
            )
            
            # Unit costs
            unit_price = product_val / Decimal(str(quantity))
            unit_landed_cost = total_landed_cost / Decimal(str(quantity))
            
            # Calculate percentages
            duty_percentage = (duty_amount / product_val * 100) if product_val > 0 else 0
            total_additional_percentage = ((total_landed_cost - product_val) / product_val * 100) if product_val > 0 else 0
            
            # Round all monetary values to 2 decimal places
            def round_decimal(val):
                return float(val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            
            result = {
                "success": True,
                "hts_code": hts_code,
                "country_code": country_code,
                "country_name": country.name,
                "input_values": {
                    "product_value": float(product_val),
                    "quantity": quantity,
                    "freight_cost": float(freight_val),
                    "insurance_cost": float(insurance_val),
                    "other_costs": float(other_val),
                    "currency": currency,
                    "exchange_rate_used": exchange_rate
                },
                "calculated_values": {
                    "cif_value": round_decimal(cif_value),
                    "duty_amount": round_decimal(duty_amount),
                    "ad_amount": round_decimal(ad_amount),
                    "cvd_amount": round_decimal(cvd_amount),
                    "mpf_amount": round_decimal(mpf_amount),
                    "hmf_amount": round_decimal(hmf_amount),
                    "total_landed_cost": round_decimal(total_landed_cost)
                },
                "unit_costs": {
                    "unit_price": round_decimal(unit_price),
                    "unit_landed_cost": round_decimal(unit_landed_cost),
                    "unit_additional_cost": round_decimal(unit_landed_cost - unit_price)
                },
                "rates_applied": {
                    "tariff_rate": effective_rate,
                    "antidumping_rate": ad_rate,
                    "countervailing_rate": cvd_rate,
                    "total_duty_rate": effective_rate + ad_rate + cvd_rate
                },
                "percentages": {
                    "duty_percentage": round_decimal(duty_percentage),
                    "total_additional_percentage": round_decimal(total_additional_percentage)
                },
                "trade_preferences": country.get_trade_preferences() if country else [],
                "calculation_metadata": {
                    "calculation_date": datetime.utcnow().isoformat(),
                    "hts_description": hts_obj.brief_description,
                    "country_risk_level": country.risk_level if country else "unknown"
                }
            }
            
            # Save calculation to database
            if user_id:
                await cls._save_calculation(
                    db, hts_obj.id, country.id, result, user_id
                )
            
            # Log business event
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            log_business_event(
                "tariff_calculation",
                user_id=str(user_id) if user_id else None,
                details={
                    "hts_code": hts_code,
                    "country": country_code,
                    "product_value": float(product_val),
                    "total_cost": round_decimal(total_landed_cost),
                    "execution_time_ms": execution_time
                }
            )
            
            logger.info(f"Calculated landed cost for {hts_code} from {country_code}: ${round_decimal(total_landed_cost)}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating landed cost: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "CALCULATION_ERROR"
            }
    
    @classmethod
    def _calculate_mpf(cls, cif_value: Decimal) -> Decimal:
        """
        Calculate Merchandise Processing Fee.
        
        Args:
            cif_value: CIF value of goods
            
        Returns:
            MPF amount
        """
        # Informal entries (under $2,500) have fixed MPF
        if cif_value < 2500:
            return cls.MPF_INFORMAL
        
        # Formal entries use percentage with min/max
        mpf = cif_value * cls.MPF_RATE_FORMAL
        
        # Apply min/max limits
        if mpf < cls.MPF_MIN_FORMAL:
            return cls.MPF_MIN_FORMAL
        elif mpf > cls.MPF_MAX_FORMAL:
            return cls.MPF_MAX_FORMAL
        
        return mpf
    
    @classmethod
    async def _get_country(cls, db: AsyncSession, country_code: str) -> Optional[Country]:
        """Get country by code."""
        from sqlalchemy import select
        
        stmt = select(Country).where(Country.code == country_code.upper())
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def _get_tariff_rate(
        cls, 
        db: AsyncSession, 
        hts_code_id: int, 
        country_id: int
    ) -> Optional[TariffRate]:
        """Get tariff rate for HTS code and country."""
        from sqlalchemy import select, and_
        
        stmt = select(TariffRate).where(
            and_(
                TariffRate.hts_code_id == hts_code_id,
                TariffRate.country_id == country_id,
                TariffRate.is_active == True
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    async def _save_calculation(
        cls,
        db: AsyncSession,
        hts_code_id: int,
        country_id: int,
        calculation_result: Dict[str, Any],
        user_id: int
    ) -> None:
        """Save calculation to database for audit trail."""
        try:
            calc_values = calculation_result["calculated_values"]
            input_values = calculation_result["input_values"]
            rates = calculation_result["rates_applied"]
            
            calculation = TariffCalculation(
                hts_code_id=hts_code_id,
                country_id=country_id,
                product_value=input_values["product_value"],
                quantity=input_values["quantity"],
                unit_price=input_values["product_value"] / input_values["quantity"],
                currency="USD",  # Always stored in USD
                freight_cost=input_values["freight_cost"],
                insurance_cost=input_values["insurance_cost"],
                other_costs=input_values["other_costs"],
                cif_value=calc_values["cif_value"],
                duty_amount=calc_values["duty_amount"],
                mpf_amount=calc_values["mpf_amount"],
                total_landed_cost=calc_values["total_landed_cost"],
                applied_tariff_rate=rates["tariff_rate"],
                applied_ad_rate=rates["antidumping_rate"],
                applied_cvd_rate=rates["countervailing_rate"],
                exchange_rate_used=input_values["exchange_rate_used"]
            )
            
            db.add(calculation)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error saving calculation: {e}")
            await db.rollback()
    
    @classmethod
    async def compare_sourcing_options(
        cls,
        db: AsyncSession,
        hts_code: str,
        product_value: float,
        countries: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compare sourcing options across multiple countries.
        
        Args:
            db: Database session
            hts_code: HTS code
            product_value: Product value
            countries: List of country codes to compare
            **kwargs: Additional calculation parameters
            
        Returns:
            Comparison results with rankings
        """
        try:
            results = []
            
            for country_code in countries:
                result = await cls.calculate_landed_cost(
                    db, hts_code, country_code, product_value, **kwargs
                )
                
                if result["success"]:
                    results.append({
                        "country_code": country_code,
                        "country_name": result["country_name"],
                        "total_cost": result["calculated_values"]["total_landed_cost"],
                        "duty_rate": result["rates_applied"]["total_duty_rate"],
                        "trade_preferences": result["trade_preferences"],
                        "risk_level": result["calculation_metadata"]["country_risk_level"],
                        "details": result
                    })
            
            # Sort by total cost (lowest first)
            results.sort(key=lambda x: x["total_cost"])
            
            # Add rankings and savings
            if results:
                baseline_cost = results[0]["total_cost"]
                for i, result in enumerate(results):
                    result["rank"] = i + 1
                    result["savings_vs_best"] = result["total_cost"] - baseline_cost
                    result["savings_percentage"] = (
                        (result["total_cost"] - baseline_cost) / baseline_cost * 100
                        if baseline_cost > 0 else 0
                    )
            
            return {
                "success": True,
                "hts_code": hts_code,
                "comparison_results": results,
                "best_option": results[0] if results else None,
                "total_countries_compared": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error comparing sourcing options: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "COMPARISON_ERROR"
            } 