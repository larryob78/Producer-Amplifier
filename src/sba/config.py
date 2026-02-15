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

# Three-tier model routing
CLAUDE_MODEL_OPUS = os.getenv("CLAUDE_MODEL_OPUS", "claude-opus-4-6")
CLAUDE_MODEL_SONNET = os.getenv("CLAUDE_MODEL_SONNET", "claude-sonnet-4-5-20250929")
CLAUDE_MODEL_HAIKU = os.getenv("CLAUDE_MODEL_HAIKU", "claude-haiku-4-5-20251001")

# ElevenLabs voice config
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

# OpenAI (for Whisper STT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Master budget path
MASTER_BUDGET_PATH = os.getenv("MASTER_BUDGET_PATH", "")

MAX_TOKENS = int(os.getenv("MAX_TOKENS", "16384"))
MAX_RETRIEVAL_CHUNKS = 40
MAX_RETRIEVAL_WORDS = 15000
