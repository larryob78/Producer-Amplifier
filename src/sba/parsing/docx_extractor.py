"""Extract text from Word (.docx) screenplay files."""

from __future__ import annotations

from pathlib import Path

try:
    from docx import Document
except ImportError:
    Document = None  # type: ignore[misc,assignment]


def extract_text_from_docx(docx_path: str | Path) -> str:
    """Extract text from a Word document, preserving paragraph breaks.

    Handles both standard docx and screenplay-formatted docs.
    """
    if Document is None:
        raise ImportError(
            "python-docx is required for Word files. " "Install it with: pip install python-docx"
        )

    docx_path = Path(docx_path)
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    doc = Document(str(docx_path))
    paragraphs: list[str] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            # Preserve uppercase lines (likely scene headings or character names)
            paragraphs.append(text)
        else:
            # Blank line separator — important for screenplay structure
            paragraphs.append("")

    return "\n".join(paragraphs)
