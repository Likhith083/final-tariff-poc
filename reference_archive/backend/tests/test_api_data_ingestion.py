import pytest
from httpx import AsyncClient
from app.db.models import DataIngestion
from datetime import datetime
import io
import json

@pytest.mark.api
class TestDataIngestion:
    """Test data ingestion endpoints."""
    
    async def test_ingest_hts_codes_success(self, client: AsyncClient, db_session):
        """Test successful HTS codes ingestion."""
        hts_data = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers, portable, weighing not more than 10 kg",
                "tariff_rate": 0.0,
                "country_origin": "US"
            },
            {
                "hts_code": "8471.30.02",
                "description": "Desktop computers",
                "tariff_rate": 2.5,
                "country_origin": "US"
            }
        ]
        
        response = await client.post("/api/v1/data/hts-codes", json=hts_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_processed"] == 2
        assert data["records_added"] == 2
        assert data["records_updated"] == 0
        assert len(data["errors"]) == 0
    
    async def test_ingest_hts_codes_with_errors(self, client: AsyncClient, db_session):
        """Test HTS codes ingestion with some errors."""
        hts_data = [
            {
                "hts_code": "8471.30.01",
                "description": "Valid HTS code",
                "tariff_rate": 0.0,
                "country_origin": "US"
            },
            {
                "hts_code": "",  # Invalid empty code
                "description": "Invalid HTS code",
                "tariff_rate": 0.0,
                "country_origin": "US"
            },
            {
                "description": "Missing HTS code",  # Missing required field
                "tariff_rate": 0.0,
                "country_origin": "US"
            }
        ]
        
        response = await client.post("/api/v1/data/hts-codes", json=hts_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_processed"] == 3
        assert data["records_added"] == 1
        assert data["records_updated"] == 0
        assert len(data["errors"]) == 2
    
    async def test_ingest_materials_success(self, client: AsyncClient, db_session):
        """Test successful materials ingestion."""
        materials_data = [
            {
                "name": "Cotton Fabric",
                "composition": {"cotton": 100.0},
                "tariff_impact": 0.0,
                "alternatives": ["Polyester blend", "Bamboo fabric"]
            },
            {
                "name": "Polyester Blend",
                "composition": {"polyester": 80.0, "cotton": 20.0},
                "tariff_impact": 2.5,
                "alternatives": ["Pure cotton", "Bamboo blend"]
            }
        ]
        
        response = await client.post("/api/v1/data/materials", json=materials_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_processed"] == 2
        assert data["records_added"] == 2
        assert data["records_updated"] == 0
        assert len(data["errors"]) == 0
    
    async def test_ingest_materials_with_errors(self, client: AsyncClient, db_session):
        """Test materials ingestion with some errors."""
        materials_data = [
            {
                "name": "Valid Material",
                "composition": {"cotton": 100.0}
            },
            {
                "composition": {"cotton": 100.0}  # Missing name
            },
            {
                "name": "Invalid Material",
                "composition": {}  # Empty composition
            }
        ]
        
        response = await client.post("/api/v1/data/materials", json=materials_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_processed"] == 3
        assert data["records_added"] == 1
        assert data["records_updated"] == 0
        assert len(data["errors"]) == 2
    
    async def test_ingest_empty_data(self, client: AsyncClient, db_session):
        """Test ingestion with empty data."""
        response = await client.post("/api/v1/data/hts-codes", json=[])
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_processed"] == 0
        assert data["records_added"] == 0
        assert data["records_updated"] == 0

@pytest.mark.api
class TestDataIngestionHistory:
    """Test data ingestion history endpoints."""
    
    async def test_get_ingestion_history(self, client: AsyncClient, db_session):
        """Test retrieval of ingestion history."""
        # Add test ingestion records
        ingestions = [
            DataIngestion(
                file_name="test_hts.xlsx",
                file_type="excel",
                records_processed=10,
                records_added=8,
                records_updated=2,
                errors=["Invalid HTS code: 9999.99.99", "Missing description for code 8888.88.88"]
            ),
            DataIngestion(
                file_name="test_materials.json",
                file_type="json",
                records_processed=5,
                records_added=5,
                records_updated=0,
                errors=[]
            )
        ]
        for ingestion in ingestions:
            db_session.add(ingestion)
        await db_session.commit()
        
        response = await client.get("/api/v1/data/history", params={"limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["ingestions"]) >= 2
    
    async def test_get_ingestion_history_with_limit(self, client: AsyncClient, db_session):
        """Test ingestion history with limit parameter."""
        response = await client.get("/api/v1/data/history", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["ingestions"]) <= 1

@pytest.mark.api
class TestDataIngestionStatistics:
    """Test data ingestion statistics endpoints."""
    
    async def test_get_ingestion_statistics(self, client: AsyncClient, db_session):
        """Test retrieval of ingestion statistics."""
        # Add test ingestion records
        ingestions = [
            DataIngestion(
                file_name="test1.xlsx",
                file_type="excel",
                records_processed=10,
                records_added=8,
                records_updated=2,
                errors=["Error 1"]
            ),
            DataIngestion(
                file_name="test2.json",
                file_type="json",
                records_processed=5,
                records_added=5,
                records_updated=0,
                errors=[]
            ),
            DataIngestion(
                file_name="test3.csv",
                file_type="csv",
                records_processed=15,
                records_added=12,
                records_updated=3,
                errors=["Error 2", "Error 3"]
            )
        ]
        for ingestion in ingestions:
            db_session.add(ingestion)
        await db_session.commit()
        
        response = await client.get("/api/v1/data/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_ingestions"] >= 3
        assert data["data"]["total_records_processed"] >= 30
        assert data["data"]["total_records_added"] >= 25
        assert "success_rate" in data["data"]
        assert "file_type_distribution" in data["data"]
        assert len(data["data"]["file_type_distribution"]) >= 3

@pytest.mark.api
class TestDataIngestionHealth:
    """Test data ingestion health check endpoint."""
    
    async def test_data_ingestion_health(self, client: AsyncClient):
        """Test data ingestion service health check."""
        response = await client.get("/api/v1/data/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "data_ingestion"
        assert "status" in data
        assert "chroma_stats" in data

@pytest.mark.api
class TestDataIngestionEdgeCases:
    """Test edge cases for data ingestion."""
    
    async def test_ingest_hts_codes_with_duplicates(self, client: AsyncClient, db_session):
        """Test HTS codes ingestion with duplicate codes."""
        hts_data = [
            {
                "hts_code": "8471.30.01",
                "description": "First description",
                "tariff_rate": 0.0,
                "country_origin": "US"
            },
            {
                "hts_code": "8471.30.01",  # Duplicate code
                "description": "Second description",
                "tariff_rate": 2.5,
                "country_origin": "US"
            }
        ]
        
        response = await client.post("/api/v1/data/hts-codes", json=hts_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should handle duplicates gracefully
        assert data["records_processed"] == 2
    
    async def test_ingest_materials_with_complex_composition(self, client: AsyncClient, db_session):
        """Test materials ingestion with complex composition."""
        materials_data = [
            {
                "name": "Complex Blend",
                "composition": {
                    "cotton": 40.0,
                    "polyester": 30.0,
                    "spandex": 20.0,
                    "elastane": 10.0
                },
                "tariff_impact": 5.0,
                "alternatives": ["Simple cotton", "Polyester blend"]
            }
        ]
        
        response = await client.post("/api/v1/data/materials", json=materials_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_added"] == 1
    
    async def test_ingest_large_dataset(self, client: AsyncClient, db_session):
        """Test ingestion of large dataset."""
        # Create large dataset
        large_hts_data = []
        for i in range(100):
            large_hts_data.append({
                "hts_code": f"8471.{i:02d}.{i:02d}",
                "description": f"Test product {i}",
                "tariff_rate": float(i % 10),
                "country_origin": "US"
            })
        
        response = await client.post("/api/v1/data/hts-codes", json=large_hts_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_processed"] == 100
        assert data["records_added"] == 100
    
    async def test_ingest_with_special_characters(self, client: AsyncClient, db_session):
        """Test ingestion with special characters in data."""
        hts_data = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers with special chars: éñç & symbols!",
                "tariff_rate": 0.0,
                "country_origin": "US"
            }
        ]
        
        response = await client.post("/api/v1/data/hts-codes", json=hts_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_added"] == 1
    
    async def test_ingest_with_missing_optional_fields(self, client: AsyncClient, db_session):
        """Test ingestion with missing optional fields."""
        hts_data = [
            {
                "hts_code": "8471.30.01",
                "description": "Minimal HTS code"
                # Missing optional fields like tariff_rate, country_origin
            }
        ]
        
        response = await client.post("/api/v1/data/hts-codes", json=hts_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["records_added"] == 1 