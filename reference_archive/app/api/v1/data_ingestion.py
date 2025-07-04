from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.hts_service import HTSService
from app.services.chroma_service import ChromaService
from app.db.models import DataIngestion
from app.core.responses import DataIngestionResponse, SuccessResponse
from loguru import logger
from datetime import datetime
import pandas as pd
import json
import os
from pathlib import Path

router = APIRouter()

class DataIngestionRequest(BaseModel):
    file_type: str  # 'excel', 'csv', 'json'
    description: Optional[str] = None
    tags: Optional[List[str]] = None

@router.post("/upload", response_model=DataIngestionResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "auto",
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a file for data ingestion"""
    try:
        # Determine file type
        if file_type == "auto":
            file_type = _detect_file_type(file.filename)
        
        # Save file temporarily
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process file based on type
        if file_type == "excel":
            result = await _process_excel_file(file_path, db)
        elif file_type == "csv":
            result = await _process_csv_file(file_path, db)
        elif file_type == "json":
            result = await _process_json_file(file_path, db)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
        
        # Clean up temp file
        os.remove(file_path)
        
        # Store ingestion record
        ingestion = DataIngestion(
            file_name=file.filename,
            file_type=file_type,
            records_processed=result['records_processed'],
            records_added=result['records_added'],
            records_updated=result['records_updated'],
            errors=result.get('errors', [])
        )
        db.add(ingestion)
        await db.commit()
        
        return DataIngestionResponse(
            success=True,
            message="File processed successfully",
            file_name=file.filename,
            records_processed=result['records_processed'],
            records_added=result['records_added'],
            records_updated=result['records_updated'],
            errors=result.get('errors', [])
        )
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hts-codes", response_model=DataIngestionResponse)
async def ingest_hts_codes(
    hts_data: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db)
):
    """Ingest HTS codes directly via API"""
    try:
        hts_service = HTSService()
        chroma_service = ChromaService()
        
        records_processed = len(hts_data)
        records_added = 0
        records_updated = 0
        errors = []
        
        # Process each HTS code
        for hts_record in hts_data:
            try:
                # Validate required fields
                if not hts_record.get('hts_code') or not hts_record.get('description'):
                    errors.append(f"Missing required fields for record: {hts_record}")
                    continue
                
                # Add to ChromaDB
                await chroma_service.add_hts_codes([hts_record])
                records_added += 1
                
            except Exception as e:
                errors.append(f"Error processing HTS code {hts_record.get('hts_code', 'unknown')}: {str(e)}")
        
        # Store ingestion record
        ingestion = DataIngestion(
            file_name="api_hts_codes",
            file_type="api",
            records_processed=records_processed,
            records_added=records_added,
            records_updated=records_updated,
            errors=errors
        )
        db.add(ingestion)
        await db.commit()
        
        return DataIngestionResponse(
            success=True,
            message="HTS codes ingested successfully",
            file_name="api_hts_codes",
            records_processed=records_processed,
            records_added=records_added,
            records_updated=records_updated,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"HTS codes ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/materials", response_model=DataIngestionResponse)
async def ingest_materials(
    materials_data: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db)
):
    """Ingest material compositions directly via API"""
    try:
        chroma_service = ChromaService()
        
        records_processed = len(materials_data)
        records_added = 0
        records_updated = 0
        errors = []
        
        # Process each material
        for material_record in materials_data:
            try:
                # Validate required fields
                if not material_record.get('name') or not material_record.get('composition'):
                    errors.append(f"Missing required fields for material: {material_record}")
                    continue
                
                # Add to ChromaDB
                await chroma_service.add_materials([material_record])
                records_added += 1
                
            except Exception as e:
                errors.append(f"Error processing material {material_record.get('name', 'unknown')}: {str(e)}")
        
        # Store ingestion record
        ingestion = DataIngestion(
            file_name="api_materials",
            file_type="api",
            records_processed=records_processed,
            records_added=records_added,
            records_updated=records_updated,
            errors=errors
        )
        db.add(ingestion)
        await db.commit()
        
        return DataIngestionResponse(
            success=True,
            message="Materials ingested successfully",
            file_name="api_materials",
            records_processed=records_processed,
            records_added=records_added,
            records_updated=records_updated,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Materials ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=SuccessResponse)
async def get_ingestion_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get recent data ingestion history"""
    try:
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(DataIngestion)
            .order_by(desc(DataIngestion.ingested_at))
            .limit(limit)
        )
        
        ingestions = result.scalars().all()
        
        history = [
            {
                'id': ingestion.id,
                'file_name': ingestion.file_name,
                'file_type': ingestion.file_type,
                'records_processed': ingestion.records_processed,
                'records_added': ingestion.records_added,
                'records_updated': ingestion.records_updated,
                'errors': ingestion.errors,
                'ingested_at': ingestion.ingested_at.isoformat()
            }
            for ingestion in ingestions
        ]
        
        return SuccessResponse(
            success=True,
            message=f"Retrieved {len(history)} ingestion records",
            data={
                'ingestions': history,
                'total_count': len(history)
            }
        )
        
    except Exception as e:
        logger.error(f"Get ingestion history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=SuccessResponse)
async def get_ingestion_statistics(db: AsyncSession = Depends(get_db)):
    """Get data ingestion statistics"""
    try:
        from sqlalchemy import select, func
        
        # Get total ingestions
        total_result = await db.execute(select(func.count(DataIngestion.id)))
        total_ingestions = total_result.scalar()
        
        # Get total records processed
        total_processed_result = await db.execute(select(func.sum(DataIngestion.records_processed)))
        total_processed = total_processed_result.scalar() or 0
        
        # Get total records added
        total_added_result = await db.execute(select(func.sum(DataIngestion.records_added)))
        total_added = total_added_result.scalar() or 0
        
        # Get file type distribution
        file_type_result = await db.execute(
            select(DataIngestion.file_type, func.count(DataIngestion.file_type))
            .group_by(DataIngestion.file_type)
        )
        file_types = [
            {'file_type': file_type, 'count': count}
            for file_type, count in file_type_result.all()
        ]
        
        return SuccessResponse(
            success=True,
            message="Ingestion statistics retrieved successfully",
            data={
                'total_ingestions': total_ingestions,
                'total_records_processed': total_processed,
                'total_records_added': total_added,
                'success_rate': round((total_added / total_processed * 100), 2) if total_processed > 0 else 0,
                'file_type_distribution': file_types,
                'last_updated': datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Get ingestion statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _detect_file_type(filename: str) -> str:
    """Detect file type based on filename extension"""
    ext = Path(filename).suffix.lower()
    
    if ext in ['.xlsx', '.xls']:
        return 'excel'
    elif ext == '.csv':
        return 'csv'
    elif ext == '.json':
        return 'json'
    else:
        return 'unknown'

async def _process_excel_file(file_path: Path, db: AsyncSession) -> Dict[str, Any]:
    """Process Excel file for data ingestion"""
    try:
        df = pd.read_excel(file_path)
        
        records_processed = len(df)
        records_added = 0
        records_updated = 0
        errors = []
        
        # Determine if this is HTS data or material data based on columns
        if 'HTS Code' in df.columns or 'hts_code' in df.columns:
            # Process as HTS data
            chroma_service = ChromaService()
            
            hts_data = []
            for _, row in df.iterrows():
                try:
                    hts_code = str(row.get('HTS Code', row.get('hts_code', ''))).strip()
                    description = str(row.get('Description', row.get('description', ''))).strip()
                    tariff_rate = float(row.get('Tariff Rate', row.get('tariff_rate', 0)))
                    country = str(row.get('Country', row.get('country', 'US'))).strip()
                    
                    if hts_code and description:
                        hts_data.append({
                            'hts_code': hts_code,
                            'description': description,
                            'tariff_rate': tariff_rate,
                            'country_origin': country
                        })
                        records_added += 1
                    else:
                        errors.append(f"Missing required fields in row: {row.to_dict()}")
                        
                except Exception as e:
                    errors.append(f"Error processing row: {str(e)}")
            
            if hts_data:
                await chroma_service.add_hts_codes(hts_data)
        
        elif 'Material' in df.columns or 'material' in df.columns:
            # Process as material data
            chroma_service = ChromaService()
            
            material_data = []
            for _, row in df.iterrows():
                try:
                    material_name = str(row.get('Material', row.get('material', ''))).strip()
                    composition = row.get('Composition', row.get('composition', {}))
                    
                    if material_name and composition:
                        material_data.append({
                            'name': material_name,
                            'composition': composition,
                            'tariff_impact': float(row.get('Tariff Impact', row.get('tariff_impact', 0))),
                            'alternatives': row.get('Alternatives', row.get('alternatives', []))
                        })
                        records_added += 1
                    else:
                        errors.append(f"Missing required fields in row: {row.to_dict()}")
                        
                except Exception as e:
                    errors.append(f"Error processing row: {str(e)}")
            
            if material_data:
                await chroma_service.add_materials(material_data)
        
        else:
            errors.append("Unknown file format - could not determine if HTS or material data")
        
        return {
            'records_processed': records_processed,
            'records_added': records_added,
            'records_updated': records_updated,
            'errors': errors
        }
        
    except Exception as e:
        logger.error(f"Excel file processing error: {e}")
        return {
            'records_processed': 0,
            'records_added': 0,
            'records_updated': 0,
            'errors': [str(e)]
        }

async def _process_csv_file(file_path: Path, db: AsyncSession) -> Dict[str, Any]:
    """Process CSV file for data ingestion"""
    try:
        df = pd.read_csv(file_path)
        
        # Similar processing logic as Excel
        return await _process_excel_file(file_path, db)
        
    except Exception as e:
        logger.error(f"CSV file processing error: {e}")
        return {
            'records_processed': 0,
            'records_added': 0,
            'records_updated': 0,
            'errors': [str(e)]
        }

async def _process_json_file(file_path: Path, db: AsyncSession) -> Dict[str, Any]:
    """Process JSON file for data ingestion"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        records_processed = len(data) if isinstance(data, list) else 1
        records_added = 0
        records_updated = 0
        errors = []
        
        chroma_service = ChromaService()
        
        if isinstance(data, list):
            for item in data:
                try:
                    if 'hts_code' in item:
                        await chroma_service.add_hts_codes([item])
                        records_added += 1
                    elif 'material_name' in item or 'name' in item:
                        await chroma_service.add_materials([item])
                        records_added += 1
                    else:
                        errors.append(f"Unknown data format: {item}")
                        
                except Exception as e:
                    errors.append(f"Error processing item: {str(e)}")
        else:
            # Single object
            try:
                if 'hts_code' in data:
                    await chroma_service.add_hts_codes([data])
                    records_added += 1
                elif 'material_name' in data or 'name' in data:
                    await chroma_service.add_materials([data])
                    records_added += 1
                else:
                    errors.append(f"Unknown data format: {data}")
                    
            except Exception as e:
                errors.append(f"Error processing data: {str(e)}")
        
        return {
            'records_processed': records_processed,
            'records_added': records_added,
            'records_updated': records_updated,
            'errors': errors
        }
        
    except Exception as e:
        logger.error(f"JSON file processing error: {e}")
        return {
            'records_processed': 0,
            'records_added': 0,
            'records_updated': 0,
            'errors': [str(e)]
        }

@router.get("/health")
async def data_ingestion_health():
    """Check data ingestion service health"""
    try:
        chroma_service = ChromaService()
        hts_stats = await chroma_service.get_collection_stats("hts_codes")
        
        return {
            "service": "data_ingestion",
            "status": "healthy",
            "chroma_stats": {
                "hts_codes": hts_stats
            }
        }
        
    except Exception as e:
        logger.error(f"Data ingestion health check error: {e}")
        return {
            "service": "data_ingestion",
            "status": "unhealthy",
            "error": str(e)
        } 