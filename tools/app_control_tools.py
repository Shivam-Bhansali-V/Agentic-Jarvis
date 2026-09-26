"""OS process and application control tools for Windows."""

import os
import shutil
import subprocess
from langchain_core.tools import tool

# Common Windows application aliases mapped to system executables / protocol commands
WINDOWS_APP_MAP = {
    "notepad": "notepad.exe",
    "notes": "notepad.exe",
    "calc": "calc.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "files": "explorer.exe",
    "cmd": "cmd.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "code": "code.cmd",
    "vscode": "code.cmd",
}


@tool
def open_application(app_name: str) -> str:
    """Opens a Windows application by name or common alias (e.g. 'notepad', 'calculator', 'chrome', 'explorer').
    
    Args:
        app_name: Name or alias of the application to launch (e.g. 'notepad', 'calculator').
        
    Returns:
        Confirmation message that the application was launched, or an error description.
    """
    cleaned_name = app_name.strip().lower()
    
    # 1. Check known alias mapping
    target_exe = WINDOWS_APP_MAP.get(cleaned_name, app_name.strip())
    
    try:
        # Check if executable exists in PATH or can be launched via Windows shell
        # Launch detached without blocking the agent ReAct loop
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        
        # Use shell execution or subprocess.Popen
        subprocess.Popen(
            target_exe,
            shell=True,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            close_fds=True
        )
        return f"Success: Launched application '{app_name}' (target: {target_exe})."
        
    except Exception as e:
        return f"Error: Failed to launch application '{app_name}': {str(e)}"
