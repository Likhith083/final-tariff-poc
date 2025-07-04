from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.db.models import Report, TariffCalculation, MaterialAnalysis, Scenario
from app.core.responses import ReportResponse, SuccessResponse
from loguru import logger
from datetime import datetime, timedelta
import uuid
import json

router = APIRouter()

class ReportRequest(BaseModel):
    report_type: str  # 'tariff_summary', 'material_analysis', 'scenario_comparison', 'custom'
    parameters: Optional[Dict[str, Any]] = None
    format: str = "json"  # 'json', 'csv', 'pdf'

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a report based on the specified type and parameters"""
    try:
        report_id = str(uuid.uuid4())
        
        # Generate report based on type
        if request.report_type == "tariff_summary":
            report_data = await _generate_tariff_summary(db, request.parameters)
        elif request.report_type == "material_analysis":
            report_data = await _generate_material_analysis_report(db, request.parameters)
        elif request.report_type == "scenario_comparison":
            report_data = await _generate_scenario_comparison_report(db, request.parameters)
        elif request.report_type == "custom":
            report_data = await _generate_custom_report(db, request.parameters)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown report type: {request.report_type}")
        
        # Store report in database
        report = Report(
            report_id=report_id,
            report_type=request.report_type,
            parameters=request.parameters,
            file_path=None  # For now, we'll return JSON directly
        )
        db.add(report)
        await db.commit()
        
        return ReportResponse(
            success=True,
            message="Report generated successfully",
            report_id=report_id,
            report_type=request.report_type,
            generated_at=datetime.now(),
            download_url=None,
            data=report_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types", response_model=SuccessResponse)
async def get_report_types():
    """Get available report types"""
    report_types = [
        {
            'id': 'tariff_summary',
            'name': 'Tariff Summary Report',
            'description': 'Summary of tariff calculations and statistics',
            'parameters': {
                'date_range': 'optional',
                'country_filter': 'optional',
                'hts_code_filter': 'optional'
            }
        },
        {
            'id': 'material_analysis',
            'name': 'Material Analysis Report',
            'description': 'Analysis of material compositions and alternatives',
            'parameters': {
                'material_type': 'optional',
                'savings_threshold': 'optional'
            }
        },
        {
            'id': 'scenario_comparison',
            'name': 'Scenario Comparison Report',
            'description': 'Comparison of different sourcing scenarios',
            'parameters': {
                'scenario_ids': 'required',
                'comparison_metrics': 'optional'
            }
        },
        {
            'id': 'custom',
            'name': 'Custom Report',
            'description': 'Custom report with user-defined parameters',
            'parameters': {
                'query_type': 'required',
                'filters': 'optional'
            }
        }
    ]
    
    return SuccessResponse(
        success=True,
        message="Available report types retrieved",
        data={
            'report_types': report_types,
            'total_types': len(report_types)
        }
    )

@router.get("/history", response_model=SuccessResponse)
async def get_report_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get recent report generation history"""
    try:
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(Report)
            .order_by(desc(Report.generated_at))
            .limit(limit)
        )
        
        reports = result.scalars().all()
        
        history = [
            {
                'report_id': report.report_id,
                'report_type': report.report_type,
                'parameters': report.parameters,
                'generated_at': report.generated_at.isoformat(),
                'file_path': report.file_path
            }
            for report in reports
        ]
        
        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(history)} reports",
            data={
                'reports': history,
                'total_count': len(history)
            }
        )
        
    except Exception as e:
        logger.error(f"Get report history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}", response_model=SuccessResponse)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific report by ID"""
    try:
        from sqlalchemy import select
        
        result = await db.execute(
            select(Report).where(Report.report_id == report_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return SuccessResponse(
            success=True,
            message="Report retrieved successfully",
            data={
                'report_id': report.report_id,
                'report_type': report.report_type,
                'parameters': report.parameters,
                'generated_at': report.generated_at.isoformat(),
                'file_path': report.file_path
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_tariff_summary(db: AsyncSession, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate tariff summary report"""
    try:
        from sqlalchemy import select, func
        
        # Build query based on parameters
        query = select(TariffCalculation)
        
        if parameters:
            if 'date_range' in parameters:
                days = parameters['date_range']
                start_date = datetime.now() - timedelta(days=days)
                query = query.where(TariffCalculation.calculated_at >= start_date)
            
            if 'country_filter' in parameters:
                query = query.where(TariffCalculation.country_origin == parameters['country_filter'])
            
            if 'hts_code_filter' in parameters:
                query = query.where(TariffCalculation.hts_code.like(f"%{parameters['hts_code_filter']}%"))
        
        result = await db.execute(query)
        calculations = result.scalars().all()
        
        # Calculate statistics
        total_calculations = len(calculations)
        total_material_cost = sum(calc.material_cost for calc in calculations)
        total_tariff_amount = sum(calc.tariff_amount for calc in calculations)
        avg_tariff_rate = sum(calc.tariff_rate for calc in calculations) / total_calculations if total_calculations > 0 else 0
        
        # Group by country
        countries = {}
        for calc in calculations:
            if calc.country_origin not in countries:
                countries[calc.country_origin] = {
                    'count': 0,
                    'total_cost': 0,
                    'total_tariff': 0
                }
            countries[calc.country_origin]['count'] += 1
            countries[calc.country_origin]['total_cost'] += calc.material_cost
            countries[calc.country_origin]['total_tariff'] += calc.tariff_amount
        
        return {
            'report_type': 'tariff_summary',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_calculations': total_calculations,
                'total_material_cost': round(total_material_cost, 2),
                'total_tariff_amount': round(total_tariff_amount, 2),
                'average_tariff_rate': round(avg_tariff_rate, 2),
                'total_landed_cost': round(total_material_cost + total_tariff_amount, 2)
            },
            'by_country': countries,
            'recent_calculations': [
                {
                    'hts_code': calc.hts_code,
                    'country': calc.country_origin,
                    'material_cost': calc.material_cost,
                    'tariff_rate': calc.tariff_rate,
                    'tariff_amount': calc.tariff_amount,
                    'total_cost': calc.total_landed_cost,
                    'calculated_at': calc.calculated_at.isoformat()
                }
                for calc in calculations[-10:]  # Last 10 calculations
            ]
        }
        
    except Exception as e:
        logger.error(f"Generate tariff summary error: {e}")
        return {'error': str(e)}

