# 2026-10-26 — Box Truck 1.2.0.0 testing release

- User approved the box detail upgrade and explicitly requested a ZIP in local testing and FTP testing.
- Active chassis center of mass: `0 0.8464 0.6`, matching rear axle height.
- Box upgrade: tessellated curtain drape, higher-resolution curtain maps, separate woven-fabric detail maps, rounded buckle hardware, rail trim, rivets, and door seals. Original assets backed up in `previews/detail_v1/before/`.
- Corrected preview-only omissions: rear tag wheel was attached under a hidden configuration group; side Pro Edition banners were not enabled. Both are shown in the updated comparison; production configurations were preserved.
- Structural validation: 719 original scene nodes preserved, 10 new visual meshes, original collision flags unchanged, 347 XML mappings resolving. Python sources compile and ZIP CRC/member-content checks passed. No in-game animation/performance test performed during this session.
- Version bumped from 1.1.0.0 to 1.2.0.0. Packaged using `source/package_testing.py`: 18 runtime files, excluding source, previews, editor settings, backups, and staging.
- ZIP: `FS25_BoxTruck_ProEdition.zip`, 33,493,897 bytes.
- SHA-256: `05056dab6a3aa0d2c9ce1063a1575a9b18df77018749e9e4d2c8e6e7f75b113f`.
- Local copy: `FarmingSimulator2025/Testing_local/FS25_BoxTruck_ProEdition.zip`, SHA-256 verified against the build.
- Uploaded via the existing SFTP upload workflow to `/testing/FS25_BoxTruck_ProEdition.zip`: pinned server host key checked, temporary upload renamed into place, final remote file read back and SHA-256 verified.
- Live server `/FTPness` and local `mods` were not changed. No commit or push requested or performed.
- GIANTS Editor minimized after preview work; Blender used in background mode.
