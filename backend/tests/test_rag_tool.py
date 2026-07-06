"""
Tests for the local RAG nutrition knowledge tool.
Verifies chunking, cosine similarity, and matching logic.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.tools.rag_tool import chunk_text, cosine_similarity, search_nutrition_knowledge


@pytest.fixture(autouse=True)
def mock_settings_key(monkeypatch):
    """
    Dummy API Key to bypass client instantiation crash.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")


def test_chunk_text_basic():
    """
    Verifies chunking splits words correctly and contains the specified overlap.
    """
    text = "one two three four five six seven eight nine ten"
    # Chunk size: 4, overlap: 1
    # Expected chunks:
    # 1: "one two three four"
    # 2: "four five six seven"
    # 3: "seven eight nine ten"
    chunks = chunk_text(text, chunk_size=4, overlap=1)
    
    assert len(chunks) == 3
    assert chunks[0] == "one two three four"
    assert chunks[1] == "four five six seven"
    assert chunks[2] == "seven eight nine ten"


def test_cosine_similarity():
    """
    Verifies cosine similarity calculations.
    """
    vec_a = [1.0, 0.0]
    vec_b = [0.0, 1.0]
    vec_c = [1.0, 1.0]
    
    # Orthogonal vectors: similarity should be 0.0
    assert cosine_similarity(vec_a, vec_b) == 0.0
    
    # Identical vectors: similarity should be 1.0
    assert abs(cosine_similarity(vec_a, vec_a) - 1.0) < 1e-6
    
    # 45 degrees: similarity should be 1 / sqrt(2) ≈ 0.7071
    sim = cosine_similarity(vec_a, vec_c)
    assert abs(sim - 0.70710678) < 1e-5


@pytest.mark.asyncio
async def test_search_nutrition_knowledge_no_docs():
    """
    Ensure it returns empty string if no docs are found.
    """
    with patch("src.agents.tools.rag_tool.glob.glob", return_value=[]):
        result = await search_nutrition_knowledge("protein requirement")
        assert result == ""


@pytest.mark.asyncio
async def test_search_nutrition_knowledge_threshold():
    """
    Verify search matches chunks based on embedding similarity and threshold filtering.
    """
    # Create simple in-memory vector store items manually
    mock_store = [
        {"text": "Protein builds muscle.", "embedding": [1.0, 0.0]},
        {"text": "Drink water for hydration.", "embedding": [0.0, 1.0]}
    ]
    
    with patch("src.agents.tools.rag_tool._vector_store", mock_store):
        with patch("src.agents.tools.rag_tool.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Query embedding is at 45 degrees to [1.0, 0.0], yielding ~0.707 similarity
            mock_emb_values = [0.70710678, 0.70710678]
            mock_emb_obj = MagicMock()
            mock_emb_obj.values = mock_emb_values
            
            mock_response = MagicMock()
            mock_response.embeddings = [mock_emb_obj]
            
            mock_client.aio.models.embed_content = AsyncMock(return_value=mock_response)
            
            # Threshold 0.6: similarity 0.707 >= 0.6, should return chunk
            result = await search_nutrition_knowledge("muscle building", threshold=0.6)
            assert result == "Protein builds muscle."
            
            # Threshold 0.8: similarity 0.707 < 0.8, should filter out and return empty string
            result_filtered = await search_nutrition_knowledge("muscle building", threshold=0.8)
            assert result_filtered == ""
