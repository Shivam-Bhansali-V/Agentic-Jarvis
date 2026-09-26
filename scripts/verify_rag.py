#!/usr/bin/env python
"""Verification CLI for the Phase 2 RAG pipeline.

Usage::

    python scripts/verify_rag.py
    python scripts/verify_rag.py --query "What is Shivam CGPA?" --k 5
    python scripts/verify_rag.py --query "Where does Shivam study?" --full

Flags:
  --query  TEXT   The search query (default: interactive prompt)
  --k      INT    Number of chunks to retrieve (default: 3)
  --full          Also run the full agent graph and print the answer
"""

from __future__ import annotations

import argparse
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def run_retrieval(query: str, k: int) -> None:
    from rag.store import query as store_query
    print(f"\n[Retrieval] Query : {query!r}")
    print(f"[Retrieval] Top-k : {k}\n")
    result = store_query(query_text=query, k=k)
    chunks = result.get("chunks", [])
    sources = result.get("sources", [])
    distances = result.get("distances", [])
    if not chunks:
        print("  [!] No chunks retrieved. Run `python -m rag.ingest` first.")
        return
    for i, (chunk, source, dist) in enumerate(zip(chunks, sources, distances), start=1):
        print(f"--- Chunk {i} | source: {source} | distance: {dist:.4f} ---")
        print(chunk[:600])
        print()


def run_full_agent(query: str) -> None:
    from agent.graph import create_agent_graph
    from langchain_core.messages import HumanMessage
    print(f"\n[Agent] Running full agent with query: {query!r}\n")
    graph = create_agent_graph()
    config = {"configurable": {"thread_id": "verify_rag_check"}}
    result = graph.invoke(
        {"messages": [HumanMessage(content=query)], "loop_count": 0, "retrieved_context": ""},
        config=config,
    )
    final_messages = result.get("messages", [])
    if final_messages:
        last = final_messages[-1]
        print("[Agent Response]\n")
        print(getattr(last, "content", str(last)))
    else:
        print("[Agent] No response messages found.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the Jarvis RAG pipeline.")
    parser.add_argument("--query", type=str, default=None)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    query = args.query
    if not query:
        try:
            query = input("Enter search query: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)
    if not query:
        print("No query provided. Exiting.")
        sys.exit(1)
    run_retrieval(query=query, k=args.k)
    if args.full:
        run_full_agent(query=query)


if __name__ == "__main__":
    main()
