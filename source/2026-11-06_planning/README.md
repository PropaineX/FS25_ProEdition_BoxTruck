# Planning files from 2026-11-06

Supporting scripts for `chat_history/2026-11-06_HANDOFF_flatbed_and_dump_plan.md` and
`chat_history/2026-11-06_goat_milk_shed_clearance.md`. None of this ships in the mod.

- `mockup_scripts/` — Pillow scripts that drew the previews in `previews/`:
  `flat.py` (flatbed_v1), `stakes.py` (flatbed_v2/v3 sliding stakes), `boards.py` (flatbed_v4 folding boards),
  `side.py` (lowered_roof_v1-v4), `shop.py` (shop_section_v1-v3; needs the user's shop screenshot, the path inside
  is from a temporary folder). Run: `python -I <script> <out.png>` (stakes/boards import flat.py from the same folder).
- `ge_measuring/` — GIANTS Editor Lua used to measure the goat milk shed, the milk pallet and the truck heights
  (paths inside point to scratch copies in `C:\Users\groov\GE_work\goatshed\`). Output: "[GS]" lines in editor_log.txt.
- `route_sim/` — AutoDrive route-following simulation for the goat milk pickup turn: `ad.py` (reads the route from
  AutoDrive_config.xml), `sim.py`/`sweep*.py` (steering model), `real.py` + `draw.py` (real route, picture
  `goatmilk_turn_v1.png`), `wheelpos2.py` (wheel/node positions from an i3d).
