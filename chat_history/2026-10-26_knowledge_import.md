# 2026-10-26 — Claude knowledge migration

User requested finding Claude's saved Markdown, commands, storage rules and knowledge and importing them for Codex. Completed: 87 provenance-tracked documents (Claude global instructions + 57 memories + 26 FS25 context documents + 3 historical scratchpad indexes), plus an inventory of 23 shared helpers.

Persistent archive: `../Library/_CodexKnowledge/claude-import-2026-10-26/`. Entry point: `../Library/_CodexKnowledge/README.md`. Global `C:/Users/groov/.codex/AGENTS.md` and this project's AGENTS.md point there. The global instructions were observed being loaded into the active conversation immediately after installation.

Current preferences are summarized separately from historical snapshots. Conflicts resolved in favor of latest user instructions: minimize tools instead of force-close, Testing_local instead of Mods in waiting, explicit packaging only, `/testing` instead of old live-upload habits, environment-only credentials. Existing sources were preserved. Credentials, raw conversations, browser profiles, vendor/plugin skills and dependency trees were excluded.

All 87 installed snapshots were byte-compared against staging and their actual SHA-256 hashes verified. The initial manifest expected pre-Windows-newline-translation hashes; corrected the manifest to stored-byte hashes and preserved the original content-hash field. Installer completed successfully. The shared FS25 knowledge index was updated with the migration and new verified editor/material findings.

User then requested exiting this program after completion. Scheduled a normal close of only the current Box Truck VS Code workspace; no forced termination or discard of unsaved work.