async def _generate_material_analysis_report(db: AsyncSession, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate material analysis report"""
    try:
        from sqlalchemy import select
        
        query = select(MaterialAnalysis)
        
        if parameters and 'material_type' in parameters:
            # Filter by material type (would need to be implemented based on composition)
            pass
        
        result = await db.execute(query)
        analyses = result.scalars().all()
        
        # Calculate statistics
        total_analyses = len(analyses)
        total_savings = sum(analysis.cost_savings for analysis in analyses)
        avg_savings = total_savings / total_analyses if total_analyses > 0 else 0
        
        # Filter by savings threshold
        if parameters and 'savings_threshold' in parameters:
            threshold = parameters['savings_threshold']
            analyses = [a for a in analyses if a.cost_savings >= threshold]
        
        return {
            'report_type': 'material_analysis',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_analyses': total_analyses,
                'total_potential_savings': round(total_savings, 2),
                'average_savings': round(avg_savings, 2)
            },
            'analyses': [
                {
                    'original_composition': analysis.original_composition,
                    'suggested_composition': analysis.suggested_composition,
                    'cost_savings': analysis.cost_savings,
                    'quality_impact': analysis.quality_impact,
                    'recommendations': analysis.recommendations,
                    'analyzed_at': analysis.analyzed_at.isoformat()
                }
                for analysis in analyses
            ]
        }
        
    except Exception as e:
        logger.error(f"Generate material analysis report error: {e}")
        return {'error': str(e)}

async def _generate_scenario_comparison_report(db: AsyncSession, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate scenario comparison report"""
    try:
        from sqlalchemy import select
        
        query = select(Scenario)
        
        if parameters and 'scenario_ids' in parameters:
            scenario_ids = parameters['scenario_ids']
            query = query.where(Scenario.id.in_(scenario_ids))
        
        result = await db.execute(query)
        scenarios = result.scalars().all()
        
        return {
            'report_type': 'scenario_comparison',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_scenarios': len(scenarios),
                'total_savings': sum(scenario.savings for scenario in scenarios),
                'average_savings': sum(scenario.savings for scenario in scenarios) / len(scenarios) if scenarios else 0
            },
            'scenarios': [
                {
                    'base_scenario': scenario.base_scenario,
                    'modified_scenario': scenario.modified_scenario,
                    'savings': scenario.savings,
                    'percentage_change': scenario.percentage_change,
                    'risk_assessment': scenario.risk_assessment,
                    'created_at': scenario.created_at.isoformat()
                }
                for scenario in scenarios
            ]
        }
        
    except Exception as e:
        logger.error(f"Generate scenario comparison report error: {e}")
        return {'error': str(e)}

async def _generate_custom_report(db: AsyncSession, parameters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate custom report based on user-defined parameters"""
    try:
        if not parameters or 'query_type' not in parameters:
            return {'error': 'Custom report requires query_type parameter'}
        
        query_type = parameters['query_type']
        
        if query_type == 'recent_activity':
            # Get recent activity across all tables
            from sqlalchemy import select, desc
            
            # Get recent calculations
            calc_result = await db.execute(
                select(TariffCalculation).order_by(desc(TariffCalculation.calculated_at)).limit(5)
            )
            recent_calculations = calc_result.scalars().all()
            
            # Get recent analyses
            analysis_result = await db.execute(
                select(MaterialAnalysis).order_by(desc(MaterialAnalysis.analyzed_at)).limit(5)
            )
            recent_analyses = analysis_result.scalars().all()
            
            return {
                'report_type': 'custom_recent_activity',
                'generated_at': datetime.now().isoformat(),
                'recent_calculations': [
                    {
                        'hts_code': calc.hts_code,
                        'country': calc.country_origin,
                        'total_cost': calc.total_landed_cost,
                        'calculated_at': calc.calculated_at.isoformat()
                    }
                    for calc in recent_calculations
                ],
                'recent_analyses': [
                    {
                        'cost_savings': analysis.cost_savings,
                        'quality_impact': analysis.quality_impact,
                        'analyzed_at': analysis.analyzed_at.isoformat()
                    }
                    for analysis in recent_analyses
                ]
            }
        else:
            return {'error': f'Unknown query type: {query_type}'}
        
    except Exception as e:
        logger.error(f"Generate custom report error: {e}")
        return {'error': str(e)}

@router.get("/health")
async def reports_health():
    """Check reports service health"""
    try:
        return {
            "service": "reports",
            "status": "healthy",
            "available_types": ["tariff_summary", "material_analysis", "scenario_comparison", "custom"]
        }
        
    except Exception as e:
        logger.error(f"Reports health check error: {e}")
        return {
            "service": "reports",
            "status": "unhealthy",
            "error": str(e)
        } 