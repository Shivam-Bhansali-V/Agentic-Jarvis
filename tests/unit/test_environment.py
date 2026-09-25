"""Unit tests for Phase 0 environment setup, package imports, and settings."""

import sys
from pathlib import Path
import pytest


def test_python_version():
    """Ensure Python version is at least 3.10."""
    assert sys.version_info >= (3, 10), f"Python version too old: {sys.version}"


def test_core_library_imports():
    """Verify that all core foundational libraries import cleanly without errors."""
    import pydantic
    import dotenv
    import psutil
    import chromadb
    import sentence_transformers
    import langchain_core
    import langgraph

    assert pydantic.__version__ is not None
    assert chromadb.__version__ is not None
    assert sentence_transformers.__version__ is not None


def test_settings_load():
    """Verify that the centralized application settings load properly."""
    from config.settings import settings

    assert settings.base_dir.exists()
    assert settings.llm_provider in ["openai", "anthropic"]
    assert settings.model_name != ""
    assert isinstance(settings.data_dir, Path)


def test_directory_structure_exists():
    """Verify that all expected project directories are present."""
    from config.settings import settings

    expected_dirs = [
        settings.base_dir / "agent",
        settings.base_dir / "agent" / "prompts",
        settings.base_dir / "tools",
        settings.base_dir / "rag",
        settings.base_dir / "voice",
        settings.base_dir / "data" / "personal_corpus",
        settings.base_dir / "logs",
        settings.base_dir / "tests" / "unit",
    ]

    for d in expected_dirs:
        assert d.exists(), f"Required directory missing: {d}"
        assert d.is_dir(), f"Path is not a directory: {d}"
