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
    vfx_categories: list[str] = field(default_factory=list)
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
