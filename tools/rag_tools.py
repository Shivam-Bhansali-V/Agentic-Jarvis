"""RAG query tool for the LangGraph agent.

Exposes a single LangChain-compatible tool `rag_query` that performs a
semantic search over the ChromaDB personal-corpus collection and returns
the top-k most relevant text chunks together with their source filenames.
"""

from __future__ import annotations

from typing import Any, Dict

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class RagQueryInput(BaseModel):
    """Input schema for the rag_query tool."""

    query: str = Field(
        ...,
        description="A natural-language question or search phrase to look up in Jarvis's personal knowledge base.",
    )
    k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of top chunks to retrieve (default 3).",
    )


@tool(args_schema=RagQueryInput)
def rag_query(query: str, k: int = 3) -> Dict[str, Any]:
    """Search Jarvis's personal knowledge base (RAG) for information relevant to *query*.

    Use this tool whenever the user asks about Shivam's background, education,
    projects, technical setup, preferences, philosophies, or any personal fact.
    Returns a dict with:
    - `chunks`    – list of relevant text excerpts
    - `sources`   – list of source filenames for each chunk
    - `distances` – cosine distances (lower = more relevant)
    """
    from rag.store import query as store_query

    result = store_query(query_text=query, k=k)
    return result
