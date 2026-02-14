# Hidden Cost & Schedule Risk Rules

Rules for identifying cost drivers, schedule risks, and commonly overlooked budget items in VFX-heavy film production. These rules help a producer anticipate problems before they become expensive.

---

## 1. CG Character / Creature Costs

**Rule:** Any scene featuring a CG creature or digital character is automatically a high-cost scene (cost_risk_score >= 4). A single hero CG character typically requires 6-12 months of development before shot work begins.

**Hidden costs:**
- Creature development (design iterations, maquette approval, texture painting, rigging, grooming) is often underestimated by 30-50%
- Each unique creature requires its own asset pipeline; reuse across creatures is limited
- Fur, hair, and feather simulation adds 2-3x render time and requires specialized artists
- Creature lighting must match per-shot, requiring per-shot lighting setups
- Interaction with practical elements (dust kicked up, ground deformation, shadow casting) adds compositing complexity

**Schedule risk:** Creature approval cycles with the director often cause the longest delays in a VFX pipeline. Flag `schedule_risk_score >= 4` for any new creature.

---

## 2. Water and Fluid Simulation

**Rule:** Large-scale water (oceans, floods, tsunamis) is among the most computationally expensive VFX work. Simulation times can exceed 48 hours per frame for hero water shots.

**Hidden costs:**
- Water simulation rarely works on the first iteration; expect 5-15 simulation passes per shot
- Interaction between water and characters/objects requires coupled simulation (much slower)
- Underwater shots require caustic lighting simulation, particulate matter, and depth-based color grading
- Practical water plates often need CG augmentation anyway (scale, timing, splash patterns)
- Wet surfaces on CG characters require separate shader work

**Schedule risk:** Water sequences should have the longest lead time after creature work. Flag `schedule_risk_score >= 4` for hero water sequences.

---

## 3. Destruction Sequences

**Rule:** Building collapses, bridge destructions, and large-scale demolition sequences require extensive simulation R&D. Each destruction event is essentially a custom engineering problem.

**Hidden costs:**
- Fracture patterns must be art-directed (physically accurate destruction often looks wrong on camera)
- Dust, smoke, and debris clouds require separate volumetric simulations layered on top
- Destruction of recognizable structures requires high-fidelity CG models of the intact building first
- Secondary destruction effects (flying debris hitting other objects, chain reactions) multiply complexity
- Post-destruction environments (rubble, dust settling) need to persist across subsequent scenes

**Schedule risk:** Flag `schedule_risk_score >= 4`. Destruction R&D typically needs 2-3 months before production shots can begin.

---

## 4. The "Simple" Wire Removal Trap

**Rule:** Wire removal and rig removal are individually inexpensive (~$500-2,000 per shot) but accumulate rapidly in action films. A single stunt sequence can generate 50-100 wire removal shots.

**Hidden costs:**
- Total wire removal budget on action films often reaches $200K-500K
- Complex wire rigs against detailed backgrounds (cityscapes, forests) take 5-10x longer than clean backgrounds
- Multiple wire passes per stunt (flying, landing, mid-air turns) multiply shot count
- Wire shadows on actors and environment require separate paint work
- Interactive wire deformation of costumes needs careful retouching

**Producer action:** When a scene involves stunt rigs, flag `production_flags.wire_rig_removal = true` and estimate 3-8 wire removal shots per stunt setup.

---

## 5. Green Screen / Blue Screen Volume

**Rule:** Every green screen shot requires keying, edge refinement, and background replacement at minimum. The cost is not just the VFX shot; it's the on-set infrastructure.

