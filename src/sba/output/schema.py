"""Pydantic models — relaxed schema that accepts Claude output variations."""

from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator

from enum import Enum

class VfxCategory(str, Enum):
    COMP = "comp"
    ROTO = "roto"
    PAINT_CLEANUP = "paint_cleanup"
    WIRE_REMOVAL = "wire_removal"
    CG_CREATURE = "cg_creature"
    CG_VEHICLE = "cg_vehicle"
    CG_PROP = "cg_prop"
    CG_ENVIRONMENT = "cg_environment"
    DIGI_DOUBLE = "digi_double"
    FACE_REPLACEMENT = "face_replacement"
    SET_EXTENSION = "set_extension"
    MATTE_PAINTING = "matte_painting"
    SKY_REPLACEMENT = "sky_replacement"
    FX_WATER = "fx_water"
    FX_FIRE = "fx_fire"
    FX_SMOKE_DUST = "fx_smoke_dust"
    FX_DESTRUCTION = "fx_destruction"
    FX_WEATHER = "fx_weather"
    FX_EXPLOSION = "fx_explosion"
    MATCHMOVE = "matchmove"
    CAMERA_PROJECTION = "camera_projection"
    CROWD_SIM = "crowd_sim"
    ZERO_G = "zero_g"
    SCREEN_INSERT = "screen_insert"
    DAY_FOR_NIGHT = "day_for_night"
    BEAUTY_WORK = "beauty_work"
    OTHER = "other"



class VfxShotCountEstimate(BaseModel):
    min: int = 0
    likely: int = 0
    max: int = 0

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, v):
        if isinstance(v, (int, float)):
            n = int(v)
            return {"min": n, "likely": n, "max": n}
        if isinstance(v, str):
            return {"min": 0, "likely": 0, "max": 0}
        if isinstance(v, dict):
            for k in ("min", "likely", "max"):
                if k in v and not isinstance(v[k], int):
                    try: v[k] = int(v[k])
                    except: v[k] = 0
        return v


class ProductionFlags(BaseModel):
    model_config = dict(extra="allow")
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
    model_config = dict(extra="allow")
    scene_id: str | int = ""
    slugline: str = ""
    int_ext: str = "unspecified"
    day_night: str = "unspecified"
    page_count_eighths: int | float | str = 0
    location_type: str = "unspecified"
    characters: list[str] | str = Field(default_factory=list)
    scene_summary: str = ""
    vfx_triggers: list[str] | str = Field(default_factory=list)
    production_flags: ProductionFlags | dict = Field(default_factory=ProductionFlags)
    vfx_categories: list[str] = Field(default_factory=list)
    vfx_shot_count_estimate: VfxShotCountEstimate | dict | int = Field(default_factory=lambda: VfxShotCountEstimate())
    invisible_vfx_likelihood: str = "none"
    cost_risk_score: int | float | str = 1
    schedule_risk_score: int | float | str = 1
    risk_reasons: list[str] | str = Field(default_factory=list)
    suggested_capture: list[str] | str = Field(default_factory=list)
    notes_for_producer: list[str] | str = ""
    uncertainties: list[str] | str = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce_fields(cls, v):
        if not isinstance(v, dict):
            return v
        for f in ("cost_risk_score", "schedule_risk_score"):
            if f in v:
                try: v[f] = max(1, min(5, int(v[f])))
                except: v[f] = 1
        for f in ("characters", "vfx_triggers", "risk_reasons", "suggested_capture", "uncertainties"):
            if f in v and isinstance(v[f], str):
                v[f] = [v[f]] if v[f] else []
        if "notes_for_producer" in v and isinstance(v["notes_for_producer"], list):
            pass
        if "page_count_eighths" in v:
            try: v["page_count_eighths"] = int(float(str(v["page_count_eighths"])))
            except: v["page_count_eighths"] = 0
        return v


class HiddenCostItem(BaseModel):
    model_config = dict(extra="allow")
    flag: str = ""
    severity: str = "medium"
    where: list[str] | str = Field(default_factory=list)
    why_it_matters: str = ""
    mitigation_ideas: list[str] | str = Field(default_factory=list)


class ProjectSummary(BaseModel):
    model_config = dict(extra="allow")
    project_title: str = ""
    date_analyzed: str = ""
    analysis_scope: str = "full_script"
    script_pages_estimate: Optional[int | float] = None
    total_scene_count: int = 0
    confidence_notes: list[str] | str = Field(default_factory=list)


class GlobalFlags(BaseModel):
    model_config = dict(extra="allow")
    overall_vfx_heaviness: str = "low"
    likely_virtual_production_fit: str = "low"
    top_risk_themes: list[str] = Field(default_factory=list)


class KeyQuestions(BaseModel):
    model_config = dict(extra="allow")
    for_producer: list[str] | str = Field(default_factory=list)
    for_vfx_supervisor: list[str] | str = Field(default_factory=list)
    for_dp_camera: list[str] | str = Field(default_factory=list)
    for_locations_art_dept: list[str] | str = Field(default_factory=list)


class BreakdownOutput(BaseModel):
    model_config = dict(extra="allow")
    project_summary: ProjectSummary = Field(default_factory=ProjectSummary)
    global_flags: GlobalFlags = Field(default_factory=GlobalFlags)
    scenes: list[Scene] = Field(default_factory=list)
    hidden_cost_radar: list[HiddenCostItem] = Field(default_factory=list)
    key_questions_for_team: KeyQuestions = Field(default_factory=KeyQuestions)
