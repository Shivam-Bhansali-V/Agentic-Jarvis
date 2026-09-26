"""Live component smoke test executing the real LangGraph agent with the configured LLM."""

import os
from pathlib import Path
from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent.graph import create_agent_graph
from config.settings import settings


def extract_text(content: Any) -> str:
    """Safely extracts a flat text string from message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content) if content else ""


def test_live_agent_end_to_end(tmp_path: Path):
    """Test the live agent executing a write task and a read task sequentially with real API."""
    if not settings.google_api_key and not settings.openai_api_key and not settings.anthropic_api_key:
        print("[Skipping live test: No API key found]")
        return

    agent = create_agent_graph()
    config = {"configurable": {"thread_id": "live_smoke_session"}}
    
    test_filepath = str(tmp_path / "live_phase1_test.txt")
    
    # 1. Ask agent to write a file
    prompt1 = f"Please write a file to '{test_filepath}' with the exact content 'Hello from Phase 1 MVP'."
    result1 = agent.invoke({"messages": [HumanMessage(content=prompt1)], "loop_count": 0}, config=config)
    
    assert Path(test_filepath).exists()
    assert Path(test_filepath).read_text(encoding="utf-8") == "Hello from Phase 1 MVP"
    
    # 2. Ask agent to read the file back
    prompt2 = f"Now read the file at '{test_filepath}' and tell me what text is inside."
    result2 = agent.invoke({"messages": [HumanMessage(content=prompt2)], "loop_count": 0}, config=config)
    
    final_reply = extract_text(result2["messages"][-1].content)
    assert "Hello from Phase 1 MVP" in final_reply or "Phase 1 MVP" in final_reply
    print(f"\n[LIVE TEST PASSED] Final Assistant Response: {final_reply}")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        test_live_agent_end_to_end(Path(td))
