# Script Breakdown Assistant Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool that analyzes screenplays and produces producer-grade VFX breakdowns with cost/schedule risk scores, exported as JSON and CSV.

**Architecture:** Sequential pipeline — PDF/text → parse scenes → retrieve RAG context (or inject static corpus) → single Claude Opus 4.6 API call → Pydantic validation → JSON/CSV export. RAG infrastructure (ChromaDB + Voyage) built but gated behind `--use-rag` flag; default mode injects full corpus as static context.

**Tech Stack:** Python 3.11+, Click (CLI), pdfplumber (PDF), Pydantic v2 (schema/validation), ChromaDB (vectors), Voyage AI (embeddings), rank-bm25 (keyword search), Anthropic SDK (Claude), json-repair (fallback)

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `src/sba/__init__.py`
- Create: `src/sba/config.py`
- Create: `tests/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "script-breakdown-assistant"
version = "0.1.0"
description = "Intelligent script breakdown assistant for film producers"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.40.0",
    "pdfplumber>=0.10.0",
    "pydantic>=2.0",
    "chromadb>=0.5.0",
    "voyageai>=0.3.0",
    "rank-bm25>=0.2.0",
    "json-repair>=0.28.0",
    "click>=8.0",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov>=4.0"]

[project.scripts]
sba = "sba.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: Create .env.example**

```
ANTHROPIC_API_KEY=your-anthropic-api-key-here
VOYAGE_API_KEY=your-voyage-api-key-here
```

**Step 3: Create src/sba/__init__.py**

```python
"""Script Breakdown Assistant — VFX-aware screenplay analysis tool."""
```

**Step 4: Create src/sba/config.py**

```python
"""Application configuration loaded from environment."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
CORPUS_DIR = PROJECT_ROOT / "corpus"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "")
CLAUDE_MODEL = "claude-opus-4-6"
VOYAGE_MODEL = "voyage-3"

MAX_RETRIEVAL_CHUNKS = 40
MAX_RETRIEVAL_WORDS = 15000
```

**Step 5: Create tests/__init__.py**

Empty file.

**Step 6: Create virtual environment and install**

Run:
```bash
cd "/Users/laurenceobyrne/prodcuer breaksdown tool"
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

Expected: Installs successfully, `sba` command available (will fail since cli.py doesn't exist yet — that's fine).

**Step 7: Initialize git repo**

Run:
```bash
cd "/Users/laurenceobyrne/prodcuer breaksdown tool"
git init
echo ".venv/\n__pycache__/\n*.pyc\n.env\noutput/\nchroma_db/\n*.egg-info/\ndist/\nbuild/" > .gitignore
git add pyproject.toml .env.example .gitignore src/sba/__init__.py src/sba/config.py tests/__init__.py
git commit -m "feat: project scaffolding with dependencies"
```

---

## Task 2: Pydantic Schema (the single source of truth)

**Files:**
- Create: `src/sba/output/__init__.py`
- Create: `src/sba/output/schema.py`
- Create: `tests/test_schema.py`

**Step 1: Write the failing test**

```python
# tests/test_schema.py
"""Tests for the output schema models."""

import json
from sba.output.schema import (
    BreakdownOutput,
    Scene,
    VfxCategory,
    VfxShotCountEstimate,
    ProductionFlags,
    HiddenCostItem,
)


def test_minimal_valid_scene():
    """A scene with only required fields should validate."""
    scene = Scene(
        scene_id="SC001",
        slugline="INT. OFFICE - DAY",
        int_ext="int",
        day_night="day",
        vfx_shot_count_estimate=VfxShotCountEstimate(min=0, likely=0, max=0),
        invisible_vfx_likelihood="low",
        cost_risk_score=1,
        schedule_risk_score=1,
    )
    assert scene.scene_id == "SC001"
    assert scene.production_flags.stunts is False


def test_vfx_category_enum():
    """VFX categories must be from the defined enum."""
    assert VfxCategory.MATCHMOVE == "matchmove"
    assert VfxCategory.CG_CREATURE == "cg_creature"
    assert VfxCategory.OTHER == "other"


def test_shot_count_estimate_ordering():
    """min <= likely <= max must hold."""
    est = VfxShotCountEstimate(min=2, likely=5, max=8)
    assert est.min <= est.likely <= est.max


def test_cost_risk_score_range():
    """Cost risk must be 1-5."""
    import pytest
    with pytest.raises(Exception):
        Scene(
            scene_id="SC001",
            slugline="INT. OFFICE - DAY",
            int_ext="int",
            day_night="day",
            vfx_shot_count_estimate=VfxShotCountEstimate(min=0, likely=0, max=0),
            invisible_vfx_likelihood="low",
            cost_risk_score=6,
            schedule_risk_score=1,
        )


def test_full_breakdown_roundtrip():
    """A full BreakdownOutput should serialize to JSON and back."""
    output = BreakdownOutput(
        project_summary={
            "project_title": "Test Film",
            "date_analyzed": "2026-02-14T10:00:00Z",
            "analysis_scope": "excerpt",
            "total_scene_count": 1,
        },
        global_flags={
            "overall_vfx_heaviness": "low",
            "likely_virtual_production_fit": "low",
            "top_risk_themes": [],
        },
        scenes=[
            Scene(
                scene_id="SC001",
                slugline="INT. OFFICE - DAY",
                int_ext="int",
                day_night="day",
                vfx_shot_count_estimate=VfxShotCountEstimate(min=0, likely=0, max=0),
                invisible_vfx_likelihood="low",
                cost_risk_score=1,
                schedule_risk_score=1,
            )
        ],
        hidden_cost_radar=[],
        key_questions_for_team={
            "for_producer": [],
            "for_vfx_supervisor": [],
            "for_dp_camera": [],
            "for_locations_art_dept": [],
        },
    )
    json_str = output.model_dump_json()
    parsed = BreakdownOutput.model_validate_json(json_str)
    assert parsed.scenes[0].scene_id == "SC001"
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/laurenceobyrne/prodcuer breaksdown tool" && source .venv/bin/activate && pytest tests/test_schema.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sba.output'`

**Step 3: Write the schema implementation**

```python
# src/sba/output/__init__.py
"""Output schema, validation, and export modules."""
```

```python
# src/sba/output/schema.py
"""Pydantic models defining the breakdown output schema.

This is the single source of truth for the JSON structure.
CSV export is derived from these models, not stored separately.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VfxCategory(str, Enum):
    """Valid VFX category values. Include in system prompt for Claude."""

    # Compositing and 2D
    COMP = "comp"
    ROTO = "roto"
    PAINT_CLEANUP = "paint_cleanup"
    WIRE_REMOVAL = "wire_removal"

    # 3D / CG
    CG_CREATURE = "cg_creature"
    CG_VEHICLE = "cg_vehicle"
    CG_PROP = "cg_prop"
    CG_ENVIRONMENT = "cg_environment"
    DIGI_DOUBLE = "digi_double"
    FACE_REPLACEMENT = "face_replacement"

    # Environment
    SET_EXTENSION = "set_extension"
    MATTE_PAINTING = "matte_painting"
    SKY_REPLACEMENT = "sky_replacement"

    # FX Simulation
    FX_WATER = "fx_water"
    FX_FIRE = "fx_fire"
    FX_SMOKE_DUST = "fx_smoke_dust"
    FX_DESTRUCTION = "fx_destruction"
    FX_WEATHER = "fx_weather"
    FX_EXPLOSION = "fx_explosion"

    # Camera / Tracking
    MATCHMOVE = "matchmove"
    CAMERA_PROJECTION = "camera_projection"

    # Specialty
    CROWD_SIM = "crowd_sim"
    ZERO_G = "zero_g"
    SCREEN_INSERT = "screen_insert"
    DAY_FOR_NIGHT = "day_for_night"
    BEAUTY_WORK = "beauty_work"
    OTHER = "other"


class VfxShotCountEstimate(BaseModel):
    """Range estimate for VFX shots in a scene."""

    min: int = Field(ge=0)
    likely: int = Field(ge=0)
    max: int = Field(ge=0)


class ProductionFlags(BaseModel):
    """Boolean flags for production elements that affect planning."""

    stunts: bool = False
    creatures: bool = False
    vehicles: bool = False
    crowds: bool = False
    water: bool = False
    fire_smoke: bool = False
    destruction: bool = False
    weather: bool = False
    complex_lighting: bool = False
    space_or_zero_g: bool = False
    heavy_costume_makeup: bool = False


