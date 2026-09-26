"""Main entrypoint for Personal Agentic AI System (Agentic Jarvis)."""

import sys
from config.settings import settings


def main() -> None:
    # Set stdout encoding to utf-8 if supported
    if sys.stdout.encoding != "utf-8" and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print(">> PERSONAL AGENTIC AI SYSTEM (AGENTIC JARVIS) - v1.0")
    print("=" * 60)
    print(f"* Python Version : {sys.version.split()[0]}")
    print(f"* Environment    : {settings.environment}")
    print(f"* Active Provider: {settings.llm_provider}")
    print(f"* Default Model  : {settings.model_name}")
    print(f"* Base Directory : {settings.base_dir}")
    print(f"* Vector Store   : {settings.vector_store_dir}")
    print("=" * 60)
    print("STATUS: Phase 0 (Environment & Setup) is complete.")
    print("Next step: Run `pytest` to run tests, or proceed to Phase 1.")
    print("=" * 60)


if __name__ == "__main__":
    main()
