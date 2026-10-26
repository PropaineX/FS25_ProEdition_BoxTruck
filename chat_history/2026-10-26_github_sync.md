# GitHub synchronization — 2026-10-26

User requested bringing GitHub fully up to date after the incoming delivery.
- Sync target: origin/main, PropaineX/FS25_ProEdition_BoxTruck. Fetch confirmed no remote divergence from the local 1.1.0.0 baseline.
- Included current 1.3.0.0 runtime assets, scripts, build/test helpers, design previews and Blender studies, session notes, and release manifests.
- README now records current behavior, exact delivered ZIP identity, /testing and /incoming verification, build command, validation, and outstanding in-game/multiplayer testing.
- Updated AGENTS.md release pointers. Local application logs, dependencies, ZIPs, raw chat transcripts, and extracted game API reference files remain excluded.
- Re-ran Lua regression checks successfully using the existing project-local Lupa runtime. All 347 vehicle mappings resolve. Incoming package CRC/member-content checks and full remote SHA-256 verification passed earlier this session.
- Staged text scan found no credential patterns; no staged file exceeds 100 MiB. Existing generated boxTruck.i3d has one blank line with trailing whitespace; preserved runtime bytes to retain the delivered package identity.