**Hidden costs:**
- Poorly lit green screens (uneven lighting, spill, wrinkles) can double compositing time
- Green screen spill on costumes and skin requires frame-by-frame correction
- Interactive lighting (the green screen doesn't emit the same light as the intended environment) needs relighting
- Hair and transparent/translucent materials (glass, smoke, liquids) through green screen keying are extremely difficult
- Tracking markers on green screen floors add paint/cleanup work

**Producer action:** Flag `production_flags.green_blue_screen = true`. Budget 20-40% more compositing time than initial estimates.

---

## 6. Crowd Multiplication and Simulation

**Rule:** Crowds of 50+ people that cannot be practically assembled require either crowd simulation or crowd tiling (photographing small groups and compositing them).

**Hidden costs:**
- Crowd tiling requires shooting plates of extras in multiple positions with matched lighting
- CG crowd agents need clothing variation, behavioral variation, and LOD (level of detail) systems
- Stadium/arena crowds require 10,000+ agents with individual animation cycles
- Crowd interaction with hero action (reacting to explosions, fleeing) requires choreographed simulation
- Period-accurate crowds (historical films) need custom costume and grooming per agent type

**Schedule risk:** Crowd simulation setup takes 4-8 weeks before shot production. Flag early.

---

## 7. The Digital Double Iceberg

**Rule:** A full digital double (CG replacement of a real actor) costs $200K-1M+ to develop and is one of the most scrutinized VFX deliveries because audiences instantly detect uncanny valley issues.

**Hidden costs:**
- Facial capture sessions (FACS poses, expressions, phonemes) require actor availability
- LiDAR and photogrammetry scanning sessions take a full day per actor
- Skin shader development (subsurface scattering, pore detail, peach fuzz) takes 4-8 weeks
- Each use of the digital double requires per-shot facial animation and lighting
- Audience scrutiny is highest on faces; rework rates are 40-60% higher than other CG work

**Producer action:** If any scene requires a digital double, flag `production_flags.digi_double_needed = true`. Budget at minimum $300K for development plus $15K-50K per hero shot.

---

## 8. Continuity VFX Across Sequences

**Rule:** When VFX elements appear across multiple scenes (a recurring CG environment, a persistent injury, a damaged building), continuity management becomes a hidden cost multiplier.

**Hidden costs:**
- A CG environment seen from 10 angles requires 10x the detail of a single-angle matte painting
- Progressive destruction (building getting more damaged across scenes) requires multiple asset versions
- Weather continuity (overcast establishing, sunny close-up) requires per-shot sky work
- Time-of-day continuity in outdoor VFX sequences requires matched lighting across shots

**Producer action:** Identify VFX sequences early and budget sequence supervision time (typically 1 VFX supervisor per 50-80 VFX shots).

---

## 9. The "Invisible VFX" Budget

**Rule:** Films that appear to have "no VFX" often have 500-1,500 invisible VFX shots (sky replacement, set extension, wire removal, screen inserts, beauty work). These are easy to overlook in breakdown.

**Hidden costs:**
- Period films: removing modern elements (cars, signage, power lines, contrails) from every exterior
- Monitor/screen inserts on 50+ shots across a film
- Window replacements (CG views outside windows to avoid location restrictions)
- Beauty/cleanup work on principal cast across hundreds of shots
- Environmental fixes (construction cranes in background, unwanted signage)

**Producer action:** For any film, assume a baseline of 200-500 invisible VFX shots beyond the hero VFX. Budget $1,000-3,000 per invisible shot.

---

## 10. Scene Complexity Multipliers

**Rule:** Certain scene characteristics multiply the base VFX cost regardless of the specific effect:

| Multiplier | Effect on Cost |
|---|---|
| Night exterior | 1.3-1.5x (harder to match lighting, more noise in plates) |
| Rain/wet surfaces | 1.4-1.6x (reflections, CG water interaction, continuity) |
| Moving camera (Steadicam/drone) | 1.3-1.5x (more complex matchmove, motion blur) |
| Crowd + hero VFX | 1.5-2.0x (interaction between systems) |
| Multiple CG characters in same shot | 1.5-2.5x per additional character |
| Underwater | 2.0-3.0x (lighting, caustics, particles, bubbles) |

---

## 11. On-Set Data Capture (Missed = Expensive)

**Rule:** Missing on-set data capture for VFX shots adds 20-50% to post-production costs. The cheapest insurance is thorough on-set data acquisition.

**Critical captures often missed:**
- HDRI lighting reference (chrome ball + grey ball per setup)
- LiDAR scan of set and key props
- Clean plates (empty set, same lighting, same lens)
- Camera metadata (lens, focal length, height, tilt, T-stop)
- Reference photography of costumes and props
- Witness cameras for complex stunts
- Tracking marker placement documentation

**Producer action:** Flag `production_flags.on_set_data_capture = true` for every scene with VFX. Budget a dedicated VFX data wrangler on shoot days with VFX.

---

## 12. The Previz / Postviz Gap

**Rule:** Sequences that require previs (pre-visualization) but don't get it typically overrun their VFX budget by 25-40%.

**Scenes needing previz:**
- Any sequence with 10+ VFX shots in continuous action
- All destruction sequences
- Complex stunt choreography with CG elements
- Virtual production / LED wall sequences
- Any scene where shot design affects set build decisions

**Hidden costs:**
- Postviz (temporary VFX in editorial) is often forgotten in the budget
- Techvis (technical previs for on-set camera/rig planning) is a separate cost from creative previs
- Previs revisions during director sessions can consume 30-50% of previs budget

---

## 13. Schedule Risk: The VFX Crunch

**Rule:** VFX work follows a predictable crunch pattern. The last 20% of shots consume 40% of the schedule because they are the most complex or were subject to the most creative revision.

**Red flags for schedule risk:**
- More than 500 VFX shots in total → Flag `schedule_risk_score >= 3`
- More than 100 hero VFX shots → Flag `schedule_risk_score >= 4`
- Any new creature/character → Flag `schedule_risk_score >= 4`
- Hero water or destruction sequence → Flag `schedule_risk_score >= 4`
- VFX work across more than 2 vendors → Flag `schedule_risk_score >= 3`
- Post-production less than 6 months with 500+ VFX shots → Flag `schedule_risk_score = 5`

---

## 14. Virtual Production Considerations

**Rule:** Virtual production (LED wall / ICVS) shifts costs from post to production but does not eliminate them. Many productions underestimate the remaining post-production VFX needed after VP shoots.

**Hidden costs:**
- LED wall content must be final or near-final before shoot day (requires earlier VFX spend)
- Moiré patterns, LED pixel visibility, and color fringing require post-production cleanup
- Reflective costumes/props pick up LED wall artifacts
- Extension of LED wall content beyond the visible wall still requires traditional VFX
- VP stage rental is $50K-150K/day; idle days due to content not being ready are expensive

**Producer action:** Flag `production_flags.virtual_production = true`. Budget 30-40% of traditional post VFX budget even with VP for cleanup and extensions.
