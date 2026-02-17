"""Smoke test: full pipeline with mocked Claude response.

Runs the complete analysis pipeline on the test fixture,
verifying valid BreakdownOutput end-to-end.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from sba.output.schema import BreakdownOutput

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _mock_claude_response() -> str:
    """Return a valid full BreakdownOutput JSON string."""
    return json.dumps(
        {
            "project_summary": {
                "project_title": "Signal Lost Excerpt",
                "date_analyzed": "2026-02-14T00:00:00Z",
                "analysis_scope": "excerpt",
                "script_pages_estimate": 2,
                "total_scene_count": 3,
                "confidence_notes": ["Short excerpt — estimates are rough."],
            },
            "global_flags": {
                "overall_vfx_heaviness": "high",
                "likely_virtual_production_fit": "high",
                "top_risk_themes": ["destruction", "crowd simulation"],
            },
            "scenes": [
                {
                    "scene_id": "1",
                    "slugline": "INT. ABANDONED WAREHOUSE - NIGHT",
                    "int_ext": "int",
                    "day_night": "night",
                    "page_count_eighths": 2,
                    "location_type": "stage",
                    "characters": ["DETECTIVE REYES", "OFFICER CHEN"],
                    "scene_summary": "SWAT team breaches a warehouse rigged with explosives.",
                    "vfx_triggers": ["explosion", "smoke"],
                    "production_flags": {"fire_smoke": True, "destruction": True},
                    "vfx_categories": [
                        "fx_explosion",
                        "fx_smoke_dust",
                        "set_extension",
                    ],
                    "vfx_shot_count_estimate": {"min": 3, "likely": 5, "max": 8},
                    "invisible_vfx_likelihood": "medium",
                    "cost_risk_score": 3,
                    "schedule_risk_score": 2,
                    "risk_reasons": ["Practical explosion augmentation", "Smoke sim"],
                    "suggested_capture": ["Clean plate", "HDRI", "Witness cameras"],
                    "notes_for_producer": ["Consider practical smoke with CG enhancement."],
                },
                {
                    "scene_id": "2",
                    "slugline": "EXT. MOUNTAIN HIGHWAY - DAY",
                    "int_ext": "ext",
                    "day_night": "day",
                    "page_count_eighths": 2,
                    "location_type": "ext_location",
                    "characters": ["MAYA"],
                    "scene_summary": "High-speed car chase along cliff-edge highway with helicopter pursuit.",
                    "vfx_triggers": ["helicopter", "vehicles"],
                    "production_flags": {"vehicles": True},
                    "vfx_categories": [
                        "cg_vehicle",
                        "sky_replacement",
                        "set_extension",
                    ],
                    "vfx_shot_count_estimate": {"min": 4, "likely": 6, "max": 10},
                    "invisible_vfx_likelihood": "high",
                    "cost_risk_score": 4,
                    "schedule_risk_score": 3,
                    "risk_reasons": [
                        "CG car tumble compositing",
                        "Helicopter aerial coordination",
                    ],
                    "suggested_capture": ["HDRI on location", "Chrome ball ref"],
                    "notes_for_producer": ["Every exterior needs consistent sky work."],
                },
                {
                    "scene_id": "3",
                    "slugline": "INT. CONTROL ROOM - NIGHT",
                    "int_ext": "int",
                    "day_night": "night",
                    "page_count_eighths": 3,
                    "location_type": "stage",
                    "characters": [],
                    "scene_summary": "Dozens of technicians monitor screens as warning lights flash.",
                    "vfx_triggers": ["monitor screens", "dozens of technicians"],
                    "production_flags": {"crowds": True, "complex_lighting": True},
                    "vfx_categories": ["crowd_sim", "screen_insert", "comp"],
                    "vfx_shot_count_estimate": {"min": 5, "likely": 8, "max": 12},
                    "invisible_vfx_likelihood": "high",
                    "cost_risk_score": 4,
                    "schedule_risk_score": 3,
                    "risk_reasons": [
                        "Crowd multiplication for technicians",
                        "Screen inserts on every display",
                    ],
                    "suggested_capture": ["Tracking markers", "Clean plates"],
                    "notes_for_producer": ["Budget crowd tiling passes."],
                },
            ],
            "hidden_cost_radar": [
                {
                    "flag": "Accumulating screen insert work",
                    "severity": "medium",
                    "where": ["3"],
                    "why_it_matters": "Every control room shot requires screen content compositing.",
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


@patch("sba.llm.generator.get_anthropic_client")
@patch("sba.llm.generator.call_claude")
def test_full_pipeline_smoke(mock_claude, mock_client):
    """Full pipeline on test fixture should produce valid BreakdownOutput."""
    from sba.llm.generator import analyze_script

    mock_claude.return_value = _mock_claude_response()
    mock_client.return_value = MagicMock()

    result = analyze_script(
        file_path=FIXTURES_DIR / "test_excerpt.txt",
        title="Signal Lost Excerpt",
    )

    assert isinstance(result, BreakdownOutput)
    assert len(result.scenes) == 3
    assert result.scenes[0].slugline == "INT. ABANDONED WAREHOUSE - NIGHT"
    assert result.global_flags.overall_vfx_heaviness == "high"
    assert len(result.hidden_cost_radar) >= 1

    # Verify roundtrip
    json_str = result.model_dump_json()
    parsed = BreakdownOutput.model_validate_json(json_str)
    assert parsed.scenes[0].scene_id == "1"


@patch("sba.llm.generator.get_anthropic_client")
@patch("sba.llm.generator.call_claude")
def test_full_pipeline_exports(mock_claude, mock_client, tmp_path):
    """Pipeline result should export to CSV, HTML, and XLSX."""
    from sba.llm.generator import analyze_script
    from sba.output.export_csv import export_scenes_csv
    from sba.output.export_html import export_html

    mock_claude.return_value = _mock_claude_response()
    mock_client.return_value = MagicMock()

    result = analyze_script(
        file_path=FIXTURES_DIR / "test_excerpt.txt",
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

    # XLSX (if openpyxl available)
    try:
        from sba.output.export_xlsx import export_xlsx

        xlsx_path = tmp_path / "test.xlsx"
        export_xlsx(result, xlsx_path)
        assert xlsx_path.exists()
    except ImportError:
        pass  # openpyxl optional
