# Gold Example: Death Star Corridor Scene

## Input Scene

```
INT. DEATH STAR - CORRIDOR - DAY

Stormtroopers march through the corridor. An EXPLOSION rocks the station.
Smoke fills the air. Sparks shower from damaged panels. A section of wall
COLLAPSES, revealing twisted metal and severed cables.

VADER
I find your lack of faith disturbing.

OFFICER
(choking)
Yes... Lord Vader.
```

## Expected Breakdown

```json
{
  "scene_id": 1,
  "slugline": "INT. DEATH STAR - CORRIDOR - DAY",
  "int_ext": "int",
  "day_night": "day",
  "page_count_eighths": 4,
  "location_type": "stage",
  "characters": ["VADER", "OFFICER"],
  "scene_summary": "Stormtroopers in Death Star corridor when explosion and structural collapse occurs. Vader interrogates officer.",
  "vfx_triggers": [
    "explosion",
    "smoke",
    "sparks",
    "wall collapse",
    "choking (Force choke)"
  ],
  "production_flags": {
    "green_blue_screen": false,
    "wire_rig_removal": false,
    "crowd_sim_needed": false,
    "digi_double_needed": false,
    "face_replacement": false,
    "full_cg_shot": false,
    "set_extension": true,
    "vehicle_work": false,
    "water_work": false,
    "fire_pyro": true,
    "virtual_production": false,
    "on_set_data_capture": true
  },
  "vfx_categories": ["fx_explosion", "fx_smoke_dust", "fx_destruction", "set_extension", "comp"],
  "vfx_shot_count_estimate": {
    "low": 6,
    "mid": 10,
    "high": 15
  },
  "invisible_vfx_likelihood": "medium",
  "cost_risk_score": 3,
  "schedule_risk_score": 2,
  "risk_reasons": [
    "Corridor destruction requires set extension and practical/CG hybrid effects",
    "Explosion and structural collapse need FX simulation and art direction",
    "Smoke interaction with corridor lighting requires careful compositing"
  ],
  "suggested_capture": [
    "HDRI of corridor set for CG lighting match",
    "Clean plate of corridor before practical effects",
    "Multiple camera angles for explosion reference",
    "LiDAR scan of corridor set for set extension"
  ],
  "notes_for_producer": "The corridor destruction can be achieved with a combination of practical effects (sparks, smoke) and CG augmentation (wall collapse, explosion enhancement). Set extension needed for the destroyed section. Force choke effect on Officer is minimal VFX (acting performance with subtle face color change).",
  "uncertainties": []
}
```

## Reasoning Notes

- **cost_risk_score: 3** — Destruction effects are moderate; corridor is a contained set (not open environment)
- **schedule_risk_score: 2** — Standard FX work, no novel creatures or characters
- **set_extension: true** — The collapsed wall section reveals structural damage beyond practical set
- **fire_pyro: true** — Explosion and sparks are pyro category
- **on_set_data_capture: true** — Must capture clean plates, HDRI, and LiDAR before practical effects
- **invisible_vfx_likelihood: medium** — Some paint/cleanup for practical effects rigs expected
- **Force choke** is a subtle effect (acting + minimal face VFX) not warranting its own VFX category
