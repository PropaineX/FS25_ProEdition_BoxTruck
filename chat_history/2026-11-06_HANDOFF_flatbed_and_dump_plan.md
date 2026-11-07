# HANDOFF: Pro Edition Trucks (flatbed + dump) — plan as of 2026-11-06

Read this first if you are picking up this work. It records everything decided with the user (PropaineX) in the
session of 2026-11-06. Companion file: `2026-11-06_goat_milk_shed_clearance.md` (the investigation that led here).

## Ground rules from the user (apply to all of this)

- **Don't change any file while the user is only asking or discussing.** Wait for a clear go ("do it", "go",
  "start building"). Ruling out one option is not a yes for another.
- **Visual changes: show a mock-up / before-after first, wait for OK.** Never overwrite an earlier preview file;
  number new ones (v1, v2, ...). Open every picture in VS Code yourself (`code -r "<path>"`).
- **Don't zip or upload until the user says "zip it".** Then: zip to `FarmingSimulator2025\Testing_local\` AND the
  server's `/testing` over SFTP per `MOD PROJECTS\Library\_FS25ServerBrief\CLAUDE.md`.
- Use **American spelling** (curb, tire, color).
- Version numbers are ours to pick; bump before zipping, tell the user. Author name: PropaineX.
- GIANTS Editor: only scratch copies (`C:\Users\groov\GE_work\...`); shut it down when done. Ask before taking the
  screen; the user plays the game meanwhile (if you need the screen, minimize the game so he notices). Never close
  the game.
- After each task add what you learned to `MOD PROJECTS\Library\_FS25Knowledge\FS25_Universal_Knowledge.md`.
- The user plays as a **client on the dedicated server**; local `savegame1` is only a copy he downloaded.

## Current state of the mod (FS25_BoxTruck_ProEdition)

