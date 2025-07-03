import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.chroma_service import ChromaService

@pytest.mark.unit
class TestChromaService:
    """Test ChromaDB service functionality."""
    
    @pytest.fixture
    def chroma_service(self):
        """Create ChromaDB service instance."""
        return ChromaService()
    
    def test_init(self, chroma_service):
        """Test ChromaDB service initialization."""
        assert chroma_service.client is None
        assert chroma_service.collections == {}
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, chroma_service):
        """Test successful ChromaDB initialization."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        with patch('chromadb.PersistentClient', return_value=mock_client), \
             patch('os.makedirs'):
            
            await chroma_service.initialize()
            
            assert chroma_service.client is not None
            assert "hts_codes" in chroma_service.collections
            assert "adcvd_faq" in chroma_service.collections
            assert "materials" in chroma_service.collections
    
    @pytest.mark.asyncio
    async def test_initialize_error(self, chroma_service):
        """Test ChromaDB initialization with error."""
        with patch('chromadb.PersistentClient', side_effect=Exception("Connection error")):
            with pytest.raises(Exception) as exc_info:
                await chroma_service.initialize()
            
            assert "Connection error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_collection_success(self, chroma_service):
        """Test successful collection retrieval."""
        chroma_service.collections["hts_codes"] = MagicMock()
        
        collection = await chroma_service.get_collection("hts_codes")
        
        assert collection is not None
    
    @pytest.mark.asyncio
    async def test_get_collection_not_found(self, chroma_service):
        """Test collection retrieval when not found."""
        with pytest.raises(ValueError) as exc_info:
            await chroma_service.get_collection("nonexistent")
        
        assert "Collection 'nonexistent' not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_hts_codes_success(self, chroma_service):
        """Test successful HTS codes search."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "metadatas": [[
                {
                    "hts_code": "8471.30.01",
                    "description": "Laptop computers",
                    "tariff_rate": 0.0,
                    "country_origin": "US"
                }
            ]],
            "distances": [[0.1]]
        }
        chroma_service.collections["hts_codes"] = mock_collection
        
        result = await chroma_service.search_hts_codes("laptop", 5)
        
        assert len(result) == 1
        assert result[0]["hts_code"] == "8471.30.01"
        assert result[0]["description"] == "Laptop computers"
        assert result[0]["similarity_score"] == 0.9  # 1 - 0.1
    
    @pytest.mark.asyncio
    async def test_search_hts_codes_empty_results(self, chroma_service):
        """Test HTS codes search with no results."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "metadatas": [[]],
            "distances": [[]]
        }
        chroma_service.collections["hts_codes"] = mock_collection
        
        result = await chroma_service.search_hts_codes("nonexistent", 5)
        
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_search_hts_codes_error(self, chroma_service):
        """Test HTS codes search with error."""
        mock_collection = MagicMock()
        mock_collection.query.side_effect = Exception("Search error")
        chroma_service.collections["hts_codes"] = mock_collection
        
        result = await chroma_service.search_hts_codes("laptop", 5)
        
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_search_adcvd_faq_success(self, chroma_service):
        """Test successful AD/CVD FAQ search."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "metadatas": [[
                {
                    "question": "What are antidumping duties?",
                    "answer": "Antidumping duties are tariffs on imports"
                }
            ]],
            "distances": [[0.2]]
        }
        chroma_service.collections["adcvd_faq"] = mock_collection
        
        result = await chroma_service.search_adcvd_faq("antidumping", 3)
        
        assert len(result) == 1
        assert result[0]["question"] == "What are antidumping duties?"
        assert result[0]["answer"] == "Antidumping duties are tariffs on imports"
        assert result[0]["similarity_score"] == 0.8  # 1 - 0.2
    
    @pytest.mark.asyncio
    async def test_search_materials_success(self, chroma_service):
        """Test successful materials search."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "metadatas": [[
                {
                    "material_name": "Cotton Fabric",
                    "composition": {"cotton": 100.0},
                    "tariff_impact": 0.0,
                    "alternatives": ["Polyester blend"]
                }
            ]],
            "distances": [[0.15]]
        }
        chroma_service.collections["materials"] = mock_collection
        
        result = await chroma_service.search_materials("cotton", 3)
        
        assert len(result) == 1
        assert result[0]["material_name"] == "Cotton Fabric"
        assert result[0]["composition"] == {"cotton": 100.0}
        assert result[0]["similarity_score"] == 0.85  # 1 - 0.15
    
    @pytest.mark.asyncio
    async def test_add_hts_codes_success(self, chroma_service):
        """Test successful HTS codes addition."""
        mock_collection = MagicMock()
        chroma_service.collections["hts_codes"] = mock_collection
        
        hts_data = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers",
                "tariff_rate": 0.0,
                "country_origin": "US"
            }
        ]
        
        await chroma_service.add_hts_codes(hts_data)
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert len(call_args[1]["documents"]) == 1
        assert len(call_args[1]["metadatas"]) == 1
        assert len(call_args[1]["ids"]) == 1
        assert call_args[1]["metadatas"][0]["hts_code"] == "8471.30.01"
    
    @pytest.mark.asyncio
    async def test_add_hts_codes_empty_data(self, chroma_service):
        """Test HTS codes addition with empty data."""
        mock_collection = MagicMock()
        chroma_service.collections["hts_codes"] = mock_collection
        
        await chroma_service.add_hts_codes([])
        
        mock_collection.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_add_hts_codes_error(self, chroma_service):
        """Test HTS codes addition with error."""
        mock_collection = MagicMock()
        mock_collection.add.side_effect = Exception("Add error")
        chroma_service.collections["hts_codes"] = mock_collection
        
        hts_data = [
            {
                "hts_code": "8471.30.01",
                "description": "Laptop computers"
            }
        ]
        
        # Should not raise exception, just log error
        await chroma_service.add_hts_codes(hts_data)
    
    @pytest.mark.asyncio
    async def test_add_materials_success(self, chroma_service):
        """Test successful materials addition."""
        mock_collection = MagicMock()
        chroma_service.collections["materials"] = mock_collection
        
        materials_data = [
            {
                "name": "Cotton Fabric",
                "composition": {"cotton": 100.0},
                "tariff_impact": 0.0,
                "alternatives": ["Polyester blend"]
            }
        ]
        
        await chroma_service.add_materials(materials_data)
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert len(call_args[1]["documents"]) == 1
        assert len(call_args[1]["metadatas"]) == 1
        assert len(call_args[1]["ids"]) == 1
        assert call_args[1]["metadatas"][0]["material_name"] == "Cotton Fabric"
    
    @pytest.mark.asyncio
    async def test_add_materials_empty_data(self, chroma_service):
        """Test materials addition with empty data."""
        mock_collection = MagicMock()
        chroma_service.collections["materials"] = mock_collection
        
        await chroma_service.add_materials([])
        
        mock_collection.add.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_reset_collection_success(self, chroma_service):
        """Test successful collection reset."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        chroma_service.client = mock_client
        chroma_service.collections["hts_codes"] = mock_collection
        
        with patch.object(chroma_service, '_init_collections'):
            await chroma_service.reset_collection("hts_codes")
            
            mock_client.delete_collection.assert_called_once_with("hts_codes")
    
    @pytest.mark.asyncio
    async def test_reset_collection_not_found(self, chroma_service):
        """Test collection reset when collection not found."""
        await chroma_service.reset_collection("nonexistent")
        # Should not raise exception, just log warning
    
    @pytest.mark.asyncio
    async def test_get_collection_stats_success(self, chroma_service):
        """Test successful collection statistics retrieval."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 100
        mock_collection.metadata = {"description": "Test collection"}
        chroma_service.collections["hts_codes"] = mock_collection
        
        result = await chroma_service.get_collection_stats("hts_codes")
        
        assert result["collection_name"] == "hts_codes"
        assert result["document_count"] == 100
        assert result["metadata"]["description"] == "Test collection"
    
    @pytest.mark.asyncio
    async def test_get_collection_stats_error(self, chroma_service):
        """Test collection statistics retrieval with error."""
        mock_collection = MagicMock()
        mock_collection.count.side_effect = Exception("Stats error")
        chroma_service.collections["hts_codes"] = mock_collection
        
        result = await chroma_service.get_collection_stats("hts_codes")
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_search_with_missing_metadata(self, chroma_service):
        """Test search with missing metadata fields."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "metadatas": [[
                {
                    "hts_code": "8471.30.01"
                    # Missing other fields
                }
            ]],
            "distances": [[0.1]]
        }
        chroma_service.collections["hts_codes"] = mock_collection
        
        result = await chroma_service.search_hts_codes("laptop", 5)
        
        assert len(result) == 1
        assert result[0]["hts_code"] == "8471.30.01"
        assert result[0]["description"] == ""  # Default value
        assert result[0]["tariff_rate"] == 0.0  # Default value
    
    @pytest.mark.asyncio
    async def test_search_with_missing_distances(self, chroma_service):
        """Test search with missing distances."""
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "metadatas": [[
                {
                    "hts_code": "8471.30.01",
                    "description": "Laptop computers"
                }
            ]],
            "distances": None  # Missing distances
        }
        chroma_service.collections["hts_codes"] = mock_collection
        
        result = await chroma_service.search_hts_codes("laptop", 5)
        
        assert len(result) == 1
        assert result[0]["similarity_score"] == 0.0  # Default value
    
    @pytest.mark.asyncio
    async def test_add_hts_codes_with_missing_fields(self, chroma_service):
        """Test adding HTS codes with missing fields."""
        mock_collection = MagicMock()
        chroma_service.collections["hts_codes"] = mock_collection
        
        hts_data = [
            {
                "hts_code": "8471.30.01"
                # Missing description and other fields
            }
        ]
        
        await chroma_service.add_hts_codes(hts_data)
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        metadata = call_args[1]["metadatas"][0]
        assert metadata["hts_code"] == "8471.30.01"
        assert metadata["description"] == ""  # Default value
        assert metadata["tariff_rate"] == 0.0  # Default value
        assert metadata["country_origin"] == "US"  # Default value
    
    @pytest.mark.asyncio
    async def test_add_materials_with_missing_fields(self, chroma_service):
        """Test adding materials with missing fields."""
        mock_collection = MagicMock()
        chroma_service.collections["materials"] = mock_collection
        
        materials_data = [
            {
                "name": "Cotton Fabric"
                # Missing composition and other fields
            }
        ]
        
        await chroma_service.add_materials(materials_data)
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        metadata = call_args[1]["metadatas"][0]
        assert metadata["material_name"] == "Cotton Fabric"
        assert metadata["composition"] == {}  # Default value
        assert metadata["tariff_impact"] == 0.0  # Default value
        assert metadata["alternatives"] == []  # Default value 