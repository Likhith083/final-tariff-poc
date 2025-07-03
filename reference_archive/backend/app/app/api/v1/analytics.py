"""
Analytics API endpoints for TariffAI
Provides analytics data for the dashboard and charts
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics data"""
    try:
        # Simulate analytics data - in a real implementation, this would come from a database
        analytics_data = {
            "searches": {
                "total": random.randint(1000, 2000),
                "today": random.randint(20, 80)
            },
            "calculations": {
                "total": random.randint(800, 1500),
                "avg_rate": round(random.uniform(5.0, 15.0), 1)
            },
            "assessments": {
                "total": random.randint(500, 1000),
                "high_risk": random.randint(15, 50)
            },
            "scenarios": {
                "total": random.randint(200, 500),
                "saved": random.randint(50, 150)
            },
            "duty_rates": [
                {"range": "0%", "count": random.randint(100, 200)},
                {"range": "1-5%", "count": random.randint(200, 300)},
                {"range": "6-15%", "count": random.randint(150, 250)},
                {"range": "16%+", "count": random.randint(50, 100)}
            ],
            "categories": [
                {"name": "Electronics", "count": random.randint(200, 300)},
                {"name": "Textiles", "count": random.randint(150, 250)},
                {"name": "Machinery", "count": random.randint(100, 200)},
                {"name": "Chemicals", "count": random.randint(80, 150)},
                {"name": "Steel", "count": random.randint(60, 120)}
            ],
            "trends": generate_trend_data(),
            "countries": [
                {"name": "China", "count": random.randint(400, 600)},
                {"name": "Mexico", "count": random.randint(200, 350)},
                {"name": "Canada", "count": random.randint(150, 250)},
                {"name": "Germany", "count": random.randint(100, 180)},
                {"name": "Japan", "count": random.randint(80, 150)}
            ],
            "risks": [
                {"level": "Low", "count": random.randint(200, 300)},
                {"level": "Medium", "count": random.randint(120, 200)},
                {"level": "High", "count": random.randint(50, 100)}
            ]
        }
        
        return {
            "success": True,
            "data": analytics_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

@router.get("/trends/{period}")
async def get_trend_analytics(period: int):
    """Get trend analytics data for specified period (days)"""
    try:
        if period not in [7, 30, 90]:
            raise HTTPException(status_code=400, detail="Period must be 7, 30, or 90 days")
        
        trends = generate_trend_data(period)
        
        return {
            "success": True,
            "data": trends,
            "period": period
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analytics error: {str(e)}")

@router.post("/export")
async def export_analytics_data(export_type: str = "json"):
    """Export analytics data in various formats"""
    try:
        analytics_data = await get_dashboard_analytics()
        
        if export_type == "json":
            return {
                "success": True,
                "data": analytics_data["data"],
                "format": "json",
                "timestamp": datetime.now().isoformat()
            }
        elif export_type == "csv":
            # Convert to CSV format
            csv_data = convert_to_csv(analytics_data["data"])
            return {
                "success": True,
                "data": csv_data,
                "format": "csv",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

def generate_trend_data(days: int = 7) -> List[Dict[str, Any]]:
    """Generate trend data for the specified number of days"""
    trends = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "searches": random.randint(40, 80),
            "calculations": random.randint(30, 60),
            "assessments": random.randint(20, 40)
        })
    
    return trends

def convert_to_csv(data: Dict[str, Any]) -> str:
    """Convert analytics data to CSV format"""
    csv_lines = []
    
    # Add summary data
    csv_lines.append("Metric,Value")
    csv_lines.append(f"Total Searches,{data['searches']['total']}")
    csv_lines.append(f"Today Searches,{data['searches']['today']}")
    csv_lines.append(f"Total Calculations,{data['calculations']['total']}")
    csv_lines.append(f"Average Duty Rate,{data['calculations']['avg_rate']}%")
    csv_lines.append(f"Total Assessments,{data['assessments']['total']}")
    csv_lines.append(f"High Risk Items,{data['assessments']['high_risk']}")
    csv_lines.append(f"Total Scenarios,{data['scenarios']['total']}")
    csv_lines.append(f"Saved Scenarios,{data['scenarios']['saved']}")
    
    # Add duty rates
    csv_lines.append("")
    csv_lines.append("Duty Rate Distribution")
    csv_lines.append("Range,Count")
    for rate in data['duty_rates']:
        csv_lines.append(f"{rate['range']},{rate['count']}")
    
    # Add categories
    csv_lines.append("")
    csv_lines.append("Category Distribution")
    csv_lines.append("Category,Count")
    for category in data['categories']:
        csv_lines.append(f"{category['name']},{category['count']}")
    
    return "\n".join(csv_lines) 