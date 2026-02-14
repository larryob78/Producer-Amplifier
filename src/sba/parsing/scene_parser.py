"""Scene heading detection and script splitting."""

from __future__ import annotations

import re

from sba.parsing.models import ParsedScene

# Scene heading pattern — handles INT., EXT., INT./EXT., scene numbers, time of day
SCENE_HEADING_RE = re.compile(
    r"^"
    r"(?:\d+[A-Z]?\s+)?"  # Optional scene number prefix
    r"(?P<ie_prefix>"
    r"(?:INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?)"  # INT./EXT. variants
    r"|I/E\.?"  # I/E. shorthand
    r"|INT\.?"  # INT.
    r"|EXT\.?"  # EXT.
    r"|EST\.?"  # EST. (establishing)
    r")"
    r"[\s.\-/]+"  # Separator
    r"(?P<location>.+?)"  # Location (non-greedy)
    r"(?:"
    r"\s*[-\u2013\u2014]+\s*"  # Dash separator
    r"(?P<time_of_day>"
    r"DAY|NIGHT|DAWN|DUSK|MORNING|AFTERNOON|EVENING"
    r"|CONTINUOUS|LATER|SAME\s*TIME|MOMENTS?\s*LATER"
    r"|SUNSET|SUNRISE"
    r")"
    r")?"
    r"(?:\s+\d+[A-Z]?)?"  # Optional scene number suffix
    r"\s*$",
    re.IGNORECASE,
)

TIME_TO_DAY_NIGHT = {
    "day": "day",
    "night": "night",
    "dawn": "dawn",
    "dusk": "dusk",
    "morning": "day",
    "afternoon": "day",
    "evening": "night",
    "continuous": "continuous",
    "later": "unspecified",
    "same time": "unspecified",
    "same": "unspecified",
    "moments later": "unspecified",
    "moment later": "unspecified",
    "sunset": "dusk",
    "sunrise": "dawn",
}


def detect_scene_heading(line: str) -> dict | None:
    """Parse a line as a scene heading. Returns dict or None."""
    line = line.strip()
    if not line:
        return None

    match = SCENE_HEADING_RE.match(line)
    if not match:
        return None

    ie_raw = match.group("ie_prefix").upper().replace(" ", "")
    if "/" in ie_raw:
        int_ext = "int_ext"
    elif ie_raw.startswith("INT"):
        int_ext = "int"
    elif ie_raw.startswith("EXT") or ie_raw.startswith("EST"):
        int_ext = "ext"
    elif ie_raw.startswith("I/E"):
        int_ext = "int_ext"
    else:
        int_ext = "unspecified"

    location = match.group("location").strip().rstrip("-\u2013\u2014 ")
    time_raw = match.group("time_of_day")
    time_of_day = None
    day_night = "unspecified"

    if time_raw:
        time_of_day = time_raw.upper().strip()
        day_night = TIME_TO_DAY_NIGHT.get(time_raw.lower().strip(), "unspecified")

    return {
        "slugline": line,
        "int_ext": int_ext,
        "location": location,
        "time_of_day": time_of_day,
        "day_night": day_night,
    }


def split_into_scenes(text: str) -> list[ParsedScene]:
    """Split preprocessed screenplay text into scenes."""
    lines = text.split("\n")
    scenes: list[ParsedScene] = []
    current_heading = None
    current_lines: list[str] = []
    scene_num = 0

    for line in lines:
        heading = detect_scene_heading(line)
        if heading:
            # Save previous scene
            if current_heading is not None:
                scene_num += 1
                raw = "\n".join(current_lines).strip()
                scenes.append(
                    ParsedScene(
                        scene_number=scene_num,
                        slugline=current_heading["slugline"],
                        int_ext=current_heading["int_ext"],
                        day_night=current_heading["day_night"],
                        location=current_heading["location"],
                        raw_text=raw,
                        word_count=len(raw.split()),
                    )
                )
            current_heading = heading
            current_lines = []
        else:
            current_lines.append(line)

    # Save last scene
    if current_heading is not None:
        scene_num += 1
        raw = "\n".join(current_lines).strip()
        scenes.append(
            ParsedScene(
                scene_number=scene_num,
                slugline=current_heading["slugline"],
                int_ext=current_heading["int_ext"],
                day_night=current_heading["day_night"],
                location=current_heading["location"],
                raw_text=raw,
                word_count=len(raw.split()),
            )
        )

    return scenes