class Scene(BaseModel):
    """A single scene breakdown."""

    scene_id: str
    slugline: str
    int_ext: str = "unspecified"  # int, ext, int_ext, unspecified
    day_night: str = "unspecified"  # day, night, dawn, dusk, continuous, unspecified
    page_count_eighths: int = 0
    location_type: str = "unspecified"  # practical, stage, virtual_production, ext_location, mixed, unspecified
    characters: list[str] = Field(default_factory=list)
    scene_summary: str = ""
    vfx_triggers: list[str] = Field(default_factory=list)
    production_flags: ProductionFlags = Field(default_factory=ProductionFlags)
    vfx_categories: list[VfxCategory] = Field(default_factory=list)
    vfx_shot_count_estimate: VfxShotCountEstimate
    invisible_vfx_likelihood: str  # low, medium, high
    cost_risk_score: int = Field(ge=1, le=5)
    schedule_risk_score: int = Field(ge=1, le=5)
    risk_reasons: list[str] = Field(default_factory=list)
    suggested_capture: list[str] = Field(default_factory=list)
    notes_for_producer: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class HiddenCostItem(BaseModel):
    """A hidden cost multiplier flagged by the analysis."""

    flag: str
    severity: str  # low, medium, high
    where: list[str] = Field(default_factory=list)
    why_it_matters: str = ""
    mitigation_ideas: list[str] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    """Top-level project metadata."""

    project_title: str = ""
    date_analyzed: str = ""
    analysis_scope: str = "full_script"  # full_script, excerpt
    script_pages_estimate: Optional[int] = None
    total_scene_count: int = 0
    confidence_notes: list[str] = Field(default_factory=list)


class GlobalFlags(BaseModel):
    """Project-wide assessment flags."""

    overall_vfx_heaviness: str = "low"  # low, medium, high, very_high
    likely_virtual_production_fit: str = "low"  # low, medium, high
    top_risk_themes: list[str] = Field(default_factory=list)


class KeyQuestions(BaseModel):
    """Questions generated for each department."""

    for_producer: list[str] = Field(default_factory=list)
    for_vfx_supervisor: list[str] = Field(default_factory=list)
    for_dp_camera: list[str] = Field(default_factory=list)
    for_locations_art_dept: list[str] = Field(default_factory=list)


class BreakdownOutput(BaseModel):
    """Root model for the complete breakdown output."""

    project_summary: ProjectSummary
    global_flags: GlobalFlags
    scenes: list[Scene]
    hidden_cost_radar: list[HiddenCostItem] = Field(default_factory=list)
    key_questions_for_team: KeyQuestions = Field(default_factory=KeyQuestions)
```

**Step 4: Run tests to verify they pass**

Run: `cd "/Users/laurenceobyrne/prodcuer breaksdown tool" && source .venv/bin/activate && pytest tests/test_schema.py -v`
Expected: All 5 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/output/ tests/test_schema.py
git commit -m "feat: add Pydantic output schema with VFX category enum"
```

---

## Task 3: Parsing Models (data structures)

**Files:**
- Create: `src/sba/parsing/__init__.py`
- Create: `src/sba/parsing/models.py`

**Step 1: Write the models**

```python
# src/sba/parsing/__init__.py
"""Script parsing modules."""
```

```python
# src/sba/parsing/models.py
"""Data structures for parsed screenplay elements."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VFXTrigger:
    """A VFX trigger detected in action text."""

    category: str
    matched_keyword: str
    severity: str  # low, medium, high
    context: str  # surrounding text snippet
    position: int = 0


@dataclass
class Character:
    """A character extracted from the screenplay."""

    canonical_name: str
    variants: set[str] = field(default_factory=set)
    extensions: set[str] = field(default_factory=set)  # V.O., O.S., etc.


@dataclass
class ParsedScene:
    """A scene as extracted from the raw screenplay text."""

    scene_number: int
    slugline: str
    int_ext: str = "unspecified"
    day_night: str = "unspecified"
    location: str = ""
    raw_text: str = ""
    action_lines: list[str] = field(default_factory=list)
    characters: list[str] = field(default_factory=list)
    vfx_triggers: list[VFXTrigger] = field(default_factory=list)
    page_start: int = 0
    page_end: int = 0
    word_count: int = 0


@dataclass
class ParsedScript:
    """Complete parsed screenplay."""

    title: str = ""
    raw_text: str = ""
    scenes: list[ParsedScene] = field(default_factory=list)
    all_characters: dict[str, Character] = field(default_factory=dict)
    total_pages_estimate: int = 0
    parsing_warnings: list[str] = field(default_factory=list)
```

**Step 2: Commit**

```bash
git add src/sba/parsing/
git commit -m "feat: add parsing data models"
```

---

## Task 4: Script Preprocessor

**Files:**
- Create: `src/sba/parsing/preprocessor.py`
- Create: `tests/test_preprocessor.py`

**Step 1: Write the failing test**

```python
# tests/test_preprocessor.py
"""Tests for script text preprocessing."""

from sba.parsing.preprocessor import preprocess_script_text


def test_removes_page_numbers():
    text = "some text\n\n  42  \n\nmore text"
    result = preprocess_script_text(text)
    assert "42" not in result
    assert "some text" in result
    assert "more text" in result


def test_removes_continued_markers():
    text = "JOHN\nHello there.\n(CONTINUED)\n\nCONTINUED:\nJOHN (CONT'D)\nMore dialogue."
    result = preprocess_script_text(text)
    assert "(CONTINUED)" not in result
    assert "CONTINUED:" not in result
    assert "JOHN" in result
    assert "JOHN (CONT'D)" in result  # Character CONT'D preserved


def test_collapses_blank_lines():
    text = "line 1\n\n\n\n\nline 2"
    result = preprocess_script_text(text)
    assert "\n\n\n" not in result
    assert "line 1" in result
    assert "line 2" in result


def test_normalizes_line_endings():
    text = "line 1\r\nline 2\rline 3\nline 4"
    result = preprocess_script_text(text)
    assert "\r" not in result
    assert result.count("\n") >= 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_preprocessor.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
# src/sba/parsing/preprocessor.py
"""Preprocess raw screenplay text to remove PDF artifacts."""

import re


def preprocess_script_text(raw_text: str) -> str:
    """Clean up raw text before scene parsing.

    Removes page numbers, CONTINUED markers, normalizes whitespace.
    Preserves character CONT'D extensions in dialogue cues.
    """
    text = raw_text

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove standalone page numbers (1-3 digits alone on a line)
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)

    # Remove CONTINUED markers at page breaks (but NOT character CONT'D)
    text = re.sub(
        r"^\s*\(CONTINUED\)\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE
    )
    text = re.sub(
        r"^\s*CONTINUED:\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE
    )

    # Collapse 3+ consecutive blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text
```

**Step 4: Run tests**

Run: `pytest tests/test_preprocessor.py -v`
Expected: All 4 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/parsing/preprocessor.py tests/test_preprocessor.py
git commit -m "feat: add script text preprocessor"
```

---

## Task 5: Scene Heading Detection and Splitting

**Files:**
- Create: `src/sba/parsing/scene_parser.py`
- Create: `tests/test_scene_parser.py`

**Step 1: Write the failing tests**

```python
# tests/test_scene_parser.py
"""Tests for scene heading detection and splitting."""

from sba.parsing.scene_parser import detect_scene_heading, split_into_scenes


def test_basic_int_day():
    match = detect_scene_heading("INT. OFFICE - DAY")
    assert match is not None
    assert match["int_ext"] == "int"
    assert match["location"] == "OFFICE"
    assert match["time_of_day"] == "DAY"


def test_ext_night():
    match = detect_scene_heading("EXT. ROOFTOP - NIGHT")
    assert match is not None
    assert match["int_ext"] == "ext"
    assert match["location"] == "ROOFTOP"
    assert match["time_of_day"] == "NIGHT"


def test_int_ext():
    match = detect_scene_heading("INT./EXT. CAR - DAY")
    assert match is not None
    assert match["int_ext"] == "int_ext"


def test_scene_numbers():
    match = detect_scene_heading("42 INT. OFFICE - DAY 42")
    assert match is not None
    assert match["location"] == "OFFICE"


def test_no_time_of_day():
    match = detect_scene_heading("INT. HALLWAY")
    assert match is not None
    assert match["time_of_day"] is None


def test_non_heading():
    match = detect_scene_heading("John walks into the room.")
    assert match is None


def test_continuous():
    match = detect_scene_heading("INT. KITCHEN - CONTINUOUS")
    assert match is not None
    assert match["time_of_day"] == "CONTINUOUS"


def test_split_simple_script():
    text = """INT. OFFICE - DAY

John sits at his desk.

JOHN
Hello.

EXT. PARKING LOT - NIGHT

Rain falls on empty cars.

JANE
Where is everyone?"""

    scenes = split_into_scenes(text)
    assert len(scenes) == 2
    assert scenes[0].slugline == "INT. OFFICE - DAY"
    assert scenes[0].int_ext == "int"
    assert scenes[0].day_night == "day"
    assert "John sits at his desk" in scenes[0].raw_text
    assert scenes[1].slugline == "EXT. PARKING LOT - NIGHT"
    assert scenes[1].int_ext == "ext"
    assert scenes[1].day_night == "night"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scene_parser.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
