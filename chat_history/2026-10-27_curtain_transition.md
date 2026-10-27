> Historical: user rejected this implementation; source and local testing ZIP were restored to 1.3.0.1. Superseded by 2026-10-27_curtain_shape_motion.md.

# Gradual curtain transition ? October 27, 2026

User requested a gradual fade into whichever randomized crumpled curtain is selected.

- Removed the end-of-animation visibility swap on both sides. Existing sheet compression remains.
- Runtime uses normalized animation time: fade starts at 50%, ends at 100%, using smoothstep. Closing reverses the same transition. Both sides, all three variants, artwork, white liners and moving hardware participate.
- Added a local vehicleShader derivative with curtainOpacity, retaining the installed FS25 shader behavior and multiplying alpha before reflection attenuation. Curtain materials use alpha blending; closed curtain materials are separate copies to avoid changing other hardware. Per-shape shader writes use shared=false. Idle blends are cached.
- Packaging file list includes shaders/*.xml for the next requested build. No packaging, copying or upload performed; packaged version remains 1.3.0.1.
- Verified with real specialization under Lupa mocks: existing random/network/save checks plus fade endpoints, midpoint, monotonicity, reversal, both sides/all variants. XML checks verify fade materials and removal of competing visibility parts. Shader parameter/API checked against local installed shader and GIANTS Editor scriptBinding.xml.
- Not yet verified in GIANTS Editor or FS25: shader compilation, transparent surface sorting/shadows and visual timing. No claim of visual/in-game verification.
