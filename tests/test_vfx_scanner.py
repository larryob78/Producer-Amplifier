"""Tests for VFX trigger keyword scanning."""

from sba.parsing.vfx_scanner import scan_for_vfx_triggers


def test_detects_explosion():
    text = "The building explodes in a massive fireball."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "fire_pyro" in categories


def test_detects_water():
    text = "She dives underwater and swims toward the submarine."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "water" in categories


def test_false_positive_fired():
    text = "John is fired from his job."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "fire_pyro" not in categories


def test_detects_creature():
    text = "A massive dragon descends from the clouds."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "creatures_animals" in categories


def test_no_triggers_in_normal_dialogue():
    text = "JOHN\nI had a great day at the office."
    triggers = scan_for_vfx_triggers(text)
    assert len(triggers) == 0


def test_multiple_triggers():
    text = "The helicopter crashes into the ocean, exploding on impact."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "vehicles" in categories or "fire_pyro" in categories
    assert len(triggers) >= 2


def test_detects_wire_removal():
    text = "The actor is suspended from a wire harness above the set."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "wire_removal_rigs" in categories


def test_detects_screen_insert():
    text = "She looks at the hologram projected from her phone screen."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "screen_inserts" in categories


def test_detects_green_screen():
    text = "The actors stand in front of a green screen."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "set_extensions" in categories


def test_false_positive_screenplay():
    """'Screenplay' should not trigger screen_inserts."""
    text = "Based on the screenplay by John Smith."
    triggers = scan_for_vfx_triggers(text)
    categories = {t.category for t in triggers}
    assert "screen_inserts" not in categories
