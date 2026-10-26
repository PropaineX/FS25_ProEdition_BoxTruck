# Box Truck Pro Edition (FS25) - work in progress

Farming Simulator 25 box truck for hauling pallets, by PropaineX.

## Current version: 1.3.0.0

Updated October 26, 2026. The current build adds three randomized gathered-curtain shapes on each side, white inner linings, higher-resolution curtain textures, woven fabric detail, and upgraded body hardware. Curtain choices are selected by the server, synchronized to clients and late joiners, and retained in saves. Existing door, board, post, curtain, and loading controls are preserved.

The chassis center of mass is now `0 0.8464 0.6`.

### Latest delivery

- ZIP filename: `FS25_BoxTruck_ProEdition.zip` (20 runtime files; 50,453,180 bytes).
- SHA-256: `85510e3800a3c06b982b34827c4be3a5d6cad974c14f2901a726ca0ca4c24389`.
- Local build: `FarmingSimulator2025/Testing_local/FS25_BoxTruck_ProEdition.zip`.
- This exact build was delivered to SFTP `/testing` and then `/incoming`; both deliveries passed full remote SHA-256 readback verification.
- Build with `python -I source/package_testing.py`. ZIPs and local test dependencies are excluded from Git.

### Validation and remaining testing

All 347 vehicle node mappings resolve. The Lua regression checks pass for random selection, server authority, event serialization, late joining, save/restore, legacy saves, all curtain designs, cleanup, mesh indices, and white linings. Packaging checks verify ZIP CRC, runtime references, and every member against source. GIANTS Editor previously loaded and displayed the integrated asset.

In-game animation/performance and an actual multiplayer session still need testing. Run `python -I source/test_gathered_runtime.py` with Lupa installed in `.local/lua-test-runtime` to repeat the mocked engine/network checks.

See [implementation notes](chat_history/2026-10-26_random_gathered_curtains.md), [testing release](chat_history/2026-10-26_1.3.0.0_testing_release.md), and [incoming delivery](chat_history/2026-10-26_incoming_release.md). These supersede older session status statements.

- Cab, chassis and 8x4 Tag axles: the game's own Volvo FH16.
- Body: our own curtain-sider (curtain sides, rear barn doors), built in Blender.
- Loading: forklift with tension belts, plus an autoload script written from scratch.

## Folders
- `source/` - Blender build scripts, texture tools, runtime checks, and ZIP packaging.
- `previews/` - preview renders and the generated .blend.
- `reference_*.md` - measurements taken from other trucks (reference only, nothing copied).
- `chat_history/` - session notes.

Private repo: the finished mod will contain GIANTS' FH16 files, which can't be published.
