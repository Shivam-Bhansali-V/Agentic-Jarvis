"""Ingestion script: reads personal corpus, chunks, embeds, and stores in ChromaDB."""

from __future__ import annotations

import glob
import os
from pathlib import Path

from rag.chunking import chunk_text
from rag.embeddings import MiniLMEmbedding
from rag.store import add_documents

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "personal_corpus"


def ingest_corpus() -> None:
    """Ingest all .txt files from the personal corpus directory into the vector store.

    Steps:
    1. Find every .txt file under `data/personal_corpus/`.
    2. Read its full text.
    3. Split into overlapping token chunks via `chunk_text`.
    4. Embed each chunk with `MiniLMEmbedding`.
    5. Build a document dict `{id, text, metadata, embedding}`.
    6. Upsert all docs into the persistent Chroma collection.
    """
    embedding_model = MiniLMEmbedding()
    all_docs: list = []

    txt_files = sorted(glob.glob(str(DATA_DIR / "*.txt")))
    if not txt_files:
        print(f"[ingest] No .txt files found in {DATA_DIR}")
        return

    for file_path in txt_files:
        source_file = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as fh:
            content = fh.read()

        # chunk_text returns list of (chunk_text, start_char, end_char)
        chunks = chunk_text(content)
        for i, (chunk_str, start_char, end_char) in enumerate(chunks):
            vector = embedding_model.embed(chunk_str)
            doc = {
                "id": f"{source_file}_chunk_{i}",
                "text": chunk_str,
                "metadata": {
                    "source_file": source_file,
                    "chunk_index": i,
                    "start_char": start_char,
                    "end_char": end_char,
                },
                "embedding": vector.tolist() if hasattr(vector, "tolist") else list(vector),
            }
            all_docs.append(doc)
        print(f"  [{source_file}] -> {len(chunks)} chunks")

    if all_docs:
        add_documents(all_docs)
        print(f"\n[OK] Ingested {len(txt_files)} file(s), {len(all_docs)} total chunks into the vector store.")
    else:
        print("[ingest] No documents were produced. Check corpus files.")


if __name__ == "__main__":
    ingest_corpus()