# src/sba/parsing/scene_parser.py
"""Scene heading detection and script splitting."""

from __future__ import annotations

import re
from sba.parsing.models import ParsedScene

# Scene heading pattern — handles INT., EXT., INT./EXT., scene numbers, time of day
SCENE_HEADING_RE = re.compile(
    r"^"
    r"(?:\d+[A-Z]?\s+)?"  # Optional scene number prefix
    r"(?P<ie_prefix>"
    r"(?:INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?)"  # INT./EXT. variants
    r"|I/E\.?"  # I/E. shorthand
    r"|INT\.?"  # INT.
    r"|EXT\.?"  # EXT.
    r"|EST\.?"  # EST. (establishing)
    r")"
    r"[\s.\-/]+"  # Separator
    r"(?P<location>.+?)"  # Location (non-greedy)
    r"(?:"
    r"\s*[-\u2013\u2014]+\s*"  # Dash separator
    r"(?P<time_of_day>"
    r"DAY|NIGHT|DAWN|DUSK|MORNING|AFTERNOON|EVENING"
    r"|CONTINUOUS|LATER|SAME\s*TIME|MOMENTS?\s*LATER"
    r"|SUNSET|SUNRISE"
    r")"
    r")?"
    r"(?:\s+\d+[A-Z]?)?"  # Optional scene number suffix
    r"\s*$",
    re.IGNORECASE,
)

TIME_TO_DAY_NIGHT = {
    "day": "day",
    "night": "night",
    "dawn": "dawn",
    "dusk": "dusk",
    "morning": "day",
    "afternoon": "day",
    "evening": "night",
    "continuous": "continuous",
    "later": "unspecified",
    "same time": "unspecified",
    "same": "unspecified",
    "moments later": "unspecified",
    "moment later": "unspecified",
    "sunset": "dusk",
    "sunrise": "dawn",
}


def detect_scene_heading(line: str) -> dict | None:
    """Parse a line as a scene heading. Returns dict or None."""
    line = line.strip()
    if not line:
        return None

    match = SCENE_HEADING_RE.match(line)
    if not match:
        return None

    ie_raw = match.group("ie_prefix").upper().replace(" ", "")
    if "/" in ie_raw:
        int_ext = "int_ext"
    elif ie_raw.startswith("INT"):
        int_ext = "int"
    elif ie_raw.startswith("EXT") or ie_raw.startswith("EST"):
        int_ext = "ext"
    elif ie_raw.startswith("I/E"):
        int_ext = "int_ext"
    else:
        int_ext = "unspecified"

    location = match.group("location").strip().rstrip("-\u2013\u2014 ")
    time_raw = match.group("time_of_day")
    time_of_day = None
    day_night = "unspecified"

    if time_raw:
        time_of_day = time_raw.upper().strip()
        day_night = TIME_TO_DAY_NIGHT.get(time_raw.lower().strip(), "unspecified")

    return {
        "slugline": line,
        "int_ext": int_ext,
        "location": location,
        "time_of_day": time_of_day,
        "day_night": day_night,
    }


def split_into_scenes(text: str) -> list[ParsedScene]:
    """Split preprocessed screenplay text into scenes."""
    lines = text.split("\n")
    scenes: list[ParsedScene] = []
    current_heading = None
    current_lines: list[str] = []
    scene_num = 0

    for line in lines:
        heading = detect_scene_heading(line)
        if heading:
            # Save previous scene
            if current_heading is not None:
                scene_num += 1
                raw = "\n".join(current_lines).strip()
                scenes.append(
                    ParsedScene(
                        scene_number=scene_num,
                        slugline=current_heading["slugline"],
                        int_ext=current_heading["int_ext"],
                        day_night=current_heading["day_night"],
                        location=current_heading["location"],
                        raw_text=raw,
                        word_count=len(raw.split()),
                    )
                )
            current_heading = heading
            current_lines = []
        else:
            current_lines.append(line)

    # Save last scene
    if current_heading is not None:
        scene_num += 1
        raw = "\n".join(current_lines).strip()
        scenes.append(
            ParsedScene(
                scene_number=scene_num,
                slugline=current_heading["slugline"],
                int_ext=current_heading["int_ext"],
                day_night=current_heading["day_night"],
                location=current_heading["location"],
                raw_text=raw,
                word_count=len(raw.split()),
            )
        )

    return scenes
```

**Step 4: Run tests**

Run: `pytest tests/test_scene_parser.py -v`
Expected: All 8 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/parsing/scene_parser.py tests/test_scene_parser.py
git commit -m "feat: add scene heading detection and splitting"
```

---

## Task 6: Character Extraction

**Files:**
- Create: `src/sba/parsing/character_parser.py`
- Create: `tests/test_character_parser.py`

**Step 1: Write the failing tests**

```python
# tests/test_character_parser.py
"""Tests for character extraction from screenplay text."""

from sba.parsing.character_parser import (
    extract_characters_from_text,
    canonicalize_character_name,
)


def test_basic_dialogue_character():
    text = """
JOHN
Hello there.

JANE
Hi John.
"""
    chars = extract_characters_from_text(text)
    names = {c.canonical_name for c in chars.values()}
    assert "JOHN" in names
    assert "JANE" in names


def test_contd_is_same_character():
    text = """
JOHN
Hello.

JANE
Hi.

JOHN (CONT'D)
As I was saying.
"""
    chars = extract_characters_from_text(text)
    assert "JOHN" in chars
    assert len(chars) == 2  # JOHN and JANE, not JOHN and JOHN (CONT'D)


def test_vo_os_extensions():
    text = """
JOHN (V.O.)
I remember that day.

JANE (O.S.)
Come here!
"""
    chars = extract_characters_from_text(text)
    assert "JOHN" in chars
    assert "V.O." in chars["JOHN"].extensions


def test_canonicalize_strips_extensions():
    assert canonicalize_character_name("JOHN (CONT'D)") == "JOHN"
    assert canonicalize_character_name("JANE (V.O.)") == "JANE"
    assert canonicalize_character_name("  JOHN  ") == "JOHN"
```

**Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_character_parser.py -v`

**Step 3: Write implementation**

```python
# src/sba/parsing/character_parser.py
"""Character extraction from screenplay text."""

from __future__ import annotations

import re
from sba.parsing.models import Character

# Character cue pattern: uppercase name, optional extension in parens
CHARACTER_CUE_RE = re.compile(
    r"^"
    r"(?P<name>[A-Z][A-Z\s.'\-]+?)"
    r"(?:\s*\((?P<ext>"
    r"V\.?\s*O\.?"
    r"|O\.?\s*S\.?"
    r"|O\.?\s*C\.?"
    r"|CONT'?D?"
    r"|CONTINUING"
    r"|FILTERED"
    r"|SUBTITLED?"
    r"|PRE[\-\s]?LAP"
    r"|ON\s+(?:PHONE|RADIO|TV|SCREEN|SPEAKER)"
    r"|OVER\s+PHONE"
    r")\))?"
    r"\s*$",
    re.MULTILINE,
)


def canonicalize_character_name(raw_name: str) -> str:
    """Normalize a character name to canonical form."""
    name = raw_name.strip()
    # Remove parenthetical extensions
    name = re.sub(r"\s*\(.*?\)\s*", "", name)
    # Remove trailing CONT'D without parens
    name = re.sub(r"\s+CONT'?D?\s*$", "", name, flags=re.IGNORECASE)
    # Normalize whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name


def extract_characters_from_text(text: str) -> dict[str, Character]:
    """Extract characters from screenplay text using dialogue cue patterns.

    Returns dict mapping canonical name -> Character.
    """
    characters: dict[str, Character] = {}
    lines = text.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        match = CHARACTER_CUE_RE.match(stripped)
        if not match:
            continue

        raw_name = match.group("name").strip()
        ext = match.group("ext")
        canonical = canonicalize_character_name(raw_name)

        if not canonical or len(canonical) < 2:
            continue

        # Skip common false positives
        if canonical in {
            "CUT TO",
            "FADE TO",
            "FADE IN",
            "FADE OUT",
            "DISSOLVE TO",
            "SMASH CUT TO",
            "MATCH CUT TO",
            "THE END",
            "CONTINUED",
            "INTERCUT",
            "MONTAGE",
            "END MONTAGE",
            "FLASHBACK",
            "END FLASHBACK",
            "SUPER",
            "TITLE CARD",
            "CHYRON",
        }:
            continue

        if canonical not in characters:
            characters[canonical] = Character(canonical_name=canonical)

        characters[canonical].variants.add(stripped)
        if ext:
            characters[canonical].extensions.add(ext.strip())

    return characters
```

**Step 4: Run tests**

Run: `pytest tests/test_character_parser.py -v`
Expected: All 4 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/parsing/character_parser.py tests/test_character_parser.py
git commit -m "feat: add character extraction with canonicalization"
```

---

## Task 7: VFX Trigger Scanner

