import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.hts_service import HTSService
from app.db.models import HTSCode
from datetime import datetime

@pytest.mark.unit
class TestHTSService:
    """Test HTS service functionality."""
    
    @pytest.fixture
    def hts_service(self):
        """Create HTS service instance."""
        return HTSService()
    
    def test_init(self, hts_service):
        """Test HTS service initialization."""
        assert hts_service.chroma_service is not None
    
    @pytest.mark.asyncio
    async def test_has_data_true(self, hts_service):
        """Test checking if data exists when it does."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = HTSCode(
            hts_code="8471.30.01",
            description="Test",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service._has_data()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_has_data_false(self, hts_service):
        """Test checking if data exists when it doesn't."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service._has_data()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_search_hts_codes_success(self, hts_service):
        """Test successful HTS code search."""
        # Mock ChromaDB results
        chroma_results = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers",
                "tariff_rate": 0.0,
                "country_origin": "US",
                "similarity_score": 0.95
            }
        ]
        
        # Mock database results
        db_results = [
            {
                "hts_code": "8471.30.02",
                "description": "Desktop computers",
                "tariff_rate": 2.5,
                "country_origin": "US",
                "similarity_score": 1.0
            }
        ]
        
        with patch.object(hts_service.chroma_service, 'search_hts_codes', return_value=chroma_results), \
             patch.object(hts_service, '_search_database', return_value=db_results):
            
            result = await hts_service.search_hts_codes("laptop", 10)
            
            assert len(result) == 2
            # Should combine and deduplicate results
            hts_codes = [r["hts_code"] for r in result]
            assert "8471.30.01" in hts_codes
            assert "8471.30.02" in hts_codes
    
    @pytest.mark.asyncio
    async def test_search_hts_codes_empty_results(self, hts_service):
        """Test HTS code search with no results."""
        with patch.object(hts_service.chroma_service, 'search_hts_codes', return_value=[]), \
             patch.object(hts_service, '_search_database', return_value=[]):
            
            result = await hts_service.search_hts_codes("nonexistent", 10)
            
            assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_search_database_hts_code_query(self, hts_service):
        """Test database search with HTS code query."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_hts = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        mock_result.scalars.return_value.all.return_value = [mock_hts]
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service._search_database("8471.30.01", 10)
            
            assert len(result) == 1
            assert result[0]["hts_code"] == "8471.30.01"
            assert result[0]["similarity_score"] == 1.0
    
    @pytest.mark.asyncio
    async def test_search_database_description_query(self, hts_service):
        """Test database search with description query."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_hts = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        mock_result.scalars.return_value.all.return_value = [mock_hts]
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service._search_database("laptop", 10)
            
            assert len(result) == 1
            assert result[0]["hts_code"] == "8471.30.01"
    
    @pytest.mark.asyncio
    async def test_get_hts_code_success(self, hts_service):
        """Test successful HTS code retrieval."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_hts = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers",
            tariff_rate=0.0,
            country_origin="US",
            effective_date=datetime.now()
        )
        mock_result.scalar_one_or_none.return_value = mock_hts
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service.get_hts_code("8471.30.01")
            
            assert result["hts_code"] == "8471.30.01"
            assert result["description"] == "Laptop computers"
            assert result["tariff_rate"] == 0.0
            assert result["country_origin"] == "US"
    
    @pytest.mark.asyncio
    async def test_get_hts_code_not_found(self, hts_service):
        """Test HTS code retrieval when not found."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service.get_hts_code("9999.99.99")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_tariff_rate_success(self, hts_service):
        """Test successful tariff rate retrieval."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_hts = HTSCode(
            hts_code="8471.30.01",
            description="Laptop computers",
            tariff_rate=2.5,
            country_origin="US",
            effective_date=datetime.now()
        )
        mock_result.scalar_one_or_none.return_value = mock_hts
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service.get_tariff_rate("8471.30.01", "US")
            
            assert result == 2.5
    
    @pytest.mark.asyncio
    async def test_get_tariff_rate_not_found(self, hts_service):
        """Test tariff rate retrieval when not found."""
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service.get_tariff_rate("9999.99.99", "US")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_update_tariff_rate_success(self, hts_service):
        """Test successful tariff rate update."""
        mock_session = AsyncMock()
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            await hts_service.update_tariff_rate("8471.30.01", 5.0, "US")
            
            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_statistics_success(self, hts_service):
        """Test successful statistics retrieval."""
        mock_session = AsyncMock()
        
        # Mock total count result
        mock_total_result = AsyncMock()
        mock_total_result.scalars.return_value.all.return_value = [MagicMock()] * 10
        mock_session.execute.return_value = mock_total_result
        
        # Mock average rate result
        mock_avg_result = AsyncMock()
        mock_avg_result.scalars.return_value.all.return_value = [2.5, 3.0, 1.5]
        mock_session.execute.return_value = mock_avg_result
        
        # Mock countries result
        mock_countries_result = AsyncMock()
        mock_countries_result.scalars.return_value.all.return_value = ["US", "China", "Mexico"]
        mock_session.execute.return_value = mock_countries_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service.get_statistics()
            
            assert result["total_hts_codes"] == 10
            assert result["average_tariff_rate"] == 2.33  # (2.5 + 3.0 + 1.5) / 3
            assert len(result["countries"]) == 3
            assert "US" in result["countries"]
            assert "last_updated" in result
    
    @pytest.mark.asyncio
    async def test_get_statistics_empty_data(self, hts_service):
        """Test statistics retrieval with empty data."""
        mock_session = AsyncMock()
        
        # Mock empty results
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        with patch('app.services.hts_service.AsyncSessionLocal') as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            
            result = await hts_service.get_statistics()
            
            assert result["total_hts_codes"] == 0
            assert result["average_tariff_rate"] == 0
            assert len(result["countries"]) == 0
    
    def test_combine_search_results(self, hts_service):
        """Test combining and deduplicating search results."""
        chroma_results = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers",
                "similarity_score": 0.8
            }
        ]
        
        db_results = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers",
                "similarity_score": 0.9  # Higher score
            },
            {
                "hts_code": "8471.30.02",
                "description": "Desktop computers",
                "similarity_score": 0.7
            }
        ]
        
        result = hts_service._combine_search_results(chroma_results, db_results)
        
        assert len(result) == 2
        # Should keep the higher similarity score for 8471.30.01
        hts_8471 = next(r for r in result if r["hts_code"] == "8471.30.01")
        assert hts_8471["similarity_score"] == 0.9
        # Should include the new code
        hts_8472 = next(r for r in result if r["hts_code"] == "8471.30.02")
        assert hts_8472["similarity_score"] == 0.7
    
    def test_combine_search_results_empty(self, hts_service):
        """Test combining search results with empty inputs."""
        result = hts_service._combine_search_results([], [])
        
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_load_tariff_data_already_exists(self, hts_service):
        """Test loading tariff data when it already exists."""
        with patch.object(hts_service, '_has_data', return_value=True):
            await hts_service.load_tariff_data()
            # Should not process data if it already exists
    
    @pytest.mark.asyncio
    async def test_load_tariff_data_new_data(self, hts_service):
        """Test loading new tariff data."""
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, {
                'HTS Code': '8471.30.01',
                'Description': 'Laptop computers',
                'Tariff Rate': 0.0,
                'Country': 'US'
            })
        ]
        
        with patch.object(hts_service, '_has_data', return_value=False), \
             patch('pandas.read_excel', return_value=mock_df), \
             patch.object(hts_service, '_process_tariff_data') as mock_process:
            
            await hts_service.load_tariff_data()
            
            mock_process.assert_called_once_with(mock_df) 