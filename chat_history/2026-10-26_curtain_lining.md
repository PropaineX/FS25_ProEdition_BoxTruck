# Curtain interior lining fix ? 2026-10-26

Added textured interior linings on both closed curtains in boxTruck.i3d, reusing original slab shapeIds 234/247 and fabric material 1321. Original cloth_panel builder supplies inward and outward faces with full curtain UVs. Linings sit 25 mm inward from the original slab position to clear the upgraded drape. Appended under existing Closed groups so curtain visibility and animation are inherited; existing scene nodes and index paths unchanged. No new textures or binary shape dependencies.

XML and all 347 mappings validated. New IDs unique. In-game appearance and animation not yet verified. Backup: previews/curtain_lining/before/boxTruck.i3d. Source only; no packaging or upload requested.
