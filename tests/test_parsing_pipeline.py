"""Tests for the full parsing pipeline."""

from sba.parsing.pipeline import parse_script_text


def test_full_pipeline_from_text():
    script = """INT. ABANDONED WAREHOUSE - NIGHT

SWAT officers stack up by the door. An EXPLOSION blows out the windows. Smoke and debris fill the air.

DETECTIVE REYES
Everyone get down! The whole place is rigged!

OFFICER CHEN
Copy that. Moving to secondary entry.

EXT. MOUNTAIN HIGHWAY - DAY

A black sedan races along the cliff edge. A HELICOPTER swoops low overhead, matching speed.

MAYA
They found us. Punch it — take the next exit!

INT. CONTROL ROOM - NIGHT

Dozens of TECHNICIANS monitor banks of screens. Warning lights flash. The room buzzes with tension.

DIRECTOR WARD
The signal is broadcasting. We have six minutes to shut it down.
"""
    result = parse_script_text(script, title="Signal Lost Test")
    assert result.title == "Signal Lost Test"
    assert len(result.scenes) == 3

    # Scene 1: explosion + smoke = fire_pyro triggers
    s1 = result.scenes[0]
    assert s1.int_ext == "int"
    assert "DETECTIVE REYES" in s1.characters
    assert "OFFICER CHEN" in s1.characters
    trigger_cats = {t.category for t in s1.vfx_triggers}
    assert len(trigger_cats) > 0  # Should detect explosion/smoke

    # Scene 2
    s2 = result.scenes[1]
    assert s2.int_ext == "ext"
    assert "MAYA" in s2.characters

    # Scene 3: crowds
    s3 = result.scenes[2]
    assert s3.day_night == "night"
    assert "DIRECTOR WARD" in s3.characters

    # All characters found
    assert "DETECTIVE REYES" in result.all_characters
    assert "MAYA" in result.all_characters
    assert "DIRECTOR WARD" in result.all_characters
