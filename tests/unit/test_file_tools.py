"""Unit tests for file management tools: read_file and write_code_file."""

import os
from pathlib import Path
import pytest
from tools.file_tools import read_file, write_code_file, resolve_smart_path


def test_write_and_read_text_file(tmp_path: Path):
    """Test writing and reading a standard text/code file."""
    test_file = tmp_path / "hello.py"
    code_content = "def hello():\n    return 'Hello, Jarvis!'"
    
    # Test write tool
    write_result = write_code_file.invoke({"filepath": str(test_file), "code_content": code_content})
    assert "Success" in write_result
    assert test_file.exists()
    
    # Test read tool
    read_result = read_file.invoke({"path": str(test_file)})
    assert read_result == code_content


def test_write_nested_directories(tmp_path: Path):
    """Test writing a file in deeply nested directories that do not yet exist."""
    test_file = tmp_path / "nested" / "deep" / "script.py"
    code_content = "print('deep directory')"
    
    write_result = write_code_file.invoke({"filepath": str(test_file), "code_content": code_content})
    assert "Success" in write_result
    assert test_file.exists()
    assert test_file.read_text(encoding="utf-8") == code_content


def test_read_nonexistent_file(tmp_path: Path):
    """Test reading a file that does not exist returns a clean observation rather than raising."""
    missing_file = tmp_path / "ghost_file.txt"
    result = read_file.invoke({"path": str(missing_file)})
    assert "Error: File not found" in result


def test_read_directory_path(tmp_path: Path):
    """Test passing a directory path instead of a file returns clean error observation."""
    result = read_file.invoke({"path": str(tmp_path)})
    assert "Error: Path" in result
    assert "is a directory" in result


def test_smart_path_fuzzy_search(tmp_path: Path, monkeypatch):
    """Test smart path resolution finding files without exact extension."""
    test_doc = tmp_path / "my_resume.pdf"
    test_doc.write_text("Resume Content", encoding="utf-8")
    
    # Monkeypatch search roots to include tmp_path
    monkeypatch.setattr("tools.file_tools.Path.home", lambda: tmp_path)
    
    resolved = resolve_smart_path("my_resume")
    assert resolved is not None
    assert resolved.name == "my_resume.pdf"
