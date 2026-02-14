"""Build chunked corpus from markdown source files for embedding and retrieval."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from sba.config import CORPUS_DIR


@dataclass
class CorpusChunk:
    """A single chunk of corpus text with metadata."""

    chunk_id: str
    text: str
    source_file: str
    section_title: str = ""
    category: str = ""
    metadata: dict = field(default_factory=dict)


def _split_markdown_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown text into (heading, body) pairs on ## headings."""
    sections: list[tuple[str, str]] = []
    parts = re.split(r"^## ", text, flags=re.MULTILINE)

    # First part is preamble (before any ## heading)
    preamble = parts[0].strip()
    if preamble:
        # Extract title from # heading if present
        title_match = re.match(r"^# (.+)", preamble, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "preamble"
        sections.append((title, preamble))

    for part in parts[1:]:
        lines = part.split("\n", 1)
        heading = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if body:
            sections.append((heading, f"## {heading}\n{body}"))

    return sections


def _chunk_id(source: str, index: int) -> str:
    """Generate a stable chunk ID from source filename and index."""
    stem = Path(source).stem
    return f"{stem}_{index:03d}"


def build_chunks_from_file(file_path: Path) -> list[CorpusChunk]:
    """Build corpus chunks from a single markdown file.

    Each ## section becomes one chunk. If a section is very long (>800 words),
    it's split further on --- dividers or paragraph boundaries.
    """
    text = file_path.read_text(encoding="utf-8")
    source_name = file_path.name
    sections = _split_markdown_sections(text)
    chunks: list[CorpusChunk] = []

    for i, (heading, body) in enumerate(sections):
        word_count = len(body.split())
        if word_count <= 800:
            chunks.append(
                CorpusChunk(
                    chunk_id=_chunk_id(source_name, len(chunks)),
                    text=body,
                    source_file=source_name,
                    section_title=heading,
                )
            )
        else:
            # Split long sections on --- dividers
            sub_parts = re.split(r"\n---\n", body)
            for sub in sub_parts:
                sub = sub.strip()
                if sub:
                    chunks.append(
                        CorpusChunk(
                            chunk_id=_chunk_id(source_name, len(chunks)),
                            text=sub,
                            source_file=source_name,
                            section_title=heading,
                        )
                    )

    return chunks


def build_corpus(corpus_dir: Path | None = None) -> list[CorpusChunk]:
    """Build the full corpus from all markdown files in the corpus directory.

    Scans the corpus directory recursively for .md files.
    """
    corpus_dir = corpus_dir or CORPUS_DIR
    all_chunks: list[CorpusChunk] = []

    md_files = sorted(corpus_dir.rglob("*.md"))
    for md_file in md_files:
        file_chunks = build_chunks_from_file(md_file)
        all_chunks.extend(file_chunks)

    return all_chunks


def load_corpus_as_text(corpus_dir: Path | None = None) -> str:
    """Load the entire corpus as a single text string for RAG-lite mode.

    Returns all markdown files concatenated with separators.
    Used when the corpus is small enough to inject directly into the prompt.
    """
    corpus_dir = corpus_dir or CORPUS_DIR
    parts: list[str] = []

    md_files = sorted(corpus_dir.rglob("*.md"))
    for md_file in md_files:
        rel_path = md_file.relative_to(corpus_dir)
        text = md_file.read_text(encoding="utf-8").strip()
        parts.append(f"=== {rel_path} ===\n{text}")

    return "\n\n".join(parts)
