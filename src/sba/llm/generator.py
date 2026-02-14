"""Orchestrates the full analysis pipeline: parse → retrieve → prompt → call → validate."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from sba.llm.claude_client import call_claude, get_anthropic_client
from sba.llm.prompts import (
    SYSTEM_PROMPT,
    build_parsing_summary,
    build_user_prompt,
)
from sba.output.validate import validate_breakdown_json
from sba.parsing.pipeline import parse_script_file, parse_script_text
from sba.rag.corpus_builder import load_corpus_as_text

if TYPE_CHECKING:
    from sba.output.schema import BreakdownOutput


def analyze_script(
    file_path: str | Path | None = None,
    text: str | None = None,
    title: str = "Untitled",
    use_rag: bool = False,
    max_retries: int = 1,
) -> BreakdownOutput:
    """Run the full script breakdown analysis pipeline.

    Args:
        file_path: Path to a screenplay file (PDF or text).
        text: Raw screenplay text (alternative to file_path).
        title: Project title.
        use_rag: If True, use full RAG retrieval. If False, use RAG-lite (static injection).
        max_retries: Number of retries on validation failure.

    Returns:
        Validated BreakdownOutput Pydantic model.

    Raises:
        ValueError: If neither file_path nor text is provided.
        RuntimeError: If validation fails after all retries.
    """
    if file_path is None and text is None:
        raise ValueError("Either file_path or text must be provided.")

    # Step 1: Parse the script
    if file_path:
        parsed = parse_script_file(Path(file_path), title=title)
        script_text = parsed.raw_text
    else:
        parsed = parse_script_text(text, title=title)
        script_text = text

    # Step 2: Get corpus context
    if use_rag:
        corpus_context = _retrieve_rag_context(parsed)
    else:
        corpus_context = load_corpus_as_text()

    # Step 3: Build prompts
    parsing_summary = build_parsing_summary(parsed)
    user_prompt = build_user_prompt(
        script_text=script_text,
        title=title,
        corpus_context=corpus_context,
        parsing_summary=parsing_summary,
    )

    # Step 4: Call Claude
    client = get_anthropic_client()
    raw_json = call_claude(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        client=client,
    )

    # Step 5: Validate
    result = validate_breakdown_json(raw_json)
    if result.is_valid:
        return result.output

    # Step 6: Retry with error feedback
    for attempt in range(max_retries):
        error_feedback = (
            f"Your previous response had validation errors:\n{result.error_message}\n\n"
            "Please fix these errors and output valid JSON. Remember: output ONLY the JSON "
            "object with no surrounding text or markdown fences."
        )
        retry_prompt = f"{user_prompt}\n\n## IMPORTANT CORRECTION\n{error_feedback}"

        raw_json = call_claude(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=retry_prompt,
            client=client,
        )

        result = validate_breakdown_json(raw_json)
        if result.is_valid:
            return result.output

    raise RuntimeError(
        f"Failed to get valid breakdown after {max_retries + 1} attempts. "
        f"Last error: {result.error_message}"
    )


def _retrieve_rag_context(parsed) -> str:
    """Use the full RAG pipeline to retrieve relevant context.

    Retrieves based on detected VFX trigger categories from parsing.
    """
    from sba.rag.corpus_builder import build_corpus
    from sba.rag.embedder import get_voyage_client
    from sba.rag.retriever import HybridRetriever
    from sba.rag.vector_store import get_or_create_collection

    # Collect unique VFX categories from all scenes
    vfx_categories: set[str] = set()
    for scene in parsed.scenes:
        for trigger in scene.vfx_triggers:
            vfx_categories.add(trigger.category)

    if not vfx_categories:
        # Fall back to full corpus if no triggers detected
        return load_corpus_as_text()

    # Build retriever
    chunks = build_corpus()
    collection = get_or_create_collection()
    voyage_client = get_voyage_client()
    retriever = HybridRetriever(
        chunks=chunks,
        collection=collection,
        voyage_client=voyage_client,
    )

    # Retrieve for detected categories
    results = retriever.retrieve_for_categories(list(vfx_categories))

    # Format as context text
    parts = []
    for chunk in results:
        parts.append(f"[{chunk.source_file} > {chunk.section_title}]\n{chunk.text}")

    return "\n\n---\n\n".join(parts)
