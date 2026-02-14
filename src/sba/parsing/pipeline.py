"""Orchestrates the full script parsing pipeline."""

from __future__ import annotations

from pathlib import Path

from sba.parsing.character_parser import extract_characters_from_text
from sba.parsing.models import ParsedScript
from sba.parsing.pdf_extractor import extract_text_from_pdf
from sba.parsing.preprocessor import preprocess_script_text
from sba.parsing.scene_parser import split_into_scenes
from sba.parsing.text_extractor import extract_text_from_file
from sba.parsing.vfx_scanner import scan_for_vfx_triggers


def parse_script_text(text: str, title: str = "") -> ParsedScript:
    """Parse raw screenplay text into a structured ParsedScript."""
    cleaned = preprocess_script_text(text)
    scenes = split_into_scenes(cleaned)

    # Extract characters and VFX triggers per scene
    all_characters = extract_characters_from_text(cleaned)

    for scene in scenes:
        # Per-scene character extraction
        scene_chars = extract_characters_from_text(scene.raw_text)
        scene.characters = list(scene_chars.keys())

        # VFX trigger scanning
        scene.vfx_triggers = scan_for_vfx_triggers(scene.raw_text)

    # Estimate pages (roughly 250 words per page for screenplays)
    total_words = sum(s.word_count for s in scenes)
    pages_estimate = max(1, round(total_words / 250))

    return ParsedScript(
        title=title,
        raw_text=cleaned,
        scenes=scenes,
        all_characters=all_characters,
        total_pages_estimate=pages_estimate,
    )


def parse_script_file(file_path: str | Path, title: str = "") -> ParsedScript:
    """Parse a screenplay file (PDF or text) into a structured ParsedScript."""
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_file(file_path)

    if not title:
        title = file_path.stem

    return parse_script_text(text, title=title)
