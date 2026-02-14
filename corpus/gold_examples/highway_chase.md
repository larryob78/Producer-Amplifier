# Gold Example: Mountain Highway Chase Scene

## Input Scene

```
EXT. MOUNTAIN HIGHWAY - DAY

A black sedan races along the cliff edge. A HELICOPTER swoops low overhead,
matching speed. The sedan swerves around a truck, tires screeching. Wind
whips through the canyon below. In the distance, a second PURSUIT VEHICLE
closes the gap.

MAYA
(into phone)
They found us. Punch it — take the next exit!

DRIVER
Hold on!

The sedan clips the guardrail and TUMBLES off the cliff edge. We follow
the car as it rolls down the rocky slope, throwing up dirt and debris.
The helicopter banks hard to follow.
```

## Expected Breakdown

```json
{
  "scene_id": 2,
  "slugline": "EXT. MOUNTAIN HIGHWAY - DAY",
  "int_ext": "ext",
  "day_night": "day",
  "page_count_eighths": 6,
  "location_type": "ext_location",
  "characters": ["MAYA", "DRIVER"],
  "scene_summary": "High-speed car chase along cliff-edge highway with helicopter pursuit. Lead car tumbles off the cliff.",
  "vfx_triggers": [
    "helicopter",
    "car chase",
    "cliff edge",
    "car tumble",
    "pursuit vehicles",
    "canyon environment"
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
  "vfx_categories": ["cg_vehicle", "cg_environment", "matte_painting", "fx_destruction", "comp"],
  "vfx_shot_count_estimate": {
    "low": 20,
    "mid": 35,
    "high": 50
  },
  "invisible_vfx_likelihood": "high",
  "cost_risk_score": 5,
  "schedule_risk_score": 5,
  "risk_reasons": [
    "Car tumble off cliff requires full CG takeover",
    "Helicopter aerial coordination is complex and weather-dependent",
    "Road closure permits and multi-unit logistics",
    "Stunt driving coordination at speed on mountain roads",
    "Wide shots may require CG environment extension for canyon"
  ],
  "suggested_capture": [
    "HDRI of highway location for CG lighting match",
    "Practical stunt driving with stunt doubles for in-car shots",
    "Drone and helicopter for aerial coverage",
    "LiDAR scan of cliff face for CG car tumble",
    "Multiple camera cars for chase coverage"
  ],
  "notes_for_producer": "This is the most complex action sequence. The practical chase can be shot with stunt drivers, but the cliff tumble requires CG takeover. Budget for 3 full days minimum with weather backup days. Lock road permits 8 weeks out. Stunt coordinator needs extensive rehearsal time.",
  "uncertainties": []
}
```

## Reasoning Notes

- **cost_risk_score: 5** — Complex multi-element sequence: practical stunts, helicopter, CG takeover
- **schedule_risk_score: 5** — Weather dependency, road permits, helicopter coordination, multi-unit
- **full_cg_shot: true** — The car tumble off the cliff will be fully CG
- **vehicle_work: true** — Multiple vehicles including helicopter
- **set_extension: true** — Canyon environment needs CG extension
- **invisible_vfx_likelihood: high** — Even simple driving shots need sky consistency and wire cleanup