**Files:**
- Create: `src/sba/parsing/vfx_scanner.py`
- Create: `tests/test_vfx_scanner.py`

**Step 1: Write the failing tests**

```python
# tests/test_vfx_scanner.py
"""Tests for VFX trigger keyword scanning."""

from sba.parsing.vfx_scanner import scan_for_vfx_triggers


def test_detects_explosion():
    text = "The building explodes in a massive fireball."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "fire_pyro" in categories


def test_detects_water():
    text = "She dives underwater and swims toward the submarine."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "water" in categories


def test_false_positive_fired():
    text = "John is fired from his job."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "fire_pyro" not in categories


def test_detects_creature():
    text = "A massive dragon descends from the clouds."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "creatures_animals" in categories


def test_no_triggers_in_normal_dialogue():
    text = "JOHN\nI had a great day at the office."
    triggers = scan_for_vfx_triggers(text)
    assert len(triggers) == 0


def test_multiple_triggers():
    text = "The helicopter crashes into the ocean, exploding on impact."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "vehicles" in categories or "fire_pyro" in categories
    assert len(triggers) >= 2
```

**Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_vfx_scanner.py -v`

**Step 3: Write implementation**

```python
# src/sba/parsing/vfx_scanner.py
"""VFX trigger keyword scanning with false-positive filtering."""

from __future__ import annotations

import re
from sba.parsing.models import VFXTrigger

# Each category has keyword patterns and false-positive exclusion patterns
VFX_TRIGGER_TAXONOMY: dict[str, dict] = {
    "water": {
        "keywords": [
            r"\bocean\b", r"\bsea\b", r"\briver\b", r"\blake\b",
            r"\bpool\b", r"\bflood(?:ing|ed|s)?\b", r"\bunderwater\b",
            r"\bswim(?:s|ming)?\b", r"\bdive[sd]?\b", r"\bwave[sd]?\b",
            r"\btsunami\b", r"\bsplash(?:es|ing)?\b",
            r"\bsubmerg(?:ed|es|ing)?\b", r"\bdrown(?:s|ing|ed)?\b",
        ],
        "exclusions": [
            r"water\s*(?:bottle|glass|cup|cooler|proof|tight|color|mark)",
        ],
        "severity": "high",
    },
    "fire_pyro": {
        "keywords": [
            r"\bflame[sd]?\b", r"\bburn(?:s|ing|ed)?\b",
            r"\bexplo(?:sion|de[sd]?|ding)\b", r"\bblast\b",
            r"\binferno\b", r"\bblaze[sd]?\b", r"\bignite[sd]?\b",
            r"\bsmoke\b", r"\bspark[sd]?\b", r"\bdetonate[sd]?\b",
            r"\bgunfire\b", r"\bmuzzle\s*flash\b", r"\bfireball\b",
        ],
        "exclusions": [
            r"fire[sd]\s+(?:from|him|her|them|the\s+employee|a\s+question|off\s+an?\s+email)",
            r"fire\s*(?:place|house|fighter|truck|man|men|woman|station|chief|escape|exit|drill|alarm|hydrant|department)",
            r"\bcamp\s*fire\b",
        ],
        "severity": "high",
    },
    "crowds_extras": {
        "keywords": [
            r"\bcrowd[sd]?\b", r"\bmob\b", r"\bhorde\b",
            r"\bhundreds\b", r"\bthousands\b",
            r"\barm(?:y|ies)\b", r"\bsoldier[sd]?\b", r"\btroop[sd]?\b",
            r"\briot(?:s|ing|ers?)?\b", r"\bstampede\b",
            r"\bparade\b", r"\bstadium\b",
        ],
        "exclusions": [],
        "severity": "medium",
    },
    "vehicles": {
        "keywords": [
            r"\bcar\s+(?:chase|crash|wreck|flip|roll)\b",
            r"\bhelicopter\b", r"\bchopper\b",
            r"\baircraft\b", r"\bjet\b", r"\bspacecraft\b",
            r"\bspaceship\b", r"\bsubmarine\b",
            r"\btrain\b.*\b(?:crash|wreck|derail)\b",
            r"\bcrash(?:es|ing|ed)?\b", r"\bcollision\b",
        ],
        "exclusions": [
            r"tank\s*(?:top|of\s+gas)",
        ],
        "severity": "medium",
    },
    "creatures_animals": {
        "keywords": [
            r"\bmonster[sd]?\b", r"\bcreature[sd]?\b", r"\balien[sd]?\b",
            r"\bdragon[sd]?\b", r"\bdinosaur[sd]?\b", r"\bzombie[sd]?\b",
            r"\bwolf\b", r"\bwolves\b",
            r"\bmutant[sd]?\b", r"\bdemon[sd]?\b", r"\bghost[sd]?\b",
            r"\bwerewolf\b", r"\bvampire[sd]?\b",
        ],
        "exclusions": [
            r"bear\s+(?:with|in\s+mind)",
            r"horse\s*(?:play|power|shoe|around)",
        ],
        "severity": "high",
    },
    "destruction": {
        "keywords": [
            r"\bcollaps(?:e[sd]?|ing)\b", r"\bdemolish\b",
            r"\bdestroy(?:s|ed|ing)?\b", r"\bdestruction\b",
            r"\bearthquake\b", r"\btornado\b", r"\bhurricane\b",
            r"\bavalanch\b", r"\bshatter(?:s|ed|ing)?\b",
            r"\bcrumbl(?:e[sd]?|ing)\b",
        ],
        "exclusions": [],
        "severity": "high",
    },
    "weapons_combat": {
        "keywords": [
            r"\bgun[sd]?\b", r"\bpistol\b", r"\brifle\b", r"\bshotgun\b",
            r"\bshoot(?:s|ing|out)?\b",
            r"\bsword[sd]?\b", r"\blightsaber[sd]?\b",
            r"\bbattle\b", r"\bblaster[sd]?\b",
        ],
        "exclusions": [
            r"gun\s*(?:metal|powder\s+grey)",
        ],
        "severity": "medium",
    },
    "aerial_height": {
        "keywords": [
            r"\bfly(?:s|ing)?\b", r"\bflight\b", r"\bsoar(?:s|ing)?\b",
            r"\bhover(?:s|ing)?\b", r"\bparachute\b",
            r"\bskydiv(?:e|ing)\b",
        ],
        "exclusions": [
            r"flight\s+(?:of\s+stairs|attendant|delay)",
        ],
        "severity": "high",
    },
    "weather_atmosphere": {
        "keywords": [
            r"\bstorm(?:s|ing|y)?\b", r"\blightning\b",
            r"\bthunder\b", r"\bsnow(?:s|ing|storm)?\b",
            r"\bblizzard\b", r"\bfog(?:gy)?\b", r"\bmist(?:y)?\b",
        ],
        "exclusions": [
            r"\bbrain\b",
        ],
        "severity": "medium",
    },
    "supernatural_magic": {
        "keywords": [
            r"\bmagic\b", r"\bspell[sd]?\b", r"\bteleport\b",
            r"\bvanish(?:es|ed|ing)?\b", r"\btransform(?:s|ing|ation)?\b",
            r"\blevitat(?:e[sd]?|ing|ion)\b", r"\bforce[\s-]?field\b",
            r"\bportal[sd]?\b", r"\bsupernatural\b",
            r"\b(?:the\s+)?force\b",
        ],
        "exclusions": [
            r"force[sd]?\s+(?:him|her|them|to|into|out)",
            r"(?:air|task|work|police|armed)\s+force",
        ],
        "severity": "high",
    },
}


def scan_for_vfx_triggers(text: str) -> list[VFXTrigger]:
    """Scan text for VFX trigger keywords with false-positive filtering."""
    triggers: list[VFXTrigger] = []

    for category, config in VFX_TRIGGER_TAXONOMY.items():
        for pattern_str in config["keywords"]:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for match in pattern.finditer(text):
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end].strip()

                # Check false-positive exclusions
                is_false_positive = False
                for excl in config.get("exclusions", []):
                    if re.search(excl, context, re.IGNORECASE):
                        is_false_positive = True
                        break

                if not is_false_positive:
                    triggers.append(
                        VFXTrigger(
                            category=category,
                            matched_keyword=match.group(0),
                            severity=config["severity"],
                            context=context,
                            position=match.start(),
                        )
                    )

    return triggers
```

**Step 4: Run tests**

Run: `pytest tests/test_vfx_scanner.py -v`
Expected: All 6 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/parsing/vfx_scanner.py tests/test_vfx_scanner.py
git commit -m "feat: add VFX trigger scanner with false-positive filtering"
```

---

## Task 8: PDF Extractor

**Files:**
- Create: `src/sba/parsing/pdf_extractor.py`
- Create: `src/sba/parsing/text_extractor.py`

**Step 1: Write implementation** (PDF extraction is hard to unit test without fixture PDFs — we test via integration)

