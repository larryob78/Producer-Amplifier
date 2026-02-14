"""CLI interface for the Script Breakdown Assistant."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from sba.config import DEFAULT_OUTPUT_DIR


@click.group()
@click.version_option(version="0.1.0", prog_name="sba")
def cli():
    """Script Breakdown Assistant — AI-powered VFX breakdown for producers."""
    pass


@cli.command()
@click.argument("script_path", type=click.Path(exists=True))
@click.option("--title", "-t", default=None, help="Project title.")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default=None,
    help="Output directory for JSON and CSV files.",
)
@click.option(
    "--use-rag",
    is_flag=True,
    default=False,
    help="Use full RAG retrieval instead of static corpus injection.",
)
@click.option(
    "--json-only",
    is_flag=True,
    default=False,
    help="Output only JSON (skip CSV export).",
)
@click.option(
    "--model",
    "-m",
    default=None,
    help="Override Claude model (default: claude-opus-4-6).",
)
@click.option(
    "--staged",
    is_flag=True,
    default=False,
    help="Use staged per-scene analysis with synthesis pass.",
)
@click.option(
    "--max-scenes",
    type=int,
    default=None,
    help="Analyze only first N scenes (for quick sampling).",
)
@click.option(
    "--batch-size",
    type=int,
    default=5,
    help="Scenes per Claude call in staged mode (default: 5).",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Bypass result cache.",
)
def analyze(
    script_path: str,
    title: str | None,
    output_dir: str | None,
    use_rag: bool,
    json_only: bool,
    model: str | None,
    staged: bool,
    max_scenes: int | None,
    batch_size: int,
    no_cache: bool,
):
    """Analyze a screenplay and generate a VFX breakdown.

    SCRIPT_PATH is the path to a screenplay file (PDF or plain text).
    """
    from sba.llm.generator import analyze_script
    from sba.output.export_csv import export_scenes_csv
    from sba.output.export_html import export_html

    script_file = Path(script_path)
    title = title or script_file.stem
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)

    click.echo(f"Analyzing: {script_file.name}")
    click.echo(f"Title: {title}")
    click.echo(f"Mode: {'Full RAG' if use_rag else 'RAG-lite (static corpus)'}")
    if staged:
        click.echo(f"Strategy: Staged (batch_size={batch_size})")
        if max_scenes:
            click.echo(f"Sampling: first {max_scenes} scenes only")
    click.echo()

    # Check API key before expensive work
    from sba.config import ANTHROPIC_API_KEY, VOYAGE_API_KEY

    if not ANTHROPIC_API_KEY:
        click.echo(
            "Error: ANTHROPIC_API_KEY not set.\n"
            "Copy .env.example to .env and add your key:\n"
            "  cp .env.example .env\n"
            "  # Then edit .env with your Anthropic API key",
            err=True,
        )
        sys.exit(1)

    if use_rag and not VOYAGE_API_KEY:
        click.echo(
            "Error: VOYAGE_API_KEY not set (required for --use-rag mode).\n"
            "Add your Voyage AI key to .env, or run without --use-rag for RAG-lite mode.",
            err=True,
        )
        sys.exit(1)

    def _progress(step: int, total: int, message: str) -> None:
        click.echo(f"  [{step}/{total}] {message}")

    try:
        if staged:
            from sba.llm.generator import analyze_script_staged

            result = analyze_script_staged(
                file_path=script_file,
                title=title,
                use_rag=use_rag,
                model=model,
                batch_size=batch_size,
                max_scenes=max_scenes,
                use_cache=not no_cache,
                progress_callback=_progress,
            )
        else:
            result = analyze_script(
                file_path=script_file,
                title=title,
                use_rag=use_rag,
                model=model,
            )
    except RuntimeError as e:
        click.echo(f"Analysis failed: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)

    # Export JSON
    json_path = out_dir / f"{safe_title}_{timestamp}.json"
    json_data = result.model_dump_json(indent=2)
    json_path.write_text(json_data, encoding="utf-8")
    click.echo(f"JSON saved: {json_path}")

    # Export CSV + HTML
    if not json_only:
        csv_path = out_dir / f"{safe_title}_{timestamp}.csv"
        export_scenes_csv(result, csv_path)
        click.echo(f"CSV saved:  {csv_path}")

        html_path = out_dir / f"{safe_title}_{timestamp}.html"
        export_html(result, html_path)
        click.echo(f"HTML saved: {html_path}")

    # Print summary
    click.echo()
    click.echo("=== Summary ===")
    click.echo(f"Scenes: {len(result.scenes)}")
    click.echo(f"VFX heaviness: {result.global_flags.overall_vfx_heaviness}")
    if result.global_flags.top_risk_themes:
        click.echo(f"Top risks: {', '.join(result.global_flags.top_risk_themes)}")
    if result.hidden_cost_radar:
        click.echo(f"Hidden cost flags: {len(result.hidden_cost_radar)}")

    total_shots_likely = sum(s.vfx_shot_count_estimate.likely for s in result.scenes)
    click.echo(f"Est. total VFX shots (likely): {total_shots_likely}")


@cli.command()
def build_corpus():
    """Build and display corpus statistics."""
    from sba.rag.corpus_builder import build_corpus as _build_corpus

    chunks = _build_corpus()
    click.echo(f"Total chunks: {len(chunks)}")

    by_source: dict[str, int] = {}
    total_words = 0
    for c in chunks:
        by_source[c.source_file] = by_source.get(c.source_file, 0) + 1
        total_words += len(c.text.split())

    click.echo(f"Total words: {total_words:,}")
    click.echo()
    click.echo("Chunks by source:")
    for source, count in sorted(by_source.items()):
        click.echo(f"  {source}: {count}")


@cli.command()
def index_corpus():
    """Index the corpus into ChromaDB for full RAG mode."""
    from sba.config import VOYAGE_API_KEY
    from sba.rag.corpus_builder import build_corpus as _build_corpus
    from sba.rag.embedder import embed_chunks, get_voyage_client
    from sba.rag.vector_store import index_chunks

    if not VOYAGE_API_KEY:
        click.echo(
            "Error: VOYAGE_API_KEY not set.\n"
            "Add your Voyage AI key to .env to use full RAG indexing.",
            err=True,
        )
        sys.exit(1)

    click.echo("Building corpus chunks...")
    chunks = _build_corpus()
    click.echo(f"  {len(chunks)} chunks built")

    click.echo("Generating Voyage embeddings...")
    client = get_voyage_client()
    embeddings = embed_chunks(chunks, client=client)
    click.echo(f"  {len(embeddings)} embeddings generated")

    click.echo("Indexing into ChromaDB...")
    collection = index_chunks(chunks, embeddings)
    click.echo(f"  {collection.count()} chunks indexed")

    click.echo("Done! Corpus is ready for RAG retrieval.")


@cli.command()
@click.argument("json_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output CSV path. Defaults to same directory as JSON.",
)
def export_csv(json_path: str, output: str | None):
    """Export a breakdown JSON file to CSV."""
    from sba.output.export_csv import export_scenes_csv
    from sba.output.schema import BreakdownOutput

    json_file = Path(json_path)
    data = json.loads(json_file.read_text(encoding="utf-8"))
    breakdown = BreakdownOutput.model_validate(data)

    csv_path = Path(output) if output else json_file.with_suffix(".csv")
    export_scenes_csv(breakdown, csv_path)
    click.echo(f"CSV exported: {csv_path}")


@cli.command()
@click.argument("json_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output HTML path. Defaults to same directory as JSON.",
)
def export_html_cmd(json_path: str, output: str | None):
    """Export a breakdown JSON file to HTML production bible."""
    from sba.output.export_html import export_html
    from sba.output.schema import BreakdownOutput

    json_file = Path(json_path)
    data = json.loads(json_file.read_text(encoding="utf-8"))
    breakdown = BreakdownOutput.model_validate(data)

    html_path = Path(output) if output else json_file.with_suffix(".html")
    export_html(breakdown, html_path)
    click.echo(f"HTML exported: {html_path}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
