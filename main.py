"""Interactive CLI loop for Agentic Jarvis (Phase 1)."""

import sys
import uuid
from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent.graph import create_agent_graph
from config.settings import settings


def extract_text(content: Any) -> str:
    """Safely extracts a flat text string from message content (handles string, list of dicts, etc.)."""
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


def run_interactive_cli() -> None:
    """Runs the interactive ReAct conversation loop."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 65)
    print("🤖  AGENTIC JARVIS — CORE RE-ACT LOOP (PHASE 1 MVP)")
    print("=" * 65)
    print(f"• Active LLM  : {settings.llm_provider.upper()} ({settings.model_name})")
    print(f"• Loaded Tools: read_file, write_code_file, open_application")
    print(f"• Type 'exit' or 'quit' to terminate the session.")
    print("=" * 65)

    try:
        agent = create_agent_graph()
    except Exception as e:
        print(f"\n[!] Failed to initialize agent graph: {e}")
        return

    thread_id = str(uuid.uuid4())[:8]
    config = {"configurable": {"thread_id": f"session_{thread_id}"}}

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            print("\n" + "-" * 40)
            inputs = {"messages": [HumanMessage(content=user_input)], "loop_count": 0}

            for event in agent.stream(inputs, config=config, stream_mode="values"):
                messages = event.get("messages", [])
                if not messages:
                    continue

                last_msg = messages[-1]

                # Show tool calls
                if isinstance(last_msg, AIMessage) and hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    for call in last_msg.tool_calls:
                        print(f"⚙️ [Action] Calling '{call['name']}' with args: {call['args']}")

                # Show tool observations
                elif isinstance(last_msg, ToolMessage):
                    obs_text = extract_text(last_msg.content)
                    preview = obs_text[:300] + ("..." if len(obs_text) > 300 else "")
                    print(f"👁️ [Observation] {preview}")

                # Show final assistant reply
                elif isinstance(last_msg, AIMessage) and last_msg.content:
                    final_text = extract_text(last_msg.content)
                    if final_text.strip():
                        print(f"\nJarvis > {final_text}")

            print("-" * 40)

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n[!] Runtime Error: {e}")


if __name__ == "__main__":
    run_interactive_cli()
