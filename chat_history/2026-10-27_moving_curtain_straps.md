# Moving curtain straps ? October 27, 2026

User requested that the black bottom straps remain on the curtain throughout the shape transition, and requested an animated preview.

- Added original closed-model Band, Straps and Buckles geometry from the approved Blender scenes to each of the six gathered variants. Original black strap and galvanized hardware materials retained; source closed dimensions/positions are the same across variants.
- Hardware targets follow the actual rendered cloth triangles in material coordinates, including outward offsets and parts below the hem. The same curtainShape parameter drives fabric, artwork and hardware together in both directions.
- Runtime now hides original closed-model Band/Straps/Buckles, preventing stationary/scaled duplicates; new attached hardware stays visible with the selected gathered variant. Existing animation controls, random selection and save/network behavior unchanged.
- Verified by source/test_curtain_straps.py: all 128,178 hardware vertices match attachment positions at closed, 25%, 50%, 75% and gathered, for all three variants on both sides, within 0.03 mm rounding tolerance. Hardware triangles are clipped to the actual cloth grid and diagonals, so the long band and strap surfaces bend with the folds rather than cutting through them. Full Lua and asset regressions pass, including original node hiding.
- GIANTS Editor loaded converted runtime meshes with the black straps visible when closed. Animated preview captured from the actual engine mesh positions in previews/curtain_straps_motion_v2/, preserving the prior strap-free preview separately. Full vehicle gameplay and multiplayer rendering remain untested.
- No packaging, copying to installed mods, or remote upload. Latest local testing ZIP remains 1.3.0.3, created before this strap addition.

Final preview: curtain_straps_open_close_loop.gif, 60 frames, 2,894,450 bytes, opening and reverse closing with endpoint holds. Visually checked closed, halfway and gathered engine captures. Opened in the existing VS Code window; GIANTS Editor minimized. Earlier curtain-only GIF and first strap capture kept separately.
