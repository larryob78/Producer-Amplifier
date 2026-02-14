# VFX Category Taxonomy

Reference taxonomy for classifying visual effects work in film production breakdowns.

---

## comp
**Compositing / Layering**
Combining multiple image layers into a final frame. Includes green/blue screen keying, plate stitching, multi-pass CG integration, lens distortion matching, and grain/noise matching. Nearly every VFX shot involves compositing as a final step.

Typical triggers: green screen, blue screen, composite, layer, keying, plate.

---

## roto
**Rotoscoping**
Hand-tracing or semi-automated masking of elements frame-by-frame for isolation, holdouts, or garbage mattes. Required when clean edges aren't available from keying. Labor-intensive and scales linearly with shot count.

Typical triggers: rotoscope, matte, isolation, holdout, edge, mask.

---

## paint_cleanup
**Paint & Cleanup**
Removing unwanted elements: wires, rigs, safety equipment, tracking markers, crew reflections, boom mics, camera rigs. Also covers skin retouching, logo removal, and set imperfection fixes.

Typical triggers: wire removal, rig removal, cleanup, paint out, marker removal, erase.

---

## wire_removal
**Wire / Rig Removal**
Specialized subset of paint cleanup focused on removing physical support wires, flying rigs, stunt harnesses, and mechanical rigs from frame. Requires clean plate photography and careful tracking.

Typical triggers: wire, harness, flying rig, cable, support rig.

---

## cg_creature
**CG Creature / Character**
Fully computer-generated creatures or characters. Includes modeling, rigging, animation, fur/hair simulation, texturing, lighting, and rendering. Among the most expensive VFX categories. Requires reference photography, maquettes, or concept art.

Typical triggers: creature, monster, dragon, alien, dinosaur, beast, animal (CG), digital character.

---

## cg_vehicle
**CG Vehicle**
Computer-generated vehicles including cars, ships, aircraft, spacecraft, trains. May involve rigid-body dynamics, destruction simulation, and environment interaction. Often combined with practical elements.

Typical triggers: spaceship, spacecraft, helicopter (CG), airplane (CG), tank, submarine, vehicle (CG).

---

## cg_prop
**CG Prop / Object**
Computer-generated props or objects that are impractical to build physically. Includes weapons, magical objects, technology, food, or any hero prop requiring impossible physics or transformations.

Typical triggers: hologram, holographic display, magical object, weapon (CG), artifact, device.

---

## cg_environment
**CG Environment**
Fully or partially computer-generated environments. Includes alien worlds, fantasy landscapes, destroyed cities, historical recreations, or any location that cannot be physically built or accessed.

Typical triggers: alien world, fantasy landscape, destroyed city, futuristic city, digital environment, CG world.

---

## digi_double
**Digital Double**
A CG replica of a real actor used for dangerous stunts, impossible camera moves, crowd multiplication, or de-aging. Requires extensive reference scanning (photogrammetry, LiDAR) and careful likeness matching.

Typical triggers: digital double, stunt double (CG), face scan, body scan, digi-double, CG actor.

---

## face_replacement
**Face Replacement / De-aging**
Replacing or modifying an actor's face in post-production. Includes de-aging, aging, face swaps between stunt doubles and actors, and digital makeup. Requires high-quality facial capture data.

Typical triggers: de-aging, aging, face swap, face replacement, digital makeup, rejuvenation.

---

## set_extension
**Set Extension**
Extending a physical set beyond what was built. Tops of buildings, distant architecture, additional floors, expanded rooms. Usually 2.5D or full 3D extensions composited onto live-action plates.

Typical triggers: set extension, extend, beyond the set, additional floors, building top, rooftop extension.

---

## matte_painting
**Matte Painting**
Digital paintings used as backgrounds or environment elements. Modern matte paintings are typically 2.5D (projected onto simple geometry) with subtle animation (clouds, water, atmospheric haze).

Typical triggers: matte painting, background painting, vista, panorama, establishing vista, painted sky.

---

## sky_replacement
**Sky Replacement**
Replacing the sky in exterior shots for weather continuity, time-of-day matching, or dramatic effect. Relatively straightforward but requires consistent tracking and edge treatment across a sequence.

Typical triggers: sky replacement, sky swap, cloud replacement, sunset sky, overcast to clear.

---