- Source: `MOD PROJECTS\FS25_BoxTruck_ProEdition\`. Version in modDesc: **1.3.2.0** (source only, NOT zipped,
  NOT tested in game).
- Only change in 1.3.2.0: **own shop section.** In modDesc.xml `<storeCategories>`:
  - `<storeType name="PROPAINEX" title="PropaineX Pro Edition" insertAfter="DRIVABLES"/>` (section heading)
  - `<storeCategory type="PROPAINEX" name="PROEDITIONTRUCKS" title="Pro Edition Trucks" image="store_boxTruck.dds"/>` (tile)
  - boxTruck.xml `<storeData><category>` changed from `trucks` to `PROEDITIONTRUCKS`.
  - Copied from Tony_7829's TFS25_SM72_SM82_Transport_Trailer.zip, which shows correctly in the user's shop.
  - Mock-up approved ("fine for now"): `previews\shop_section_v3.png`.
- **The box truck itself stays as it is.** Decided: no lowering of the box, no spoiler/XL collision changes. "That's
  not the truck you drive to pick up milk pallets." (The lowered-roof study is kept only as a record.)

## The plan: three trucks, one shop tile

Shop: section "PropaineX Pro Edition" > tile "Pro Edition Trucks" holds exactly three entries, each its own store
item in the same mod (NOT one truck with a body option — that would mix specializations and be fragile):

1. Box Truck Pro Edition (exists)
2. **Flatbed Truck Pro Edition — BUILD THIS FIRST (user said go, then asked for these notes)**
3. Dump Truck Pro Edition — later (details not decided)

Names "PropaineX Pro Edition", "Pro Edition Trucks", "Flatbed Truck Pro Edition", "Dump Truck Pro Edition" are
Claude's suggestions; user accepted the section names; truck names not explicitly confirmed.

## Flatbed: everything decided

Base: same Volvo FH16 8x4 Tag cab, chassis, engines, color and cab options as the Box Truck (the box truck's i3d
has the game's FH16 cab/chassis already; its body was built in Blender by `source/build_body.py`, exported with
`source/export_body.py`, vehicle xml made by `source/make_vehicle_xml.py`).

Sizes (approved: "whatever sizes the boards are in these mockups, that looks good"). Truck root coordinates; the
ground is ~0.30 below the root:
- Deck underside 1.50, deck top **1.62** (1.32 m above ground). Tire tops are at 1.40.
- Deck from z **1.50** (front, behind the headboard) to **-5.35** (rear): 6.85 m long, 2.55 m wide.
- **Headboard** at the front of the deck, top **3.738** = level with the Sleeper cab roof (3.44 m above ground).
- Side option chosen in the shop (a configuration):
  - **Side boards**: 3 aluminum drop-side boards per side, **0.60 m** tall, posts between them (0.09 m).
  - **Stake posts**: **6** steel stakes per side, **1.20 m** tall, in pockets/slide shoes on a rail at the deck edge.
- Rear light bar + underrun like the box truck.

Animations, key **X** (both sides always move together):
- **Stake version:** stakes numbered 1-6 from the rear (1) to the front (6, behind the headboard). X slides **1, 3
  and 5 forward** along the rail to sit right behind 2, 4 and 6 (Fliegl timber-trailer style). X again slides them
  back. Closed z: -5.10, -3.83, -2.56, -1.29, -0.02, 1.25. Open: 1 -> -3.97, 3 -> -1.43, 5 -> 1.11 (0.14 m behind its
  partner). Gaps when open: ~1.3 m at the rear, ~2.3 m between pairs.
- **Side board version:** X **folds all boards down** (outward, hinged on the deck edge; they hang outside the
  wheels). X again raises them. The posts between the boards **stay up** (user: "looks good" to the mock-up).

Aero Parts (existing FH16 `design2Configurations`, "Aero Parts"):
- **Default = None** (no roof spoiler). User: "lose the spoiler, I don't want it default on this."
- Keep the other choices available; the user specifically wants the **low side skirts** (= `sidePlanks_fh16`,
  shop choice "Design 1": skirts only, no spoiler) available as an option.
- Reference: None = nothing; Design 1 = side skirts; Design 2 = cab extenders + roof spoiler; Yes = all.

Loading:
- **Shift+R** (= UNIVERSALAUTOLOAD_TOGGLE_LOADING, Universal Autoload). Needs tension belts (UAL takes any vehicle
  with >= 2 belts).
- Keep Universal Autoload's own shop button exactly as UAL provides it ("A — AUTOLOAD" in the bottom bar of the
  shop config screen; the user showed a screenshot). Untouched = plain Shift+R loading.
- So **do NOT force the UAL config** the way `scripts/BoxTruckBody.lua` `onPreLoad` does for the box truck (it writes
  `UniversalAutoload.VEHICLE_CONFIGURATIONS[name] = {ALL = ...}` on every load, overriding the shop menu). At most
  supply a default loading area when UAL has nothing saved for the flatbed.
- Loading area: floor top 1.62, 2.45 wide, ~6.85 long. Goat milk pallets: 10 per layer, 2 layers.

Why it matters (the goat milk shed): two layers of goat milk pallets on the flatbed reach 3.38 m (can lids),
headboard 3.44 m, the shed's roof underside where the truck passes is 3.66-3.75 m -> clears. The roof spoiler
(3.83 m) would not, hence Aero Parts default None.

Mock-ups (all in `previews\`):
- `flatbed_v1_mockup.png` — both side options, loaded view, rear views.
- `flatbed_v3_sliding_stakes.png` — numbered stakes, closed / after X / loaded. (v2 had overlapping numbers.)
- `flatbed_v4_folding_boards.png` — boards up / folded down / rear view of the fold.
- Scripts that drew them: Claude's scratchpad `flatmock\flat.py`, `stakes.py`, `boards.py` (temporary folder; the
  numbers above are what matter).

Version: adding the flatbed is a new feature -> mod version **1.4.0.0** when it is built.

## Suggested build approach (not started)

1. New store item `flatbedTruck.xml` + `flatbedTruck.i3d` in the same mod, category `PROEDITIONTRUCKS`.
2. Start from the box truck's i3d/xml (cab, chassis, 8x4 Tag wheels, configurations) and replace the box body with
   a new flatbed body built in Blender (headless `blender.exe -b`, like build_body.py), exported with the GIANTS
   exporter (installed in Blender 5.2.2).
3. Side type as a configuration (objectChange visibility for boards vs stakes, plus their collisions).
4. Two animations (stakes slide / boards fold); a small specialization binds **X** to whichever one the chosen
   configuration has (box truck uses X for rear doors; the flatbed has no doors). Sync in multiplayer and save state.
5. Tension belts over the deck; UAL left at defaults (see above).
6. Aero Parts default -> None.
7. Show the user a GIANTS Editor preview before calling it done; test in game; then wait for "zip it".

## Dump truck (later, NOT decided)

Still open questions for the user: what it hauls (grain, gravel/lime, silage, manure...), rear tip only or 3-way,
size/volume. Same cab/chassis, same shop tile.

## Other open/side items

- Globetrotter XL roof collision question: moot now (box stays as is).
- The game log shows repeated `FS25_FarmInventory\scripts\FarmInventory.lua:538: attempt to index nil with
  'sptOwner'` (our own mod); not looked at.
- Universal Autoload has a density-based stacking limit (option "disableHeightLimit", default false) that by its
  code should stop full milk pallets stacking; the user says they do stack. Verify on the first flatbed test.

## Where the supporting files are

All copied into this mod folder (2026-11-06): `source/2026-11-06_planning/` (mock-up scripts, GIANTS Editor
measuring Lua, AutoDrive route simulation; see its README.md). Route picture also in
`previews/goatmilk_turn_v1_route.png`. The original scratch locations were temporary.
