"""Unit tests for OS application control tools."""

import subprocess
import pytest
from unittest.mock import patch, MagicMock
from tools.app_control_tools import open_application, WINDOWS_APP_MAP


def test_app_map_contains_standards():
    """Ensure standard system applications are registered in alias mapping."""
    assert "notepad" in WINDOWS_APP_MAP
    assert "calc" in WINDOWS_APP_MAP
    assert "explorer" in WINDOWS_APP_MAP


@patch("subprocess.Popen")
def test_open_application_success(mock_popen: MagicMock):
    """Test launching an application maps alias and invokes subprocess.Popen."""
    mock_popen.return_value = MagicMock()
    
    result = open_application.invoke({"app_name": "notepad"})
    
    assert "Success: Launched application 'notepad'" in result
    mock_popen.assert_called_once()
    args, kwargs = mock_popen.call_args
    assert args[0] == "notepad.exe"
    assert kwargs.get("shell") is True


@patch("subprocess.Popen", side_effect=OSError("Access denied"))
def test_open_application_error_handling(mock_popen: MagicMock):
    """Test that subprocess failure returns clean error observation without crashing."""
    result = open_application.invoke({"app_name": "forbidden_app"})
    assert "Error:" in result
    assert "Access denied" in result
