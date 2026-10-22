# Box Truck Pro Edition: session 2026-10-21 (Claude Code session 5970d74f-5da5-4e13-9652-6776d10cd758)

Full chat: `2026-10-21_session_5970d74f.jsonl` (copy of the Claude Code transcript). To reopen the chat itself:
VS Code Claude panel > past conversations, or in a terminal in this folder: `claude --resume 5970d74f-5da5-4e13-9652-6776d10cd758`.

## Decided
- New box truck for hauling pallets, model built from scratch in Blender (not the base-game International CV Series).
- Loading: BOTH autoload (own script, from scratch) and forklift loading with tension belts in the box.
- 2026-10-22: size and layout = a near copy of the FH16 Box Truck measurements (`..\reference_fh16BoxTruck.md`):
  8x4 with steering tag axle, wheelbase 3.81 m, box about 6.9 x 2.48 m, floor about 1.49 m. Our own model and files,
  nothing copied from Onur Emre's mod. (Answers the old "size" question; FH16 Tandem sheet is now just extra reference.)

## Done
- Measured `mods\FS25_VolvoFH16Tandem.zip` (ALXXA) for reference only -> `..\reference_FH16Tandem.md`
  (wheelbase 5.15 m, box about 7.35 x 2.52 m, floor about 1.4 m, about 18 EUR pallets).
- Its "lift axle" (key V, FOLDABLESTEPS_NEXT_POS) is really ride height: both rear axles move 12.4 cm together.
  The game's LiftableAxle spec can lift a real axle by key and/or automatically by fill level.

- 2026-10-22: measured `mods\FS25_fh16BoxTruck.zip` (Onur Emre) too -> `..\reference_fh16BoxTruck.md`
  (curtain-sider with rear doors, 8x4 with steering tag axle, wheelbase 3.81 m, box about 6.9 x 2.48 m, floor about 1.49 m,
  about 15-17 EUR pallets).

- 2026-10-22: CAB = the game's own Volvo FH16 cab (`data\vehicles\volvo\fh16`). BODY = curtain-sider (curtain sides +
  rear doors). Note: Onur Emre's truck is the base FH16 (same price 137,000, same size 2.65 x 9.05 x 4, base "8x4 Tag"
  wheel config) with a body added, so the cab, chassis and 8x4 Tag axles can all come from the game FH16 in GIANTS
  Editor; only the curtain body (+ belts, doors, curtains, autoload) is ours, built in Blender.
  The game's .i3d.shapes are encrypted: Blender can't open the cab; joining cab + body happens in GIANTS Editor.

- 2026-10-22: axles = the steering tag axle (game FH16 "8×4 Tag"), no lift axle.

- 2026-10-22: body v1 modelled by script `..\source\build_body.py` (game coords -> Blender (x, -z, y)); output
  `..\previews\body_v1.blend` + 4 renders `body_v1_*.png` with blue stand-in cab / black stand-in wheels at the game
  FH16 8x4 Tag positions. Body: 2.55 wide, floor top 1.50, roof 4.00, front wall z 2.00, rear doors z -4.98, curtain
  each side with straps every 0.55 m, middle post z -1.45, barn doors with 2 lock bars each, rear + side under-run.
  WAITING for the user's OK on the shape before anything goes into the mod.
  Game FH16 facts: 8x4 Tag config shows chassis8x4 + chassis8x4_tag, moves backlights -2.702, plate to z -4.113,
  trailerAttacherJointSemi to z -2.944 (fifth wheel: to be removed in our version).

- 2026-10-22: on GitHub, PRIVATE: https://github.com/PropaineX/FS25_ProEdition_BoxTruck (full chat .jsonl not uploaded).

- 2026-10-22: body v1 APPROVED by the user ("fine the way it sits"). Mock-up on the real game FH16 (8x4 Tag) in GE:
  `..\previews\body_v1_onFH16_{front,rear,side}.png`. Fits; fifth wheel hidden by the floor. Waiting for OK to build
  the mod files (i3d, vehicle xml, modDesc, icon). Export: `..\source\export_body.py` (fixed colours + no glow).
  User rule: minimise GIANTS Editor whenever Claude is done with it.
