# Gold Example: Tatooine Desert Scene

## Input Scene

```
EXT. TATOOINE - DESERT - DAY

Twin suns beat down on the endless sand. A SPEEDER races across the dunes,
kicking up a massive trail of dust. In the distance, a SANDCRAWLER moves
slowly across the horizon, tiny against the vast landscape.

LUKE
(frustrated)
I was going to Tosche Station to pick up some power converters!

OWEN (O.S.)
You can waste time with your friends when your chores are done.

The speeder banks hard, throwing up a wall of sand as it changes direction
toward the moisture farm. We can see BANTHAS grazing near rock formations
in the middle distance.
```

## Expected Breakdown

```json
{
  "scene_id": 2,
  "slugline": "EXT. TATOOINE - DESERT - DAY",
  "int_ext": "ext",
  "day_night": "day",
  "page_count_eighths": 6,
  "location_type": "ext_location",
  "characters": ["LUKE", "OWEN"],
  "scene_summary": "Luke crosses Tatooine desert in speeder, passing Sandcrawler and Banthas. Owen calls him back to the moisture farm.",
  "vfx_triggers": [
    "twin suns",
    "speeder vehicle",
    "dust trail",
    "Sandcrawler vehicle",
    "vast landscape/environment",
    "Banthas (creatures)"
  ],
  "production_flags": {
    "green_blue_screen": false,
    "wire_rig_removal": false,
    "crowd_sim_needed": false,
    "digi_double_needed": false,
    "face_replacement": false,
    "full_cg_shot": true,
    "set_extension": true,
    "vehicle_work": true,
    "water_work": false,
    "fire_pyro": false,
    "virtual_production": false,
    "on_set_data_capture": true
  },
  "vfx_categories": ["cg_vehicle", "cg_creature", "cg_environment", "matte_painting", "sky_replacement", "fx_smoke_dust", "comp"],
  "vfx_shot_count_estimate": {
    "low": 8,
    "mid": 14,
    "high": 20
  },
  "invisible_vfx_likelihood": "high",
  "cost_risk_score": 4,
  "schedule_risk_score": 3,
  "risk_reasons": [
    "Multiple CG assets required: speeder, Sandcrawler, Banthas",
    "CG creatures (Banthas) require modeling, rigging, and animation",
    "Twin suns sky replacement on every exterior shot in sequence",
    "Speeder dust interaction requires FX simulation",
    "Wide establishing shots may be full CG or heavy matte painting"
  ],
  "suggested_capture": [
    "Desert location HDRI for all CG asset lighting",
    "Practical speeder rig reference for dust interaction",
    "Bantha scale and movement reference (physical maquette or concept art)",
    "LiDAR scan of practical desert set/location for CG ground extension",
    "Sand texture and color reference photography"
  ],
  "notes_for_producer": "This scene is VFX-heavy despite appearing as a simple desert exterior. The twin suns require sky replacement on every shot. The speeder, Sandcrawler, and Banthas are all CG assets. Wide shots may be entirely CG environments with matte paintings. The dust interaction with the speeder requires FX simulation per shot. Consider virtual production (LED wall with desert environment) for actor close-ups to reduce compositing.",
  "uncertainties": []
}
```

## Reasoning Notes

- **cost_risk_score: 4** — Multiple unique CG assets (speeder, Sandcrawler, Banthas) each requiring full asset pipeline
- **schedule_risk_score: 3** — CG creatures (Banthas) need development time but are background elements, not hero creatures
- **full_cg_shot: true** — Wide establishing shots will likely be fully CG
- **vehicle_work: true** — Both the speeder and Sandcrawler are CG vehicles
- **set_extension: true** — Desert environment needs CG extension for alien landscape
- **sky_replacement** — Twin suns require sky replacement on every single shot
- **invisible_vfx_likelihood: high** — Even close-ups need twin-sun sky and alien environment cleanup
