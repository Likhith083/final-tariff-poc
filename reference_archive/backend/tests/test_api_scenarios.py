import pytest
from httpx import AsyncClient
from app.db.models import Scenario
from datetime import datetime

@pytest.mark.api
class TestScenarioSimulation:
    """Test scenario simulation endpoints."""
    
    async def test_simulate_scenario_success(self, client: AsyncClient, db_session):
        """Test successful scenario simulation."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "8471.30.01",
                "country": "China",
                "material_cost": 500.0
            },
            "changes": {
                "country": "Mexico"
            },
            "scenario_name": "Test Scenario"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["base_scenario"]["hts_code"] == "8471.30.01"
        assert data["base_scenario"]["country"] == "China"
        assert data["base_scenario"]["material_cost"] == 500.0
        assert "modified_scenario" in data
        assert "savings" in data
        assert "percentage_change" in data
    
    async def test_simulate_scenario_missing_base_scenario(self, client: AsyncClient):
        """Test scenario simulation with missing base scenario."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "changes": {
                "country": "Mexico"
            }
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_simulate_scenario_missing_changes(self, client: AsyncClient):
        """Test scenario simulation with missing changes."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "8471.30.01",
                "country": "China",
                "material_cost": 500.0
            }
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_simulate_scenario_country_change(self, client: AsyncClient, db_session):
        """Test scenario simulation with country change."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "8471.30.01",
                "country": "China",
                "material_cost": 500.0
            },
            "changes": {
                "country": "Mexico"
            },
            "scenario_name": "Country Change Scenario"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["base_scenario"]["country"] == "China"
        assert "modified_scenario" in data
    
    async def test_simulate_scenario_material_change(self, client: AsyncClient, db_session):
        """Test scenario simulation with material composition change."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "4015.19.05",
                "country": "China",
                "material_cost": 100.0
            },
            "changes": {
                "material_composition": {"cotton": 80, "polyester": 20}
            },
            "scenario_name": "Material Change Scenario"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modified_scenario" in data
    
    async def test_simulate_scenario_volume_change(self, client: AsyncClient, db_session):
        """Test scenario simulation with volume change."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "8471.30.01",
                "country": "China",
                "material_cost": 500.0
            },
            "changes": {
                "volume": "large",
                "discount_rate": 0.15
            },
            "scenario_name": "Volume Discount Scenario"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modified_scenario" in data

