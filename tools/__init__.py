"""Tool registry module for Agentic Jarvis."""

from tools.file_tools import read_file, write_code_file
from tools.app_control_tools import open_application
from tools.rag_tools import rag_query

ALL_PHASE_1_TOOLS = [
    read_file,
    write_code_file,
    open_application,
    rag_query,
]

__all__ = [
    "read_file",
    "write_code_file",
    "open_application",
    "rag_query",
    "ALL_PHASE_1_TOOLS",
]
