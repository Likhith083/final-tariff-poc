import pytest
from httpx import AsyncClient
from app.db.models import HTSCode, TariffCalculation
from datetime import datetime

@pytest.mark.api
class TestTariffCalculation:
    """Test tariff calculation endpoints."""
    
    async def test_calculate_tariff_success(self, client: AsyncClient, db_session):
        """Test successful tariff calculation."""
        # Add test HTS code
        hts_code = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        db_session.add(hts_code)
        await db_session.commit()
        
        response = await client.post("/api/v1/tariff/calculate", json={
            "hts_code": "8471.30.01",
            "country_origin": "US",
            "material_cost": 500.0,
            "currency": "USD",
            "freight_cost": 50.0,
            "insurance_cost": 10.0,
            "other_costs": 5.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["hts_code"] == "8471.30.01"
        assert data["tariff_rate"] == 0.0
        assert data["tariff_amount"] == 0.0
        assert data["total_landed_cost"] == 565.0  # 500 + 0 + 50 + 10 + 5
    
    async def test_calculate_tariff_with_tariff_rate(self, client: AsyncClient, db_session):
        """Test tariff calculation with non-zero tariff rate."""
        # Add test HTS code with tariff rate
        hts_code = HTSCode(
            hts_code="8471.30.02",
            description="Desktop computers",
            tariff_rate=2.5,
            country_origin="US",
            effective_date=datetime.now()
        )
        db_session.add(hts_code)
        await db_session.commit()
        
        response = await client.post("/api/v1/tariff/calculate", json={
            "hts_code": "8471.30.02",
            "country_origin": "US",
            "material_cost": 1000.0,
            "currency": "USD"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["tariff_rate"] == 2.5
        assert data["tariff_amount"] == 25.0  # 1000 * 0.025
        assert data["total_landed_cost"] == 1025.0  # 1000 + 25
    
    async def test_calculate_tariff_hts_not_found(self, client: AsyncClient):
        """Test tariff calculation with non-existent HTS code."""
        response = await client.post("/api/v1/tariff/calculate", json={
            "hts_code": "9999.99.99",
            "country_origin": "US",
            "material_cost": 500.0,
            "currency": "USD"
        })
        
        assert response.status_code == 404
    
    async def test_calculate_tariff_invalid_data(self, client: AsyncClient):
        """Test tariff calculation with invalid data."""
        response = await client.post("/api/v1/tariff/calculate", json={
            "hts_code": "8471.30.01",
            "country_origin": "US",
            "material_cost": -100.0,  # Invalid negative cost
            "currency": "USD"
        })
        
        assert response.status_code == 422  # Validation error

@pytest.mark.api
class TestBulkTariffCalculation:
    """Test bulk tariff calculation endpoints."""
    
    async def test_calculate_bulk_tariffs_success(self, client: AsyncClient, db_session):
        """Test successful bulk tariff calculation."""
        # Add test HTS codes
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
        
        response = await client.post("/api/v1/tariff/calculate-bulk", json={
            "calculations": [
                {
                    "hts_code": "8471.30.01",
                    "country_origin": "US",
                    "material_cost": 500.0,
                    "currency": "USD"
                },
                {
                    "hts_code": "8471.30.02",
                    "country_origin": "US",
                    "material_cost": 1000.0,
                    "currency": "USD"
                }
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_processed"] == 2
        assert data["data"]["successful"] == 2
        assert data["data"]["failed"] == 0
    
    async def test_calculate_bulk_tariffs_partial_failure(self, client: AsyncClient, db_session):
        """Test bulk tariff calculation with some failures."""
        # Add only one test HTS code
        hts_code = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        db_session.add(hts_code)
        await db_session.commit()
        
        response = await client.post("/api/v1/tariff/calculate-bulk", json={
            "calculations": [
                {
                    "hts_code": "8471.30.01",
                    "country_origin": "US",
                    "material_cost": 500.0,
                    "currency": "USD"
                },
                {
                    "hts_code": "9999.99.99",  # Non-existent
                    "country_origin": "US",
                    "material_cost": 1000.0,
                    "currency": "USD"
                }
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_processed"] == 2
        assert data["data"]["successful"] == 1
        assert data["data"]["failed"] == 1

@pytest.mark.api
class TestTariffHistory:
    """Test tariff calculation history endpoints."""
    
    async def test_get_calculation_history(self, client: AsyncClient, db_session):
        """Test retrieval of calculation history."""
        # Add test calculations
        calculations = [
            TariffCalculation(
                hts_code="8471.30.01",
                country_origin="US",
                material_cost=500.0,
                tariff_rate=0.0,
                tariff_amount=0.0,
                total_landed_cost=500.0,
                currency="USD"
            ),
            TariffCalculation(
                hts_code="8471.30.02",
                country_origin="US",
                material_cost=1000.0,
                tariff_rate=2.5,
                tariff_amount=25.0,
                total_landed_cost=1025.0,
                currency="USD"
            )
        ]
        for calc in calculations:
            db_session.add(calc)
        await db_session.commit()
        
        response = await client.get("/api/v1/tariff/history", params={"limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["calculations"]) >= 2
    
    async def test_get_calculation_history_with_limit(self, client: AsyncClient, db_session):
        """Test calculation history with limit parameter."""
        response = await client.get("/api/v1/tariff/history", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["calculations"]) <= 1

@pytest.mark.api
class TestTariffStatistics:
    """Test tariff statistics endpoints."""
    
    async def test_get_calculation_statistics(self, client: AsyncClient, db_session):
        """Test retrieval of calculation statistics."""
        # Add test calculations
        calculations = [
            TariffCalculation(
                hts_code="8471.30.01",
                country_origin="US",
                material_cost=500.0,
                tariff_rate=0.0,
                tariff_amount=0.0,
                total_landed_cost=500.0,
                currency="USD"
            ),
            TariffCalculation(
                hts_code="8471.30.02",
                country_origin="US",
                material_cost=1000.0,
                tariff_rate=2.5,
                tariff_amount=25.0,
                total_landed_cost=1025.0,
                currency="USD"
            )
        ]
        for calc in calculations:
            db_session.add(calc)
        await db_session.commit()
        
        response = await client.get("/api/v1/tariff/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_calculations"] >= 2
        assert "average_tariff_rate" in data["data"]
        assert "total_tariff_amount" in data["data"]

@pytest.mark.api
class TestTariffHealth:
    """Test tariff calculator health check endpoint."""
    
    async def test_tariff_health(self, client: AsyncClient):
        """Test tariff calculator service health check."""
        response = await client.get("/api/v1/tariff/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "tariff_calculator"
        assert "status" in data 