"""File-based result caching for script analysis.

Cache key is derived from script text + model + prompt version.
Results are stored as JSON in a .sba_cache/ directory.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sba.config import PROJECT_ROOT

CACHE_DIR = PROJECT_ROOT / ".sba_cache"
PROMPT_VERSION = "v1"  # Bump when prompts change significantly


def _cache_key(script_text: str, model: str) -> str:
    """Generate a deterministic cache key."""
    content = f"{script_text}|{model}|{PROMPT_VERSION}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def get_cached(script_text: str, model: str) -> dict | None:
    """Return cached result dict if available, else None."""
    key = _cache_key(script_text, model)
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def set_cached(script_text: str, model: str, result_dict: dict) -> Path:
    """Write result dict to cache. Returns the cache file path."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _cache_key(script_text, model)
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(json.dumps(result_dict, indent=2), encoding="utf-8")
    return cache_file
