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
    int_ext: str = "unspecified"
    day_night: str = "unspecified"
    page_count_eighths: int = 0
    location_type: str = "unspecified"
    characters: list[str] = Field(default_factory=list)
    scene_summary: str = ""
    vfx_triggers: list[str] = Field(default_factory=list)
    production_flags: ProductionFlags = Field(default_factory=ProductionFlags)
    vfx_categories: list[VfxCategory] = Field(default_factory=list)
    vfx_shot_count_estimate: VfxShotCountEstimate
    invisible_vfx_likelihood: str
    cost_risk_score: int = Field(ge=1, le=5)
    schedule_risk_score: int = Field(ge=1, le=5)
    risk_reasons: list[str] = Field(default_factory=list)
    suggested_capture: list[str] = Field(default_factory=list)
    notes_for_producer: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)


class HiddenCostItem(BaseModel):
    """A hidden cost multiplier flagged by the analysis."""

    flag: str
    severity: str
    where: list[str] = Field(default_factory=list)
    why_it_matters: str = ""
    mitigation_ideas: list[str] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    """Top-level project metadata."""

    project_title: str = ""
    date_analyzed: str = ""
    analysis_scope: str = "full_script"
    script_pages_estimate: Optional[int] = None
    total_scene_count: int = 0
    confidence_notes: list[str] = Field(default_factory=list)


class GlobalFlags(BaseModel):
    """Project-wide assessment flags."""

    overall_vfx_heaviness: str = "low"
    likely_virtual_production_fit: str = "low"
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
