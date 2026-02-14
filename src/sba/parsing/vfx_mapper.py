"""Mapping from VFX scanner trigger categories to output schema VfxCategory enum values."""

from __future__ import annotations

from sba.output.schema import VfxCategory

# Maps each scanner trigger category to one or more VfxCategory enum values.
# Used to pre-populate vfx_categories on parsed scenes before Claude analysis.
TRIGGER_TO_VFX_CATEGORY: dict[str, list[VfxCategory]] = {
    "water": [VfxCategory.FX_WATER],
    "fire_pyro": [VfxCategory.FX_FIRE, VfxCategory.FX_SMOKE_DUST],
    "crowds_extras": [VfxCategory.CROWD_SIM],
    "creatures_animals": [VfxCategory.CG_CREATURE],
    "vehicles": [VfxCategory.CG_VEHICLE],
    "destruction": [VfxCategory.FX_DESTRUCTION],
    "weapons_combat": [VfxCategory.COMP, VfxCategory.FX_EXPLOSION],
    "aerial_height": [VfxCategory.ZERO_G, VfxCategory.WIRE_REMOVAL],
    "weather_atmosphere": [VfxCategory.FX_WEATHER],
    "supernatural_magic": [VfxCategory.COMP, VfxCategory.CG_ENVIRONMENT],
    "wire_removal_rigs": [VfxCategory.WIRE_REMOVAL],
    "cleanup_paint": [VfxCategory.PAINT_CLEANUP],
    "screen_inserts": [VfxCategory.SCREEN_INSERT],
    "set_extensions": [VfxCategory.SET_EXTENSION],
    "reflections_glass": [VfxCategory.COMP],
    "beauty_retouching": [VfxCategory.BEAUTY_WORK],
    "rig_removal": [VfxCategory.WIRE_REMOVAL, VfxCategory.PAINT_CLEANUP],
    "stabilization": [VfxCategory.MATCHMOVE],
}


def map_triggers_to_categories(trigger_categories: list[str]) -> list[VfxCategory]:
    """Map a list of scanner trigger category names to VfxCategory enum values.

    Args:
        trigger_categories: Category strings from the VFX scanner (e.g., ["water", "fire_pyro"]).

    Returns:
        Deduplicated list of VfxCategory enum values.
    """
    seen: set[VfxCategory] = set()
    result: list[VfxCategory] = []

    for cat in trigger_categories:
        for vfx_cat in TRIGGER_TO_VFX_CATEGORY.get(cat, []):
            if vfx_cat not in seen:
                seen.add(vfx_cat)
                result.append(vfx_cat)

    return result