- 2026-10-22: user asked to raise the box top to the cab top. FH16 Globetrotter XL roof measured at about 4.23 m
  (side capture, 86 px/m from body top 4.00 / side rail 1.22). body v2: ROOF_Y 4.23 (inside height about 2.55 m).
  Previews `..\previews\body_v2_*.png` and `body_v2_onFH16_{front,rear,side}.png`: body top and cab top now on the
  same pixel row. Waiting for the user's OK. (xml <size height> will need about 4.25.)

- 2026-10-22: v2 height APPROVED ("perfect"); MOD FILES BUILT (not zipped, not tested in game):
  `boxTruck.i3d/.shapes` = game FH16 + body v3 (game-ready nodes), saved in GE (File > Save on a work copy in
  %LOCALAPPDATA%\Temp\claude\bt, then renamed). `boxTruck.xml` from `source\make_vehicle_xml.py` (game fh16.xml: only
  8x4 Tag, no fifth wheel, animations boxRearDoors/boxCurtainLeft/boxCurtainRight, 9 tension belts, 29 mappings).
  `scripts\BoxTruckBody.lua` (X/Y/Z = IMPLEMENT_EXTRA2/3/4, saves positions, MP join sync). `modDesc.xml` (descVersion 115,
  type boxTruckPro parent tractor + tensionBelts + boxTruckBody, EN/DE). Store image still the game's FH16 picture.
  Icon preview `..\previews\icon_BoxTruck_v3_preview.png` waiting for OK (icon_BoxTruck.dds not written yet).
  Body materials are plain colours (no game vehicle shader yet).
  User: wheels in the icon looked bad -> mock-up only showed tyre + outer rim ring (hollow). Mock-up now builds wheels
  like WheelVisual/WheelVisualPart (part attrs: vehicle <wheel> > tyre xml configuration(configId) > default; right
  wheels use nodeRight, no 180 turn; additionalWheel at offset + w/2 + w/2 outward, carries the dualConnector hub).
  Mock-up now runs on a copy of the MOD's boxTruck.i3d + boxTruck.xml. New: `..\previews\icon_BoxTruck_v4_preview.png`,
  `body_v3_onFH16_*.png`, `wheels_v1_left.png`. Icon v4 APPROVED -> `..\icon_BoxTruck.dds` (512x512, identical to
  the preview).
- 2026-10-22 ZIP NAME DECIDED: `FS25_BoxTruck_ProEdition.zip` (permanent; project folder name unchanged).
  1.0.0.0 zipped (6 files: modDesc, boxTruck.xml/.i3d/.i3d.shapes, icon_BoxTruck.dds, scripts/BoxTruckBody.lua;
  26,843,831 B, sha256 105df211d334...) to Mods in waiting, copied to mods (sha match), uploaded to server /testing
  (upload_stage.py: host key ok, temp name -> rename, SHA-256 read back matched). NOT tested in game yet.
