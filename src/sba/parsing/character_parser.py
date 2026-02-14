"""Character extraction from screenplay text."""

from __future__ import annotations

import re

from sba.parsing.models import Character

# Character cue pattern: uppercase name, optional extension in parens
CHARACTER_CUE_RE = re.compile(
    r"^"
    r"(?P<name>[A-Z][A-Z\s.'\-]+?)"
    r"(?:\s*\((?P<ext>"
    r"V\.?\s*O\.?"
    r"|O\.?\s*S\.?"
    r"|O\.?\s*C\.?"
    r"|CONT'?D?"
    r"|CONTINUING"
    r"|FILTERED"
    r"|SUBTITLED?"
    r"|PRE[\-\s]?LAP"
    r"|ON\s+(?:PHONE|RADIO|TV|SCREEN|SPEAKER)"
    r"|OVER\s+PHONE"
    r")\))?"
    r"\s*$",
    re.MULTILINE,
)


def canonicalize_character_name(raw_name: str) -> str:
    """Normalize a character name to canonical form."""
    name = raw_name.strip()
    # Remove parenthetical extensions
    name = re.sub(r"\s*\(.*?\)\s*", "", name)
    # Remove trailing CONT'D without parens
    name = re.sub(r"\s+CONT'?D?\s*$", "", name, flags=re.IGNORECASE)
    # Normalize whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name


def extract_characters_from_text(text: str) -> dict[str, Character]:
    """Extract characters from screenplay text using dialogue cue patterns.

    Returns dict mapping canonical name -> Character.
    """
    characters: dict[str, Character] = {}
    lines = text.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        match = CHARACTER_CUE_RE.match(stripped)
        if not match:
            continue

        raw_name = match.group("name").strip()
        ext = match.group("ext")
        canonical = canonicalize_character_name(raw_name)

        if not canonical or len(canonical) < 2:
            continue

        # Skip common false positives
        if canonical in {
            "CUT TO",
            "FADE TO",
            "FADE IN",
            "FADE OUT",
            "DISSOLVE TO",
            "SMASH CUT TO",
            "MATCH CUT TO",
            "THE END",
            "CONTINUED",
            "INTERCUT",
            "MONTAGE",
            "END MONTAGE",
            "FLASHBACK",
            "END FLASHBACK",
            "SUPER",
            "TITLE CARD",
            "CHYRON",
        }:
            continue

        if canonical not in characters:
            characters[canonical] = Character(canonical_name=canonical)

        characters[canonical].variants.add(stripped)
        if ext:
            characters[canonical].extensions.add(ext.strip())

    return characters
