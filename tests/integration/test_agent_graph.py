"""Integration tests for LangGraph state machine, tool routing, and memory checkpointer."""

import pytest
from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration

from agent.graph import create_agent_graph
from tools.file_tools import write_code_file, read_file
from tools.app_control_tools import open_application


class FakeToolCallingLLM(BaseChatModel):
    """A deterministic mock LLM for testing graph routing and tool execution without external APIs."""

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        last_msg = messages[-1]
        
        # If last message was a tool result, produce final answer
        if isinstance(last_msg, ToolMessage):
            return ChatResult(generations=[
                ChatGeneration(message=AIMessage(content=f"Received observation: {last_msg.content}"))
            ])
            
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        
        # Simulate tool call request for file write
        if "write a file" in content.lower():
            ai_msg = AIMessage(
                content="",
                tool_calls=[{
                    "name": "write_code_file",
                    "args": {"filepath": "test_mock.py", "code_content": "print('mock')"},
                    "id": "call_123",
                    "type": "tool_call",
                }]
            )
            return ChatResult(generations=[ChatGeneration(message=ai_msg)])
            
        # Standard chat reply
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="Hello! How can I help you?"))])

    def bind_tools(self, tools, **kwargs):
        """Mock tool binding returning self."""
        return self

    @property
    def _llm_type(self) -> str:
        return "fake_tool_calling_llm"


def test_graph_compilation_and_basic_turn():
    """Verify graph compiles and responds to basic user query."""
    fake_llm = FakeToolCallingLLM()
    app = create_agent_graph(llm=fake_llm)
    
    config = {"configurable": {"thread_id": "test_thread_1"}}
    inputs = {"messages": [HumanMessage(content="Hello there!")], "loop_count": 0}
    
    result = app.invoke(inputs, config=config)
    messages = result["messages"]
    
    assert len(messages) >= 2
    assert messages[-1].content == "Hello! How can I help you?"


def test_graph_executes_tool_and_completes_loop(tmp_path):
    """Verify graph executes a tool call and loops back to reasoning for final answer."""
    fake_llm = FakeToolCallingLLM()
    app = create_agent_graph(llm=fake_llm)
    
    config = {"configurable": {"thread_id": "test_thread_2"}}
    inputs = {"messages": [HumanMessage(content="Please write a file for me")], "loop_count": 0}
    
    result = app.invoke(inputs, config=config)
    messages = result["messages"]
    
    # Check that tool call occurred and observation was returned
    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert "Success: File 'test_mock.py' written successfully" in tool_messages[0].content
    assert "Received observation" in messages[-1].content
