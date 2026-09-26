"""Embedding wrapper for the RAG pipeline using ChromaDB's built-in ONNX embedder.

Uses chromadb.utils.embedding_functions.DefaultEmbeddingFunction which is based on
ONNX Runtime (no TensorFlow / PyTorch / sentence-transformers required).
"""

from __future__ import annotations

from typing import List
import numpy as np

# Lazy-load to keep import fast
_chroma_ef = None


def _get_chroma_ef():
    global _chroma_ef
    if _chroma_ef is None:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        _chroma_ef = DefaultEmbeddingFunction()
    return _chroma_ef


class MiniLMEmbedding:
    """Embedding wrapper backed by ChromaDB's DefaultEmbeddingFunction.

    This uses the same all-MiniLM-L6-v2 model but loaded via ONNX Runtime,
    avoiding the TensorFlow / Keras / sentence-transformers dependency chain.

    Usage::

        emb = MiniLMEmbedding()
        vector = emb.embed("hello world")           # shape (384,)
        vectors = emb.embed_batch(["a", "b", "c"])  # shape (3, 384)
    """

    def embed(self, text: str) -> np.ndarray:
        """Return a 1-D embedding vector for *text*."""
        ef = _get_chroma_ef()
        result = ef([text])
        return np.array(result[0], dtype=np.float32)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Return a 2-D array of embedding vectors for a list of texts."""
        ef = _get_chroma_ef()
        result = ef(texts)
        return np.array(result, dtype=np.float32)

