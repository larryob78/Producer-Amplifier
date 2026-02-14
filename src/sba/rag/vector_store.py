"""ChromaDB vector store for corpus embeddings."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import chromadb

from sba.config import PROJECT_ROOT

if TYPE_CHECKING:
    from sba.rag.corpus_builder import CorpusChunk

DEFAULT_PERSIST_DIR = PROJECT_ROOT / ".chromadb"
COLLECTION_NAME = "sba_corpus"


def get_chroma_client(persist_dir: Path | None = None) -> chromadb.ClientAPI:
    """Create a persistent ChromaDB client."""
    persist_dir = persist_dir or DEFAULT_PERSIST_DIR
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def get_or_create_collection(
    client: chromadb.ClientAPI | None = None,
    persist_dir: Path | None = None,
    collection_name: str = COLLECTION_NAME,
) -> chromadb.Collection:
    """Get or create the corpus collection."""
    client = client or get_chroma_client(persist_dir)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(
    chunks: list[CorpusChunk],
    embeddings: list[list[float]],
    collection: chromadb.Collection | None = None,
    persist_dir: Path | None = None,
) -> chromadb.Collection:
    """Index corpus chunks with their embeddings into ChromaDB.

    Clears existing data and re-indexes from scratch.
    """
    collection = collection or get_or_create_collection(persist_dir=persist_dir)

    # Clear existing data
    existing = collection.count()
    if existing > 0:
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)

    # Add chunks in batches (ChromaDB supports large batches but let's be safe)
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_embeddings = embeddings[i : i + batch_size]

        collection.add(
            ids=[c.chunk_id for c in batch_chunks],
            embeddings=batch_embeddings,
            documents=[c.text for c in batch_chunks],
            metadatas=[
                {
                    "source_file": c.source_file,
                    "section_title": c.section_title,
                    "category": c.category,
                }
                for c in batch_chunks
            ],
        )

    return collection


def query_collection(
    query_embedding: list[float],
    collection: chromadb.Collection | None = None,
    persist_dir: Path | None = None,
    n_results: int = 10,
) -> list[dict]:
    """Query the vector store and return ranked results.

    Returns list of dicts with keys: chunk_id, text, score, metadata.
    """
    collection = collection or get_or_create_collection(persist_dir=persist_dir)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    items: list[dict] = []
    if results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            items.append(
                {
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                }
            )

    return items
