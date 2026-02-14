"""Orchestrates the full script parsing pipeline.

Accepts any screenplay format: PDF, DOCX, FDX (Final Draft), TXT, RTF.
"""

from __future__ import annotations

from pathlib import Path

from sba.parsing.models import ParsedScript
from sba.parsing.preprocessor import preprocess_script_text
from sba.parsing.scene_parser import split_into_scenes
from sba.parsing.character_parser import extract_characters_from_text
from sba.parsing.vfx_scanner import scan_for_vfx_triggers
from sba.parsing.pdf_extractor import extract_text_from_pdf
from sba.parsing.text_extractor import extract_text_from_file

# Supported file extensions
SUPPORTED_FORMATS = {".pdf", ".txt", ".text", ".docx", ".doc", ".fdx", ".rtf", ".fountain"}


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


def extract_text_from_any(file_path: Path) -> str:
    """Extract text from any supported screenplay format."""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)

    elif suffix == ".docx":
        from sba.parsing.docx_extractor import extract_text_from_docx
        return extract_text_from_docx(file_path)

    elif suffix == ".fdx":
        from sba.parsing.fdx_extractor import extract_text_from_fdx
        return extract_text_from_fdx(file_path)

    elif suffix in {".txt", ".text", ".fountain", ".rtf"}:
        return extract_text_from_file(file_path)

    else:
        # Try plain text as fallback
        return extract_text_from_file(file_path)


def parse_script_file(file_path: str | Path, title: str = "") -> ParsedScript:
    """Parse a screenplay file (any format) into a structured ParsedScript.

    Supported formats:
      - .pdf (via pdfplumber)
      - .docx (via python-docx)
      - .fdx (Final Draft XML)
      - .txt / .text / .fountain (plain text)
      - .rtf (best-effort plain text)
    """
    file_path = Path(file_path)

    if file_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {file_path.suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    text = extract_text_from_any(file_path)

    if not title:
        title = file_path.stem.replace("_", " ").replace("-", " ").title()

    return parse_script_text(text, title=title)
