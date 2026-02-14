"""Voyage AI embedding wrapper for corpus chunks and queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voyageai

from sba.config import VOYAGE_API_KEY, VOYAGE_MODEL

if TYPE_CHECKING:
    from sba.rag.corpus_builder import CorpusChunk


def get_voyage_client() -> voyageai.Client:
    """Create a Voyage AI client."""
    if not VOYAGE_API_KEY:
        raise ValueError(
            "VOYAGE_API_KEY not set. Add it to .env or set the environment variable."
        )
    return voyageai.Client(api_key=VOYAGE_API_KEY)


def embed_chunks(
    chunks: list[CorpusChunk],
    client: voyageai.Client | None = None,
    model: str = VOYAGE_MODEL,
    batch_size: int = 64,
) -> list[list[float]]:
    """Embed a list of corpus chunks, returning embedding vectors.

    Batches requests to stay within API limits.
    """
    client = client or get_voyage_client()
    texts = [c.text for c in chunks]
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        result = client.embed(batch, model=model, input_type="document")
        all_embeddings.extend(result.embeddings)

    return all_embeddings


def embed_query(
    query: str,
    client: voyageai.Client | None = None,
    model: str = VOYAGE_MODEL,
) -> list[float]:
    """Embed a single query string for retrieval."""
    client = client or get_voyage_client()
    result = client.embed([query], model=model, input_type="query")
    return result.embeddings[0]
