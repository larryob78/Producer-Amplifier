"""Tests for HTML production bible export."""

from sba.output.export_html import _build_html
from sba.output.schema import BreakdownOutput


def _make_breakdown() -> BreakdownOutput:
    """Create a minimal BreakdownOutput for testing."""
    return BreakdownOutput.model_validate(
        {
            "project_summary": {
                "project_title": "Test Film",
                "date_analyzed": "2026-02-14",
                "total_scene_count": 1,
            },
            "global_flags": {"overall_vfx_heaviness": "medium"},
            "scenes": [
                {
                    "scene_id": "1",
                    "slugline": "INT. OFFICE - DAY",
                    "int_ext": "int",
                    "day_night": "day",
                    "scene_summary": "A normal day at the office.",
                    "vfx_shot_count_estimate": {"min": 0, "likely": 1, "max": 2},
                    "invisible_vfx_likelihood": "low",
                    "cost_risk_score": 2,
                    "schedule_risk_score": 1,
                    "characters": ["JOHN"],
                    "risk_reasons": ["Minor wire removal"],
                }
            ],
            "hidden_cost_radar": [
                {
                    "flag": "Accumulating wire work",
                    "severity": "medium",
                    "where": ["1"],
                    "why_it_matters": "Wire removal adds up across scenes.",
                }
            ],
            "key_questions_for_team": {
                "for_producer": ["Check wire removal budget"],
            },
        }
    )


def test_html_contains_embedded_json():
    """HTML should embed the breakdown data as JSON."""
    breakdown = _make_breakdown()
    html = _build_html(breakdown)
    assert "const DATA =" in html
    assert '"project_title"' in html or "project_title" in html


def test_html_renders_scene():
    """HTML should contain at least one scene reference."""
    breakdown = _make_breakdown()
    html = _build_html(breakdown)
    assert "INT. OFFICE - DAY" in html or "scene_id" in html


def test_html_has_esc_function():
    """HTML must include the XSS-protection esc() function."""
    breakdown = _make_breakdown()
    html = _build_html(breakdown)
    assert "function esc(" in html


def test_html_xss_escaped_user_data():
    """User data in innerHTML calls should use esc()."""
    breakdown = _make_breakdown()
    html = _build_html(breakdown)
    # Scene rendering should use esc() for user strings
    assert "esc(s.slugline)" in html
    assert "esc(s.scene_summary" in html
    assert "esc(c.flag)" in html


def test_html_structure():
    """HTML should have expected sections."""
    breakdown = _make_breakdown()
    html = _build_html(breakdown)
    assert "<!DOCTYPE html>" in html
    assert 'id="summary"' in html
    assert 'id="scenes"' in html
    assert 'id="costs"' in html
    assert 'id="questions"' in html
    assert "</html>" in html