@pytest.mark.api
class TestScenarioComparison:
    """Test scenario comparison endpoints."""
    
    async def test_compare_scenarios_success(self, client: AsyncClient):
        """Test successful scenario comparison."""
        response = await client.post("/api/v1/scenarios/compare", json={
            "scenarios": [
                {
                    "hts_code": "8471.30.01",
                    "country": "China",
                    "material_cost": 500.0,
                    "name": "China Scenario"
                },
                {
                    "hts_code": "8471.30.01",
                    "country": "Mexico",
                    "material_cost": 550.0,
                    "name": "Mexico Scenario"
                },
                {
                    "hts_code": "8471.30.01",
                    "country": "Vietnam",
                    "material_cost": 480.0,
                    "name": "Vietnam Scenario"
                }
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["scenarios"]) == 3
        assert "best_scenario" in data["data"]
        assert data["data"]["total_scenarios"] == 3
    
    async def test_compare_scenarios_empty_list(self, client: AsyncClient):
        """Test scenario comparison with empty scenarios list."""
        response = await client.post("/api/v1/scenarios/compare", json={
            "scenarios": []
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_compare_scenarios_single_scenario(self, client: AsyncClient):
        """Test scenario comparison with single scenario."""
        response = await client.post("/api/v1/scenarios/compare", json={
            "scenarios": [
                {
                    "hts_code": "8471.30.01",
                    "country": "China",
                    "material_cost": 500.0,
                    "name": "Single Scenario"
                }
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["scenarios"]) == 1
        assert data["data"]["best_scenario"] is not None
    
    async def test_compare_scenarios_with_errors(self, client: AsyncClient):
        """Test scenario comparison with some scenarios having errors."""
        response = await client.post("/api/v1/scenarios/compare", json={
            "scenarios": [
                {
                    "hts_code": "8471.30.01",
                    "country": "China",
                    "material_cost": 500.0,
                    "name": "Valid Scenario"
                },
                {
                    "hts_code": "9999.99.99",  # Invalid HTS code
                    "country": "Invalid",
                    "material_cost": 100.0,
                    "name": "Invalid Scenario"
                }
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["scenarios"]) == 2
        # Check that one scenario has an error
        scenarios_with_errors = [s for s in data["data"]["scenarios"] if "error" in s]
        assert len(scenarios_with_errors) >= 1

@pytest.mark.api
class TestScenarioHistory:
    """Test scenario history endpoints."""
    
    async def test_get_scenario_history(self, client: AsyncClient, db_session):
        """Test retrieval of scenario history."""
        # Add test scenarios
        scenarios = [
            Scenario(
                base_scenario={"hts_code": "8471.30.01", "country": "China", "material_cost": 500.0},
                modified_scenario={"hts_code": "8471.30.01", "country": "Mexico", "material_cost": 550.0},
                savings=50.0,
                percentage_change=10.0,
                risk_assessment="Low"
            ),
            Scenario(
                base_scenario={"hts_code": "4015.19.05", "country": "China", "material_cost": 100.0},
                modified_scenario={"hts_code": "4015.19.05", "country": "Vietnam", "material_cost": 90.0},
                savings=10.0,
                percentage_change=-10.0,
                risk_assessment="Medium"
            )
        ]
        for scenario in scenarios:
            db_session.add(scenario)
        await db_session.commit()
        
        response = await client.get("/api/v1/scenarios/history", params={"limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["scenarios"]) >= 2
    
    async def test_get_scenario_history_with_limit(self, client: AsyncClient, db_session):
        """Test scenario history with limit parameter."""
        response = await client.get("/api/v1/scenarios/history", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["scenarios"]) <= 1

@pytest.mark.api
class TestScenarioTemplates:
    """Test scenario templates endpoints."""
    
    async def test_get_scenario_templates(self, client: AsyncClient):
        """Test retrieval of scenario templates."""
        response = await client.get("/api/v1/scenarios/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "templates" in data["data"]
        assert data["data"]["total_templates"] > 0
        
        # Check template structure
        templates = data["data"]["templates"]
        assert len(templates) > 0
        
        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "base_scenario" in template
            assert "changes" in template

@pytest.mark.api
class TestScenarioHealth:
    """Test scenario simulation health check endpoint."""
    
    async def test_scenarios_health(self, client: AsyncClient):
        """Test scenario simulation service health check."""
        response = await client.get("/api/v1/scenarios/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "scenario_simulation"
        assert "status" in data
        assert "hts_statistics" in data

@pytest.mark.api
class TestScenarioEdgeCases:
    """Test edge cases for scenario simulation."""
    
    async def test_simulate_scenario_with_zero_cost(self, client: AsyncClient, db_session):
        """Test scenario simulation with zero material cost."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "8471.30.01",
                "country": "China",
                "material_cost": 0.0
            },
            "changes": {
                "country": "Mexico"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    async def test_simulate_scenario_with_negative_cost(self, client: AsyncClient):
        """Test scenario simulation with negative material cost."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "8471.30.01",
                "country": "China",
                "material_cost": -100.0  # Invalid negative cost
            },
            "changes": {
                "country": "Mexico"
            }
        })
        
        assert response.status_code == 422  # Validation error
    
    async def test_simulate_scenario_with_multiple_changes(self, client: AsyncClient, db_session):
        """Test scenario simulation with multiple changes."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "8471.30.01",
                "country": "China",
                "material_cost": 500.0
            },
            "changes": {
                "country": "Mexico",
                "material_composition": {"cotton": 80, "polyester": 20},
                "volume": "large"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modified_scenario" in data
    
    async def test_simulate_scenario_with_invalid_hts_code(self, client: AsyncClient, db_session):
        """Test scenario simulation with invalid HTS code."""
        response = await client.post("/api/v1/scenarios/simulate", json={
            "base_scenario": {
                "hts_code": "9999.99.99",  # Invalid HTS code
                "country": "China",
                "material_cost": 500.0
            },
            "changes": {
                "country": "Mexico"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        # Should still succeed but with limited data
        assert data["success"] is True 