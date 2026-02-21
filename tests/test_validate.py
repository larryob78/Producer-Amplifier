"""Tests for JSON validation and repair pipeline."""

import json

from sba.output.validate import validate_breakdown_json


def _make_valid_json() -> str:
    """Return a minimal valid breakdown JSON string."""
    data = {
        "project_summary": {
            "project_title": "Test",
            "date_analyzed": "2026-02-14",
            "total_scene_count": 1,
        },
        "global_flags": {
            "overall_vfx_heaviness": "low",
            "top_risk_themes": [],
        },
        "scenes": [
            {
                "scene_id": "1",
                "slugline": "INT. OFFICE - DAY",
                "characters": [],
                "vfx_shot_count_estimate": {"min": 0, "likely": 0, "max": 0},
                "invisible_vfx_likelihood": "none",
                "cost_risk_score": 1,
                "schedule_risk_score": 1,
            }
        ],
    }
    return json.dumps(data)


def test_valid_json_passes():
    result = validate_breakdown_json(_make_valid_json())
    assert result.is_valid
    assert result.output is not None
    assert result.output.project_summary.project_title == "Test"


def test_markdown_fences_stripped():
    raw = f"```json\n{_make_valid_json()}\n```"
    result = validate_breakdown_json(raw)
    assert result.is_valid
    assert result.output is not None


def test_invalid_json_reports_error():
    result = validate_breakdown_json("{not valid json")
    assert not result.is_valid
    assert result.error_message != ""


def test_valid_json_but_invalid_schema():
    # Missing required fields
    result = validate_breakdown_json('{"foo": "bar"}')
assert result.is_valid  # schema is permissive; extra fields use defaults
assert result.output is not None


def test_cost_risk_out_of_range():
    data = json.loads(_make_valid_json())
    data["scenes"][0]["cost_risk_score"] = 10  # Out of range (1-5)
    result = validate_breakdown_json(json.dumps(data))
    assert result.is_valid  # schema clamps to 5, doesn't reject
    assert result.output.scenes[0].cost_risk_score == 5


def test_repairs_trailing_comma():
    # json_repair should handle trailing commas
    raw = _make_valid_json()
    # Add a trailing comma before the last }
    broken = raw[:-1] + ",}"
    result = validate_breakdown_json(broken)
    assert result.is_valid
    assert result.repair_applied


def test_empty_string_fails():
    result = validate_breakdown_json("")
    assert not result.is_valid


def test_valid_with_vfx_categories():
    data = json.loads(_make_valid_json())
    data["scenes"][0]["vfx_categories"] = ["comp", "roto", "wire_removal"]
    result = validate_breakdown_json(json.dumps(data))
    assert result.is_valid
    assert len(result.output.scenes[0].vfx_categories) == 3
