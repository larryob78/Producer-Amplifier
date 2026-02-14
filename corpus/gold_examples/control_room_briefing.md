# Gold Example: Control Room Briefing Scene

## Input Scene

```
INT. CONTROL ROOM - NIGHT

Dozens of TECHNICIANS monitor banks of screens showing the signal broadcast.
Warning lights flash. The room buzzes with tension. A massive HOLOGRAPHIC
DISPLAY at the center shows a cascading data visualization — the signal
propagating outward across a map.

DIRECTOR WARD
The signal is broadcasting. We have six minutes to shut it down.

DR. VASQUEZ
The encryption is military-grade. I need direct access to the mainframe.

A detailed schematic appears on the holographic display, zooming into the
signal tower's architecture. Engineers lean forward, studying the weak points.

TECH WILSON
There — the auxiliary relay. Cut that and the whole network goes dark.
```

## Expected Breakdown

```json
{
  "scene_id": 3,
  "slugline": "INT. CONTROL ROOM - NIGHT",
  "int_ext": "int",
  "day_night": "night",
  "page_count_eighths": 6,
  "location_type": "stage",
  "characters": ["DIRECTOR WARD", "DR. VASQUEZ", "TECH WILSON"],
  "scene_summary": "Team races to shut down a rogue signal broadcast from the control room. Holographic displays show the signal propagation and tower schematics.",
  "vfx_triggers": [
    "dozens of technicians (crowd)",
    "banks of monitor screens",
    "holographic display",
    "data visualization animation",
    "schematic animation"
  ],
  "production_flags": {
    "green_blue_screen": false,
    "wire_rig_removal": false,
    "crowd_sim_needed": true,
    "digi_double_needed": false,
    "face_replacement": false,
    "full_cg_shot": false,
    "set_extension": true,
    "vehicle_work": false,
    "water_work": false,
    "fire_pyro": false,
    "virtual_production": false,
    "on_set_data_capture": true
  },
  "vfx_categories": ["screen_insert", "cg_prop", "crowd_sim", "set_extension", "comp"],
  "vfx_shot_count_estimate": {
    "low": 5,
    "mid": 8,
    "high": 12
  },
  "invisible_vfx_likelihood": "high",
  "cost_risk_score": 3,
  "schedule_risk_score": 2,
  "risk_reasons": [
    "Holographic displays require CG screen inserts with interactive lighting on actors",
    "Hero holographic projection is a featured CG prop requiring animation",
    "Dozens of technicians may require crowd multiplication for wide shots",
    "Set extension to show full scale of control room beyond practical set"
  ],
  "suggested_capture": [
    "HDRI of control room set for hologram lighting integration",
    "Clean plates of set without crowd (for crowd multiplication)",
    "Interactive light reference for hologram glow on actors (use practical LED panel as stand-in)",
    "Screen tracking markers on any practical monitor props",
    "Multiple extra groupings for crowd tiling plates"
  ],
  "notes_for_producer": "The holographic displays are the main VFX cost driver. The hero signal visualization requires CG modeling and animation with interactive lighting on nearby actors. Budget for interactive LED panels on set to provide proper hologram glow on actors' faces. The 'dozens of technicians' language suggests crowd work: shoot 15-20 extras in sections for crowd tiling. Set extension needed to expand practical set to full control room scale.",
  "uncertainties": []
}
```

## Reasoning Notes

- **cost_risk_score: 3** — Holograms are well-understood VFX work; crowd tiling is routine
- **schedule_risk_score: 2** — No novel technology or creatures; standard pipeline work
- **crowd_sim_needed: true** — "Dozens of technicians" implies crowd multiplication needed
- **screen_insert** — Multiple monitor screens throughout the scene
- **cg_prop** — The hero holographic projection is a CG prop with animation
- **set_extension: true** — The control room needs to appear larger than the practical set
- **invisible_vfx_likelihood: high** — Nearly every shot will have screen display elements
- The schematic animation sequence is essentially a CG animation (screen insert + cg_prop)
