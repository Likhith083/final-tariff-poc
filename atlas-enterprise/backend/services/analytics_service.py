"""
Advanced Analytics Service for ATLAS Enterprise
Business intelligence, predictive analytics, and performance monitoring.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

from ..core.database import get_cache, get_session
from ..core.logging import get_logger, log_business_event
from ..core.config import settings
from .enhanced_exchange_rate_service import EnhancedExchangeRateService

logger = get_logger(__name__)


class MetricType(Enum):
    """Types of metrics for analytics."""
    USAGE = "usage"
    PERFORMANCE = "performance"
    FINANCIAL = "financial"
    COMPLIANCE = "compliance"
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_HEALTH = "system_health"


class AnalyticsGranularity(Enum):
    """Time granularity for analytics."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class AnalyticsResult:
    """Analytics query result."""
    metric: str
    data: List[Dict[str, Any]]
    aggregations: Dict[str, float]
    trend: Dict[str, Any]
    insights: List[str]
    chart_data: Optional[Dict[str, Any]] = None
    prediction: Optional[Dict[str, Any]] = None


class AnalyticsService:
    """Advanced analytics and business intelligence service."""
    
    def __init__(self):
        """Initialize analytics service."""
        self.cache = None
        self.exchange_service = None
        self._initialized = False
        
        # Predefined metrics and their configurations
        self.metrics_config = {
            "api_requests": {
                "type": MetricType.USAGE,
                "description": "API request volume",
                "unit": "requests",
                "chart_type": "line"
            },
            "calculation_volume": {
                "type": MetricType.USAGE,
                "description": "Tariff calculations performed",
                "unit": "calculations",
                "chart_type": "bar"
            },
            "response_time": {
                "type": MetricType.PERFORMANCE,
                "description": "Average API response time",
                "unit": "milliseconds",
                "chart_type": "line"
            },
            "cost_savings": {
                "type": MetricType.FINANCIAL,
                "description": "Estimated cost savings from platform use",
                "unit": "USD",
                "chart_type": "area"
            },
            "compliance_score": {
                "type": MetricType.COMPLIANCE,
                "description": "Overall compliance rating",
                "unit": "percentage",
                "chart_type": "gauge"
            },
            "user_engagement": {
                "type": MetricType.USER_BEHAVIOR,
                "description": "User activity and engagement",
                "unit": "score",
                "chart_type": "line"
            },
            "currency_volatility": {
                "type": MetricType.FINANCIAL,
                "description": "Exchange rate volatility index",
                "unit": "index",
                "chart_type": "line"
            },
            "knowledge_base_growth": {
                "type": MetricType.USAGE,
                "description": "Knowledge base document count",
                "unit": "documents",
                "chart_type": "bar"
            }
        }
    
    async def initialize(self):
        """Initialize the analytics service."""
        if self._initialized:
            return
        
        self.cache = get_cache()
        self.exchange_service = EnhancedExchangeRateService()
        self._initialized = True
        logger.info("Analytics service initialized")
    
    async def query_metric(self, metric: str, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None, filters: Optional[Dict[str, Any]] = None,
                          granularity: str = "day", user_id: Optional[str] = None) -> AnalyticsResult:
        """Query a specific metric with optional filters."""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Check cache first
            cache_key = f"analytics:{metric}:{start_date.date()}:{end_date.date()}:{granularity}:{user_id}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return AnalyticsResult(**cached_result)
            
            # Generate metric data based on metric type
            if metric in self.metrics_config:
                data = await self._generate_metric_data(
                    metric, start_date, end_date, granularity, filters, user_id
                )
            else:
                raise ValueError(f"Unknown metric: {metric}")
            
            # Calculate aggregations
            aggregations = self._calculate_aggregations(data)
            
            # Analyze trends
            trend = self._analyze_trend(data)
            
            # Generate insights
            insights = await self._generate_insights(metric, data, aggregations, trend)
            
            # Create chart data
            chart_data = self._create_chart_data(metric, data, granularity)
            
            # Generate predictions if applicable
            prediction = None
            if len(data) >= 7:  # Need minimum data points for prediction
                prediction = await self._generate_prediction(metric, data)
            
            result = AnalyticsResult(
                metric=metric,
                data=data,
                aggregations=aggregations,
                trend=trend,
                insights=insights,
                chart_data=chart_data,
                prediction=prediction
            )
            
            # Cache result for 1 hour
            await self.cache.set(cache_key, result.__dict__, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Analytics query failed for metric {metric}: {e}")
            raise
    
    async def get_dashboard_data(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        try:
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": {},
                "charts": {},
                "kpis": {},
                "alerts": []
            }
            
            # Key metrics for dashboard
            key_metrics = [
                "api_requests",
                "calculation_volume", 
                "response_time",
                "cost_savings",
                "compliance_score"
            ]
            
            # Fetch data for each metric
            for metric in key_metrics:
                try:
                    result = await self.query_metric(
                        metric=metric,
                        start_date=datetime.now() - timedelta(days=7),
                        granularity="day",
                        user_id=user_id
                    )
                    
                    dashboard_data["summary"][metric] = {
                        "current_value": result.aggregations.get("latest", 0),
                        "trend": result.trend.get("direction", "stable"),
                        "change_percent": result.trend.get("change_percent", 0)
                    }
                    
                    dashboard_data["charts"][metric] = result.chart_data
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch dashboard metric {metric}: {e}")
                    dashboard_data["summary"][metric] = {"error": str(e)}
            
            # Calculate KPIs
            dashboard_data["kpis"] = await self._calculate_kpis(user_id)
            
            # Check for alerts
            dashboard_data["alerts"] = await self._check_alerts(user_id)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def get_predictive_analytics(self, metric: str, days_ahead: int = 30,
                                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get predictive analytics for a specific metric."""
        try:
            # Get historical data
            start_date = datetime.now() - timedelta(days=90)  # 90 days of history
            end_date = datetime.now()
            
            result = await self.query_metric(
                metric=metric,
                start_date=start_date,
                end_date=end_date,
                granularity="day",
                user_id=user_id
            )
            
            if len(result.data) < 14:
                return {
                    "error": "Insufficient historical data for prediction",
                    "required_days": 14,
                    "available_days": len(result.data)
                }
            
            # Generate detailed prediction
            prediction = await self._generate_detailed_prediction(
                metric, result.data, days_ahead
            )
            
            return {
                "metric": metric,
                "prediction_horizon": days_ahead,
                "prediction": prediction,
                "confidence_intervals": prediction.get("confidence_intervals"),
                "model_performance": prediction.get("model_performance"),
                "key_drivers": prediction.get("key_drivers", [])
            }
            
        except Exception as e:
            logger.error(f"Predictive analytics failed for {metric}: {e}")
            return {"error": str(e)}
    
    async def _generate_metric_data(self, metric: str, start_date: datetime,
                                  end_date: datetime, granularity: str,
                                  filters: Optional[Dict[str, Any]],
                                  user_id: Optional[str]) -> List[Dict[str, Any]]:
        """Generate metric data based on metric type."""
        data = []
        
        # Generate time series based on granularity
        if granularity == "hour":
            time_delta = timedelta(hours=1)
        elif granularity == "day":
            time_delta = timedelta(days=1)
        elif granularity == "week":
            time_delta = timedelta(weeks=1)
        elif granularity == "month":
            time_delta = timedelta(days=30)
        else:
            time_delta = timedelta(days=1)
        
        current_date = start_date
        while current_date <= end_date:
            
            if metric == "api_requests":
                # Simulate API request volume with some seasonality
                base_value = 1000
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * current_date.hour / 24)
                random_factor = 1 + np.random.normal(0, 0.1)
                value = int(base_value * seasonal_factor * random_factor)
                
            elif metric == "calculation_volume":
                # Business hours pattern
                if 9 <= current_date.hour <= 17:
                    base_value = 500
                else:
                    base_value = 100
                value = int(base_value * (1 + np.random.normal(0, 0.2)))
                
            elif metric == "response_time":
                # Response time with occasional spikes
                base_time = 150  # ms
                spike_probability = 0.05
                if np.random.random() < spike_probability:
                    value = base_time * (3 + np.random.random() * 2)
                else:
                    value = base_time * (1 + np.random.normal(0, 0.1))
                value = max(50, value)  # Minimum 50ms
                
            elif metric == "cost_savings":
                # Cumulative cost savings
                daily_savings = 500 + np.random.normal(0, 100)
                value = max(0, daily_savings)
                
            elif metric == "compliance_score":
                # Compliance score between 80-100%
                value = 85 + 10 * np.random.beta(2, 1) + np.random.normal(0, 2)
                value = max(0, min(100, value))
                
            elif metric == "user_engagement":
                # User engagement score
                base_score = 75
                weekly_cycle = 1 + 0.2 * np.sin(2 * np.pi * current_date.weekday() / 7)
                value = base_score * weekly_cycle * (1 + np.random.normal(0, 0.1))
                
            elif metric == "currency_volatility":
                # Currency volatility index
                value = 0.5 + 0.3 * np.random.random() + 0.1 * np.sin(current_date.timestamp() / 86400)
                
            elif metric == "knowledge_base_growth":
                # Steady growth with occasional content additions
                growth_rate = 2 + np.random.poisson(1)
                value = growth_rate
                
            else:
                value = np.random.normal(100, 20)
            
            data.append({
                "timestamp": current_date.isoformat(),
                "value": round(value, 2),
                "date": current_date.strftime("%Y-%m-%d"),
                "hour": current_date.hour if granularity == "hour" else None
            })
            
            current_date += time_delta
        
        return data
    
    def _calculate_aggregations(self, data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate aggregations for the data."""
        values = [d["value"] for d in data]
        
        if not values:
            return {}
        
        return {
            "sum": sum(values),
            "average": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1] if values else 0,
            "first": values[0] if values else 0,
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "count": len(values)
        }
    
    def _analyze_trend(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trend in the data."""
        if len(data) < 2:
            return {"direction": "insufficient_data"}
        
        values = [d["value"] for d in data]
        
        # Simple linear trend
        x = list(range(len(values)))
        slope = np.polyfit(x, values, 1)[0]
        
        # Calculate percent change
        first_value = values[0]
        last_value = values[-1]
        change_percent = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        
        # Determine direction
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        return {
            "direction": direction,
            "slope": slope,
            "change_percent": round(change_percent, 2),
            "volatility": statistics.stdev(values) if len(values) > 1 else 0
        }
    
    async def _generate_insights(self, metric: str, data: List[Dict[str, Any]],
                               aggregations: Dict[str, float], trend: Dict[str, Any]) -> List[str]:
        """Generate insights based on the analytics data."""
        insights = []
        
        # Trend-based insights
        if trend["direction"] == "increasing":
            insights.append(f"{metric.replace('_', ' ').title()} is trending upward with a {trend['change_percent']:.1f}% increase")
        elif trend["direction"] == "decreasing":
            insights.append(f"{metric.replace('_', ' ').title()} is trending downward with a {trend['change_percent']:.1f}% decrease")
        else:
            insights.append(f"{metric.replace('_', ' ').title()} has remained relatively stable")
        
        # Volatility insights
        if trend.get("volatility", 0) > aggregations.get("average", 0) * 0.5:
            insights.append("High volatility detected - consider investigating underlying causes")
        
        # Performance insights based on metric type
        if metric == "response_time":
            avg_time = aggregations.get("average", 0)
            if avg_time > 500:
                insights.append("Response times are above optimal threshold (>500ms)")
            elif avg_time < 200:
                insights.append("Excellent response time performance (<200ms)")
        
        elif metric == "compliance_score":
            score = aggregations.get("average", 0)
            if score > 95:
                insights.append("Excellent compliance performance maintained")
            elif score < 85:
                insights.append("Compliance score below target - review may be needed")
        
        elif metric == "cost_savings":
            total_savings = aggregations.get("sum", 0)
            insights.append(f"Total estimated cost savings: ${total_savings:,.2f}")
        
        return insights
    
    def _create_chart_data(self, metric: str, data: List[Dict[str, Any]], granularity: str) -> Dict[str, Any]:
        """Create chart data for visualization."""
        try:
            config = self.metrics_config.get(metric, {})
            chart_type = config.get("chart_type", "line")
            
            # Prepare data for chart
            timestamps = [d["timestamp"] for d in data]
            values = [d["value"] for d in data]
            
            if chart_type == "line":
                chart = go.Figure()
                chart.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=metric.replace('_', ' ').title(),
                    line=dict(color='#1f77b4', width=2),
                    marker=dict(size=4)
                ))
                
            elif chart_type == "bar":
                chart = go.Figure()
                chart.add_trace(go.Bar(
                    x=timestamps,
                    y=values,
                    name=metric.replace('_', ' ').title(),
                    marker_color='#1f77b4'
                ))
                
            elif chart_type == "area":
                chart = go.Figure()
                chart.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    fill='tonexty',
                    mode='lines',
                    name=metric.replace('_', ' ').title(),
                    line=dict(color='#1f77b4')
                ))
            
            else:  # Default to line
                chart = go.Figure()
                chart.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines',
                    name=metric.replace('_', ' ').title()
                ))
            
            # Update layout
            chart.update_layout(
                title=f"{metric.replace('_', ' ').title()} Over Time",
                xaxis_title="Time",
                yaxis_title=config.get("unit", "Value"),
                hovermode='x unified',
                template='plotly_white'
            )
            
            return json.loads(json.dumps(chart, cls=PlotlyJSONEncoder))
            
        except Exception as e:
            logger.error(f"Chart creation failed: {e}")
            return {"error": str(e)}
    
    async def _generate_prediction(self, metric: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate simple prediction for metric."""
        try:
            values = [d["value"] for d in data]
            
            # Simple linear regression prediction
            X = np.array(range(len(values))).reshape(-1, 1)
            y = np.array(values)
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next 7 days
            future_X = np.array(range(len(values), len(values) + 7)).reshape(-1, 1)
            predictions = model.predict(future_X)
            
            # Calculate model performance
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            return {
                "model_type": "linear_regression",
                "next_7_days": predictions.tolist(),
                "r2_score": r2,
                "mean_absolute_error": mae,
                "confidence": min(max(r2, 0), 1)  # Clamp between 0 and 1
            }
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return {"error": str(e)}
    
    async def _generate_detailed_prediction(self, metric: str, data: List[Dict[str, Any]], 
                                          days_ahead: int) -> Dict[str, Any]:
        """Generate detailed prediction with confidence intervals."""
        try:
            values = [d["value"] for d in data]
            
            # Create features (time index, day of week, etc.)
            X = []
            for i, d in enumerate(data):
                timestamp = datetime.fromisoformat(d["timestamp"])
                features = [
                    i,  # Time index
                    timestamp.weekday(),  # Day of week
                    timestamp.hour if "hour" in d else 12,  # Hour of day
                    np.sin(2 * np.pi * timestamp.weekday() / 7),  # Weekly cycle
                    np.cos(2 * np.pi * timestamp.weekday() / 7),
                ]
                X.append(features)
            
            X = np.array(X)
            y = np.array(values)
            
            # Train Random Forest for better prediction with uncertainty
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Generate future features
            future_X = []
            last_timestamp = datetime.fromisoformat(data[-1]["timestamp"])
            
            for i in range(days_ahead):
                future_time = last_timestamp + timedelta(days=i+1)
                features = [
                    len(data) + i,  # Time index
                    future_time.weekday(),
                    12,  # Default hour
                    np.sin(2 * np.pi * future_time.weekday() / 7),
                    np.cos(2 * np.pi * future_time.weekday() / 7),
                ]
                future_X.append(features)
            
            future_X = np.array(future_X)
            
            # Generate predictions with uncertainty
            predictions = []
            for estimator in model.estimators_:
                pred = estimator.predict(future_X)
                predictions.append(pred)
            
            predictions = np.array(predictions)
            
            # Calculate confidence intervals
            mean_pred = np.mean(predictions, axis=0)
            std_pred = np.std(predictions, axis=0)
            
            lower_bound = mean_pred - 1.96 * std_pred
            upper_bound = mean_pred + 1.96 * std_pred
            
            # Model performance
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            
            return {
                "model_type": "random_forest",
                "predictions": mean_pred.tolist(),
                "confidence_intervals": {
                    "lower": lower_bound.tolist(),
                    "upper": upper_bound.tolist(),
                    "confidence_level": 0.95
                },
                "model_performance": {
                    "r2_score": r2,
                    "mean_absolute_error": mae,
                    "feature_importance": model.feature_importances_.tolist()
                },
                "key_drivers": [
                    "Time trend",
                    "Day of week",
                    "Hour of day",
                    "Weekly seasonality"
                ]
            }
            
        except Exception as e:
            logger.error(f"Detailed prediction failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_kpis(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Calculate key performance indicators."""
        try:
            # This would calculate real KPIs based on actual data
            return {
                "system_uptime": 99.8,
                "user_satisfaction": 4.5,
                "cost_efficiency": 85.2,
                "automation_rate": 78.5,
                "data_accuracy": 96.7
            }
        except Exception as e:
            logger.error(f"KPI calculation failed: {e}")
            return {}
    
    async def _check_alerts(self, user_id: Optional[str]) -> List[Dict[str, Any]]:
        """Check for system alerts and anomalies."""
        try:
            alerts = []
            
            # Example alert conditions
            # In production, these would be based on real data and thresholds
            
            # Performance alert
            alerts.append({
                "type": "performance",
                "severity": "warning",
                "message": "API response time increased by 15% in the last hour",
                "timestamp": datetime.now().isoformat(),
                "metric": "response_time"
            })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Alert checking failed: {e}")
            return []
    
    async def export_analytics_report(self, metrics: List[str], start_date: datetime,
                                    end_date: datetime, format: str = "json") -> Dict[str, Any]:
        """Export comprehensive analytics report."""
        try:
            report = {
                "report_id": f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "metrics": {}
            }
            
            for metric in metrics:
                try:
                    result = await self.query_metric(
                        metric=metric,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    report["metrics"][metric] = {
                        "data": result.data,
                        "aggregations": result.aggregations,
                        "trend": result.trend,
                        "insights": result.insights
                    }
                    
                except Exception as e:
                    report["metrics"][metric] = {"error": str(e)}
            
            return report
            
        except Exception as e:
            logger.error(f"Analytics report export failed: {e}")
            return {"error": str(e)}


# Global analytics service instance
analytics_service = AnalyticsService() 