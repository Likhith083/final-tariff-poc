import pytest
from httpx import AsyncClient
from app.db.models import MaterialAnalysis
from datetime import datetime

@pytest.mark.api
class TestMaterialAnalysis:
    """Test material analysis endpoints."""
    
    async def test_analyze_materials_success(self, client: AsyncClient, db_session):
        """Test successful material analysis."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {
                "cotton": 80.0,
                "polyester": 20.0
            },
            "product_name": "Cotton T-Shirt",
            "current_cost": 10.0,
            "target_savings": 15.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["original_composition"]["cotton"] == 80.0
        assert data["original_composition"]["polyester"] == 20.0
        assert "suggested_composition" in data
        assert "cost_savings" in data
        assert "quality_impact" in data
        assert "recommendations" in data
    
    async def test_analyze_materials_empty_composition(self, client: AsyncClient):
        """Test material analysis with empty composition."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {},
            "product_name": "Test Product"
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_analyze_materials_invalid_percentages(self, client: AsyncClient):
        """Test material analysis with invalid percentages."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {
                "cotton": 120.0,  # Over 100%
                "polyester": 20.0
            },
            "product_name": "Test Product"
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_analyze_materials_with_cost_data(self, client: AsyncClient, db_session):
        """Test material analysis with cost data."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {
                "silk": 60.0,
                "wool": 40.0
            },
            "product_name": "Luxury Scarf",
            "current_cost": 50.0,
            "target_savings": 20.0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["original_composition"]["silk"] == 60.0
        assert data["original_composition"]["wool"] == 40.0

@pytest.mark.api
class TestMaterialSearch:
    """Test material search endpoints."""
    
    async def test_search_materials_success(self, client: AsyncClient):
        """Test successful material search."""
        response = await client.post("/api/v1/materials/search", json={
            "query": "cotton fabric",
            "limit": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data["data"]
        assert "total_results" in data["data"]
    
    async def test_search_materials_empty_query(self, client: AsyncClient):
        """Test material search with empty query."""
        response = await client.post("/api/v1/materials/search", json={
            "query": "",
            "limit": 10
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_search_materials_with_limit(self, client: AsyncClient):
        """Test material search with limit parameter."""
        response = await client.post("/api/v1/materials/search", json={
            "query": "textile",
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["results"]) <= 5

@pytest.mark.api
class TestMaterialHistory:
    """Test material analysis history endpoints."""
    
    async def test_get_analysis_history(self, client: AsyncClient, db_session):
        """Test retrieval of analysis history."""
        # Add test analyses
        analyses = [
            MaterialAnalysis(
                original_composition={"cotton": 80.0, "polyester": 20.0},
                suggested_composition={"cotton": 70.0, "polyester": 30.0},
                cost_savings=10.0,
                quality_impact="Minimal",
                recommendations=["Consider polyester blend for cost savings"]
            ),
            MaterialAnalysis(
                original_composition={"silk": 100.0},
                suggested_composition={"silk": 80.0, "cotton": 20.0},
                cost_savings=25.0,
                quality_impact="Moderate",
                recommendations=["Blend with cotton for affordability"]
            )
        ]
        for analysis in analyses:
            db_session.add(analysis)
        await db_session.commit()
        
        response = await client.get("/api/v1/materials/history", params={"limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["analyses"]) >= 2
    
    async def test_get_analysis_history_with_limit(self, client: AsyncClient, db_session):
        """Test analysis history with limit parameter."""
        response = await client.get("/api/v1/materials/history", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["analyses"]) <= 1

@pytest.mark.api
class TestMaterialHealth:
    """Test material analysis health check endpoint."""
    
    async def test_materials_health(self, client: AsyncClient):
        """Test material analysis service health check."""
        response = await client.get("/api/v1/materials/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "material_analysis"
        assert "status" in data
        assert "chroma_stats" in data

@pytest.mark.api
class TestMaterialAnalysisEdgeCases:
    """Test edge cases for material analysis."""
    
    async def test_analyze_materials_single_component(self, client: AsyncClient, db_session):
        """Test material analysis with single component."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {
                "cotton": 100.0
            },
            "product_name": "Pure Cotton Shirt"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["original_composition"]["cotton"] == 100.0
    
    async def test_analyze_materials_multiple_components(self, client: AsyncClient, db_session):
        """Test material analysis with multiple components."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {
                "cotton": 40.0,
                "polyester": 30.0,
                "spandex": 20.0,
                "elastane": 10.0
            },
            "product_name": "Stretch Fabric"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["original_composition"]) == 4
    
    async def test_analyze_materials_with_negative_cost(self, client: AsyncClient):
        """Test material analysis with negative cost."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {
                "cotton": 80.0,
                "polyester": 20.0
            },
            "product_name": "Test Product",
            "current_cost": -10.0  # Invalid negative cost
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_analyze_materials_with_high_target_savings(self, client: AsyncClient, db_session):
        """Test material analysis with high target savings."""
        response = await client.post("/api/v1/materials/analyze", json={
            "material_composition": {
                "silk": 100.0
            },
            "product_name": "Luxury Item",
            "current_cost": 100.0,
            "target_savings": 80.0  # 80% savings target
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "suggested_composition" in data 