import pytest
from httpx import AsyncClient
from app.db.models import Report, TariffCalculation, MaterialAnalysis, Scenario
from datetime import datetime

@pytest.mark.api
class TestReportGeneration:
    """Test report generation endpoints."""
    
    async def test_generate_tariff_summary_report(self, client: AsyncClient, db_session):
        """Test successful tariff summary report generation."""
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
        
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "tariff_summary",
            "parameters": {
                "date_range": 30,
                "country_filter": "US"
            },
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["report_type"] == "tariff_summary"
        assert data["report_id"] is not None
        assert "data" in data
        assert "summary" in data["data"]
    
    async def test_generate_material_analysis_report(self, client: AsyncClient, db_session):
        """Test successful material analysis report generation."""
        # Add test analyses
        analyses = [
            MaterialAnalysis(
                original_composition={"cotton": 80.0, "polyester": 20.0},
                suggested_composition={"cotton": 70.0, "polyester": 30.0},
                cost_savings=10.0,
                quality_impact="Minimal",
                recommendations=["Consider polyester blend"]
            )
        ]
        for analysis in analyses:
            db_session.add(analysis)
        await db_session.commit()
        
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "material_analysis",
            "parameters": {
                "material_type": "textile",
                "savings_threshold": 5.0
            },
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["report_type"] == "material_analysis"
        assert "data" in data
        assert "summary" in data["data"]
    
    async def test_generate_scenario_comparison_report(self, client: AsyncClient, db_session):
        """Test successful scenario comparison report generation."""
        # Add test scenarios
        scenarios = [
            Scenario(
                base_scenario={"hts_code": "8471.30.01", "country": "China", "material_cost": 500.0},
                modified_scenario={"hts_code": "8471.30.01", "country": "Mexico", "material_cost": 550.0},
                savings=50.0,
                percentage_change=10.0,
                risk_assessment="Low"
            )
        ]
        for scenario in scenarios:
            db_session.add(scenario)
        await db_session.commit()
        
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "scenario_comparison",
            "parameters": {
                "scenario_ids": [1],
                "comparison_metrics": ["cost", "risk"]
            },
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["report_type"] == "scenario_comparison"
        assert "data" in data
        assert "summary" in data["data"]
    
    async def test_generate_custom_report(self, client: AsyncClient, db_session):
        """Test successful custom report generation."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "custom",
            "parameters": {
                "query_type": "recent_activity",
                "filters": {"limit": 5}
            },
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["report_type"] == "custom"
        assert "data" in data
    
    async def test_generate_report_invalid_type(self, client: AsyncClient):
        """Test report generation with invalid report type."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "invalid_type",
            "parameters": {},
            "format": "json"
        })
        
        assert response.status_code == 400
    
    async def test_generate_report_missing_parameters(self, client: AsyncClient):
        """Test report generation with missing required parameters."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "custom",
            "format": "json"
        })
        
        assert response.status_code == 200  # Should still work with default parameters

@pytest.mark.api
class TestReportTypes:
    """Test report types endpoint."""
    
    async def test_get_report_types(self, client: AsyncClient):
        """Test retrieval of available report types."""
        response = await client.get("/api/v1/reports/types")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "report_types" in data["data"]
        assert data["data"]["total_types"] > 0
        
        # Check report type structure
        report_types = data["data"]["report_types"]
        assert len(report_types) > 0
        
        for report_type in report_types:
            assert "id" in report_type
            assert "name" in report_type
            assert "description" in report_type
            assert "parameters" in report_type

@pytest.mark.api
class TestReportHistory:
    """Test report history endpoints."""
    
    async def test_get_report_history(self, client: AsyncClient, db_session):
        """Test retrieval of report history."""
        # Add test reports
        reports = [
            Report(
                report_id="test-report-1",
                report_type="tariff_summary",
                parameters={"date_range": 30},
                file_path=None
            ),
            Report(
                report_id="test-report-2",
                report_type="material_analysis",
                parameters={"material_type": "textile"},
                file_path=None
            )
        ]
        for report in reports:
            db_session.add(report)
        await db_session.commit()
        
        response = await client.get("/api/v1/reports/history", params={"limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["reports"]) >= 2
    
    async def test_get_report_history_with_limit(self, client: AsyncClient, db_session):
        """Test report history with limit parameter."""
        response = await client.get("/api/v1/reports/history", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["reports"]) <= 1

@pytest.mark.api
class TestReportRetrieval:
    """Test report retrieval endpoints."""
    
    async def test_get_report_by_id_success(self, client: AsyncClient, db_session):
        """Test successful report retrieval by ID."""
        # Add test report
        report = Report(
            report_id="test-report-retrieval",
            report_type="tariff_summary",
            parameters={"date_range": 30},
            file_path=None
        )
        db_session.add(report)
        await db_session.commit()
        
        response = await client.get("/api/v1/reports/test-report-retrieval")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["report_id"] == "test-report-retrieval"
        assert data["data"]["report_type"] == "tariff_summary"
    
    async def test_get_report_by_id_not_found(self, client: AsyncClient):
        """Test report retrieval for non-existent report."""
        response = await client.get("/api/v1/reports/nonexistent-report")
        
        assert response.status_code == 404

@pytest.mark.api
class TestReportHealth:
    """Test reports health check endpoint."""
    
    async def test_reports_health(self, client: AsyncClient):
        """Test reports service health check."""
        response = await client.get("/api/v1/reports/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "reports"
        assert "status" in data
        assert "available_types" in data

@pytest.mark.api
class TestReportEdgeCases:
    """Test edge cases for report generation."""
    
    async def test_generate_report_with_empty_parameters(self, client: AsyncClient, db_session):
        """Test report generation with empty parameters."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "tariff_summary",
            "parameters": {},
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    async def test_generate_report_with_invalid_format(self, client: AsyncClient):
        """Test report generation with invalid format."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "tariff_summary",
            "parameters": {},
            "format": "invalid_format"
        })
        
        assert response.status_code == 200  # Should default to JSON
        data = response.json()
        assert data["success"] is True
    
    async def test_generate_report_with_large_date_range(self, client: AsyncClient, db_session):
        """Test report generation with large date range."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "tariff_summary",
            "parameters": {
                "date_range": 365  # One year
            },
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    async def test_generate_report_with_specific_filters(self, client: AsyncClient, db_session):
        """Test report generation with specific filters."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "tariff_summary",
            "parameters": {
                "country_filter": "China",
                "hts_code_filter": "8471"
            },
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    async def test_generate_custom_report_with_invalid_query_type(self, client: AsyncClient):
        """Test custom report generation with invalid query type."""
        response = await client.post("/api/v1/reports/generate", json={
            "report_type": "custom",
            "parameters": {
                "query_type": "invalid_query_type"
            },
            "format": "json"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should return error in data
        assert "error" in data["data"] 