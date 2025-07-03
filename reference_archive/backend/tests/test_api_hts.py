import pytest
from httpx import AsyncClient
from app.db.models import HTSCode
from datetime import datetime

@pytest.mark.api
class TestHTSSearch:
    """Test HTS search endpoints."""
    
    async def test_search_hts_codes_success(self, client: AsyncClient, db_session):
        """Test successful HTS code search."""
        # Add test data
        hts_code = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers, portable, weighing not more than 10 kg",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        db_session.add(hts_code)
        await db_session.commit()
        
        response = await client.get("/api/v1/hts/search", params={
            "query": "laptop",
            "limit": 10,
            "country_origin": "US"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["results"]) > 0
        assert "laptop" in data["data"]["results"][0]["description"].lower()
    
    async def test_search_hts_codes_no_results(self, client: AsyncClient):
        """Test HTS search with no results."""
        response = await client.get("/api/v1/hts/search", params={
            "query": "nonexistentproduct",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["results"]) == 0
    
    async def test_search_hts_codes_invalid_params(self, client: AsyncClient):
        """Test HTS search with invalid parameters."""
        response = await client.get("/api/v1/hts/search", params={
            "limit": -1  # Invalid limit
        })
        
        assert response.status_code == 422  # Validation error

@pytest.mark.api
class TestHTSClassification:
    """Test HTS classification endpoints."""
    
    async def test_classify_product_success(self, client: AsyncClient):
        """Test successful product classification."""
        response = await client.post("/api/v1/hts/classify", json={
            "product_description": "Laptop computer with Intel processor",
            "include_alternatives": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "classification" in data["data"]
    
    async def test_classify_product_empty_description(self, client: AsyncClient):
        """Test product classification with empty description."""
        response = await client.post("/api/v1/hts/classify", json={
            "product_description": "",
            "include_alternatives": True
        })
        
        assert response.status_code == 422  # Validation error

@pytest.mark.api
class TestHTSCodeDetails:
    """Test HTS code detail endpoints."""
    
    async def test_get_hts_code_success(self, client: AsyncClient, db_session):
        """Test successful HTS code retrieval."""
        # Add test data
        hts_code = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers, portable, weighing not more than 10 kg",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        db_session.add(hts_code)
        await db_session.commit()
        
        response = await client.get("/api/v1/hts/code/8471.30.01")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["hts_code"] == "8471.30.01"
    
    async def test_get_hts_code_not_found(self, client: AsyncClient):
        """Test HTS code retrieval for non-existent code."""
        response = await client.get("/api/v1/hts/code/9999.99.99")
        
        assert response.status_code == 404

@pytest.mark.api
class TestTariffRate:
    """Test tariff rate endpoints."""
    
    async def test_get_tariff_rate_success(self, client: AsyncClient, db_session):
        """Test successful tariff rate retrieval."""
        # Add test data
        hts_code = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers, portable, weighing not more than 10 kg",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        db_session.add(hts_code)
        await db_session.commit()
        
        response = await client.get("/api/v1/hts/tariff-rate/8471.30.01", params={
            "country_origin": "US"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tariff_rate"] == 0.0
    
    async def test_get_tariff_rate_not_found(self, client: AsyncClient):
        """Test tariff rate retrieval for non-existent code."""
        response = await client.get("/api/v1/hts/tariff-rate/9999.99.99")
        
        assert response.status_code == 404

@pytest.mark.api
class TestHTSStatistics:
    """Test HTS statistics endpoints."""
    
    async def test_get_hts_statistics(self, client: AsyncClient, db_session):
        """Test HTS statistics retrieval."""
        # Add test data
        hts_codes = [
            HTSCode(
                hts_code="8471.30.01",
                description="Laptop computers",
                tariff_rate=0.0,
                country_origin="US",
                effective_date=datetime.now()
            ),
            HTSCode(
                hts_code="8471.30.02",
                description="Desktop computers",
                tariff_rate=2.5,
                country_origin="US",
                effective_date=datetime.now()
            )
        ]
        for hts in hts_codes:
            db_session.add(hts)
        await db_session.commit()
        
        response = await client.get("/api/v1/hts/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_hts_codes"] >= 2

@pytest.mark.api
class TestHTSSuggestions:
    """Test HTS suggestions endpoints."""
    
    async def test_get_hts_suggestions(self, client: AsyncClient, db_session):
        """Test HTS suggestions retrieval."""
        # Add test data
        hts_code = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers, portable, weighing not more than 10 kg",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        db_session.add(hts_code)
        await db_session.commit()
        
        response = await client.get("/api/v1/hts/suggestions", params={
            "query": "8471",
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["suggestions"]) > 0

@pytest.mark.api
class TestHTSHealth:
    """Test HTS health check endpoint."""
    
    async def test_hts_health(self, client: AsyncClient):
        """Test HTS service health check."""
        response = await client.get("/api/v1/hts/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "hts_search"
        assert "status" in data 