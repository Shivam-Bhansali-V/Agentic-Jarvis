"""Unit tests for tools.rag_tools and rag.store query interface."""

import pytest
from unittest.mock import patch, MagicMock


class TestRagQueryTool:
    """Tests for the rag_query LangChain tool."""

    def test_rag_query_returns_expected_keys(self):
        """rag_query must return a dict with 'chunks', 'sources', 'distances'."""
        mock_result = {
            "chunks": ["Shivam is a B.Tech student at VIT Vellore."],
            "sources": ["identity_and_background.txt"],
            "distances": [0.12],
        }
        with patch("rag.store.query", return_value=mock_result):
            from tools.rag_tools import rag_query
            result = rag_query.invoke({"query": "Who is Shivam?", "k": 1})

        assert "chunks" in result
        assert "sources" in result
        assert "distances" in result

    def test_rag_query_chunks_are_strings(self):
        mock_result = {
            "chunks": ["chunk one", "chunk two"],
            "sources": ["file1.txt", "file2.txt"],
            "distances": [0.1, 0.2],
        }
        with patch("rag.store.query", return_value=mock_result):
            from tools.rag_tools import rag_query
            result = rag_query.invoke({"query": "test query", "k": 2})

        assert all(isinstance(c, str) for c in result["chunks"])

    def test_rag_query_sources_match_chunks(self):
        mock_result = {
            "chunks": ["a", "b", "c"],
            "sources": ["f1.txt", "f2.txt", "f3.txt"],
            "distances": [0.1, 0.2, 0.3],
        }
        with patch("rag.store.query", return_value=mock_result):
            from tools.rag_tools import rag_query
            result = rag_query.invoke({"query": "anything", "k": 3})

        assert len(result["chunks"]) == len(result["sources"])

    def test_rag_query_default_k(self):
        """Default k=3 should call store.query with k=3."""
        mock_result = {"chunks": [], "sources": [], "distances": []}
        with patch("rag.store.query", return_value=mock_result) as mock_q:
            from tools.rag_tools import rag_query
            rag_query.invoke({"query": "test"})
            mock_q.assert_called_once_with(query_text="test", k=3)


class TestRagQueryInput:
    def test_schema_has_query_field(self):
        from tools.rag_tools import RagQueryInput
        schema = RagQueryInput.model_json_schema()
        assert "query" in schema["properties"]

    def test_schema_has_k_field(self):
        from tools.rag_tools import RagQueryInput
        schema = RagQueryInput.model_json_schema()
        assert "k" in schema["properties"]
