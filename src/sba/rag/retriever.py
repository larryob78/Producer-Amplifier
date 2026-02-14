"""Hybrid retriever combining dense (Voyage) and sparse (BM25) retrieval.

Deduplicates results by VFX category to avoid redundant context injection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rank_bm25 import BM25Okapi

from sba.config import MAX_RETRIEVAL_CHUNKS, MAX_RETRIEVAL_WORDS
from sba.rag.corpus_builder import CorpusChunk, build_corpus
from sba.rag.embedder import embed_query, get_voyage_client
from sba.rag.vector_store import get_or_create_collection, query_collection

if TYPE_CHECKING:
    import chromadb
    import voyageai


class HybridRetriever:
    """Retriever combining dense vector search with BM25 sparse search.

    Deduplicates results by source section to prevent bloated context.
    Enforces a word budget cap for total retrieved context.
    """

    def __init__(
        self,
        chunks: list[CorpusChunk] | None = None,
        collection: chromadb.Collection | None = None,
        voyage_client: voyageai.Client | None = None,
        max_chunks: int = MAX_RETRIEVAL_CHUNKS,
        max_words: int = MAX_RETRIEVAL_WORDS,
    ):
        self.chunks = chunks or build_corpus()
        self.collection = collection or get_or_create_collection()
        self.voyage_client = voyage_client or get_voyage_client()
        self.max_chunks = max_chunks
        self.max_words = max_words

        # Build BM25 index
        tokenized = [c.text.lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)
        self._chunk_id_to_chunk = {c.chunk_id: c for c in self.chunks}

    def retrieve(
        self,
        query: str,
        n_dense: int = 10,
        n_sparse: int = 10,
        dense_weight: float = 0.7,
    ) -> list[CorpusChunk]:
        """Retrieve relevant chunks using hybrid search.

        Args:
            query: The search query (e.g., scene text or VFX category description).
            n_dense: Number of results from dense retrieval.
            n_sparse: Number of results from BM25 retrieval.
            dense_weight: Weight for dense scores in fusion (0-1).

        Returns:
            Deduplicated, word-budget-capped list of CorpusChunks.
        """
        # Dense retrieval
        query_embedding = embed_query(query, client=self.voyage_client)
        dense_results = query_collection(
            query_embedding, collection=self.collection, n_results=n_dense
        )

        # BM25 sparse retrieval
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Score all chunks from both sources
        chunk_scores: dict[str, float] = {}

        # Dense scores (convert cosine distance to similarity)
        for r in dense_results:
            cid = r["chunk_id"]
            similarity = 1.0 - r["distance"]
            chunk_scores[cid] = chunk_scores.get(cid, 0.0) + dense_weight * similarity

        # BM25 scores (normalize to 0-1 range)
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
        sparse_weight = 1.0 - dense_weight
        scored_indices = sorted(
            range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
        )[:n_sparse]

        for idx in scored_indices:
            if bm25_scores[idx] > 0:
                cid = self.chunks[idx].chunk_id
                norm_score = bm25_scores[idx] / max_bm25
                chunk_scores[cid] = (
                    chunk_scores.get(cid, 0.0) + sparse_weight * norm_score
                )

        # Rank by combined score
        ranked_ids = sorted(chunk_scores, key=lambda cid: chunk_scores[cid], reverse=True)

        # Deduplicate by source section (keep best-scoring chunk per section)
        seen_sections: set[str] = set()
        deduplicated: list[CorpusChunk] = []

        for cid in ranked_ids:
            chunk = self._chunk_id_to_chunk.get(cid)
            if chunk is None:
                continue
            section_key = f"{chunk.source_file}::{chunk.section_title}"
            if section_key in seen_sections:
                continue
            seen_sections.add(section_key)
            deduplicated.append(chunk)

            if len(deduplicated) >= self.max_chunks:
                break

        # Enforce word budget
        result: list[CorpusChunk] = []
        total_words = 0
        for chunk in deduplicated:
            words = len(chunk.text.split())
            if total_words + words > self.max_words:
                break
            result.append(chunk)
            total_words += words

        return result

    def retrieve_for_categories(
        self,
        vfx_categories: list[str],
    ) -> list[CorpusChunk]:
        """Retrieve context relevant to a set of VFX categories.

        Deduplicates across categories to avoid redundant context.
        Used when you already know what VFX categories are involved.
        """
        all_chunks: dict[str, CorpusChunk] = {}

        for category in vfx_categories:
            results = self.retrieve(
                f"VFX category: {category}", n_dense=5, n_sparse=5
            )
            for chunk in results:
                if chunk.chunk_id not in all_chunks:
                    all_chunks[chunk.chunk_id] = chunk

        # Enforce word budget on merged results
        result: list[CorpusChunk] = []
        total_words = 0
        for chunk in all_chunks.values():
            words = len(chunk.text.split())
            if total_words + words > self.max_words:
                break
            result.append(chunk)
            total_words += words

        return result
