# Box Truck 1.3.0.0 — three randomized gathered curtains

Implemented the three approved layouts from `previews/gathered_distinct_v1/version_1..3/gathered_proposal.blend`, for both left and right curtains. Rules retained: tidy shallow rail folds, gradual fullness toward the hem, independently irregular bunching, 9/11/10 inch lower flare, exterior-only artwork.

Runtime assets: `gatheredCurtains.i3d` plus `gatheredCurtains.i3d.shapes`. Six side/version groups, each containing cloth, an opaque white inner liner, and separate exterior artwork for ProEdition, Krone, FSL and GIANTS. Plain configuration hides all artwork. Meshes are sampled from the approved studies; decal polygons are clipped from the actual cloth triangles to avoid intersections in deep folds. Total asset: 155,832 triangles across all six groups and all four artwork options; only the selected group/design renders. Binary conversion uses the installed official Blender exporter `util/i3dConverter.exe`. ASCII source validation copy and mesh manifest are in `previews/gathered_integration/`.

`scripts/BoxTruckBody.lua` loads the visual asset through the game's synchronous shared-I3D manager and attaches groups beneath the existing `curtainLeftOpen`/`curtainRightOpen` animation pivots. Original gathered meshes/rigid straps are hidden at load; original hierarchy, mapping indices, collisions, opening animations, boards, posts, doors and autoload logic remain intact.

An overwritten `playAnimation` chooses 1–3 on the server on each fresh opening, including reversing a closing curtain. Repeated positive calls during the same opening do not reroll. Closing retains the choice. Left/right selections are independent; repeats are allowed. A server-only variant event sends the choice to clients; both choices also stream to late joiners and persist in savegame attributes `gatheredLeft`/`gatheredRight`. Old saves default to shape 1. Shared asset request released on delete.

White interiors: added opaque white liners to each open variant to obscure outward fold returns viewed across the load bay. Both existing closed inner liners now use a separate white material (`boxTruckWhiteInnerLining`, white diffuse, default normal, white color scale). Original main I3D immediately before that material-only edit is backed up at `previews/gathered_integration/before/boxTruck.i3d`.

Validation:
- `source/test_gathered_runtime.py` runs the real Lua specialization in a project-local Lupa runtime with mocked engine/network bindings. Passed: all three choices, no mid-opening/closing rerolls, reopening while closing, independent sides, client cannot choose server state, serialized event roundtrip, late joining, save/restore, legacy saves, all five design configurations, release cleanup, triangle indices and white interior textures.
- `check_i3dmappings.py`: 347 mappings, zero broken.
- GIANTS Editor 10.0.14 loaded the final binary asset and attached it to the actual production truck in an unsaved preview. Inspected `previews/gathered_integration/engine_pro_edition.png`: clean exterior banner, opposite inner lining white. Editor minimized; production truck preview not saved. Earlier failed console commands in editor log are tooling/quoting attempts, not runtime Lua errors.
- No in-game animation/performance or live multiplayer session test performed.

Version is now 1.3.0.0. Packaging file list includes both new runtime files. No ZIP built, installed, copied or uploaded; no commit/push. Existing unrelated working-tree edits preserved.

Build: run Blender background with `source/build_gathered_runtime.py`; `source/set_white_inner_lining.py` is idempotent. Tests require project-local `.local/lua-test-runtime` Lupa (installed for this task, ignored by Git). Editor validation helper accepts `-WindowHandle`; always verify the intended actual desktop editor handle before using it.