- 2026-10-22 TestRunner 0.9.23 on the 1.0.0.0 zip (Claude ran it; the user's permission rule works): 13/15 pass,
  slots ~31. FAIL DXTCheck: icon must be DXT1 (ours uncompressed) -> DXT1 copy made (Pillow
  `save(pixel_format='DXT1')`), side-by-side preview `..\previews\icon_BoxTruck_v4_dxt1_preview.png`, waiting for OK.
  FAIL EditorCheck: 416,830 triangles (warning > 250,000): the FH16 file holds both cabs (FH16 + FH Electric), all
  4 chassis variants + LODs; our body ~1.3k. boxTruck.xml inherited the FH16 motor list incl. FH Electric 330/490
  (swaps to the electric cab). Asked the user: keep the electric options? remove unused parts to cut triangles?
  Reports: `MOD PROJECTS\Library\_TestRunner\testResult_FS25_BoxTruck_ProEdition_tmp_7512_FAIL.xml/.html`.
- 2026-10-22 USER: delete all chassis options except 8x4 Tag. Done in GE on a work copy (bt\strip\delete.lua deletes
  chassis4x2, chassis6x4, chassis8x4_push, colPart4x2Part01, colPart6x4Part01/02; File > Save). make_vehicle_xml.py
  now drops the 31 mappings inside deleted parts + 23 elements using them (objectChanges incl. motor-config chassis
  switches, 13 kardan speedRotatingParts, the Push steering movingPart) and remaps all other FH16 mappings by node
  name chain (game fh16.i3d -> our i3d). 304 mappings, 0 broken. Shapes 26.65 -> 24.59 MB. TestRunner on the stage
  folder: 388,261 triangles (was 416,830), slots 29 (was 31); DXT1 icon still pending. NOT re-zipped/uploaded
  (mods + /testing still hold the first 1.0.0.0 zip). FH Electric cab/engines still in (user not answered).
- 2026-10-22: DXT1 icon APPROVED and swapped in (`..\icon_BoxTruck.dds`, DXT1, 131,200 B). TestRunner: DXTCheck now
  passes; only EditorCheck (triangle warning) fails.
- 2026-10-22 (user asked) second build, still version 1.0.0.0 (chassis stripped + DXT1 icon): 24,659,281 B,
  sha256 286716185709... -> Mods in waiting + mods (overwrote the first build; sha match) + server /testing (replaced
  the first build: upload_stage.py --replace = temp name then posix_rename, SHA-256 read back matched).
- 2026-10-22 BUG in that second build: truck STROBES (shop, GE). Cause: the FH16's chassisMain_lod0/lod1 is ONE skinned
  mesh for all chassis variants; variants are shown/hidden through its bone TGs (chassis4x2_lod0, chassis6x4_lod0,
  chassis8x4Push_lod0/lod1, wheelBack01Left/RightRepr, steeringHydraulicPush(+Punch)). Deleting chassis4x2/6x4/
  8x4_push deleted those bones; GE's save then DROPPED chassisMain's whole skinBindNodeIds -> strobing. log.txt showed
  no error. FIX (strip2, from the first build's merged i3d bt\fh16.i3d): delete only Shapes inside the 3 groups whose
  subtree holds no bone (33 shapes) + the 3 colParts; keep the TGs, set the 3 group roots visibility false. All 8
  skinned meshes keep full bone lists. Same shapes size (24,589,489), XML identical except mappings, 304/0 broken.
  GE test: 4 grabs in a row identical, shop views fine. Fixed files in the project + stage; NOT zipped yet (mods,
  Mods in waiting and /testing still hold the strobing second build).
  Shop picture choices `..\previews\store_v3_choices_preview.png` (1/2/3): user picked 3 -> `..\store_boxTruck.dds`
  (512x512 DXT5), storeData <image> now store_boxTruck.dds. Stage = 7 files. TestRunner: 14/15 pass, only the
  triangle warning (388,261) left; slots 29.
- 2026-10-22 (user asked) third build = FIXED (no strobe, shop image), still 1.0.0.0, 7 files, 24,704,299 B,
  sha256 b402c60a5837... -> Mods in waiting + mods (game closed; sha match) + /testing (--replace, SHA-256 verified).
- 2026-10-22: user saw it in the shop (solid now). Asked for the PRO EDITION banner on the shop picture: preview
  `..\previews\store_v4_banner_preview.png` (banner top_y 40, above the truck which starts at y 127) APPROVED ->
  `..\store_boxTruck.dds` (DXT5) + stage. Not zipped yet.
- 2026-10-22 USER (in-game screenshots): wheels clip into the body, box touches the cab back, rear under-run bar must
  sit between the VOLVO mudflap lettering and the number plate, truck white looks silver next to the box white.
  Measured in GE (vertices): tyres reach y 1.40; cab spoiler back to z 1.97-2.04, hoses 1.94, aero trim 1.78; cab rocks
  +-0.17 m. build_body.py now has LIFT (floor + everything under it) and ROOF_Y args; FRONT_Z 2.00 -> 1.70 (box 0.30 m
  shorter, rear unchanged: 6.54 m inside, 15 EUR long / 16 turned); rear bar y 0.69-0.79. Options built:
  body_v4A (LIFT 0.25, roof 4.48 = 0.25 above cab), body_v4B (LIFT 0.25, roof 4.23 = level with cab, inside 2.30 m).
  GE previews `..\previews\body_v4_AB_side_3.png`, `_front_3.png`, `body_v4_AB_rear.png` (A), `body_v4_AB_gap.png`.
  White: plan = extra baseColorConfiguration color "0.90 0.90 0.88" + calibratedPaint (non-metallic), matching the
  box material. Waiting for the user's A/B choice.
- 2026-10-22 USER: option A, but "the box the same size, just moved up". build_body.py: SHIFT_Z -0.30 (whole box back,
  FRONT_Z 1.70, REAR_Z -5.28, full length kept), LIFT 0.25, roof 4.48. Rear bar stays on the CHASSIS end (z -4.88..-4.76,
  y 0.69-0.79): on the box end it lined up over the VOLVO lettering. Body v5 -> bt\boxBody_v5b.i3d.
  Previews `..\previews\body_v5b_onFH16_side.png`, `_rear.png` (+ body_v5_onFH16_front/gap). Waiting for OK.
- 2026-10-22 USER: engines = only 425/515/585/600, themed names like "FH600"; FH425 default $0, then +15k/+20k/+25k.
  Done in make_vehicle_xml.py + boxTruck.xml (project + stage): FH425 City Hauler, FH515 Regional Hauler, FH585 Long
  Hauler, FH600 Heavy Hauler; all on the game's 600 setup (D17K600 curve, ATO3112F, sound), torqueScale 2.465*hp/600;
  diesel 170/206/234/240 l/h, DEF 14.2/17.2/19.5/20; only FH600 shows the "600" cab badge; FH Electric parts forced off
  (the electric options were isSelectable=false anyway). White paint option "White (body)" = color 0.90 0.90 0.88 +
  calibratedPaint added. modDesc text updated (engines, 425-600 hp). 304 mappings, 0 broken. NOT zipped.
  Body v5 (raised/moved back) still waiting for the user's OK; boxTruck.i3d in the project is still the v3 body.
- 2026-10-22 USER: rear bar up 2-3 cm, as close under the plate as possible, never covering it. US plate 0.30 x 0.15
  hangs from licensePlateBack y 0.909 (placementArea top 0.07 -> 0.005 lower): plate bottom ~0.829 (frame maybe
  0.814). Bar now y 0.71-0.81 (+2 cm), z -4.88..-4.76 (chassis end; plate is at z -4.11, 0.7 m further forward).
  Body v5c -> bt\boxBody_v5c.i3d. The game's plate i3d stays invisible in GE (number not generated); the user asked
  for a simple white block: drawn into `..\previews\rearbar_v2_platemock_close.png` / `_rear.png`.
- 2026-10-22 APPROVED ("go with that"). Body v5c merged into the mod model in GE (bt\v5merge\merge5.lua: delete old
  boxBody, link v5c, File > Save); all 8 skinned meshes keep full bone lists, stripped chassis still hidden.
  boxTruck.xml regenerated: size 2.65 x 9.81 (lengthOffset -0.375) x 4.50, middle-post anim from the i3d,
  engines + white paint in. 304 mappings, 0 broken. TestRunner: only the triangle warning (388,261), slots 29.
  Project + stage updated.
- 2026-10-22 (user asked) 4th build zipped, still version 1.0.0.0, 7 files, 24,721,051 B, sha256 e96f73b3328e... ->
  Mods in waiting + mods (game closed, sha match) + /testing (--replace, SHA-256 verified). User is testing in game.
  Later (user said "later"): remove the unused FH Electric cab to cut triangles (keep skin bones!).
- 2026-10-22 USER: in the shop the store-image banner sits way too high (next to the truck above). The shop draws the
  512 px store image with its top ~180 px ABOVE the card (vehicles overflow the card top), so a banner at y 40 is
  outside the card. Options in a mock card: `..\previews\store_v5_banner_options_preview.png` A = banner top_y 190
  (across the cab top), B = top_y 425 (across the bottom). User wanted it "between the word Volvo and the FH16, below
  it" -> the VOLVO logo and title are drawn by the game below the picture, so: truck scaled 0.88 (436 x 332) with its
  bottom at y 428, banner top_y 436 under it (just above the VOLVO logo).
  Preview `..\previews\store_v6_banner_under_truck_preview.png` (work file bt\store_bannerC.png). APPROVED ->
  `..\store_boxTruck.dds` (DXT5) + stage. Not zipped yet.
- 2026-10-22 USER (in game): right rear door dark, left light ("coloring messed up"). Geometry identical (checked);
  cause = plain non-shader materials. export_body.py now rewrites the body materials to vehicleShader (white_diffuse,
  default_normal, default_vmask + template detail maps, linear colorScale): curtain/door = calibratedPaint
  0.90 0.90 0.88 (= the "White (body)" cab paint), alu = metalPainted 0.34, steelDark = metalPainted 0.02,
  strap = plasticPainted 0.015, floor = wood2Oak. Exported bt\boxBody_v5d.i3d. User OK'd the materials.
- 2026-10-22 USER (in game, white cab + white box look right): cab still touching the box, wants ~2 cm gap.
  Skinned cab shell vertices are bone-relative (useless for measuring); measured instead with a long-lens side shot
  (createCamera fov 8 deg at x 60, box hidden; scale checked on the old box front: 2.036 vs real 2.02).
  Cab rear edge: z 2.04 @ y4.2, 1.81 @ y3.0, 1.72 @ y2.2, 1.68 @ y1.7 (lower rear corner) vs box front posts at 1.72.
  SHIFT_Z -0.30 -> -0.37 (posts end at 1.65, ~3 cm clear; doors at -5.35; xml size 9.88 / -0.41). Body v5e
  (game materials) -> bt\boxBody_v5e.i3d. Previews `..\previews\body_v5e_materials_{gap,rear,front,side}.png`:
  rear doors now the same shade. User: looks good, but bring the roof back down to the cab top.
- 2026-10-22: ROOF_Y default 4.23 (level with the cab), floor lift kept -> inside height 2.30 m. XML size height
  4.25, belt defaultHeight 2.2. Body v5f -> bt\boxBody_v5f.i3d; previews `..\previews\body_v5f_roofdown_*.png`.
  Waiting for OK, then: merge in GE, regenerate XML, checks, zip, three places.
- 2026-10-22 USER: v5f "it's right" + make the SLEEPER roof the default (design config 2, price 0; Globetrotter XL
  is config 1 +5000). Long-lens measurement: Globetrotter XL roof top ~4.29 (incl. roof hatch), Sleeper ~4.12.
  With box roof 4.23 the box sits ~0.11 m above a Sleeper cab. User: KEEP the box at 4.23.
  make_vehicle_xml.py: designConfiguration 2 (Sleeper) isDefault="true". Body v5f merged in GE (bt\v6merge), all
  checks OK (skins full, chassis hidden, 1 body, game materials; door+curtain materials merged by GE, identical).
  XML regenerated (size 9.88 / -0.41 / 4.25, belts defaultHeight 2.2), 304/0 broken, TestRunner only the triangle
  warning. 5th build, still 1.0.0.0, 7 files, 24,710,433 B, sha256 3119e6f9a573... -> Mods in waiting + /testing
  (verified). NOT yet in mods: the game was running (holds the zip open); copy when the user closes the game.
- 2026-10-22 USER: cab-side engine badge for every engine (425/515/585/600). Facts: engine600/700/780_decals share
  material fh16Decals_chrome_mat (vehicleShader variation vmaskUV2_normalUV3; fh16Decals_diffuse 1024 BC7 alpha
  letters, fh16Decals_normal 512, fh16B_vmask). The atlas only has single digits 6 (27,776-121,853) and 7/8/0 in the
  "780" row (y 260-344; 7 x1-89, 8 x90-196, 0 x197-291): decals are built digit by digit. Font: verticals ~16 px,
  horizontals ~7-8 px, corner radius ~25 px, height ~83 px. New 4/2/5/1 drawn by scratchpad scripts\volvo_digits.py;
  preview `..\previews\badge_digits_v1_preview.png`. Plan after OK: new decal texture (copy of the atlas + new
  digits), get the 600 decal's quads/UVs from GE (getShapeVertexPositions/TexCoords), build engine425/515/585 decal
  meshes in Blender, merge in GE, one objectChange per engine.
  User: v1 digits "look horrible". v2/v3 built from game glyph pieces (6->5, 8->2, 7+0+8->4): notches, 2 read as S.
  v5 = Michroma font (Google Fonts, SIL OFL 1.1, scratchpad fonts_dl\ incl. OFL.txt) fitted to the game digits
  (75 px tall, game widths) with the Volvo contrast: uprights spread +5 px, bars thinned 2 px (game 0: V16/H6;
  Michroma raw V11/H8). Michroma's own 7806 nearly matches the game's. Scripts: scratchpad scripts\volvo_digits3.py.
  Preview `..\previews\badge_digits_v5_preview.png`, waiting for OK.
  Also (user asked): Claude Code spinner verb "Cerebrating" added in C:\Users\groov\.claude\settings.json
  (spinnerVerbs append; file was new).
  User asked about uploading: options explained (ModHub / mod sites / own server); undecided; aim for ModHub standard.

## Open questions
- Folder name: keep `FS25_ProEdition_BoxTruck` or rename to `FS25_BoxTruck_ProEdition`?

## Blocker (solved 2026-10-22)
- GIANTS Blender exporter 10.0.2 (FS25) installed in Blender 5.2.2 and a test export worked (i3d + .i3d.shapes).
  The first download (10.5.0) was the Project Motor Racing exporter and was not installed.
  Headless export recipe is in the knowledge index (Box Truck entry). Next: model the curtain body.
- GIANTS TestRunner 0.9.23 (official mod checker) set up in `MOD PROJECTS\Library\_TestRunner\` for checking this mod
  before release. Claude running it was blocked by the permission check; waiting on the user.

## 2026-10-22 (late morning): cab engine badges 425 / 515 / 585 — DONE in source folder (not zipped)
- User approved the GE preview ("Those are fine. That looks good.").
- source/make_badge_textures.py -> boxTruckBadges_diffuse.dds (DXT5) + _normal.dds (DXT1), 512x256, full mip chains;
  digits 4 2 5 1 8 in Michroma (source/fonts, OFL) via source/volvo_digits.py, EURO 6 plate copied from the game atlas.
- source/build_badges.py + export_badges.py (Blender) -> engine425/515/585_decals: the game's engine600_decals quads
  (same corners, same vmask uv1), material = copy of fh16Decals_chrome_mat with our textures.
- Merged in GE (bt\v7merge, merge7.lua) under engine_fh16_decals at the 600's translation; File > Save; 8 skinned
  meshes, 0 broken bone refs. make_vehicle_xml.py: each engine shows its own badge (FH600 keeps the game's 600).
- boxTruck.xml: 307 mappings, 0 broken. TestRunner: all pass except the known polycount warning (388,309 tris).
- Not yet zipped / copied anywhere (waiting for the user).

## 2026-10-22 (later): curtain controls, pallet fix, ProEdition curtain — build 6 sent
- In-game feedback: box looks low-poly (rebuild still to plan with the user), pallets sank/jiggled, left curtain
  wouldn't open (Y is taken in the user's game).
- Controls now: X rear doors, Z open/close selected curtain, U (TOGGLE_TIPSIDE) select left/right (like ProfiLiner).
- Side collision walls now lift 2.5 m straight up (were folding inward and swinging through the load on closing).
- ProfiLiner textures copied to Library\_KroneProfiLinerTextures (user: refer to the game's files, don't copy into mod).
  Krone / FS League / GIANTS curtain options NOT added yet (need fitting to our 6.7 m curtain + previews).
- New shop option "Curtain design" (design8): Plain white (default) / ProEdition ($0) = waving PRO EDITION banner decal
  (make_curtain_texture.py, build_body.py decal(), body v6, GE merge bt\v8merge). User approved wavy v2.
- Build 6: FS25_BoxTruck_ProEdition.zip 24,935,806 B sha256 e6fdeb2feb8d... -> Mods in waiting, mods, /testing
  (verified). TestRunner: only the known polycount warning.

## 2026-10-22 (midday): box v7 rebuild (in the source folder, NOT zipped yet)
- User wanted the box to look like a real curtain-sider (reference: another mod's box, used as a picture only) and the
  Krone ProfiLiner's opening ANIMATION (not its graphics), opening front to back, doors only ~100 deg, all liner options.
- source/build_body.py v7 (v6 kept in source/old/): curtain outside the rails with our own fold textures
  (make_curtain_maps.py), dark band, ~20 buckle straps per side hooked under the bottom rail, corner marks, top-rail
  lip, stake pockets, ribbed front wall + red kick plate, roof bows, dark floor + anti-slip strips, 2 matte sliding
  posts per side (hidden behind the curtain), 12 side boards per side, gathered curtain at the rear (pleats), doors
  with frame/rivets/lock bars/cams/hinges, inside 6 pressed panels, spare lock rod (left), stickers (right,
  make_sticker_texture.py, own drawings).
- Designs (design8): Plain, ProEdition, Krone, Farming Simulator League, GIANTS. The three ad designs are our own
  layouts of pieces of the game's profiLinerPaintjob1-3 sheets (referenced via $data, not copied). White pieces left out.
- Animation (make_vehicle_xml.py): ProfiLiner sequence - closed->gathered swap 0-0.1 s, boards hide 0.1-1.0 s,
  rear-middle post tilts 0.65 and slides 1.0-2.33, front post 2.33-4.0, ProfiLiner sounds. Doors 100 deg in 2 s.
- GE merge bt\v9merge (editor started with the i3d as argument: no Open dialog), saved; texture paths fixed.
  345 mappings / 0 broken; TestRunner only polycount 393,651. Previews: bt\look\ge9_sheet.png, v7e_*.png.
- Still open: pallet sinking/tilting + belts through the load (floor collision measured correct; needs in-game test).
- Build 7 (box v7) zipped: 26,785,827 B sha256 0d3bd7971774... -> Mods in waiting, mods, /testing (verified), 2026-10-22.

## 2026-10-22 (afternoon): build 8 in the source folder (NOT zipped)
- User approved the ProfiLiner rear (preview previews\rear_profiliner_v1_preview.png): game's ProfiLiner doors (plain
  white, 0.875 height), rear frame + latches + sill keepers cut from its body (source\build_rear.py, objcut.py,
  export_rear.py), lock levers on our doors. Merged (bt\v12merge, merge12.lua) -> mod boxTruck.i3d/.shapes/.xml.
  345 mappings 0 broken. TestRunner: only polycount (402,099).
- Curtain now slides back over 1.2 s (scale part on curtainXClosed), then boards/posts as before (make_vehicle_xml.py).
- Pallet blink/sink = Universal Autoload (its saved loadingArea y 1.50 for our truck; floor is 1.75). User chose our own
  autoload: scripts\BoxTruckAutoLoad.lua (Ctrl+L load/stop, Alt+L release; pull-in animation ~1-2.5 s per pallet,
  kinematic mount = no sinking). modDesc: spec, actions, bindings, l10n, description. NOT tested in game yet.
  DONE (game closed): our truck's entry removed from modSettings\UniversalAutoload.xml; backup
  UniversalAutoload_backup_2026-10-22.xml next to it.
- User asked for the ProfiLiner's corrugated FRONT: source\build_front.py + body v9 (white roof cap, header panel,
  front posts white and behind, colFrontWall moved to the sheet, autoload FRONT_Z 1.48). Preview
  previews\front_profiliner_v1_preview.png - WAITING for OK before merging. Open: Krone logos on the band (left out).
- User approved front v2 (previews\front_profiliner_v2_preview.png): band up under the white cap, Krone logos kept
  (frontLogos decal: OBJ + dumped uv1/uv2), sheet lower half takes the upper half's UVs (no baked coupling shadows),
  coupling columns removed, top side rails end at FRONT_Z-0.16, our front posts behind. Merged (bt\v15merge,
  merge15.lua) -> mod files; 345 mappings 0 broken; TestRunner only polycount 403,227.
- BUILD 8 zipped 2026-10-22: FS25_BoxTruck_ProEdition.zip (still 1.0.0.0), 13 files (boxTruckStickers_diffuse.dds no
  longer used, left out), 27,995,564 B, sha256 939866b472ad... -> Mods in waiting, mods, /testing (replaced build 7,
  temp name + rename, SHA verified). Autoload + curtain slide + rear + front NOT yet tested in game.
