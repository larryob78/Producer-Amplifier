"""Application configuration loaded from environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-6")
VOYAGE_MODEL = "voyage-3"

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "16384"))
MAX_RETRIEVAL_CHUNKS = 40
MAX_RETRIEVAL_WORDS = 15000
