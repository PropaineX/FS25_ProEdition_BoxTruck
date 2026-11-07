# Flatbed runtime ? source build 1.4.0.0

The flatbed is integrated into the mod, not just a preview fragment. Root
flatbedTruck.xml is registered as a second store item. Its separate flatbedPro
vehicle type inherits the native tractor, adds tensionBelts/Foldable and
FlatbedBody, and never runs BoxTruckBody.

## Current behavior

- Native folding configuration is the shop's Body sides selector: Side walls or Sliding stakes.
- X: outward folding boards (1.5 seconds) or alternating stake slides (0.7 seconds).
- Left Alt + T: independent tailgate (1.2 seconds), on the side-wall configuration only.
- Nine belt pairs and activation trigger; 29 collision shapes with configuration-specific side collisions.
- Native running/brake/indicator/reverse-light controls, with 13 per-vertex lens colors. Existing rear real-light helpers retained; original rear donor lens meshes hidden.
- Full-width striped tube uses the native vehicleShader reflector variation. Metal panels use brushed silver details.
- UAL is optional. FlatbedBody:onPreLoad supplies defaults only if the vehicle has no existing configuration group, preserving shop/user choices. Area width2.38,length6.70,height2.20,offset0/1.625/-1.925. Width fits between stakes. No curtain behavior or global pallet-spacing override.
- Tailgate server receives target requests, uses its own current phase, broadcasts phase/target; joining clients preserve direction. Saves retain the target endpoint. Native Foldable handles the side state.

## Build pipeline

1. build_body.py in background Blender, starting from the saved approved tailgate/stripe proposal. Exports build/flatbedBody.i3d and shapes, pivots, belts, collisions, native materials and lamp vertex colors.
2. prepare_merge.py makes a PRIVATE scratch copy of the original Box Truck I3D/shapes. Never save a scene referencing production shapes.
3. GIANTS Editor opens that scratch file. merge_body.lua removes only the old box body and imports the new one, preserving the native cab/chassis and rear real lights, and relocating the rear plate mount. merge_body.ps1 drives the save. Reuse ONE Editor instance; preserve work and close it when done.
4. python -I source/flatbed_runtime/build_vehicle.py writes root flatbedTruck.i3d, .shapes and .xml. Rebuilds mappings against the actual saved hierarchy, normalizes belt transforms, applies brushed metal materials and writes configs/animations/lighting.
4b. python -I source/flatbed_runtime/add_tire_options.py adds the 13 off-road single-tire shop options (flatbed only; re-runnable). Must run again after every build_vehicle.py.
5. python -I source/flatbed_runtime/validate_source.py checks runtime references and membership WITHOUT making a ZIP.
6. python -I source/flatbed_runtime/test_flatbed_runtime.py executes actual Lua state/event logic and installed native Foldable reversal logic with .local/lua-test-runtime (unsandboxed read access may be needed).
7. python -I source/test_gathered_runtime.py runs the existing Box Truck regressions.

prepare_editor_check.py creates a private runtime-check copy and an XML-driven
renderer check; check_editor*.ps1 captures poses. These checks are not a shop
purchase or live gameplay input test. build/source_validation.json records all
26 runtime members and unchanged original-file hashes. package_testing.py now
includes the flatbed WHEN the user separately requests packaging. No package
was made in this task.

## Fliegl provenance

The user explicitly requested copying the installed Fliegl Timber Runner's
animation logic. stake_folding.xml adapts native Foldable configuration and
additionalForks timing/sound setup from
mods/FS25_FlieglTimberRunnerAutoload.zip:timberRunner15.xml. The 20 m version uses
the same structure; the 12 m version has no sliding-stake block. Only XML control
and timing structure is reused, with our own nodes/travel. No donor Lua/autoload
code or geometry is copied. The fragment and body-local node contract remain as
provenance/build inputs; final whole-truck mappings are in flatbedTruck.xml.

## Validation and limits

Source validation, all 363 mappings, all 13 lamp vertex-color channels, native
Foldable direction changes, tailgate events/authority/join/save/config gating,
optional UAL/default preservation and original Box Truck regressions pass.
GIANTS Editor loads the actual saved asset without reported errors. The belt
anchors use the established convention: start+X, rotationY-90, end localZ+2.46.

Untested in game: shop purchase/config changes, keys while driving, real
physics/collisions, tension belts, UAL loading/stacking/shop UI, nighttime
lighting/reflectors, and a real multiplayer/save session. No in-game test is
claimed. No ZIP, install, upload, Git commit or push was performed.
