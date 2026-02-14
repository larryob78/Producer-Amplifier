# Gold Example: Rebel Base Command Center

## Input Scene

```
INT. REBEL BASE - COMMAND CENTER - NIGHT

Hundreds of REBEL SOLDIERS study holographic displays showing the Death Star
approach. The room buzzes with tension. TACTICAL OFFICERS move between
stations. A massive HOLOGRAPHIC PROJECTION of the Death Star rotates slowly
at the center of the room, red indicators pulsing on its surface.

LEIA
The Empire is coming. We must prepare.

GENERAL DODONNA
The target area is only two meters wide. It's a small thermal exhaust port
right below the main port.

A detailed cross-section of the Death Star appears on the holographic display,
zooming into the exhaust port. Pilots lean forward, studying the approach vector.

WEDGE
That's impossible, even for a computer.
```

## Expected Breakdown

```json
{
  "scene_id": 3,
  "slugline": "INT. REBEL BASE - COMMAND CENTER - NIGHT",
  "int_ext": "int",
  "day_night": "night",
  "page_count_eighths": 6,
  "location_type": "stage",
  "characters": ["LEIA", "GENERAL DODONNA", "WEDGE"],
  "scene_summary": "Rebel commanders brief pilots on Death Star attack plan using holographic displays. Hundreds of soldiers observe the tactical presentation.",
  "vfx_triggers": [
    "hundreds of soldiers (crowd)",
    "holographic displays",
    "holographic projection of Death Star",
    "cross-section holographic animation"
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
    "Hero holographic Death Star projection is a featured CG prop requiring animation",
    "Hundreds of soldiers may require crowd multiplication/simulation for wide shots",
    "Set extension to show full scale of command center beyond practical set"
  ],
  "suggested_capture": [
    "HDRI of command center set for hologram lighting integration",
    "Clean plates of set without crowd (for crowd multiplication)",
    "Interactive light reference for hologram glow on actors (use practical LED panel as stand-in)",
    "Screen tracking markers on any practical monitor props",
    "Multiple extra groupings for crowd tiling plates"
  ],
  "notes_for_producer": "The holographic displays are the main VFX cost driver. The hero Death Star hologram requires CG modeling and animation with interactive lighting on nearby actors. Budget for interactive LED panels on set to provide proper hologram glow on actors' faces. The 'hundreds of soldiers' language suggests crowd work: shoot 40-60 extras in sections for crowd tiling, or use CG crowd for wide establishing shots. Set extension needed to expand practical set to command center scale.",
  "uncertainties": []
}
```

## Reasoning Notes

- **cost_risk_score: 3** — Holograms are well-understood VFX work; crowd tiling is routine
- **schedule_risk_score: 2** — No novel technology or creatures; standard pipeline work
- **crowd_sim_needed: true** — "Hundreds of rebel soldiers" implies crowd multiplication needed
- **screen_insert** — Multiple holographic displays throughout the scene
- **cg_prop** — The hero Death Star holographic projection is a CG prop with animation
- **set_extension: true** — The command center needs to appear larger than the practical set
- **invisible_vfx_likelihood: high** — Nearly every shot will have holographic display elements
- The cross-section animation sequence is essentially a CG animation (screen insert + cg_prop)
