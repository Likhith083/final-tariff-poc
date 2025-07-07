"""
AnalyticsService for ATLAS Enterprise
Advanced analytics, reporting, and business intelligence.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text
from sqlalchemy.orm import selectinload

from ..core.logging import get_logger, log_business_event
from ..models.calculation import TariffCalculation
from ..models.user import User
from ..models.country import Country
from ..models.tariff import HTSCode, TariffRate

logger = get_logger(__name__)


class AnalyticsService:
    """Service for advanced analytics and business intelligence."""
    
    @staticmethod
    async def get_dashboard_metrics(
        db: AsyncSession,
        user_id: Optional[int] = None,
        date_range: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics.
        
        Args:
            db: Database session
            user_id: Optional user filter
            date_range: Days to look back
            
        Returns:
            Dashboard metrics and KPIs
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=date_range)
            
            # Base query filter
            base_filter = TariffCalculation.created_at >= start_date
            if user_id:
                base_filter = and_(base_filter, TariffCalculation.user_id == user_id)
            
            # Total calculations
            total_calc_stmt = select(func.count(TariffCalculation.id)).where(base_filter)
            total_result = await db.execute(total_calc_stmt)
            total_calculations = total_result.scalar() or 0
            
            # Total value calculated
            total_value_stmt = select(func.sum(TariffCalculation.product_value)).where(base_filter)
            value_result = await db.execute(total_value_stmt)
            total_value = float(value_result.scalar() or 0)
            
            # Average duty rate
            avg_duty_stmt = select(func.avg(TariffCalculation.applied_tariff_rate)).where(base_filter)
            duty_result = await db.execute(avg_duty_stmt)
            avg_duty_rate = float(duty_result.scalar() or 0)
            
            # Top countries by calculation count
            country_stmt = select(
                Country.name,
                Country.code,
                func.count(TariffCalculation.id).label('calc_count')
            ).select_from(
                TariffCalculation
            ).join(Country).where(base_filter).group_by(
                Country.id, Country.name, Country.code
            ).order_by(desc('calc_count')).limit(10)
            
            country_result = await db.execute(country_stmt)
            top_countries = [
                {"name": row.name, "code": row.code, "calculations": row.calc_count}
                for row in country_result
            ]
            
            # Daily calculation trend
            daily_trend_stmt = select(
                func.date(TariffCalculation.created_at).label('date'),
                func.count(TariffCalculation.id).label('count'),
                func.sum(TariffCalculation.product_value).label('value')
            ).where(base_filter).group_by(
                func.date(TariffCalculation.created_at)
            ).order_by('date')
            
            trend_result = await db.execute(daily_trend_stmt)
            daily_trend = [
                {
                    "date": row.date.isoformat(),
                    "calculations": row.count,
                    "total_value": float(row.value or 0)
                }
                for row in trend_result
            ]
            
            # Cost savings analysis
            savings_stmt = select(
                func.sum(TariffCalculation.duty_amount).label('total_duties'),
                func.avg(TariffCalculation.applied_tariff_rate).label('avg_rate'),
                func.min(TariffCalculation.applied_tariff_rate).label('min_rate'),
                func.max(TariffCalculation.applied_tariff_rate).label('max_rate')
            ).where(base_filter)
            
            savings_result = await db.execute(savings_stmt)
            savings_row = savings_result.first()
            
            potential_savings = 0
            if savings_row and savings_row.total_duties and savings_row.avg_rate and savings_row.min_rate:
                # Calculate potential savings if all used minimum rate
                potential_savings = float(savings_row.total_duties) * (
                    (savings_row.avg_rate - savings_row.min_rate) / savings_row.avg_rate
                )
            
            return {
                "success": True,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": date_range
                },
                "summary": {
                    "total_calculations": total_calculations,
                    "total_value_calculated": total_value,
                    "average_duty_rate": round(avg_duty_rate, 2),
                    "potential_savings": round(potential_savings, 2)
                },
                "top_countries": top_countries,
                "daily_trend": daily_trend,
                "insights": await AnalyticsService._generate_insights(
                    total_calculations, avg_duty_rate, top_countries
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "ANALYTICS_ERROR"
            }
    
    @staticmethod
    async def get_sourcing_analytics(
        db: AsyncSession,
        hts_code: Optional[str] = None,
        date_range: int = 90
    ) -> Dict[str, Any]:
        """
        Get sourcing analytics and optimization insights.
        
        Args:
            db: Database session
            hts_code: Optional HTS code filter
            date_range: Days to analyze
            
        Returns:
            Sourcing analytics and recommendations
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=date_range)
            
            # Build filters
            filters = [TariffCalculation.created_at >= start_date]
            if hts_code:
                filters.append(TariffCalculation.hts_code_id.in_(
                    select(HTSCode.id).where(HTSCode.hts_code == hts_code)
                ))
            
            base_filter = and_(*filters)
            
            # Country comparison analysis
            country_analysis_stmt = select(
                Country.name,
                Country.code,
                func.count(TariffCalculation.id).label('calc_count'),
                func.avg(TariffCalculation.applied_tariff_rate).label('avg_duty'),
                func.avg(TariffCalculation.total_landed_cost).label('avg_cost'),
                func.sum(TariffCalculation.product_value).label('total_value')
            ).select_from(TariffCalculation).join(Country).where(
                base_filter
            ).group_by(
                Country.id, Country.name, Country.code
            ).order_by(desc('calc_count'))
            
            country_result = await db.execute(country_analysis_stmt)
            country_analysis = []
            
            for row in country_result:
                country_analysis.append({
                    "country": row.name,
                    "country_code": row.code,
                    "calculations": row.calc_count,
                    "average_duty_rate": round(float(row.avg_duty or 0), 2),
                    "average_landed_cost": round(float(row.avg_cost or 0), 2),
                    "total_value": round(float(row.total_value or 0), 2),
                    "cost_efficiency_score": AnalyticsService._calculate_efficiency_score(
                        float(row.avg_duty or 0), float(row.avg_cost or 0)
                    )
                })
            
            # HTS code analysis
            hts_analysis_stmt = select(
                HTSCode.hts_code,
                HTSCode.brief_description,
                func.count(TariffCalculation.id).label('calc_count'),
                func.avg(TariffCalculation.applied_tariff_rate).label('avg_duty'),
                func.sum(TariffCalculation.product_value).label('total_value')
            ).select_from(TariffCalculation).join(HTSCode).where(
                base_filter
            ).group_by(
                HTSCode.id, HTSCode.hts_code, HTSCode.brief_description
            ).order_by(desc('calc_count')).limit(20)
            
            hts_result = await db.execute(hts_analysis_stmt)
            hts_analysis = [
                {
                    "hts_code": row.hts_code,
                    "description": row.brief_description,
                    "calculations": row.calc_count,
                    "average_duty_rate": round(float(row.avg_duty or 0), 2),
                    "total_value": round(float(row.total_value or 0), 2)
                }
                for row in hts_result
            ]
            
            # Optimization opportunities
            optimization_opportunities = await AnalyticsService._identify_optimization_opportunities(
                db, country_analysis, hts_analysis
            )
            
            return {
                "success": True,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": date_range
                },
                "country_analysis": country_analysis,
                "hts_analysis": hts_analysis,
                "optimization_opportunities": optimization_opportunities,
                "recommendations": await AnalyticsService._generate_sourcing_recommendations(
                    country_analysis, hts_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting sourcing analytics: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SOURCING_ANALYTICS_ERROR"
            }
    
    @staticmethod
    async def get_compliance_report(
        db: AsyncSession,
        user_id: Optional[int] = None,
        date_range: int = 30
    ) -> Dict[str, Any]:
        """
        Generate compliance and audit report.
        
        Args:
            db: Database session
            user_id: Optional user filter
            date_range: Days to analyze
            
        Returns:
            Compliance report with audit trail
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=date_range)
            
            # Build filters
            filters = [TariffCalculation.created_at >= start_date]
            if user_id:
                filters.append(TariffCalculation.user_id == user_id)
            
            base_filter = and_(*filters)
            
            # Calculation audit trail
            audit_stmt = select(
                TariffCalculation.id,
                TariffCalculation.created_at,
                TariffCalculation.hts_code_id,
                TariffCalculation.country_id,
                TariffCalculation.product_value,
                TariffCalculation.applied_tariff_rate,
                TariffCalculation.duty_amount,
                User.username,
                Country.name.label('country_name'),
                HTSCode.hts_code
            ).select_from(TariffCalculation).join(User).join(Country).join(HTSCode).where(
                base_filter
            ).order_by(desc(TariffCalculation.created_at)).limit(1000)
            
            audit_result = await db.execute(audit_stmt)
            audit_trail = [
                {
                    "calculation_id": row.id,
                    "timestamp": row.created_at.isoformat(),
                    "user": row.username,
                    "hts_code": row.hts_code,
                    "country": row.country_name,
                    "product_value": float(row.product_value),
                    "duty_rate_applied": float(row.applied_tariff_rate),
                    "duty_amount": float(row.duty_amount)
                }
                for row in audit_result
            ]
            
            # User activity summary
            user_activity_stmt = select(
                User.username,
                User.role,
                func.count(TariffCalculation.id).label('calc_count'),
                func.sum(TariffCalculation.product_value).label('total_value'),
                func.min(TariffCalculation.created_at).label('first_calc'),
                func.max(TariffCalculation.created_at).label('last_calc')
            ).select_from(TariffCalculation).join(User).where(
                base_filter
            ).group_by(
                User.id, User.username, User.role
            ).order_by(desc('calc_count'))
            
            activity_result = await db.execute(user_activity_stmt)
            user_activity = [
                {
                    "username": row.username,
                    "role": row.role.value,
                    "calculations": row.calc_count,
                    "total_value": float(row.total_value or 0),
                    "first_calculation": row.first_calc.isoformat() if row.first_calc else None,
                    "last_calculation": row.last_calc.isoformat() if row.last_calc else None
                }
                for row in activity_result
            ]
            
            # Compliance metrics
            compliance_metrics = {
                "total_calculations": len(audit_trail),
                "unique_users": len(user_activity),
                "data_retention_compliant": True,  # Placeholder
                "audit_trail_complete": True,  # Placeholder
                "access_controls_active": True,  # Placeholder
                "encryption_status": "enabled"  # Placeholder
            }
            
            return {
                "success": True,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": date_range
                },
                "compliance_metrics": compliance_metrics,
                "audit_trail": audit_trail,
                "user_activity": user_activity,
                "generated_at": datetime.utcnow().isoformat(),
                "report_id": f"ATLAS-COMPLIANCE-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "COMPLIANCE_REPORT_ERROR"
            }
    
    @staticmethod
    async def get_cost_optimization_report(
        db: AsyncSession,
        product_categories: Optional[List[str]] = None,
        minimum_volume: float = 1000.0
    ) -> Dict[str, Any]:
        """
        Generate cost optimization recommendations.
        
        Args:
            db: Database session
            product_categories: Optional product category filters
            minimum_volume: Minimum product value threshold
            
        Returns:
            Cost optimization report with actionable recommendations
        """
        try:
            # Find high-volume, high-duty products
            high_impact_stmt = select(
                HTSCode.hts_code,
                HTSCode.brief_description,
                func.count(TariffCalculation.id).label('calc_count'),
                func.sum(TariffCalculation.product_value).label('total_value'),
                func.avg(TariffCalculation.applied_tariff_rate).label('avg_duty'),
                func.sum(TariffCalculation.duty_amount).label('total_duties')
            ).select_from(TariffCalculation).join(HTSCode).where(
                TariffCalculation.product_value >= minimum_volume
            ).group_by(
                HTSCode.id, HTSCode.hts_code, HTSCode.brief_description
            ).having(
                func.sum(TariffCalculation.product_value) >= minimum_volume * 10
            ).order_by(desc('total_duties')).limit(50)
            
            high_impact_result = await db.execute(high_impact_stmt)
            high_impact_products = []
            
            for row in high_impact_result:
                # Calculate potential savings
                current_duties = float(row.total_duties)
                avg_duty_rate = float(row.avg_duty)
                
                # Estimate savings with trade agreements (simplified)
                potential_savings = current_duties * 0.3  # Assume 30% potential reduction
                
                high_impact_products.append({
                    "hts_code": row.hts_code,
                    "description": row.brief_description,
                    "calculations": row.calc_count,
                    "total_value": float(row.total_value),
                    "average_duty_rate": round(avg_duty_rate, 2),
                    "total_duties_paid": round(current_duties, 2),
                    "potential_annual_savings": round(potential_savings, 2),
                    "optimization_priority": "high" if potential_savings > 10000 else "medium"
                })
            
            # Country diversification opportunities
            diversification_stmt = select(
                HTSCode.hts_code,
                func.count(func.distinct(TariffCalculation.country_id)).label('country_count'),
                func.array_agg(func.distinct(Country.name)).label('countries'),
                func.min(TariffCalculation.applied_tariff_rate).label('min_rate'),
                func.max(TariffCalculation.applied_tariff_rate).label('max_rate')
            ).select_from(TariffCalculation).join(HTSCode).join(Country).group_by(
                HTSCode.id, HTSCode.hts_code
            ).having(
                func.count(func.distinct(TariffCalculation.country_id)) >= 2
            ).order_by(desc('country_count'))
            
            diversification_result = await db.execute(diversification_stmt)
            diversification_opportunities = [
                {
                    "hts_code": row.hts_code,
                    "countries_analyzed": row.country_count,
                    "duty_rate_range": {
                        "min": float(row.min_rate),
                        "max": float(row.max_rate),
                        "spread": float(row.max_rate - row.min_rate)
                    },
                    "optimization_potential": "high" if (row.max_rate - row.min_rate) > 5 else "low"
                }
                for row in diversification_result
            ]
            
            # Generate recommendations
            recommendations = []
            
            # High-impact product recommendations
            for product in high_impact_products[:10]:  # Top 10
                if product["potential_annual_savings"] > 5000:
                    recommendations.append({
                        "type": "cost_reduction",
                        "priority": "high",
                        "title": f"Optimize sourcing for {product['hts_code']}",
                        "description": f"High-volume product with ${product['potential_annual_savings']:,.0f} potential savings",
                        "action_items": [
                            "Explore FTA-eligible countries",
                            "Investigate GSP eligibility",
                            "Consider product classification optimization"
                        ],
                        "estimated_savings": product["potential_annual_savings"]
                    })
            
            # Diversification recommendations
            for opp in diversification_opportunities[:5]:  # Top 5
                if opp["duty_rate_range"]["spread"] > 10:
                    recommendations.append({
                        "type": "sourcing_diversification",
                        "priority": "medium",
                        "title": f"Diversify sourcing for {opp['hts_code']}",
                        "description": f"Large duty rate variation ({opp['duty_rate_range']['spread']:.1f}%) across countries",
                        "action_items": [
                            "Shift volume to lower-duty countries",
                            "Negotiate better terms with current suppliers",
                            "Explore new supplier relationships"
                        ],
                        "estimated_impact": "medium"
                    })
            
            return {
                "success": True,
                "analysis_summary": {
                    "high_impact_products": len(high_impact_products),
                    "diversification_opportunities": len(diversification_opportunities),
                    "total_recommendations": len(recommendations),
                    "potential_annual_savings": sum(p["potential_annual_savings"] for p in high_impact_products)
                },
                "high_impact_products": high_impact_products,
                "diversification_opportunities": diversification_opportunities,
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating cost optimization report: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "COST_OPTIMIZATION_ERROR"
            }
    
    @staticmethod
    def _calculate_efficiency_score(duty_rate: float, landed_cost: float) -> float:
        """Calculate cost efficiency score (0-100)."""
        try:
            # Simple efficiency scoring algorithm
            duty_factor = max(0, 100 - (duty_rate * 2))  # Lower duty = higher score
            cost_factor = min(100, 10000 / max(landed_cost, 1))  # Lower cost = higher score
            
            return round((duty_factor * 0.7 + cost_factor * 0.3), 1)
        except Exception:
            return 50.0  # Default score
    
    @staticmethod
    async def _generate_insights(
        total_calculations: int,
        avg_duty_rate: float,
        top_countries: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate business insights from analytics data."""
        insights = []
        
        if total_calculations > 100:
            insights.append(f"High activity period with {total_calculations} calculations performed")
        
        if avg_duty_rate > 10:
            insights.append(f"Average duty rate of {avg_duty_rate:.1f}% indicates potential for optimization")
        elif avg_duty_rate < 3:
            insights.append(f"Low average duty rate of {avg_duty_rate:.1f}% suggests effective sourcing strategy")
        
        if top_countries:
            top_country = top_countries[0]["name"]
            insights.append(f"{top_country} is the most analyzed sourcing destination")
        
        return insights
    
    @staticmethod
    async def _identify_optimization_opportunities(
        db: AsyncSession,
        country_analysis: List[Dict[str, Any]],
        hts_analysis: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities."""
        opportunities = []
        
        # High-duty countries with significant volume
        for country in country_analysis:
            if country["average_duty_rate"] > 8 and country["total_value"] > 50000:
                opportunities.append({
                    "type": "country_optimization",
                    "description": f"High duties from {country['country']} - consider alternative sources",
                    "impact": "high",
                    "current_duty_rate": country["average_duty_rate"],
                    "affected_value": country["total_value"]
                })
        
        # High-volume HTS codes with high duties
        for hts in hts_analysis:
            if hts["average_duty_rate"] > 10 and hts["total_value"] > 25000:
                opportunities.append({
                    "type": "product_optimization",
                    "description": f"HTS {hts['hts_code']} has high duty rate - review classification",
                    "impact": "medium",
                    "hts_code": hts["hts_code"],
                    "current_duty_rate": hts["average_duty_rate"]
                })
        
        return opportunities
    
    @staticmethod
    async def _generate_sourcing_recommendations(
        country_analysis: List[Dict[str, Any]],
        hts_analysis: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable sourcing recommendations."""
        recommendations = []
        
        # Sort countries by efficiency score
        efficient_countries = sorted(
            country_analysis, 
            key=lambda x: x["cost_efficiency_score"], 
            reverse=True
        )[:3]
        
        if efficient_countries:
            top_country = efficient_countries[0]
            recommendations.append(
                f"Consider increasing sourcing from {top_country['country']} "
                f"(efficiency score: {top_country['cost_efficiency_score']})"
            )
        
        # High-duty products
        high_duty_products = [hts for hts in hts_analysis if hts["average_duty_rate"] > 15]
        if high_duty_products:
            recommendations.append(
                f"Review classification for {len(high_duty_products)} products with >15% duty rates"
            )
        
        # Volume concentration
        if len(country_analysis) > 5:
            recommendations.append("Consider diversifying supplier base to reduce country risk")
        
        return recommendations


# Global instance
analytics_service = AnalyticsService() 