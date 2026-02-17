"""Tests for CSV export functionality."""

import csv
import io

from sba.output.export_csv import (
    CSV_COLUMNS,
    export_scenes_csv,
    export_scenes_csv_string,
)
from sba.output.schema import BreakdownOutput


def _make_breakdown() -> BreakdownOutput:
    """Create a minimal BreakdownOutput for testing."""
    data = {
        "project_summary": {
            "project_title": "Test Film",
            "date_analyzed": "2026-02-14",
            "total_scene_count": 2,
        },
        "global_flags": {
            "overall_vfx_heaviness": "medium",
            "top_risk_themes": ["destruction", "creatures"],
        },
        "scenes": [
            {
                "scene_id": "1",
                "slugline": "INT. OFFICE - DAY",
                "int_ext": "int",
                "day_night": "day",
                "page_count_eighths": 4,
                "characters": ["JOHN", "JANE"],
                "vfx_categories": ["comp", "wire_removal"],
                "vfx_triggers": ["wire rig", "green screen"],
                "production_flags": {"stunts": True, "creatures": False},
                "vfx_shot_count_estimate": {"min": 2, "likely": 5, "max": 8},
                "invisible_vfx_likelihood": "low",
                "cost_risk_score": 2,
                "schedule_risk_score": 1,
                "risk_reasons": ["Wire removal for stunt"],
                "suggested_capture": ["Clean plate", "HDRI"],
                "notes_for_producer": ["Budget wire removal for 5 shots"],
            },
            {
                "scene_id": "2",
                "slugline": "EXT. ROOFTOP - NIGHT",
                "int_ext": "ext",
                "day_night": "night",
                "page_count_eighths": 8,
                "characters": ["HERO", "VILLAIN", "SIDEKICK", "EXTRA1"],
                "vfx_categories": [
                    "cg_creature",
                    "fx_destruction",
                    "set_extension",
                    "comp",
                ],
                "vfx_triggers": ["monster", "building collapse"],
                "production_flags": {"creatures": True, "destruction": True},
                "vfx_shot_count_estimate": {"min": 15, "likely": 25, "max": 40},
                "invisible_vfx_likelihood": "high",
                "cost_risk_score": 5,
                "schedule_risk_score": 4,
            },
        ],
    }
    return BreakdownOutput.model_validate(data)


def test_csv_string_has_header():
    breakdown = _make_breakdown()
    csv_str = export_scenes_csv_string(breakdown)
    reader = csv.reader(io.StringIO(csv_str))
    header = next(reader)
    assert header == CSV_COLUMNS


def test_csv_string_has_correct_row_count():
    breakdown = _make_breakdown()
    csv_str = export_scenes_csv_string(breakdown)
    reader = csv.reader(io.StringIO(csv_str))
    rows = list(reader)
    assert len(rows) == 3  # header + 2 scenes


def test_pipe_delimited_characters():
    breakdown = _make_breakdown()
    csv_str = export_scenes_csv_string(breakdown)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    # Scene 1 has 2 characters
    assert rows[0]["characters"] == "JOHN|JANE"


def test_pipe_delimited_capped_at_3():
    breakdown = _make_breakdown()
    csv_str = export_scenes_csv_string(breakdown)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    assert "(+1 more)" in rows[1]["characters"]
    # First 3 characters should be present
    assert "HERO" in rows[1]["characters"]
    assert "VILLAIN" in rows[1]["characters"]
    assert "SIDEKICK" in rows[1]["characters"]


def test_vfx_categories_pipe_delimited():
    breakdown = _make_breakdown()
    csv_str = export_scenes_csv_string(breakdown)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    assert "comp" in rows[0]["vfx_categories"]
    assert "|" in rows[0]["vfx_categories"]


def test_production_flags_shows_active_only():
    breakdown = _make_breakdown()
    csv_str = export_scenes_csv_string(breakdown)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    assert rows[0]["production_flags"] == "stunts"
    assert "creatures" in rows[1]["production_flags"]
    assert "destruction" in rows[1]["production_flags"]


def test_pipe_join_no_truncation():
    """Short lists should not have truncation indicator."""
    breakdown = _make_breakdown()
    csv_str = export_scenes_csv_string(breakdown)
    reader = csv.DictReader(io.StringIO(csv_str))
    rows = list(reader)
    # Scene 1 has only 2 characters — no truncation
    assert "(+" not in rows[0]["characters"]


def test_export_to_file(tmp_path):
    breakdown = _make_breakdown()
    csv_path = tmp_path / "test_output.csv"
    result_path = export_scenes_csv(breakdown, csv_path)
    assert result_path.exists()
    content = result_path.read_text()
    assert "INT. OFFICE - DAY" in content
    assert "EXT. ROOFTOP - NIGHT" in content