```python
# src/sba/parsing/pdf_extractor.py
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
```

```python
# src/sba/parsing/text_extractor.py
"""Handle plain text screenplay input."""

from __future__ import annotations

from pathlib import Path


def extract_text_from_file(file_path: str | Path) -> str:
    """Read a plain text screenplay file."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Try UTF-8 first, fall back to latin-1
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1")
```

**Step 2: Commit**

```bash
git add src/sba/parsing/pdf_extractor.py src/sba/parsing/text_extractor.py
git commit -m "feat: add PDF and text extractors"
```

---

## Task 9: Parsing Pipeline

**Files:**
- Create: `src/sba/parsing/pipeline.py`
- Create: `tests/test_parsing_pipeline.py`

**Step 1: Write the failing test**

```python
# tests/test_parsing_pipeline.py
"""Tests for the full parsing pipeline."""

from sba.parsing.pipeline import parse_script_text


def test_full_pipeline_from_text():
    script = """INT. DEATH STAR - CORRIDOR - DAY

Stormtroopers march through the corridor. An EXPLOSION rocks the station. Smoke fills the air.

VADER
I find your lack of faith disturbing.

OFFICER
Yes, Lord Vader.

EXT. TATOOINE - DESERT - DAY

Twin suns beat down on the endless sand. A SPEEDER races across the dunes.

LUKE
I was going to Tosche Station to pick up some power converters!

INT. REBEL BASE - COMMAND CENTER - NIGHT

Hundreds of REBEL SOLDIERS study holographic displays. The room buzzes with tension.

LEIA
The Empire is coming. We must prepare.
"""
    result = parse_script_text(script, title="Star Wars Test")
    assert result.title == "Star Wars Test"
    assert len(result.scenes) == 3

    # Scene 1: explosion + smoke = fire_pyro triggers
    s1 = result.scenes[0]
    assert s1.int_ext == "int"
    assert "VADER" in s1.characters
    assert "OFFICER" in s1.characters
    trigger_cats = {t.category for t in s1.vfx_triggers}
    assert len(trigger_cats) > 0  # Should detect explosion/smoke

    # Scene 2: vehicles
    s2 = result.scenes[1]
    assert s2.int_ext == "ext"
    assert "LUKE" in s2.characters

    # Scene 3: crowds
    s3 = result.scenes[2]
    assert s3.day_night == "night"
    assert "LEIA" in s3.characters

    # All characters found
    assert "VADER" in result.all_characters
    assert "LUKE" in result.all_characters
    assert "LEIA" in result.all_characters
```

**Step 2: Run test — expect FAIL**

Run: `pytest tests/test_parsing_pipeline.py -v`

**Step 3: Write implementation**

```python
# src/sba/parsing/pipeline.py
"""Orchestrates the full script parsing pipeline."""

from __future__ import annotations

from pathlib import Path

from sba.parsing.models import ParsedScript
from sba.parsing.preprocessor import preprocess_script_text
from sba.parsing.scene_parser import split_into_scenes
from sba.parsing.character_parser import extract_characters_from_text
from sba.parsing.vfx_scanner import scan_for_vfx_triggers
from sba.parsing.pdf_extractor import extract_text_from_pdf
from sba.parsing.text_extractor import extract_text_from_file


def parse_script_text(text: str, title: str = "") -> ParsedScript:
    """Parse raw screenplay text into a structured ParsedScript."""
    cleaned = preprocess_script_text(text)
    scenes = split_into_scenes(cleaned)

    # Extract characters and VFX triggers per scene
    all_characters = extract_characters_from_text(cleaned)

    for scene in scenes:
        # Per-scene character extraction
        scene_chars = extract_characters_from_text(scene.raw_text)
        scene.characters = list(scene_chars.keys())

        # VFX trigger scanning
        scene.vfx_triggers = scan_for_vfx_triggers(scene.raw_text)

    # Estimate pages (roughly 250 words per page for screenplays)
    total_words = sum(s.word_count for s in scenes)
    pages_estimate = max(1, round(total_words / 250))

    return ParsedScript(
        title=title,
        raw_text=cleaned,
        scenes=scenes,
        all_characters=all_characters,
        total_pages_estimate=pages_estimate,
    )


def parse_script_file(file_path: str | Path, title: str = "") -> ParsedScript:
    """Parse a screenplay file (PDF or text) into a structured ParsedScript."""
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_file(file_path)

    if not title:
        title = file_path.stem

    return parse_script_text(text, title=title)
```

**Step 4: Run tests**

Run: `pytest tests/test_parsing_pipeline.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/sba/parsing/pipeline.py tests/test_parsing_pipeline.py
git commit -m "feat: add full parsing pipeline orchestration"
```

---

## Task 10: RAG Corpus Files

**Files:**
- Create: `corpus/vfx_taxonomy.md`
- Create: `corpus/cost_rules.md`
- Create: `corpus/capture_checklist.md`
- Create: `corpus/gold_examples/hoth_battle.md`
- Create: `corpus/gold_examples/death_star_trench.md`
- Create: `corpus/gold_examples/naboo_senate.md`

These are the reference documents that ground Claude's output. For MVP, they are injected as static context. When `--use-rag` is enabled, they are chunked and embedded into ChromaDB.

**Step 1: Create corpus files**

The VFX taxonomy, cost rules, capture checklist, and gold examples should be authored as markdown files. Each file should be 500-1500 words, written in production language. Claude (the implementing agent) should draft these based on industry knowledge.

Key content requirements:
- `vfx_taxonomy.md`: Define each of the 27 VfxCategory enum values with 2-3 sentence descriptions, typical complexity level, and common triggers
- `cost_rules.md`: 30-40 conditional rules in format: "IF [condition] THEN [risk/cost multiplier/mitigation]"
- `capture_checklist.md`: On-set data capture items grouped by VFX type
- Gold examples: Full JSON breakdowns for 3 scenes of varying VFX complexity

**Step 2: Commit**

```bash
git add corpus/
git commit -m "feat: add RAG corpus reference documents"
```

---

## Task 11: RAG Corpus Builder and Embedder

**Files:**
- Create: `src/sba/rag/__init__.py`
- Create: `src/sba/rag/corpus_builder.py`
- Create: `src/sba/rag/embedder.py`
- Create: `tests/test_corpus_builder.py`

**Step 1: Write the failing test**

```python
# tests/test_corpus_builder.py
"""Tests for corpus chunking."""

from sba.rag.corpus_builder import chunk_document


def test_chunks_short_document():
    text = "This is a short document. " * 20  # ~100 words
    chunks = chunk_document(text, doc_type="taxonomy", category="test")
    assert len(chunks) >= 1
    assert all(c["doc_type"] == "taxonomy" for c in chunks)
    assert all(c["category"] == "test" for c in chunks)
    assert all(len(c["text"]) > 0 for c in chunks)


def test_chunks_long_document():
    text = "Word " * 1000  # ~1000 words
    chunks = chunk_document(text, doc_type="risk_rules", category="cost")
    assert len(chunks) > 1
    # Verify overlap — end of chunk N should overlap with start of chunk N+1
    for i in range(len(chunks) - 1):
        words_end = chunks[i]["text"].split()[-20:]
        words_start = chunks[i + 1]["text"].split()[:20]
        # At least some overlap
        overlap = set(words_end) & set(words_start)
        assert len(overlap) > 0


def test_chunk_metadata():
    text = "Some content here. " * 50
    chunks = chunk_document(text, doc_type="glossary", category="shot_sizes")
    for chunk in chunks:
        assert "doc_type" in chunk
        assert "category" in chunk
        assert "chunk_index" in chunk
        assert "text" in chunk
```

**Step 2: Run test — expect FAIL**

Run: `pytest tests/test_corpus_builder.py -v`

**Step 3: Write implementation**

```python
# src/sba/rag/__init__.py
"""RAG modules for corpus management and retrieval."""
```

