"""CSV export from BreakdownOutput Pydantic models.

Uses pipe-delimited arrays capped at 3 items for Excel compatibility.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from sba.output.schema import BreakdownOutput, Scene


def _pipe_join(items: list[str], max_items: int = 3) -> str:
    """Join list items with pipe delimiter, capped at max_items."""
    truncated = items[:max_items]
    return "|".join(truncated)


def _scene_to_row(scene: Scene) -> dict[str, str]:
    """Convert a Scene model to a flat CSV row dict."""
    flags = scene.production_flags
    active_flags = [
        name
        for name, val in [
            ("stunts", flags.stunts),
            ("creatures", flags.creatures),
            ("vehicles", flags.vehicles),
            ("crowds", flags.crowds),
            ("water", flags.water),
            ("fire_smoke", flags.fire_smoke),
            ("destruction", flags.destruction),
            ("weather", flags.weather),
            ("complex_lighting", flags.complex_lighting),
            ("space_or_zero_g", flags.space_or_zero_g),
            ("heavy_costume_makeup", flags.heavy_costume_makeup),
        ]
        if val
    ]

    return {
        "scene_id": scene.scene_id,
        "slugline": scene.slugline,
        "int_ext": scene.int_ext,
        "day_night": scene.day_night,
        "page_count_eighths": str(scene.page_count_eighths),
        "location_type": scene.location_type,
        "characters": _pipe_join(scene.characters),
        "scene_summary": scene.scene_summary,
        "vfx_categories": _pipe_join([c.value for c in scene.vfx_categories]),
        "vfx_triggers": _pipe_join(scene.vfx_triggers),
        "production_flags": _pipe_join(active_flags),
        "vfx_shots_min": str(scene.vfx_shot_count_estimate.min),
        "vfx_shots_likely": str(scene.vfx_shot_count_estimate.likely),
        "vfx_shots_max": str(scene.vfx_shot_count_estimate.max),
        "invisible_vfx": scene.invisible_vfx_likelihood,
        "cost_risk": str(scene.cost_risk_score),
        "schedule_risk": str(scene.schedule_risk_score),
        "risk_reasons": _pipe_join(scene.risk_reasons),
        "suggested_capture": _pipe_join(scene.suggested_capture),
        "notes_for_producer": _pipe_join(
            scene.notes_for_producer
            if isinstance(scene.notes_for_producer, list)
            else [scene.notes_for_producer]
        ),
        "uncertainties": _pipe_join(scene.uncertainties),
    }


CSV_COLUMNS = [
    "scene_id",
    "slugline",
    "int_ext",
    "day_night",
    "page_count_eighths",
    "location_type",
    "characters",
    "scene_summary",
    "vfx_categories",
    "vfx_triggers",
    "production_flags",
    "vfx_shots_min",
    "vfx_shots_likely",
    "vfx_shots_max",
    "invisible_vfx",
    "cost_risk",
    "schedule_risk",
    "risk_reasons",
    "suggested_capture",
    "notes_for_producer",
    "uncertainties",
]


def export_scenes_csv(breakdown: BreakdownOutput, output_path: Path) -> Path:
    """Export scene breakdown to CSV file.

    Returns the path to the written file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for scene in breakdown.scenes:
            writer.writerow(_scene_to_row(scene))

    return output_path


def export_scenes_csv_string(breakdown: BreakdownOutput) -> str:
    """Export scene breakdown to a CSV string (for testing / display)."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for scene in breakdown.scenes:
        writer.writerow(_scene_to_row(scene))
    return output.getvalue()
