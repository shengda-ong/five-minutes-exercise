# core/tests/conftest.py

import os
from dotenv import load_dotenv
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "config" / ".env")

@pytest.fixture
def gemini_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found in environment.")
    return key