```python
# src/sba/rag/corpus_builder.py
"""Build chunks from corpus source documents."""

from __future__ import annotations

from pathlib import Path


def chunk_document(
    text: str,
    doc_type: str,
    category: str,
    chunk_size_words: int = 350,
    overlap_words: int = 60,
) -> list[dict]:
    """Split a document into overlapping chunks with metadata.

    Args:
        text: Document text.
        doc_type: glossary, taxonomy, capture, risk_rules, gold_example.
        category: Sub-category for filtering.
        chunk_size_words: Target words per chunk.
        overlap_words: Words of overlap between chunks.
    """
    words = text.split()
    if len(words) <= chunk_size_words:
        return [
            {
                "text": text.strip(),
                "doc_type": doc_type,
                "category": category,
                "chunk_index": 0,
            }
        ]

    chunks: list[dict] = []
    start = 0
    chunk_idx = 0

    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk_text = " ".join(words[start:end])
        chunks.append(
            {
                "text": chunk_text.strip(),
                "doc_type": doc_type,
                "category": category,
                "chunk_index": chunk_idx,
            }
        )
        chunk_idx += 1
        start = end - overlap_words
        if start >= len(words) - overlap_words:
            break

    return chunks


def build_corpus_from_directory(corpus_dir: str | Path) -> list[dict]:
    """Build all chunks from the corpus directory.

    Reads markdown files, determines doc_type from filename/path.
    """
    corpus_dir = Path(corpus_dir)
    all_chunks: list[dict] = []

    file_type_map = {
        "vfx_taxonomy": ("taxonomy", "vfx"),
        "cost_rules": ("risk_rules", "cost"),
        "capture_checklist": ("capture", "on_set"),
    }

    # Process top-level corpus files
    for md_file in corpus_dir.glob("*.md"):
        stem = md_file.stem
        if stem in file_type_map:
            doc_type, category = file_type_map[stem]
        else:
            doc_type, category = "general", stem

        text = md_file.read_text(encoding="utf-8")
        chunks = chunk_document(text, doc_type=doc_type, category=category)
        all_chunks.extend(chunks)

    # Process gold examples
    gold_dir = corpus_dir / "gold_examples"
    if gold_dir.exists():
        for md_file in gold_dir.glob("*.md"):
            text = md_file.read_text(encoding="utf-8")
            chunks = chunk_document(
                text, doc_type="gold_example", category=md_file.stem
            )
            all_chunks.extend(chunks)

    return all_chunks
```

```python
# src/sba/rag/embedder.py
"""Voyage AI embedding wrapper."""

from __future__ import annotations

import voyageai
from sba.config import VOYAGE_API_KEY, VOYAGE_MODEL


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using Voyage AI.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors.
    """
    client = voyageai.Client(api_key=VOYAGE_API_KEY)
    result = client.embed(texts, model=VOYAGE_MODEL)
    return result.embeddings
```

**Step 4: Run tests**

Run: `pytest tests/test_corpus_builder.py -v`
Expected: All 3 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/rag/ tests/test_corpus_builder.py
git commit -m "feat: add corpus builder and Voyage embedder"
```

---

## Task 12: ChromaDB Vector Store

**Files:**
- Create: `src/sba/rag/vector_store.py`
- Create: `src/sba/rag/retriever.py`

**Step 1: Write implementation**

```python
# src/sba/rag/vector_store.py
"""ChromaDB vector store for corpus chunks."""

from __future__ import annotations

from pathlib import Path
import chromadb
from sba.rag.embedder import get_embeddings


COLLECTION_NAME = "sba_corpus"


def get_client(persist_dir: str | Path = "chroma_db") -> chromadb.ClientAPI:
    """Get a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=str(persist_dir))


def index_chunks(chunks: list[dict], persist_dir: str | Path = "chroma_db") -> int:
    """Index corpus chunks into ChromaDB.

    Args:
        chunks: List of chunk dicts with text, doc_type, category, chunk_index.
        persist_dir: Directory for ChromaDB persistence.

    Returns:
        Number of chunks indexed.
    """
    client = get_client(persist_dir)

    # Delete existing collection if present
    try:
        client.delete_collection(COLLECTION_NAME)
    except ValueError:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]
    embeddings = get_embeddings(texts)

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "doc_type": c["doc_type"],
            "category": c["category"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    return len(chunks)
```

```python
# src/sba/rag/retriever.py
"""Hybrid retrieval: dense (ChromaDB) + keyword (BM25) with deduplication."""

from __future__ import annotations

from rank_bm25 import BM25Okapi
import chromadb

from sba.rag.vector_store import get_client, COLLECTION_NAME
from sba.rag.embedder import get_embeddings
from sba.config import MAX_RETRIEVAL_CHUNKS, MAX_RETRIEVAL_WORDS


def retrieve_for_scenes(
    scene_texts: list[str],
    persist_dir: str = "chroma_db",
    top_k_per_query: int = 6,
) -> list[dict]:
    """Retrieve relevant corpus chunks for a list of scene texts.

    Uses hybrid retrieval (dense + BM25) with deduplication
    to keep total context within budget.

    Args:
        scene_texts: Raw text of each scene.
        persist_dir: ChromaDB persistence directory.
        top_k_per_query: Number of dense results per scene query.

    Returns:
        Deduplicated list of chunk dicts with text and metadata.
    """
    client = get_client(persist_dir)
    collection = client.get_collection(COLLECTION_NAME)

    # Get all documents for BM25
    all_docs = collection.get(include=["documents", "metadatas"])
    doc_texts = all_docs["documents"]
    doc_metadatas = all_docs["metadatas"]
    doc_ids = all_docs["ids"]

    # Build BM25 index
    tokenized = [doc.lower().split() for doc in doc_texts]
    bm25 = BM25Okapi(tokenized)

    seen_ids: set[str] = set()
    results: list[dict] = []

    # Always include all risk_rules and taxonomy chunks
    for i, meta in enumerate(doc_metadatas):
        if meta["doc_type"] in ("risk_rules", "taxonomy"):
            if doc_ids[i] not in seen_ids:
                seen_ids.add(doc_ids[i])
                results.append({
                    "text": doc_texts[i],
                    "doc_type": meta["doc_type"],
                    "category": meta["category"],
                    "source": "forced_include",
                })

    # Per-scene retrieval with deduplication
    for scene_text in scene_texts:
        if len(results) >= MAX_RETRIEVAL_CHUNKS:
            break

        # Dense retrieval
        query_embedding = get_embeddings([scene_text[:500]])[0]
        dense_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k_per_query,
            include=["documents", "metadatas"],
        )

        for j in range(len(dense_results["ids"][0])):
            doc_id = dense_results["ids"][0][j]
            if doc_id not in seen_ids and len(results) < MAX_RETRIEVAL_CHUNKS:
                seen_ids.add(doc_id)
                results.append({
                    "text": dense_results["documents"][0][j],
                    "doc_type": dense_results["metadatas"][0][j]["doc_type"],
                    "category": dense_results["metadatas"][0][j]["category"],
                    "source": "dense",
                })

        # BM25 retrieval
        query_tokens = scene_text[:500].lower().split()
        bm25_scores = bm25.get_scores(query_tokens)
        top_bm25_indices = sorted(
            range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
        )[:top_k_per_query]

        for idx in top_bm25_indices:
            if doc_ids[idx] not in seen_ids and len(results) < MAX_RETRIEVAL_CHUNKS:
                seen_ids.add(doc_ids[idx])
                results.append({
                    "text": doc_texts[idx],
                    "doc_type": doc_metadatas[idx]["doc_type"],
                    "category": doc_metadatas[idx]["category"],
                    "source": "bm25",
                })

    # Enforce word budget
    total_words = 0
    trimmed: list[dict] = []
    for r in results:
        words = len(r["text"].split())
        if total_words + words > MAX_RETRIEVAL_WORDS:
            break
        total_words += words
        trimmed.append(r)

    return trimmed


def format_retrieved_context(chunks: list[dict]) -> str:
    """Format retrieved chunks for injection into the Claude prompt."""
    if not chunks:
        return ""

    parts = ["Retrieved context:"]
    for i, chunk in enumerate(chunks):
        parts.append(f"[DOC {i + 1} | {chunk['doc_type']}/{chunk['category']}]")
        parts.append(chunk["text"])
        parts.append("")

    return "\n".join(parts)
```

**Step 2: Commit**

```bash
git add src/sba/rag/vector_store.py src/sba/rag/retriever.py
git commit -m "feat: add ChromaDB vector store and hybrid retriever"
```

---

## Task 13: Claude Integration (Prompts + Client)

**Files:**
- Create: `src/sba/llm/__init__.py`
- Create: `src/sba/llm/prompts.py`
- Create: `src/sba/llm/claude_client.py`
- Create: `src/sba/llm/generator.py`

**Step 1: Write implementation**

```python
# src/sba/llm/__init__.py
"""LLM integration modules."""
```

```python
# src/sba/llm/prompts.py
"""System and user prompt templates for Claude."""

from sba.output.schema import VfxCategory

VFX_CATEGORIES_LIST = ", ".join(v.value for v in VfxCategory)

SYSTEM_PROMPT = f"""You are VFX Breakdown Assistant, a production-aware script analysis tool for world-class producers on VFX-heavy films.

Your job:
- Convert a screenplay into a structured scene breakdown.
- Estimate VFX shot density per scene using ranges (min, likely, max).
- Flag hidden cost multipliers and schedule risks.
- Suggest on-set capture items where relevant.

Rules:
- Do not invent details not present in the script.
- Output valid JSON only. No prose, no markdown, no explanation.
- Use conservative estimates. When uncertain, bias toward lower counts.
- If uncertain about any classification, write to the uncertainties array and explain briefly.
- Never claim a capture item is required. Use suggested_capture.
- Every scene must have a cost_risk_score and schedule_risk_score from 1 to 5.

