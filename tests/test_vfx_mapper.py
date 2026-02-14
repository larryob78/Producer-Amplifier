"""Tests for VFX scanner → schema category mapping."""

from sba.output.schema import VfxCategory
from sba.parsing.vfx_mapper import TRIGGER_TO_VFX_CATEGORY, map_triggers_to_categories


def test_all_trigger_categories_map_to_valid_enum():
    """Every mapped VfxCategory must be a valid enum member."""
    for cat, vfx_list in TRIGGER_TO_VFX_CATEGORY.items():
        for vfx_cat in vfx_list:
            assert isinstance(
                vfx_cat, VfxCategory
            ), f"Trigger '{cat}' maps to invalid VfxCategory: {vfx_cat}"


def test_water_maps_to_fx_water():
    result = map_triggers_to_categories(["water"])
    assert VfxCategory.FX_WATER in result


def test_fire_pyro_maps_to_fire_and_smoke():
    result = map_triggers_to_categories(["fire_pyro"])
    assert VfxCategory.FX_FIRE in result
    assert VfxCategory.FX_SMOKE_DUST in result


def test_multiple_categories_deduplicated():
    """Duplicate VfxCategory values from different triggers should be merged."""
    result = map_triggers_to_categories(["weapons_combat", "reflections_glass"])
    comp_count = sum(1 for c in result if c == VfxCategory.COMP)
    assert comp_count == 1  # COMP appears in both but should only appear once


def test_unknown_category_ignored():
    """Unknown trigger categories should not cause errors."""
    result = map_triggers_to_categories(["nonexistent_category"])
    assert result == []


def test_empty_input():
    result = map_triggers_to_categories([])
    assert result == []


def test_all_scanner_categories_have_mapping():
    """Every category in the VFX scanner taxonomy should have a mapping."""
    from sba.parsing.vfx_scanner import VFX_TRIGGER_TAXONOMY

    for cat in VFX_TRIGGER_TAXONOMY:
        assert (
            cat in TRIGGER_TO_VFX_CATEGORY
        ), f"Scanner category '{cat}' has no mapping in TRIGGER_TO_VFX_CATEGORY"
