"""OS process and application control tools for Windows."""

import os
import subprocess
from pathlib import Path
from langchain_core.tools import tool
from tools.file_tools import resolve_smart_path

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
    """Opens a Windows application by name/alias (e.g. 'notepad', 'calculator', 'chrome', 'explorer')
    or launches a specific document/file in its default Windows application.
    
    Args:
        app_name: Name/alias of the application (e.g. 'notepad') or name/path of a file to open.
        
    Returns:
        Confirmation message that the application/file was launched, or an error description.
    """
    cleaned_name = app_name.strip()
    lookup_key = cleaned_name.lower()
    
    # 1. Check if app_name refers to a local file on Desktop/Workspace/Downloads
    matched_file = resolve_smart_path(cleaned_name)
    if matched_file and matched_file.is_file():
        try:
            os.startfile(str(matched_file))
            return f"Success: Opened file '{matched_file.name}' in its default application (path: {matched_file})."
        except Exception as e:
            return f"Error opening file '{matched_file}': {str(e)}"

    # 2. Check known alias mapping
    target_exe = WINDOWS_APP_MAP.get(lookup_key, cleaned_name)
    
    try:
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        
        subprocess.Popen(
            target_exe,
            shell=True,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            close_fds=True
        )
        return f"Success: Launched application '{app_name}' (target: {target_exe})."
        
    except Exception as e:
        return f"Error: Failed to launch application '{app_name}': {str(e)}"
