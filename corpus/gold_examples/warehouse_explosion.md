# Gold Example: Warehouse Explosion Scene

## Input Scene

```
INT. ABANDONED WAREHOUSE - NIGHT

SWAT officers stack up by the door. An EXPLOSION blows out the windows. Smoke
and debris fill the air. Sparks shower from severed electrical conduits.
A section of the mezzanine COLLAPSES, sending twisted metal crashing down.

DETECTIVE REYES
Everyone get down! The whole place is rigged!

OFFICER CHEN
(into radio)
Copy that. Moving to secondary entry.
```

## Expected Breakdown

```json
{
  "scene_id": 1,
  "slugline": "INT. ABANDONED WAREHOUSE - NIGHT",
  "int_ext": "int",
  "day_night": "night",
  "page_count_eighths": 4,
  "location_type": "stage",
  "characters": ["DETECTIVE REYES", "OFFICER CHEN"],
  "scene_summary": "SWAT team breaches warehouse when explosion and structural collapse occurs. Reyes orders team to take cover.",
  "vfx_triggers": [
    "explosion",
    "smoke",
    "sparks",
    "mezzanine collapse",
    "debris"
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
    "Warehouse destruction requires set extension and practical/CG hybrid effects",
    "Explosion and structural collapse need FX simulation and art direction",
    "Smoke interaction with warehouse lighting requires careful compositing"
  ],
  "suggested_capture": [
    "HDRI of warehouse set for CG lighting match",
    "Clean plate of warehouse before practical effects",
    "Multiple camera angles for explosion reference",
    "LiDAR scan of warehouse set for set extension"
  ],
  "notes_for_producer": "The warehouse destruction can be achieved with a combination of practical effects (sparks, smoke) and CG augmentation (mezzanine collapse, explosion enhancement). Set extension needed for the destroyed section. Pre-rig for controlled pyro charges with safety protocols.",
  "uncertainties": []
}
```

## Reasoning Notes

- **cost_risk_score: 3** — Destruction effects are moderate; warehouse is a contained set (not open environment)
- **schedule_risk_score: 2** — Standard FX work, no novel creatures or characters
- **set_extension: true** — The collapsed mezzanine section reveals structural damage beyond practical set
- **fire_pyro: true** — Explosion and sparks are pyro category
- **on_set_data_capture: true** — Must capture clean plates, HDRI, and LiDAR before practical effects
- **invisible_vfx_likelihood: medium** — Some paint/cleanup for practical effects rigs expected
