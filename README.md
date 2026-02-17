# Napkin Producer Amplifier (NPA)

**AI-Powered Production Intelligence for Film & Television Producers**

Upload a screenplay. Get an instant scene-by-scene breakdown with VFX detection, risk scoring, cost estimates, and a live budget — all through a single web interface with an AI copilot that knows your entire script.

Built for productions like Star Wars, Marvel, and major studio features.

## What It Does

```
Script Upload → Scene Parsing → VFX Detection → Risk Scoring → Live Budget → AI Chat
```

- **Multi-format script parsing** — PDF, Word (.docx/.doc), Final Draft (.fdx), Fountain, Plain Text, RTF
- **13-category VFX detection** — creatures, destruction, weather, set extension, vehicles, weapons, supernatural, water, fire, aerial, crowds, digital augmentation, stunts
- **Risk scoring (1–5)** — colour-coded severity per scene based on VFX complexity
- **Live Excel budget** — reads and writes standard film industry budget spreadsheets (Account codes 1100–9000)
- **AI Producer Copilot** — three-tier Claude routing (Opus for deep reasoning, Sonnet for analysis, Haiku for quick lookups)
- **Voice interface** — Whisper STT + ElevenLabs TTS for hands-free production queries
- **VFX Provisor** — cost intelligence engine mapping VFX triggers to shot estimates, vendor rates, and budget line items

## Quick Start

```bash
git clone git@github.com:larryob78/Producer-Amplifier.git
cd Producer-Amplifier

cp .env.example .env
# Fill in your API keys (see Configuration below)

pip install -r requirements.txt

cd src && uvicorn sba.app:app --reload
```

Open `http://localhost:8000` and drop a screenplay.

## Web Interface

The NPA web UI (`script-breakdown-ui.html`) provides:

- **Hero upload area** — drag-and-drop or click to upload any supported screenplay format
- **Scene cards** — each scene shows slugline (INT/EXT, DAY/NIGHT), characters, VFX triggers with category tags, and risk score
- **Filters** — filter scenes by All, Has VFX, High Risk, INT, EXT
- **Red LIVE BUDGET button** — pulsing indicator, opens budget panel showing total/actual/variance from the master Excel file
- **AI Chat panel** — auto-opens on load, ask questions like "What VFX does Scene 5 need?" or "Compare costs between Scene 3 and Scene 9"
- **Voice input** — 15-second capture with automatic Whisper transcription, sends to chat

## Architecture

