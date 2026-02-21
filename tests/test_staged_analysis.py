"""Tests for staged analysis and caching."""

import json
from unittest.mock import patch

from sba.cache import _cache_key, get_cached, set_cached
from sba.output.schema import BreakdownOutput


def _mock_scene_response() -> str:
    """Return a minimal valid JSON array for scene analysis."""
    return json.dumps(
        [
            {
                "scene_id": "1",
                "slugline": "INT. OFFICE - DAY",
                "int_ext": "INT",
                "day_night": "DAY",
                "scene_summary": "John sits at his desk.",
                "characters": ["JOHN"],
                "vfx_triggers": [],
                "vfx_categories": [],
                "production_flags": {},
                "vfx_shot_count_estimate": {"min": 0, "likely": 1, "max": 2},
                "cost_risk_score": 1,
                "schedule_risk_score": 1,
                "risk_reasons": [],
                "suggested_capture": [],
                "notes_for_producer": [],
                "uncertainties": [],
            }
        ]
    )


def _mock_global_response() -> str:
    """Return a minimal valid global summary JSON."""
    return json.dumps(
        {
            "global_flags": {
                "overall_vfx_heaviness": "low",
                "likely_virtual_production_fit": "low",
                "top_risk_themes": [],
            },
            "hidden_cost_radar": [],
            "key_questions_for_team": {
                "for_producer": ["Check budget"],
                "for_vfx_supervisor": [],
                "for_dp_camera": [],
                "for_locations_art_dept": [],
            },
        }
    )


@patch("sba.llm.generator._call_claude")
def test_staged_analysis_produces_valid_output(mock_claude):
    """Staged analysis with mocked _call_claude should produce valid BreakdownOutput."""
    from sba.llm.generator import analyze_script_staged

    # First call = chunk scene analysis, second call = global summary
    mock_claude.side_effect = [_mock_scene_response(), _mock_global_response()]

    result = analyze_script_staged(
        text="INT. OFFICE - DAY\n\nJohn sits at his desk.\n",
        title="Test Film",
    )

    assert isinstance(result, BreakdownOutput)
    assert len(result.scenes) >= 1
    assert result.scenes[0].scene_id == "1"


def test_cache_write_and_read(tmp_path, monkeypatch):
    """Cache should roundtrip correctly."""
    monkeypatch.setattr("sba.cache.CACHE_DIR", tmp_path)
    data = {"project_summary": {"project_title": "Cached"}, "scenes": []}
    set_cached("script text", "model-1", data)
    result = get_cached("script text", "model-1")
    assert result is not None
    assert result["project_summary"]["project_title"] == "Cached"


def test_cache_miss(tmp_path, monkeypatch):
    """Missing cache entry should return None."""
    monkeypatch.setattr("sba.cache.CACHE_DIR", tmp_path)
    result = get_cached("nonexistent", "model-1")
    assert result is None


def test_cache_key_deterministic():
    """Same inputs should produce same key."""
    k1 = _cache_key("script", "model")
    k2 = _cache_key("script", "model")
    assert k1 == k2


def test_cache_key_varies_with_model():
    """Different models should produce different keys."""
    k1 = _cache_key("script", "model-a")
    k2 = _cache_key("script", "model-b")
    assert k1 != k2
