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
