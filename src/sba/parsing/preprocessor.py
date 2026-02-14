"""Preprocess raw screenplay text to remove PDF artifacts."""

import re


def preprocess_script_text(raw_text: str) -> str:
    """Clean up raw text before scene parsing.

    Removes page numbers, CONTINUED markers, normalizes whitespace.
    Preserves character CONT'D extensions in dialogue cues.
    """
    text = raw_text

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove standalone page numbers (1-3 digits alone on a line)
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Remove CONTINUED markers at page breaks (but NOT character CONT'D)
    text = re.sub(
        r"^\s*\(CONTINUED\)\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE
    )
    text = re.sub(
        r"^\s*CONTINUED:\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE
    )

    # Collapse 3+ consecutive blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text
