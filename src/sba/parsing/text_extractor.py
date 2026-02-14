"""Handle plain text screenplay input."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str | Path) -> str:
    """Read a plain text screenplay file."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Try UTF-8 first, fall back to latin-1
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("UTF-8 decode failed for %s; falling back to latin-1", file_path)
        return file_path.read_text(encoding="latin-1")
