# Box body detail upgrade

The comparison uses actual GIANTS Editor captures at matching camera positions and lighting. `before_after.html` supports switching between full views and close-ups and zooming; `before_after.svg` embeds the same captures for a portable side-by-side image.

Implemented: 4096 x 2048 curtain diffuse and RGB normal maps (previously 4096 x 1024); separate 2048 x 2048 fabric detail diffuse, normal, and smoothness/AO/metalness maps; BC7 compression with full mip chains. The cloth now uses a nonmetallic coated-fabric material rather than the painted-metal detail maps. Added tessellated shallow curtain drape, welded hems in the maps, chamfered open buckle frames and keepers, rail trim, rivets, and door seals.

Ten grouped visual meshes are appended under the existing body, closed curtain groups, and door pivots. Existing cloth slabs and block buckles are hidden. All original nodes and collision flags are preserved; all 347 XML mappings resolve. The curtains' original gathered/open visuals are retained. Performance and animation playback still require an in-game check.

`before/` preserves the original model and textures. `work/` is the reviewed staging scene; do not package preview rigs, screenshots, source blends, or staging files into the mod. New runtime dependencies are the three `boxTruckFabric_detail_*.dds` files in the project root; include them when packaging.

Sources: `source/make_body_detail.py`, `build_body_detail.py` (Blender), `integrate_body_detail.lua` (GIANTS Editor), and `finalize_body_detail.py`. Finalizer validates node paths, restores original editor-only visibility/transforms, and installs the seven runtime asset files only when passed `--install`. Do not rebuild the entire older body scene: later door/banner/front-gap/board-stow work exists in the current model.