```
src/sba/
├── app.py              FastAPI application — serves UI + REST API
├── config.py           Environment config, model routing, paths
├── cli.py              Command-line interface (napkin analyze, export)
├── cache.py            Response caching
│
├── parsing/            12 files — the core script engine
│   ├── pipeline.py         Main pipeline: parse_script_file() → structured output
│   ├── scene_parser.py     INT/EXT, DAY/NIGHT, location extraction
│   ├── character_parser.py Character detection per scene
│   ├── vfx_scanner.py      13-category VFX trigger detection with severity
│   ├── vfx_mapper.py       Trigger-to-category mapping
│   ├── pdf_extractor.py    PDF parsing (pdfplumber)
│   ├── docx_extractor.py   Word document parsing (python-docx)
│   ├── fdx_extractor.py    Final Draft XML parsing
│   ├── text_extractor.py   Plain text / Fountain / RTF
│   ├── preprocessor.py     Script text normalisation
│   └── models.py           Data models
│
├── chat/               5 files — AI Producer Copilot
│   ├── router.py           FastAPI chat endpoints
│   ├── model_router.py     Three-tier Claude routing (Opus/Sonnet/Haiku)
│   ├── system_prompt.py    Production-aware system prompt
│   └── tools.py            Chat tool definitions
│
├── llm/                4 files — LLM abstraction
│   ├── claude_client.py    Anthropic API wrapper
│   ├── generator.py        Analysis orchestration
│   └── prompts.py          Prompt templates
│
├── budget/             3 files — Live Excel budget
│   ├── excel_reader.py     Read standard film budgets (Account 1100–9000)
│   └── excel_writer.py     Write budget updates with audit trail
│
├── voice/              3 files — Voice interface
│   ├── stt.py              OpenAI Whisper speech-to-text
│   └── tts.py              ElevenLabs text-to-speech
│
├── rag/                5 files — Script-aware retrieval
│   ├── corpus_builder.py   Build searchable corpus from screenplay
│   ├── embedder.py         Voyage AI embeddings
│   ├── retriever.py        Hybrid retrieval
│   └── vector_store.py     Vector storage
│
└── output/             5 files — Export formats
    ├── export_csv.py       CSV scene table
    ├── export_html.py      Self-contained HTML production bible
    ├── schema.py           Pydantic output schema
    └── validate.py         Output validation
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the NPA web interface |
| GET | `/npa-integration.js` | Serve the integration layer (chat, budget, voice) |
| POST | `/api/script/upload` | Upload and parse a screenplay (returns scenes, characters, VFX triggers) |
| GET | `/api/script/current` | Get the currently loaded script data |
| GET | `/api/script/formats` | List supported screenplay formats |
| POST | `/api/chat/message` | Send a message to the AI Producer Copilot |
| GET | `/api/budget/summary` | Get budget totals (total, actual, variance) |
| GET | `/api/budget/vfx` | Get VFX cost detail by scene |
| GET | `/api/budget/account/{code}` | Read a specific budget account (1100–9000) |
| POST | `/api/budget/update` | Update a budget value with audit trail |
| POST | `/api/voice/transcribe` | Transcribe audio via Whisper |
| POST | `/api/voice/speak` | Text-to-speech via ElevenLabs |
| GET | `/api/health` | Health check (status, versions, loaded state) |

## VFX Categories

NPA detects 13 industry-standard VFX categories:

| Category | Examples | Typical Severity |
|----------|----------|-----------------|
| Creatures/Animals | CG dinosaur, hero animal | HIGH |
| Set Extension | Extend practical set digitally | MEDIUM |
| Destruction/Damage | Building collapse, explosions | HIGH |
| Weather/Atmosphere | Rain, fog, sandstorm | MEDIUM |
| Vehicles/Mech | Spaceships, mech suits | HIGH |
| Weapons/Combat | Muzzle flash, laser, sword glow | LOW |
| Supernatural/Magic | Force powers, portals, spells | HIGH |
| Water Work | Ocean, underwater, flooding | HIGH |
| Fire/Pyro | CG fire, lava, plasma | MEDIUM |
| Aerial/Height | Flying, falling, wire removal | MEDIUM |
| Crowd/Extras | CG crowd duplication | LOW |
| Digital Augmentation | Screen inserts, sign replacement | LOW |
| Stunts | Wire removal, face replacement | MEDIUM |

## Master Budget Template

`NPA_MasterBudget_v1.xlsx` — a three-sheet Excel template following standard film industry structure:

- **Top Sheet** — accounts 1100–9000 with Budget, Actual, Variance, Var % columns
- **VFX Detail** — per-scene VFX breakdown (Account 4300) with shot counts and category costs
- **Schedule** — shooting schedule overview with days, locations, cast, risk ratings

## Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Required keys:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here     # Required — powers all AI features
OPENAI_API_KEY=sk-your-openai-key-here     # Required for voice input (Whisper)
ELEVENLABS_API_KEY=your-key-here           # Required for voice output (TTS)
VOYAGE_API_KEY=your-voyage-key-here        # Required for RAG embeddings
MASTER_BUDGET_PATH=./NPA_MasterBudget_v1.xlsx  # Path to budget file
```

## CLI Commands

The CLI is still available for batch processing:

```bash
napkin analyze myscript.pdf --title "My Film"
napkin export-csv output.json
napkin export-html-cmd output.json
napkin build-corpus
napkin index-corpus
```

## Running Tests

```bash
pytest                    # Run all tests
pytest --tb=short -q      # Quick summary
pytest --cov=sba          # With coverage
```

## Project Documents

- `NPA-PRD-v05.docx` — Product Requirements Document (everything built + roadmap)
- `VFX-Provisor-Planning-v1.docx` — VFX cost intelligence engine planning document
- `NPA_MasterBudget_v1.xlsx` — Master budget template

## Tech Stack

- **Runtime:** Python 3.11+ / FastAPI / uvicorn
- **AI:** Claude Opus 4.6, Sonnet 4.5, Haiku 4.5 (Anthropic API)
- **Voice:** OpenAI Whisper (STT), ElevenLabs (TTS)
- **Embeddings:** Voyage AI (voyage-3)
- **Budget:** openpyxl for Excel read/write
- **Parsing:** pdfplumber (PDF), python-docx (Word), XML (Final Draft)
- **Frontend:** Vanilla HTML/CSS/JS — no framework, fully self-contained

## License

MIT — see LICENSE.
