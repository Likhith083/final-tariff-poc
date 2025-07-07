"""
Data Update Tasks for ATLAS Enterprise
Background tasks for updating exchange rates and tariff data.
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from .celery_app import celery_app
from ..core.database import get_async_session
from ..core.logging import get_logger
from ..services.exchange_rate_service import ExchangeRateService

logger = get_logger(__name__)


@celery_app.task(name="backend.tasks.data_tasks.update_exchange_rates_task")
def update_exchange_rates_task() -> Dict[str, Any]:
    """
    Update exchange rates from external API.
    
    Returns:
        Update results
    """
    try:
        async def _update_rates():
            async with get_async_session() as db:
                result = await ExchangeRateService.update_exchange_rates(db)
                return result
        
        result = asyncio.run(_update_rates())
        
        if result["success"]:
            logger.info(f"Exchange rates updated: {result['updated_count']} rates")
        else:
            logger.error(f"Exchange rate update failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in exchange rate update task: {e}")
        return {"success": False, "error": str(e)}


@celery_app.task(name="backend.tasks.data_tasks.refresh_tariff_data_task")
def refresh_tariff_data_task() -> Dict[str, Any]:
    """
    Refresh tariff data from official sources.
    
    Returns:
        Refresh results
    """
    try:
        # This would integrate with USITC or other official tariff APIs
        # For now, return a placeholder result
        
        logger.info("Tariff data refresh task executed (placeholder)")
        
        return {
            "success": True,
            "message": "Tariff data refresh completed (placeholder)",
            "updated_records": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in tariff data refresh task: {e}")
        return {"success": False, "error": str(e)} 