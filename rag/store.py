"""ChromaDB-backed vector store for the RAG pipeline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings

# Persist the DB next to the rag/ package so it survives restarts
_DB_PATH = str(Path(__file__).resolve().parents[1] / "vector_store" / "chroma_db")
_COLLECTION_NAME = "jarvis_personal_corpus"

_client: chromadb.Client | None = None
_collection: Any = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        os.makedirs(_DB_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=_DB_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_documents(docs: List[Dict[str, Any]]) -> None:
    """Upsert a list of document dicts into the vector store.

    Each dict must have the keys:
        - `id`        (str)  – unique document / chunk id
        - `text`      (str)  – raw text of the chunk
        - `metadata`  (dict) – arbitrary metadata (source_file, chunk_index …)
        - `embedding` (list) – pre-computed embedding vector

    If `embedding` is absent, it is computed on the fly via MiniLMEmbedding.
    """
    from rag.embeddings import MiniLMEmbedding

    col = _get_collection()
    emb_model = MiniLMEmbedding()

    ids = []
    texts = []
    embeddings = []
    metadatas = []

    for doc in docs:
        ids.append(doc["id"])
        texts.append(doc["text"])
        metadatas.append(doc.get("metadata", {}))
        if "embedding" in doc:
            embeddings.append(doc["embedding"])
        else:
            embeddings.append(emb_model.embed(doc["text"]).tolist())

    col.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query(query_text: str, k: int = 3) -> Dict[str, Any]:
    """Semantic search: return top-k chunks closest to *query_text*.

    Returns a dict::

        {
            "chunks":   [str, ...],        # chunk texts
            "sources":  [str, ...],        # source filenames
            "distances": [float, ...],     # cosine distances (lower = closer)
        }
    """
    from rag.embeddings import MiniLMEmbedding

    col = _get_collection()
    emb_model = MiniLMEmbedding()
    query_emb = emb_model.embed(query_text).tolist()

    results = col.query(
        query_embeddings=[query_emb],
        n_results=min(k, col.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    sources = [m.get("source_file", "unknown") for m in metadatas]

    return {
        "chunks": chunks,
        "sources": sources,
        "distances": distances,
    }
