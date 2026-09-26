# Agentic Jarvis

An autonomous personal AI assistant built on LangGraph, running locally on Windows.
Jarvis combines a powerful ReAct agent loop with a personal knowledge base (RAG)
so it can answer questions about Shivam using his own documents.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
copy .env.example .env
```

### 3. Ingest personal corpus (Phase 2 RAG)

Before running Jarvis for the first time (or after updating your corpus), populate the vector store:

```bash
python -m rag.ingest
```

Expected output:
```
  [identity_and_background.txt] -> 4 chunks
  [philosophies_and_quirks.txt] -> 2 chunks
  ...
[OK] Ingested 6 file(s), 23 total chunks into the vector store.
```

### 4. Run Jarvis

```bash
python main.py
```

Persona options:

```bash
python main.py --persona friend   # Casual, friendly mode
python main.py --persona study    # Focused study assistant mode
python main.py --persona default  # Standard Jarvis mode (default)
```

---

## RAG Setup (Phase 2)

### How it works

1. **Corpus** – Your personal `.txt` files live in `data/personal_corpus/`.
   Add or edit any file and re-run `python -m rag.ingest` to update the knowledge base.

2. **Ingestion** (`rag/ingest.py`) – Reads every `.txt` file, splits it into
   token-based overlapping chunks (200 tokens, 50-token overlap), embeds each
   chunk with `all-MiniLM-L6-v2` (runs fully offline), and stores them in a
   persistent ChromaDB collection under `vector_store/chroma_db/`.

3. **RAG Query Tool** (`tools/rag_tools.py`) – Exposes a LangChain tool called
   `rag_query` that Jarvis calls automatically whenever you ask personal questions.
   Returns the top-3 most relevant chunks along with their source filenames.

4. **Graph wiring** (`agent/graph.py`) – After each `rag_query` tool call, the
   retrieved chunks are stored in the agent state and injected into the system
   prompt at the start of the next reasoning step.

### Verify the pipeline

```bash
python scripts/verify_rag.py --query "What is Shivam's CGPA?"
# with full agent response:
python scripts/verify_rag.py --query "Where does Shivam study?" --full
```

### Run tests

```bash
pytest tests/unit/test_chunking.py -v
pytest tests/unit/test_rag_tool.py -v
pytest tests/ -v   # all tests
```

---

## Project Structure

```
Agentic Jarvis/
├── agent/
│   ├── graph.py          # LangGraph StateGraph (ReAct loop + RAG wiring)
│   ├── state.py          # AgentState schema (messages, loop_count, retrieved_context)
│   └── prompts/
│       ├── system_prompt.py   # Default system prompt ({retrieved_context} placeholder)
│       ├── persona_friend.py  # Casual friend persona
│       └── persona_study.py   # Study assistant persona
├── data/
│   └── personal_corpus/  # Your .txt knowledge-base files (6 files)
├── rag/
│   ├── chunking.py       # Token-based text chunker
│   ├── embeddings.py     # MiniLM embedding wrapper (offline)
│   ├── store.py          # ChromaDB vector store (add_documents, query)
│   └── ingest.py         # Ingestion script
├── tools/
│   ├── file_tools.py     # read_file, write_code_file
│   ├── app_control_tools.py  # open_application
│   └── rag_tools.py      # rag_query tool
├── scripts/
│   └── verify_rag.py     # RAG verification CLI
├── tests/
│   └── unit/
│       ├── test_chunking.py
│       └── test_rag_tool.py
├── vector_store/
│   └── chroma_db/        # Persisted ChromaDB (auto-created by ingest)
├── main.py
└── requirements.txt
```

---

## Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | Complete | Core ReAct agent, file tools, app control, fallback LLM cascade |
| Phase 2 | Complete | Personal RAG pipeline, persona prompts, verify script |
| Phase 3 | Planned  | Voice interface, calendar/email tools, proactive reminders |
