"""Smoke test: full pipeline with mocked Claude response.

Verifies the parsing pipeline and schema work end-to-end without real API calls.
"""

import json
from pathlib import Path
from unittest.mock import patch

from sba.output.schema import BreakdownOutput

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _mock_scene_json() -> str:
    """Return a valid JSON array of scenes (as returned by _call_claude chunk analysis)."""
    return json.dumps(
        [
            {
                "scene_id": "1",
                "slugline": "INT. ABANDONED WAREHOUSE - NIGHT",
                "int_ext": "INT",
                "day_night": "NIGHT",
                "scene_summary": "SWAT team breaches a warehouse rigged with explosives.",
                "characters": ["DETECTIVE REYES", "OFFICER CHEN"],
                "vfx_triggers": ["explosion", "smoke"],
                "vfx_categories": ["fx_explosion", "fx_smoke_dust", "set_extension"],
                "production_flags": {"fire_smoke": True, "destruction": True},
                "vfx_shot_count_estimate": {"min": 3, "likely": 5, "max": 8},
                "cost_risk_score": 3,
                "schedule_risk_score": 2,
                "risk_reasons": ["Practical explosion augmentation"],
                "suggested_capture": ["Clean plate", "HDRI"],
                "notes_for_producer": ["Consider practical smoke with CG enhancement."],
                "uncertainties": [],
            }
        ]
    )


def _mock_global_json() -> str:
    """Return a valid global summary JSON (as returned by _generate_global_summary)."""
    return json.dumps(
        {
            "global_flags": {
                "overall_vfx_heaviness": "high",
                "likely_virtual_production_fit": "high",
                "top_risk_themes": ["destruction", "crowd simulation"],
            },
            "hidden_cost_radar": [
                {
                    "flag": "Accumulating screen insert work",
                    "severity": "medium",
                    "where": ["1"],
                    "why_it_matters": "Every control room shot requires screen compositing.",
                    "mitigation_ideas": ["Pre-produce screen content before shoot"],
                }
            ],
            "key_questions_for_team": {
                "for_producer": ["Is the car tumble practical stunt or fully CG?"],
                "for_vfx_supervisor": ["Crowd approach: tiling or digital?"],
                "for_dp_camera": ["Need consistent HDRI capture on all exteriors"],
                "for_locations_art_dept": ["Mountain highway location scouting"],
            },
        }
    )


@patch("sba.llm.generator._call_claude")
def test_full_pipeline_smoke(mock_claude):
    """Full pipeline with mocked _call_claude should produce valid BreakdownOutput."""
    from sba.llm.generator import analyze_script_staged

    # First call = chunk scene analysis, second call = global summary
    mock_claude.side_effect = [_mock_scene_json(), _mock_global_json()]

    result = analyze_script_staged(
        text="INT. ABANDONED WAREHOUSE - NIGHT\n\nSWAT team breaches a warehouse.",
        title="Signal Lost Excerpt",
    )

    assert isinstance(result, BreakdownOutput)
    assert len(result.scenes) >= 1
    assert result.global_flags.overall_vfx_heaviness == "high"
    assert len(result.hidden_cost_radar) >= 1

    # Verify roundtrip
    json_str = result.model_dump_json()
    parsed = BreakdownOutput.model_validate_json(json_str)
    assert parsed.scenes[0].scene_id == "1"


@patch("sba.llm.generator._call_claude")
def test_full_pipeline_exports(mock_claude, tmp_path):
    """Pipeline result should export to CSV and HTML."""
    from sba.llm.generator import analyze_script_staged
    from sba.output.export_csv import export_scenes_csv
    from sba.output.export_html import export_html

    mock_claude.side_effect = [_mock_scene_json(), _mock_global_json()]

    result = analyze_script_staged(
        text="INT. ABANDONED WAREHOUSE - NIGHT\n\nSWAT team breaches a warehouse.",
        title="Signal Lost Excerpt",
    )

    # CSV
    csv_path = tmp_path / "test.csv"
    export_scenes_csv(result, csv_path)
    assert csv_path.exists()
    csv_content = csv_path.read_text()
    assert "WAREHOUSE" in csv_content

    # HTML
    html_path = tmp_path / "test.html"
    export_html(result, html_path)
    assert html_path.exists()
    html_content = html_path.read_text()
    assert "<!DOCTYPE html>" in html_content
