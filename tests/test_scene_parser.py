"""Tests for scene heading detection and splitting."""

from sba.parsing.scene_parser import detect_scene_heading, split_into_scenes


def test_basic_int_day():
    match = detect_scene_heading("INT. OFFICE - DAY")
    assert match is not None
    assert match["int_ext"] == "int"
    assert match["location"] == "OFFICE"
    assert match["time_of_day"] == "DAY"


def test_ext_night():
    match = detect_scene_heading("EXT. ROOFTOP - NIGHT")
    assert match is not None
    assert match["int_ext"] == "ext"
    assert match["location"] == "ROOFTOP"
    assert match["time_of_day"] == "NIGHT"


def test_int_ext():
    match = detect_scene_heading("INT./EXT. CAR - DAY")
    assert match is not None
    assert match["int_ext"] == "int_ext"


def test_scene_numbers():
    match = detect_scene_heading("42 INT. OFFICE - DAY 42")
    assert match is not None
    assert match["location"] == "OFFICE"


def test_no_time_of_day():
    match = detect_scene_heading("INT. HALLWAY")
    assert match is not None
    assert match["time_of_day"] is None


def test_non_heading():
    match = detect_scene_heading("John walks into the room.")
    assert match is None


def test_continuous():
    match = detect_scene_heading("INT. KITCHEN - CONTINUOUS")
    assert match is not None
    assert match["time_of_day"] == "CONTINUOUS"


def test_split_simple_script():
    text = """INT. OFFICE - DAY

John sits at his desk.

JOHN
Hello.

EXT. PARKING LOT - NIGHT

Rain falls on empty cars.

JANE
Where is everyone?"""

    scenes = split_into_scenes(text)
    assert len(scenes) == 2
    assert scenes[0].slugline == "INT. OFFICE - DAY"
    assert scenes[0].int_ext == "int"
    assert scenes[0].day_night == "day"
    assert "John sits at his desk" in scenes[0].raw_text
    assert scenes[1].slugline == "EXT. PARKING LOT - NIGHT"
    assert scenes[1].int_ext == "ext"
    assert scenes[1].day_night == "night"
