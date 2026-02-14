"""Tests for corpus builder chunking logic."""

from pathlib import Path

from sba.rag.corpus_builder import (
    build_chunks_from_file,
    build_corpus,
    load_corpus_as_text,
)


def test_build_chunks_from_taxonomy():
    taxonomy = Path(__file__).parent.parent / "corpus" / "vfx_taxonomy.md"
    chunks = build_chunks_from_file(taxonomy)
    assert len(chunks) > 0
    # Should have one chunk per ## section (27 categories + preamble)
    assert len(chunks) >= 20
    # Each chunk should have a source file
    assert all(c.source_file == "vfx_taxonomy.md" for c in chunks)
    # Each chunk should have an ID
    assert all(c.chunk_id for c in chunks)
    # IDs should be unique
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_build_chunks_from_cost_rules():
    cost_rules = Path(__file__).parent.parent / "corpus" / "cost_rules.md"
    chunks = build_chunks_from_file(cost_rules)
    assert len(chunks) > 0
    # Should have chunks for the 14 rules
    assert len(chunks) >= 10


def test_build_full_corpus():
    corpus_dir = Path(__file__).parent.parent / "corpus"
    chunks = build_corpus(corpus_dir)
    # Should have chunks from all files
    source_files = {c.source_file for c in chunks}
    assert "vfx_taxonomy.md" in source_files
    assert "cost_rules.md" in source_files
    assert "capture_checklist.md" in source_files
    # Should have gold example chunks
    assert any("death_star" in c.source_file for c in chunks)


def test_load_corpus_as_text():
    corpus_dir = Path(__file__).parent.parent / "corpus"
    text = load_corpus_as_text(corpus_dir)
    assert "VFX Category Taxonomy" in text
    assert "Hidden Cost" in text
    assert "Capture Checklist" in text
    # Should have file separators
    assert "===" in text


def test_chunk_ids_are_stable():
    taxonomy = Path(__file__).parent.parent / "corpus" / "vfx_taxonomy.md"
    chunks_1 = build_chunks_from_file(taxonomy)
    chunks_2 = build_chunks_from_file(taxonomy)
    ids_1 = [c.chunk_id for c in chunks_1]
    ids_2 = [c.chunk_id for c in chunks_2]
    assert ids_1 == ids_2
