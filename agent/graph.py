"""LangGraph StateGraph definition for the ReAct Agent Loop."""

import os
from typing import List, Optional, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from config.settings import settings
from agent.state import AgentState
from agent.prompts.system_prompt import BASE_SYSTEM_PROMPT
from tools import ALL_PHASE_1_TOOLS


def get_llm(provider: Optional[str] = None, model_name: Optional[str] = None) -> BaseChatModel:
    """Factory creating the configured ChatModel instance based on application settings."""
    active_provider = provider or settings.llm_provider
    active_model = model_name or settings.model_name
    
    if active_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = settings.google_api_key or os.environ.get("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=active_model,
            google_api_key=api_key,
            temperature=0.1,
        )
    elif active_provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
        return ChatOpenAI(
            model=active_model,
            openai_api_key=api_key,
            temperature=0.1,
        )
    elif active_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = settings.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        return ChatAnthropic(
            model=active_model,
            anthropic_api_key=api_key,
            temperature=0.1,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {active_provider}")


def create_agent_graph(
    tools: Optional[List[Any]] = None,
    llm: Optional[BaseChatModel] = None,
    checkpointer: Optional[Any] = None,
    system_prompt: str = BASE_SYSTEM_PROMPT,
    max_loops: int = 8,
):
    """Constructs and compiles the stateful LangGraph ReAct agent loop."""
    active_tools = tools if tools is not None else ALL_PHASE_1_TOOLS
    active_llm = llm or get_llm()
    llm_with_tools = active_llm.bind_tools(active_tools)
    tool_node = ToolNode(active_tools)

    # 1. Reasoning Node (LLM Call)
    def reasoning_node(state: AgentState) -> dict:
        messages = list(state["messages"])
        
        # Ensure system prompt is the first message
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages
            
        response = llm_with_tools.invoke(messages)
        current_loops = state.get("loop_count", 0) + 1
        
        return {
            "messages": [response],
            "loop_count": current_loops,
        }

    # 2. Conditional Edge Router
    def should_continue(state: AgentState) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        loop_count = state.get("loop_count", 0)

        # Enforce hard recursion limit
        if loop_count >= max_loops:
            return END

        # Check if the LLM requested a tool execution
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
            
        return END

    # 3. Build Graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("reasoning")
    
    workflow.add_conditional_edges(
        "reasoning",
        should_continue,
        {
            "tools": "tools",
            END: END,
        }
    )
    
    workflow.add_edge("tools", "reasoning")
    
    # 4. Checkpointer for conversation continuity
    active_checkpointer = checkpointer if checkpointer is not None else MemorySaver()
    
    return workflow.compile(checkpointer=active_checkpointer)
