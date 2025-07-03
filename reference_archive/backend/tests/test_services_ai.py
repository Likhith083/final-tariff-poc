import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai_service import AIService

@pytest.mark.unit
class TestAIService:
    """Test AI service functionality."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance."""
        return AIService()
    
    def test_init(self, ai_service):
        """Test AI service initialization."""
        assert ai_service.base_url == "http://localhost:11434"
        assert ai_service.model == "llama3.2:3b"
        assert ai_service.client is not None
    
    @pytest.mark.asyncio
    async def test_build_prompt_without_context(self, ai_service):
        """Test prompt building without context."""
        prompt = "What is the tariff rate for laptops?"
        full_prompt = ai_service._build_prompt(prompt)
        
        assert "TariffAI" in full_prompt
        assert "intelligent assistant" in full_prompt
        assert prompt in full_prompt
        assert "Context Information:" not in full_prompt
    
    @pytest.mark.asyncio
    async def test_build_prompt_with_context(self, ai_service):
        """Test prompt building with context."""
        prompt = "What is the tariff rate for laptops?"
        context = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers"
            },
            {
                "question": "What are HTS codes?",
                "answer": "Harmonized Tariff Schedule codes"
            }
        ]
        
        full_prompt = ai_service._build_prompt(prompt, context)
        
        assert "Context Information:" in full_prompt
        assert "8471.30.01" in full_prompt
        assert "Laptop computers" in full_prompt
        assert "What are HTS codes?" in full_prompt
    
    @pytest.mark.asyncio
    async def test_call_ollama_success(self, ai_service):
        """Test successful Ollama API call."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "The tariff rate for laptops is 0%",
            "confidence": 0.9,
            "prompt_eval_count": 100,
            "eval_count": 50
        }
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            result = await ai_service._call_ollama("Test prompt")
            
            assert result["response"] == "The tariff rate for laptops is 0%"
            assert result["confidence"] == 0.9
            assert result["prompt_eval_count"] == 100
            assert result["eval_count"] == 50
    
    @pytest.mark.asyncio
    async def test_call_ollama_error(self, ai_service):
        """Test Ollama API call with error."""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            with pytest.raises(Exception) as exc_info:
                await ai_service._call_ollama("Test prompt")
            
            assert "Ollama API returned status 500" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, ai_service):
        """Test successful response generation."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "The tariff rate for laptops is 0%",
            "confidence": 0.9,
            "prompt_eval_count": 100,
            "eval_count": 50
        }
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            result = await ai_service.generate_response("What is the tariff rate for laptops?")
            
            assert result["response"] == "The tariff rate for laptops is 0%"
            assert result["confidence"] == 0.9
            assert result["model"] == "llama3.2:3b"
            assert result["prompt_tokens"] == 100
            assert result["response_tokens"] == 50
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, ai_service):
        """Test response generation with context."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Based on the HTS code 8471.30.01, the tariff rate is 0%",
            "confidence": 0.95,
            "prompt_eval_count": 150,
            "eval_count": 75
        }
        
        context = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers"
            }
        ]
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            result = await ai_service.generate_response(
                "What is the tariff rate for laptops?",
                context
            )
            
            assert result["response"] == "Based on the HTS code 8471.30.01, the tariff rate is 0%"
            assert result["confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_generate_response_error(self, ai_service):
        """Test response generation with error."""
        with patch.object(ai_service.client, 'post', side_effect=Exception("Network error")):
            result = await ai_service.generate_response("Test prompt")
            
            assert "I apologize, but I encountered an error" in result["response"]
            assert result["confidence"] == 0.0
            assert result["error"] == "Network error"
    
    @pytest.mark.asyncio
    async def test_classify_product_success(self, ai_service):
        """Test successful product classification."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"primary_hts_code": "8471.30.01", "explanation": "Laptop computers", "alternatives": ["8471.30.02"], "considerations": ["Check weight limit"]}',
            "confidence": 0.9
        }
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            result = await ai_service.classify_product("Laptop computer with Intel processor")
            
            assert result["success"] is True
            assert result["classification"]["primary_hts_code"] == "8471.30.01"
            assert result["classification"]["explanation"] == "Laptop computers"
            assert result["classification"]["alternatives"] == ["8471.30.02"]
            assert result["classification"]["considerations"] == ["Check weight limit"]
    
    @pytest.mark.asyncio
    async def test_classify_product_invalid_json(self, ai_service):
        """Test product classification with invalid JSON response."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is not valid JSON",
            "confidence": 0.9
        }
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            result = await ai_service.classify_product("Laptop computer")
            
            assert result["success"] is False
            assert result["response"] == "This is not valid JSON"
    
    @pytest.mark.asyncio
    async def test_analyze_materials_success(self, ai_service):
        """Test successful material analysis."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"current_analysis": {"tariff_impact": "Low", "estimated_rate": "2.5%"}, "alternatives": [{"composition": {"cotton": 70, "polyester": 30}, "cost_savings": "15%", "quality_impact": "Minimal", "implementation": "Easy"}], "recommendations": ["Consider polyester blend"]}',
            "confidence": 0.85
        }
        
        material_composition = {"cotton": 80.0, "polyester": 20.0}
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            result = await ai_service.analyze_materials(material_composition)
            
            assert result["success"] is True
            assert result["analysis"]["current_analysis"]["tariff_impact"] == "Low"
            assert result["analysis"]["alternatives"][0]["cost_savings"] == "15%"
            assert result["analysis"]["recommendations"] == ["Consider polyester blend"]
    
    @pytest.mark.asyncio
    async def test_simulate_scenario_success(self, ai_service):
        """Test successful scenario simulation."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"new_calculation": {"new_tariff_rate": "0%", "new_tariff_amount": "$0", "new_total_cost": "$550"}, "impact": {"cost_change": "$50", "percentage_change": "10%", "savings": false}, "risk_assessment": "Low", "recommendations": ["Consider volume discounts"]}',
            "confidence": 0.8
        }
        
        base_scenario = {
            "hts_code": "8471.30.01",
            "country": "China",
            "material_cost": 500.0
        }
        changes = {"country": "Mexico"}
        
        with patch.object(ai_service.client, 'post', return_value=mock_response):
            result = await ai_service.simulate_scenario(base_scenario, changes)
            
            assert result["success"] is True
            assert result["simulation"]["new_calculation"]["new_tariff_rate"] == "0%"
            assert result["simulation"]["impact"]["cost_change"] == "$50"
            assert result["simulation"]["risk_assessment"] == "Low"
    
    @pytest.mark.asyncio
    async def test_check_health_success(self, ai_service):
        """Test successful health check."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:3b"},
                {"name": "llama3.2:7b"}
            ]
        }
        
        with patch.object(ai_service.client, 'get', return_value=mock_response):
            result = await ai_service.check_health()
            
            assert result["healthy"] is True
            assert "llama3.2:3b" in result["available_models"]
            assert result["target_model"] == "llama3.2:3b"
            assert result["model_available"] is True
    
    @pytest.mark.asyncio
    async def test_check_health_model_not_available(self, ai_service):
        """Test health check when target model is not available."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:7b"}
            ]
        }
        
        with patch.object(ai_service.client, 'get', return_value=mock_response):
            result = await ai_service.check_health()
            
            assert result["healthy"] is True
            assert result["target_model"] == "llama3.2:3b"
            assert result["model_available"] is False
    
    @pytest.mark.asyncio
    async def test_check_health_error(self, ai_service):
        """Test health check with error."""
        with patch.object(ai_service.client, 'get', side_effect=Exception("Connection error")):
            result = await ai_service.check_health()
            
            assert result["healthy"] is False
            assert "Connection error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_close(self, ai_service):
        """Test closing the AI service."""
        with patch.object(ai_service.client, 'aclose') as mock_close:
            await ai_service.close()
            mock_close.assert_called_once() 