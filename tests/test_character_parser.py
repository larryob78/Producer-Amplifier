"""Tests for character extraction from screenplay text."""

from sba.parsing.character_parser import (
    extract_characters_from_text,
    canonicalize_character_name,
)


def test_basic_dialogue_character():
    text = """
JOHN
Hello there.

JANE
Hi John.
"""
    chars = extract_characters_from_text(text)
    names = {c.canonical_name for c in chars.values()}
    assert "JOHN" in names
    assert "JANE" in names


def test_contd_is_same_character():
    text = """
JOHN
Hello.

JANE
Hi.

JOHN (CONT'D)
As I was saying.
"""
    chars = extract_characters_from_text(text)
    assert "JOHN" in chars
    assert len(chars) == 2  # JOHN and JANE, not JOHN and JOHN (CONT'D)


def test_vo_os_extensions():
    text = """
JOHN (V.O.)
I remember that day.

JANE (O.S.)
Come here!
"""
    chars = extract_characters_from_text(text)
    assert "JOHN" in chars
    assert "V.O." in chars["JOHN"].extensions


def test_canonicalize_strips_extensions():
    assert canonicalize_character_name("JOHN (CONT'D)") == "JOHN"
    assert canonicalize_character_name("JANE (V.O.)") == "JANE"
    assert canonicalize_character_name("  JOHN  ") == "JOHN"
