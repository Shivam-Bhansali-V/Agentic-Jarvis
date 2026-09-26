"""State schema definition for the LangGraph agent."""

from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """The central state dictionary maintained across ReAct graph steps."""
    
    # Message history with automatic append reducer
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Execution metrics and safety safeguards
    loop_count: int
