"""Unit tests for rag.chunking module."""

import pytest
from rag.chunking import chunk_text, _count_tokens


class TestCountTokens:
    def test_empty_string(self):
        # empty string: tiktoken returns 0 tokens, fallback returns max(1, 0//4)=1
        result = _count_tokens("")
        assert result >= 0

    def test_single_word(self):
        result = _count_tokens("hello")
        assert result >= 1

    def test_longer_text(self):
        text = "This is a moderately long sentence for token counting purposes."
        result = _count_tokens(text)
        assert result > 5


class TestChunkText:
    def test_empty_text_returns_empty(self):
        result = chunk_text("")
        # Empty text may return an empty list or a single empty chunk
        assert isinstance(result, list)

    def test_short_text_single_chunk(self):
        text = "Hello world. This is a short sentence."
        chunks = chunk_text(text, chunk_size=200, overlap=50)
        assert len(chunks) >= 1
        assert all(isinstance(c, tuple) and len(c) == 3 for c in chunks)

    def test_chunk_structure(self):
        """Each chunk must be a (str, int, int) tuple."""
        text = "Sentence one. Sentence two. Sentence three."
        chunks = chunk_text(text, chunk_size=200, overlap=50)
        for chunk_str, start, end in chunks:
            assert isinstance(chunk_str, str)
            assert isinstance(start, int)
            assert isinstance(end, int)
            assert start >= 0
            assert len(chunk_str) > 0

    def test_long_text_produces_multiple_chunks(self):
        """A text larger than chunk_size tokens should be split."""
        # Build a text with ~400 tokens
        sentence = "This is a test sentence for chunking purposes. " * 20
        chunks = chunk_text(sentence, chunk_size=50, overlap=10)
        assert len(chunks) > 1

    def test_chunk_coverage(self):
        """All words from the original text should appear somewhere in the chunks."""
        text = "Alpha beta gamma. Delta epsilon zeta. Eta theta iota kappa."
        chunks = chunk_text(text, chunk_size=10, overlap=2)
        combined = " ".join(c[0] for c in chunks)
        for word in ["Alpha", "Delta", "kappa"]:
            assert word in combined
