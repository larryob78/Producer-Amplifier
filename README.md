# Script Breakdown Assistant (SBA)

AI-powered VFX script breakdown tool for film producers. Parses screenplays (PDF or plain text), uses Claude to produce scene-by-scene VFX analysis with shot count estimates, cost/schedule risk scores, hidden cost flags, and department-specific questions. Outputs JSON, CSV, and a self-contained HTML production bible.

## Quick Start

```bash
git clone git@github.com:larryob78/Producer-Amplifier.git
cd Producer-Amplifier

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Edit .env and add your Anthropic API key

sba analyze myscript.pdf --title "My Film"
```

## CLI Commands

| Command | Description | Key Flags |
|---------|-------------|-----------|
| `sba analyze SCRIPT` | Full VFX breakdown analysis | `--title`, `--output-dir`, `--model`, `--use-rag`, `--json-only` |
| `sba build-corpus` | Display corpus statistics | |
| `sba index-corpus` | Index corpus into ChromaDB for full RAG | Requires `VOYAGE_API_KEY` |
| `sba export-csv JSON` | Export breakdown JSON to CSV | `--output` |
| `sba export-html-cmd JSON` | Export breakdown JSON to HTML | `--output` |

## Architecture

```
PDF/Text → Parsing Pipeline → RAG Context → Claude API → Pydantic Validation → JSON/CSV/HTML
```

| Package | Role |
|---------|------|
| `sba.parsing` | Scene detection, character extraction, VFX trigger scanning |
| `sba.rag` | Corpus building, Voyage embeddings, ChromaDB, hybrid retrieval |
| `sba.llm` | Prompt templates, Claude API wrapper, analysis orchestration |
| `sba.output` | Pydantic schema, JSON validation, CSV export, HTML production bible |

### RAG Modes

- **RAG-lite (default):** Injects the full corpus (~5,000 words) as static context. No embedding API needed.
- **Full RAG (`--use-rag`):** ChromaDB + Voyage AI hybrid retrieval. Requires `VOYAGE_API_KEY`. Use when corpus exceeds ~20k words.

## Configuration

Create a `.env` file (see `.env.example`):

```bash
# Required for analysis
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Required only for full RAG mode
VOYAGE_API_KEY=your-voyage-key-here

# Optional overrides
# CLAUDE_MODEL=claude-opus-4-6
# MAX_TOKENS=16384
```

## Running Tests

```bash
pytest                    # Run all tests
pytest --tb=short -q      # Quick summary
pytest --cov=sba          # With coverage
```

## Output Files

After running `sba analyze`, the `output/` directory contains:

- `{title}_{timestamp}.json` — Full structured breakdown (Pydantic-validated)
- `{title}_{timestamp}.csv` — Flat scene table for spreadsheets
- `{title}_{timestamp}.html` — Self-contained production bible (open in browser)

## License

MIT — see [LICENSE](LICENSE).