## fx_water
**Water FX / Fluid Simulation**
Simulated water effects including oceans, rivers, rain interaction, splashes, flooding, underwater caustics, and liquid dynamics. Computationally expensive. Practical water elements often supplemented with CG.

Typical triggers: ocean, flood, underwater, splash, wave, river, rain, tsunami, water, dive, swim, drown.

---

## fx_fire
**Fire FX / Pyro Simulation**
Simulated or enhanced fire effects. Includes campfires, building fires, flamethrowers, magical fire, engine exhaust. Often a mix of practical fire elements and CG augmentation.

Typical triggers: fire, flame, burn, inferno, blaze, ignite, torch, engulf.

---

## fx_smoke_dust
**Smoke, Dust & Atmospheric FX**
Volumetric smoke, dust clouds, fog, haze, and atmospheric effects. Used for explosions aftermath, desert storms, magical mist, industrial environments. Can be practical or CG.

Typical triggers: smoke, dust, fog, haze, mist, ash, soot, sandstorm, debris cloud.

---

## fx_destruction
**Destruction FX**
Large-scale destruction simulation: collapsing buildings, shattering glass, crumbling walls, bridge collapse, dam breaks. Requires rigid-body dynamics, fracture simulation, and debris systems.

Typical triggers: collapse, crumble, shatter, demolish, destroy, rubble, wreckage, disintegrate.

---

## fx_weather
**Weather FX**
Simulated weather phenomena: snow, rain, lightning, tornadoes, hurricanes, storms. Includes both atmospheric and ground-interaction elements.

Typical triggers: storm, lightning, tornado, hurricane, blizzard, snow, hail, thunder, weather.

---

## fx_explosion
**Explosion FX**
Explosions ranging from small squibs to massive detonations. Combines fireball, shockwave, debris, smoke, and destruction elements. Often practical plates enhanced with CG elements.

Typical triggers: explosion, explode, detonate, blast, bomb, blow up, eruption, shockwave.

---

## matchmove
**Matchmove / Camera Tracking**
Reconstructing the real camera's motion and lens properties in 3D space so CG elements can be precisely integrated. Required for nearly all CG-heavy shots. Includes object tracking and body tracking.

Typical triggers: camera track, matchmove, motion track, 3D track, solve camera.

---

## camera_projection
**Camera Projection / Projection Mapping**
Projecting 2D images or footage onto 3D geometry to create parallax and dimensional depth from flat sources. Used for set extensions, environment creation, and 2.5D matte paintings.

Typical triggers: projection, camera projection, projected texture, 2.5D, parallax.

---

## crowd_sim
**Crowd Simulation**
Generating large crowds of digital characters with autonomous behavior. Includes stadiums, armies, city pedestrians, and background populations. Requires agent-based simulation systems.

Typical triggers: hundreds, thousands, army, crowd, legion, masses, horde, battalion, stadium, arena.

---

## zero_g
**Zero Gravity / Microgravity**
Simulating weightless environments. Requires wire rigs (removed in post), CG hair/clothing simulation, floating debris/liquid simulation, and careful compositing of practical and digital elements.

Typical triggers: zero gravity, weightless, floating, microgravity, space station interior, zero-g.

---

## screen_insert
**Screen Insert / Monitor Replacement**
Replacing or adding content to screens, monitors, phones, tablets, and displays within the scene. Requires tracking, perspective matching, and screen-light interaction on actors/environment.

Typical triggers: computer screen, phone screen, monitor, display, holographic display, television, tablet.

---

## day_for_night
**Day-for-Night / Time-of-Day Conversion**
Converting footage shot during one time of day to appear as another. Most commonly day-for-night but also includes night-for-day, dawn-for-dusk. Requires color grading, sky replacement, and lighting adjustments.

Typical triggers: day for night, night for day, time conversion, moonlight look.

---

## beauty_work
**Beauty Work / Digital Cosmetics**
Subtle digital enhancement of actors: skin smoothing, blemish removal, sweat/tear addition, bruise/wound enhancement, tattoo cover-up. Low complexity per shot but high shot count.

Typical triggers: beauty work, skin cleanup, digital cosmetics, blemish, scar, bruise, wound.

---

## other
**Other / Uncategorized**
VFX work that doesn't fit neatly into the above categories. When using this category, always provide explanation in the `uncertainties` field. Examples: time-lapse, speed ramping, lens flares, title integration, unique one-off effects.
