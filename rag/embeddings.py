"""Embedding wrapper for the RAG pipeline using sentence-transformers."""

from __future__ import annotations

from typing import List, Union
import numpy as np

# Lazy-load the model so import is fast even without GPU
_model = None

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


class MiniLMEmbedding:
    """Singleton-style wrapper around all-MiniLM-L6-v2.

    Usage::

        emb = MiniLMEmbedding()
        vector = emb.embed("hello world")          # shape (384,)
        vectors = emb.embed_batch(["a", "b", "c"]) # shape (3, 384)
    """

    def embed(self, text: str) -> np.ndarray:
        """Return a 1-D embedding vector for *text*."""
        model = _get_model()
        return model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Return a 2-D array of embedding vectors for a list of texts."""
        model = _get_model()
        return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
