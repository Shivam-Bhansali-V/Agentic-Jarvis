"""Centralized application settings and environment variable validation."""

import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the repository
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core LLM configurations
    llm_provider: Literal["openai", "anthropic", "google"] = Field(
        default="google",
        description="Active LLM provider for agent reasoning",
    )
    model_name: str = Field(
        default="gemini-3.7-flash",
        description="Model name/id to use with provider",
    )
    google_api_key: Optional[str] = Field(
        default=None,
        description="API key for Google Gemini",
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="API key for OpenAI",
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="API key for Anthropic Claude",
    )

    # Environment
    environment: Literal["development", "production", "test"] = Field(
        default="development",
    )

    # Directory Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    vector_store_dir: Path = BASE_DIR / "vector_store"
    logs_dir: Path = BASE_DIR / "logs"

    # Coding sandbox settings (Phase 3)
    docker_image: str = "python:3.11-slim"
    e2b_api_key: Optional[str] = None


# Global settings singleton
settings = Settings()
