"""Extract text from screenplay PDFs using pdfplumber."""

from __future__ import annotations

from pathlib import Path
import pdfplumber


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract text from a PDF file, preserving layout.

    Uses pdfplumber's layout-preserving extraction which maintains
    the indentation structure critical for screenplay parsing.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages_text: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(layout=True)
            if text:
                pages_text.append(text)

    return "\n\n".join(pages_text)
