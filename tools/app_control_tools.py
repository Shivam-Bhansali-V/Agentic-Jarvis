"""OS process and application control tools for Windows."""

import os
import subprocess
from pathlib import Path
from langchain_core.tools import tool
from tools.file_tools import find_matching_paths

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
    If multiple files match a partial file query, lists the matching files for user selection.
    
    Args:
        app_name: Name/alias of the application (e.g. 'notepad') or keyword/path of a file to open.
        
    Returns:
        Confirmation message that the application/file was launched, or a list of options if ambiguous.
    """
    cleaned_name = app_name.strip()
    lookup_key = cleaned_name.lower()

    # 1. Check if app_name is a known application alias first (e.g. 'notepad', 'calculator')
    if lookup_key in WINDOWS_APP_MAP:
        target_exe = WINDOWS_APP_MAP[lookup_key]
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

    # 2. Search for matching files across workspace, Desktop, Downloads, Documents
    matches = find_matching_paths(cleaned_name)
    
    if len(matches) > 1:
        options = "\n".join([f"{i+1}. {m.name} (Path: {m})" for i, m in enumerate(matches[:10])])
        return (
            f"Multiple matching files found for '{app_name}':\n{options}\n\n"
            f"Please ask the user which specific file they would like to open."
        )

    if len(matches) == 1:
        target_file = matches[0]
        try:
            os.startfile(str(target_file))
            return f"Success: Opened file '{target_file.name}' in its default application (path: {target_file})."
        except Exception as e:
            return f"Error opening file '{target_file}': {str(e)}"

    # 3. Fallback: Try launching as direct executable or Windows shell command
    try:
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        subprocess.Popen(
            cleaned_name,
            shell=True,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            close_fds=True
        )
        return f"Success: Launched application '{app_name}'."
    except Exception as e:
        return f"Error: Could not find or launch application/file '{app_name}': {str(e)}"
