# Box Truck vs the goat milk shed (2026-11-06)

Status: **investigation and mock-ups only. Nothing in the mod has been changed.** Box Truck is still 1.3.1.0.
The user is going to explore another option; everything below is the record of this one.

## The problem

- On the server game (map NF Marsch 4fach oG, AutoDrive 3.0.1.4-od.62), the Box Truck drives the AutoDrive route
  to **"Goat Milk #1 PICKUP"**, clips the milk pallet shed next to the goat barn, and gets stuck.
- The MAN milk truck (mods\FS25_Man_Milk_Pack.zip, LS Sakura) makes the same turn without trouble.
- The route is staying as it is (the user's decision: other vehicles use it and work fine).

## What causes it (confirmed)

- **It's a height problem, not a steering problem.** User screenshots showed the top of the cab/box catching the
  shed's roof overhang; side by side in game the MAN is clearly lower.
- Coming out of the U-turn the box truck sits slightly crooked (rear wheels on the AutoDrive line, nose about 1 m
  toward the shed), so its left side runs **0.65-0.95 m under the shed roof's edge**.
- The shed roof slopes down toward the back, so the further under the edge, the lower the roof.
- In the simulation every truck (the MAN too) gets its front-left corner to the shed's north corner; the MAN only
  gets through because it is lower.

## Ruled out along the way

- **Turning radius:** box truck about 13 m across (tightest of the trucks compared), MAN milk truck about 16.9 m,
  FS22 TGS 18.500 about 19 m, FS22 TGX 26.640 about 16.8 m. The box truck turns tighter than the MAN.
- **AutoDrive aim distance (`<ai><steeringNode node="wheelsBack01"/>`):** first idea, but AutoDrive's
  "waypoint reached" distance (half the truck length, 4.94 m) already makes it aim 5 m+ ahead. The change moves the
  front only 0.1-0.2 m. **Not a fix; don't use it.**
- **Tail swing:** the user saw the front end hit, not the back.

## The route (savegame1 copy of the server save, AutoDrive_config.xml)

- Marker "Goat Milk #1 PICKUP" = id 33981 at x 979.54, z -1089.43.
- Approach: straight north on x 965.5, then a right-hand U-turn of about 7 m radius (waypoints 35699-35712),
  then south on x 979.7 past the shed to the marker.
- The route line runs only about 1.9 m from the shed roof's edge.

## Measurements (GIANTS Editor 10, real meshes, scratch copies in C:\Users\groov\GE_work\goatshed\)

All heights in meters above the ground. The road beside the shed is inside the barn's terrain-leveling area, so it's
level with the shed floor. Possible error about 5 cm (how high the truck sits on its tires).

| Thing | Height |
|---|---|
| Shed roof underside at its outer edge | 3.95 |
| Shed roof underside where the truck's side passes (0.65-0.95 m in) | 3.75 to 3.66 |
| Shed roof slope | drops 0.30 m per meter going in |
| Box Truck box top (now) | 3.93 |
| Sleeper roof spoiler (aero part) | 3.83 |
| Sleeper cab roof without the spoiler | 3.44 |
| Globetrotter XL raised roof (its collision) | 3.25 to 3.93 |
| Goat milk pallet, collision (what Universal Autoload uses) | 0.975 tall |
| Goat milk pallet, can lids (looks only) | 1.08 tall |

Shed details: Fed Mods Pack sheepBarnBig3 (schafstall_big.i3d), node garageWoodRoof; roof over world x 981.04-987.01,
z -1102.81 to -1086.43; corner posts about 0.75 m in from the roof edge.

## Loading (Universal Autoload)

- The user loads with **Shift+R** = UNIVERSALAUTOLOAD_TOGGLE_LOADING (Universal Autoload).
- Box Truck UAL loading area: floor 1.75 (truck coordinates), 2.45 x 6.60 m, **height 2.37 m** (BoxTruckBody.lua,
  UAL_LOADING_AREA).
- Goat milk pallets: 10 per layer (2 across x 5 rows). Two layers need 1.96 m (0.975 + 0.005 spacing, twice).
- The user says the milk does stack two high today.
- Note: Universal Autoload has a weight-based stacking limit (option "limit stacking height by density", default on)
  that, by its code, shouldn't let full milk pallets stack. The user sees them stack, so something allows it.
  Check two layers still load on the first test of any lowered box.

## Options worked out

### Lower the box roof

| Lower the box by | Box top | Room under the shed roof | Top can lids vs roof bows | Room above the 2nd layer |
|---|---|---|---|---|
| **0.30 m** (user's pick) | 3.63 | 3-12 cm | 1 cm below, hidden | 11 cm |
| 0.35 m | 3.58 | 8-17 cm | 4 cm into the bows | 6 cm |
| 0.40 m (most that keeps 2 layers) | 3.53 | 13-22 cm | 9 cm into the bows | 1 cm |
| ~0.49 m (down to the Sleeper cab roof) | 3.44 | more | n/a | only 1 layer (10 pallets) |

- The user chose **0.30 m** so the milk cans don't poke through the roof.
- 0.30 m clearance under the shed is tight (3-12 cm, with about 5 cm possible error).
- Lowering the box means rebuilding the box: curtains, posts, doors, rear banner, gathered curtains and the UAL
  loading height all get shorter. In build_body.py the box top is ROOF_Y (4.23 now, would be 3.93). Version would
  become 1.4.0.0.
- Any load taller than about 2 m would no longer fit.

### The Sleeper spoiler (also too high, 3.83)

- Option A: keep it on the truck but remove its collision (colPartAeroSleeper). It would slide through the shed roof
  edge. The collision is switched on in three places in boxTruck.xml: the Sleeper roof option (designConfiguration 2)
  and the Aero Parts choices Design 2 and Yes (design2Configurations).
- Option B: no mod change. The shop already has an **Aero Parts** option (None / Design 1 / Design 2 / Yes, default
  Yes). Picking **None** or **Design 1** hides the spoiler and its collision is already off.

### Globetrotter XL roof option

- There is one box for both roof options. The box was built level with the XL roof, so a lowered box leaves an XL cab
  sticking up above it, and XL trucks would still hit this shed.
- The user asked about removing the XL collision (colPartGlobetrotterXL). Possible, but it is the whole raised roof
  (3.25-3.93 m): the top half meter of an XL cab would pass through everything, and you'd see it sink 20-30 cm into
  the shed roof. **Not decided.**

## Open decisions (nothing done)

1. Lower the box: 0.30 m was the pick, waiting for a go-ahead.
2. Spoiler: remove its collision (option A) or use Aero Parts None / Design 1 (option B).
3. XL roof: leave it, or remove its collision.
4. The user is exploring another option first.

## Files from this investigation

- Mock-ups (box truck previews folder): lowered_roof_v1_before_after.png, v2, v3 (0.40 m),
  **lowered_roof_v4_030_before_after.png (0.30 m, current)**.
- Route picture: scratchpad turnsim\goatmilk_turn_v1.png (temporary folder).
- GIANTS Editor measuring scripts: C:\Users\groov\GE_work\goatshed\measure_v1.lua, measure_v2.lua.
- Knowledge index: FS25_Universal_Knowledge.md, entries dated 2026-11-06 (Claude).

## Also seen (not looked at)

- The game log fills with FS25_FarmInventory errors: FarmInventory.lua:538 "attempt to index nil with 'sptOwner'".

## DECISION (user, 2026-11-06)

**Leave the box alone.** The box truck's box is not lowered, the spoiler and XL collisions are not touched. The box
truck simply isn't the truck for picking up milk pallets at that shed. Everything above stays as a record only.
Milk pallets will be handled by the planned flatbed truck instead (same mod, own shop section "PropaineX Pro Edition"
/ tile "Pro Edition Trucks", added in 1.3.2.0).