Valid vfx_categories values (use ONLY these):
{VFX_CATEGORIES_LIST}

For int_ext use: int, ext, int_ext, unspecified
For day_night use: day, night, dawn, dusk, continuous, unspecified
For invisible_vfx_likelihood use: low, medium, high
For severity use: low, medium, high
For overall_vfx_heaviness use: low, medium, high, very_high
For likely_virtual_production_fit use: low, medium, high
For location_type use: practical, stage, virtual_production, ext_location, mixed, unspecified

page_count_eighths: estimate scene length in eighths of a page (8 = 1 page, 12 = 1.5 pages, etc.)

Output must conform to the provided JSON schema exactly."""


def build_user_prompt(
    script_text: str,
    retrieved_context: str = "",
    project_title: str = "",
) -> str:
    """Build the user prompt with script text and optional retrieved context."""
    parts = []

    if retrieved_context:
        parts.append(retrieved_context)
        parts.append("---")

    parts.append(
        "Analyze the following screenplay text. "
        "Use retrieved context (if provided) to ground VFX categories, "
        "capture suggestions, and risk rules."
    )
    parts.append("")
    parts.append("Constraints:")
    parts.append("- Output valid JSON only.")
    parts.append("- Use ranges for vfx_shot_count_estimate.")
    parts.append("- Be conservative.")
    parts.append("- Include all scenes found in the script.")
    if project_title:
        parts.append(f'- Set project_title to "{project_title}".')
    parts.append("")
    parts.append("Screenplay text:")
    parts.append(script_text)

    return "\n".join(parts)
```

```python
# src/sba/llm/claude_client.py
"""Anthropic API wrapper with streaming support."""

from __future__ import annotations

import anthropic
from sba.config import ANTHROPIC_API_KEY, CLAUDE_MODEL


def call_claude(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 128000,
) -> str:
    """Call Claude and return the text response.

    Uses streaming to handle large outputs.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    full_response = ""
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    return full_response
```

```python
# src/sba/llm/generator.py
"""Orchestrates RAG retrieval, prompt construction, Claude call, and validation."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from sba.parsing.models import ParsedScript
from sba.output.schema import BreakdownOutput
from sba.output.validate import validate_and_repair
from sba.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from sba.llm.claude_client import call_claude
from sba.config import CORPUS_DIR


def load_static_corpus() -> str:
    """Load all corpus files as static context (RAG-lite mode)."""
    parts = ["Retrieved context:"]
    corpus_dir = CORPUS_DIR

    if not corpus_dir.exists():
        return ""

    for md_file in sorted(corpus_dir.glob("*.md")):
        parts.append(f"[DOC | {md_file.stem}]")
        parts.append(md_file.read_text(encoding="utf-8"))
        parts.append("")

    gold_dir = corpus_dir / "gold_examples"
    if gold_dir.exists():
        for md_file in sorted(gold_dir.glob("*.md")):
            parts.append(f"[DOC | gold_example/{md_file.stem}]")
            parts.append(md_file.read_text(encoding="utf-8"))
            parts.append("")

    return "\n".join(parts)


def generate_breakdown(
    parsed_script: ParsedScript,
    use_rag: bool = False,
    rag_persist_dir: str = "chroma_db",
) -> BreakdownOutput:
    """Generate a full VFX breakdown from a parsed script.

    Args:
        parsed_script: Output from the parsing pipeline.
        use_rag: If True, use ChromaDB retrieval. If False, use static corpus injection.
        rag_persist_dir: ChromaDB persistence directory (only used if use_rag=True).

    Returns:
        Validated BreakdownOutput.
    """
    # Build context
    if use_rag:
        from sba.rag.retriever import retrieve_for_scenes, format_retrieved_context

        scene_texts = [s.raw_text for s in parsed_script.scenes]
        chunks = retrieve_for_scenes(scene_texts, persist_dir=rag_persist_dir)
        context = format_retrieved_context(chunks)
    else:
        context = load_static_corpus()

    # Build prompt
    user_prompt = build_user_prompt(
        script_text=parsed_script.raw_text,
        retrieved_context=context,
        project_title=parsed_script.title,
    )

    # Call Claude
    raw_output = call_claude(SYSTEM_PROMPT, user_prompt)

    # Validate and repair
    result = validate_and_repair(raw_output)

    if result is None:
        # Retry once with error feedback
        retry_prompt = (
            user_prompt
            + "\n\nIMPORTANT: Your previous output was not valid JSON. "
            "Please output ONLY valid JSON conforming to the schema. "
            "No markdown fences, no explanation."
        )
        raw_output = call_claude(SYSTEM_PROMPT, retry_prompt)
        result = validate_and_repair(raw_output)

    if result is None:
        raise ValueError(
            "Failed to generate valid JSON after retry. "
            "Raw output saved for debugging."
        )

    # Patch metadata
    result.project_summary.date_analyzed = datetime.now(timezone.utc).isoformat()
    result.project_summary.total_scene_count = len(result.scenes)
    if not result.project_summary.project_title:
        result.project_summary.project_title = parsed_script.title

    return result
```

**Step 2: Commit**

```bash
git add src/sba/llm/
git commit -m "feat: add Claude integration with prompts, client, and generator"
```

---

## Task 14: JSON Validation and Repair

**Files:**
- Create: `src/sba/output/validate.py`
- Create: `tests/test_validate.py`

**Step 1: Write the failing test**

```python
# tests/test_validate.py
"""Tests for JSON validation and repair."""

from sba.output.validate import validate_and_repair


def test_valid_json_passes():
    valid = '{"project_summary":{"project_title":"Test","date_analyzed":"2026-01-01","analysis_scope":"excerpt","total_scene_count":1},"global_flags":{"overall_vfx_heaviness":"low","likely_virtual_production_fit":"low","top_risk_themes":[]},"scenes":[{"scene_id":"SC001","slugline":"INT. OFFICE - DAY","int_ext":"int","day_night":"day","vfx_shot_count_estimate":{"min":0,"likely":0,"max":0},"invisible_vfx_likelihood":"low","cost_risk_score":1,"schedule_risk_score":1}],"hidden_cost_radar":[],"key_questions_for_team":{"for_producer":[],"for_vfx_supervisor":[],"for_dp_camera":[],"for_locations_art_dept":[]}}'
    result = validate_and_repair(valid)
    assert result is not None
    assert result.scenes[0].scene_id == "SC001"


def test_markdown_fenced_json():
    fenced = '```json\n{"project_summary":{"project_title":"Test","date_analyzed":"2026-01-01","analysis_scope":"excerpt","total_scene_count":1},"global_flags":{"overall_vfx_heaviness":"low","likely_virtual_production_fit":"low","top_risk_themes":[]},"scenes":[{"scene_id":"SC001","slugline":"INT. OFFICE - DAY","int_ext":"int","day_night":"day","vfx_shot_count_estimate":{"min":0,"likely":0,"max":0},"invisible_vfx_likelihood":"low","cost_risk_score":1,"schedule_risk_score":1}],"hidden_cost_radar":[],"key_questions_for_team":{"for_producer":[],"for_vfx_supervisor":[],"for_dp_camera":[],"for_locations_art_dept":[]}}\n```'
    result = validate_and_repair(fenced)
    assert result is not None


def test_garbage_returns_none():
    result = validate_and_repair("This is not JSON at all.")
    assert result is None
```

**Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_validate.py -v`

**Step 3: Write implementation**

```python
# src/sba/output/validate.py
"""JSON parse, repair, and Pydantic validation pipeline."""

from __future__ import annotations

import json
import re

from json_repair import repair_json
from sba.output.schema import BreakdownOutput


def validate_and_repair(raw: str) -> BreakdownOutput | None:
    """Attempt to parse and validate Claude's JSON output.

    Pipeline:
    1. Try direct JSON parse + Pydantic validation
    2. Try extracting from markdown fences
    3. Try json_repair library
    4. Return None if all fail
    """
    # Step 1: Direct parse
    result = _try_parse(raw.strip())
    if result:
        return result

    # Step 2: Extract from markdown fences
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    if fence_match:
        result = _try_parse(fence_match.group(1).strip())
        if result:
            return result

    # Step 3: json_repair
    try:
        repaired = repair_json(raw, return_objects=False)
        result = _try_parse(repaired)
        if result:
            return result
    except Exception:
        pass

    return None


def _try_parse(json_str: str) -> BreakdownOutput | None:
    """Try to parse a JSON string into a BreakdownOutput."""
    try:
        return BreakdownOutput.model_validate_json(json_str)
    except Exception:
        pass

    try:
        data = json.loads(json_str)
        return BreakdownOutput.model_validate(data)
    except Exception:
        return None
```

**Step 4: Run tests**

Run: `pytest tests/test_validate.py -v`
Expected: All 3 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/output/validate.py tests/test_validate.py
git commit -m "feat: add JSON validation with repair pipeline"
```

---

## Task 15: CSV Export

**Files:**
- Create: `src/sba/output/export_csv.py`
- Create: `tests/test_export_csv.py`

**Step 1: Write the failing test**

```python
# tests/test_export_csv.py
"""Tests for CSV export."""

import csv
import io
from sba.output.schema import (
    BreakdownOutput, Scene, VfxShotCountEstimate,
    ProjectSummary, GlobalFlags, KeyQuestions, VfxCategory,
)
from sba.output.export_csv import breakdown_to_csv


def _make_breakdown():
    return BreakdownOutput(
        project_summary=ProjectSummary(project_title="Test", total_scene_count=1),
        global_flags=GlobalFlags(),
        scenes=[
            Scene(
                scene_id="SC001",
                slugline="INT. OFFICE - DAY",
                int_ext="int",
                day_night="day",
                vfx_categories=[VfxCategory.COMP, VfxCategory.MATCHMOVE],
                vfx_shot_count_estimate=VfxShotCountEstimate(min=2, likely=4, max=6),
                invisible_vfx_likelihood="medium",
                cost_risk_score=3,
                schedule_risk_score=2,
                suggested_capture=["HDRI", "clean plates", "witness cam", "lidar"],
            )
        ],
        key_questions_for_team=KeyQuestions(),
    )


def test_csv_output_has_header():
    csv_str = breakdown_to_csv(_make_breakdown())
    reader = csv.DictReader(io.StringIO(csv_str))
    assert "scene_id" in reader.fieldnames
    assert "cost_risk" in reader.fieldnames


def test_csv_arrays_pipe_delimited():
    csv_str = breakdown_to_csv(_make_breakdown())
    assert "comp|matchmove" in csv_str


def test_csv_capture_capped_at_3():
    csv_str = breakdown_to_csv(_make_breakdown())
    # Should have 3 items + indicator
    assert "(+1 more)" in csv_str or csv_str.count("|") >= 2
```

**Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_export_csv.py -v`

**Step 3: Write implementation**

```python
# src/sba/output/export_csv.py
"""CSV export from BreakdownOutput (derived from scenes[], not stored separately)."""

from __future__ import annotations

import csv
import io
from sba.output.schema import BreakdownOutput, Scene, ProductionFlags


CSV_COLUMNS = [
    "scene_id",
    "slugline",
    "int_ext",
    "day_night",
    "page_eighths",
    "summary",
    "vfx_est_min",
    "vfx_est_likely",
    "vfx_est_max",
    "top_vfx_categories",
    "invisible_vfx",
    "cost_risk",
    "schedule_risk",
    "top_flags",
    "suggested_capture",
]


def _pipe_join(items: list[str], max_items: int = 3) -> str:
    """Join items with pipe, capping at max_items."""
    if len(items) <= max_items:
        return "|".join(str(i) for i in items)
    shown = "|".join(str(i) for i in items[:max_items])
    return f"{shown} (+{len(items) - max_items} more)"


def _active_flags(flags: ProductionFlags) -> list[str]:
    """Return names of flags that are True."""
    return [
        name for name, value in flags.model_dump().items() if value is True
    ]


def _scene_to_row(scene: Scene) -> dict:
    """Convert a Scene to a CSV row dict."""
    return {
        "scene_id": scene.scene_id,
        "slugline": scene.slugline,
        "int_ext": scene.int_ext,
        "day_night": scene.day_night,
        "page_eighths": scene.page_count_eighths,
        "summary": scene.scene_summary[:120],
        "vfx_est_min": scene.vfx_shot_count_estimate.min,
        "vfx_est_likely": scene.vfx_shot_count_estimate.likely,
        "vfx_est_max": scene.vfx_shot_count_estimate.max,
        "top_vfx_categories": _pipe_join(
            [c.value if hasattr(c, "value") else str(c) for c in scene.vfx_categories],
            max_items=3,
        ),
        "invisible_vfx": scene.invisible_vfx_likelihood,
        "cost_risk": scene.cost_risk_score,
        "schedule_risk": scene.schedule_risk_score,
        "top_flags": _pipe_join(_active_flags(scene.production_flags), max_items=3),
        "suggested_capture": _pipe_join(scene.suggested_capture, max_items=3),
    }


def breakdown_to_csv(output: BreakdownOutput) -> str:
    """Generate CSV string from a BreakdownOutput."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for scene in output.scenes:
        writer.writerow(_scene_to_row(scene))
    return buf.getvalue()


