"""Tests for the full parsing pipeline."""

from sba.parsing.pipeline import parse_script_text


def test_full_pipeline_from_text():
    script = """INT. DEATH STAR - CORRIDOR - DAY

Stormtroopers march through the corridor. An EXPLOSION rocks the station. Smoke fills the air.

VADER
I find your lack of faith disturbing.

OFFICER
Yes, Lord Vader.

EXT. TATOOINE - DESERT - DAY

Twin suns beat down on the endless sand. A SPEEDER races across the dunes.

LUKE
I was going to Tosche Station to pick up some power converters!

INT. REBEL BASE - COMMAND CENTER - NIGHT

Hundreds of REBEL SOLDIERS study holographic displays. The room buzzes with tension.

LEIA
The Empire is coming. We must prepare.
"""
    result = parse_script_text(script, title="Star Wars Test")
    assert result.title == "Star Wars Test"
    assert len(result.scenes) == 3

    # Scene 1: explosion + smoke = fire_pyro triggers
    s1 = result.scenes[0]
    assert s1.int_ext == "int"
    assert "VADER" in s1.characters
    assert "OFFICER" in s1.characters
    trigger_cats = {t.category for t in s1.vfx_triggers}
    assert len(trigger_cats) > 0  # Should detect explosion/smoke

    # Scene 2
    s2 = result.scenes[1]
    assert s2.int_ext == "ext"
    assert "LUKE" in s2.characters

    # Scene 3: crowds
    s3 = result.scenes[2]
    assert s3.day_night == "night"
    assert "LEIA" in s3.characters

    # All characters found
    assert "VADER" in result.all_characters
    assert "LUKE" in result.all_characters
    assert "LEIA" in result.all_characters