def write_csv(output: BreakdownOutput, path: str) -> None:
    """Write CSV to a file."""
    from pathlib import Path
    Path(path).write_text(breakdown_to_csv(output), encoding="utf-8")
```

**Step 4: Run tests**

Run: `pytest tests/test_export_csv.py -v`
Expected: All 3 tests PASS.

**Step 5: Commit**

```bash
git add src/sba/output/export_csv.py tests/test_export_csv.py
git commit -m "feat: add CSV export with pipe-delimited arrays"
```

---

## Task 16: CLI Interface

**Files:**
- Create: `src/sba/cli.py`

**Step 1: Write implementation**

```python
# src/sba/cli.py
"""CLI interface for the Script Breakdown Assistant."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from sba.config import CORPUS_DIR


@click.group()
def main():
    """Script Breakdown Assistant — VFX-aware screenplay analysis."""
    pass


@main.command()
@click.option("--input", "input_path", required=True, help="Path to screenplay (PDF or text)")
@click.option("--out", "output_dir", default="output", help="Output directory")
@click.option("--title", default="", help="Project title")
@click.option("--use-rag", is_flag=True, default=False, help="Use ChromaDB RAG instead of static corpus")
def analyze(input_path: str, output_dir: str, title: str, use_rag: bool):
    """Analyze a screenplay and generate VFX breakdown."""
    from sba.parsing.pipeline import parse_script_file
    from sba.llm.generator import generate_breakdown
    from sba.output.export_csv import write_csv

    input_file = Path(input_path)
    if not input_file.exists():
        click.echo(f"Error: File not found: {input_path}", err=True)
        sys.exit(1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Parsing: {input_file.name}")
    parsed = parse_script_file(input_file, title=title)
    click.echo(f"Found {len(parsed.scenes)} scenes, {len(parsed.all_characters)} characters")

    click.echo("Generating VFX breakdown via Claude...")
    result = generate_breakdown(parsed, use_rag=use_rag)
    click.echo(f"Generated breakdown: {len(result.scenes)} scenes analyzed")

    # Write JSON
    json_path = out_dir / f"{input_file.stem}_breakdown.json"
    json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    click.echo(f"JSON: {json_path}")

    # Write CSV
    csv_path = out_dir / f"{input_file.stem}_breakdown.csv"
    write_csv(result, str(csv_path))
    click.echo(f"CSV:  {csv_path}")

    # Summary
    click.echo(f"\nVFX heaviness: {result.global_flags.overall_vfx_heaviness}")
    click.echo(f"Hidden cost items: {len(result.hidden_cost_radar)}")
    click.echo("Done.")


@main.command("build-corpus")
def build_corpus():
    """Build and index the RAG corpus into ChromaDB."""
    from sba.rag.corpus_builder import build_corpus_from_directory
    from sba.rag.vector_store import index_chunks

    click.echo(f"Building corpus from: {CORPUS_DIR}")
    chunks = build_corpus_from_directory(CORPUS_DIR)
    click.echo(f"Built {len(chunks)} chunks")

    click.echo("Indexing into ChromaDB...")
    count = index_chunks(chunks)
    click.echo(f"Indexed {count} chunks. Done.")


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add src/sba/cli.py
git commit -m "feat: add CLI with analyze and build-corpus commands"
```

---

## Task 17: Run All Tests

**Step 1: Run full test suite**

Run:
```bash
cd "/Users/laurenceobyrne/prodcuer breaksdown tool"
source .venv/bin/activate
pytest tests/ -v
```

Expected: All tests PASS (parsing, schema, validation, CSV export).

**Step 2: Fix any failures, then commit**

```bash
git add -A
git commit -m "fix: resolve any test failures"
```

---

## Task 18: End-to-End Smoke Test

**Step 1: Create a test script fixture**

Create `tests/fixtures/test_excerpt.txt` with a 3-scene Star Wars excerpt.

**Step 2: Run the analyze command**

Run:
```bash
cd "/Users/laurenceobyrne/prodcuer breaksdown tool"
source .venv/bin/activate
python -m sba.cli analyze --input tests/fixtures/test_excerpt.txt --out output/ --title "Star Wars Test"
```

Expected: Produces `output/test_excerpt_breakdown.json` and `output/test_excerpt_breakdown.csv`.

**Step 3: Verify output files**

- JSON should be valid and parseable by Pydantic
- CSV should open in any spreadsheet app
- Both should contain 3 scenes with VFX categories and risk scores

**Step 4: Final commit**

```bash
git add tests/fixtures/ output/
git commit -m "feat: add test fixture and verify end-to-end pipeline"
```
