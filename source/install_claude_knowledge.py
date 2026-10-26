"""Install the explicitly requested knowledge migration. Run after staging/review.

Writes only the shared knowledge archive/index, a managed global AGENTS section,
and an append-only entry in the existing shared knowledge index. Preserves sources.
"""
from pathlib import Path
import hashlib, json, shutil

ROOT=Path(__file__).resolve().parent.parent
STAGE=ROOT/'.local/claude-import-2026-10-26'
LIBRARY=ROOT.parent/'Library'
CENTRAL=LIBRARY/'_CodexKnowledge'
DEST=CENTRAL/'claude-import-2026-10-26'
CENTRAL.mkdir(parents=True,exist_ok=True)
DEST.mkdir(exist_ok=True)
inventory=json.loads((STAGE/'inventory.json').read_text(encoding='utf-8'))
count=0
for f in STAGE.rglob('*'):
    if not f.is_file() or f.name=='global-AGENTS.md':continue
    target=DEST/f.relative_to(STAGE)
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert target.read_bytes()==f.read_bytes(),f'Existing archive differs: {target}'
    else:shutil.copy2(f,target)
    assert target.read_bytes()==f.read_bytes()
    count+=1

central_text='''# Codex shared knowledge

Persistent local references migrated from Claude at the user's request on 2026-10-26.

- [Current working rules](claude-import-2026-10-26/CURRENT_RULES.md)
- [Commands and storage locations](claude-import-2026-10-26/COMMANDS_AND_LOCATIONS.md)
- [Full import and scope](claude-import-2026-10-26/README.md)
- [87-document catalog](claude-import-2026-10-26/CATALOG.md)
- [Topic map and 23 shared helper files](claude-import-2026-10-26/TOPICS_AND_TOOLS.md)
- [Original shared FS25 technical index](../_FS25Knowledge/README.md)
- [Current server policy](../_FS25ServerBrief/CLAUDE.md)

The source Markdown files remain in place. Historical snapshots are reference material; the current user's instructions override imported preferences. Keep the existing FS25 knowledge index as the live technical reference and this archive as a traceable snapshot.

For Box Truck work, read the project's latest release notes. Do not resurrect an old "done" state, older output folders, live-server upload habits, or an instruction to force-close the editor.
'''
index=CENTRAL/'README.md'
if not index.exists():index.write_text(central_text,encoding='utf-8')
elif 'claude-import-2026-10-26' not in index.read_text(encoding='utf-8'):
    with index.open('a',encoding='utf-8') as f:f.write('\n'+central_text)

codex=Path('C:/Users/groov/.codex')
assert codex.is_dir(),'Codex configuration directory not found'
global_file=codex/('AGENTS.override.md' if (codex/'AGENTS.override.md').exists() else 'AGENTS.md')
old=global_file.read_text(encoding='utf-8') if global_file.exists() else ''
start='<!-- BEGIN CLAUDE KNOWLEDGE IMPORT 2026-10-26 -->'
end='<!-- END CLAUDE KNOWLEDGE IMPORT 2026-10-26 -->'
block=start+'\n'+(STAGE/'global-AGENTS.md').read_text(encoding='utf-8').rstrip()+'\n'+end+'\n'
if start not in old:
    if old:
        backup=codex/(global_file.stem+'.before-claude-import-2026-10-26.md')
        if not backup.exists():shutil.copy2(global_file,backup)
    global_file.write_text(old.rstrip()+'\n\n'+block if old else block,encoding='utf-8')
else:
    assert end in old,'Incomplete existing managed import block'
assert start in global_file.read_text(encoding='utf-8')

live=LIBRARY/'_FS25Knowledge/README.md'
entry='''

## Codex handoff — 2026-10-26

- At the user's explicit request, migrated Claude's global preferences, 57 per-project memory files, related FS25 Markdown and three historical scratchpad indexes into `Library/_CodexKnowledge/claude-import-2026-10-26/`: 87 provenance-tracked snapshots and a 23-helper inventory. Current preferences and commands are in its CURRENT_RULES.md and COMMANDS_AND_LOCATIONS.md. Existing sources remain intact. Global Codex AGENTS instructions point to the shared index.
- Current editor rule (explicit user instruction, October 26): announce use of GIANTS Editor, Blender or Krita; no repeated permission request; minimize afterward and preserve open work. Supersedes older close/force-close instructions. Foreground must still be verified before GUI input.
- Verified on Box Truck: `vehicleShader` detailSpecular RGB means smoothness / ambient occlusion / metalness. Zero in green made the new fabric black. The installed shader source confirmed the channel meanings.
- Verified on Box Truck: I3D `Files` must precede `Materials` for imported material texture references; node name `visuals` can resolve inside a rear door rather than the static body. Use exact intended parents and preserve node-index mappings by appending new nodes.
- GIANTS Editor preview scripts were cached across scene reloads; a fresh script filename executed reliably. Click the viewport before Ctrl+S and verify the on-disk result/editor save log. Hidden editor instances may have no usable main-window handle in another desktop context; identify the actual desktop window before input.
- Box Truck 1.2.0.0 delivered October 26: detailed curtain maps/mesh/hardware, chassis center of mass `0 0.8464 0.6`; all 347 node mappings resolve. ZIP 33,493,897 bytes, SHA-256 `05056dab6a3aa0d2c9ce1063a1575a9b18df77018749e9e4d2c8e6e7f75b113f`; local Testing_local and SFTP `/testing` copies verified. In-game animation/performance still untested during that session. See the project's `chat_history/2026-10-26_testing_release.md`.
'''
if '## Codex handoff — 2026-10-26' not in live.read_text(encoding='utf-8'):
    with live.open('a',encoding='utf-8') as f:f.write(entry)

assert len(list((DEST/'snapshots').glob('*.md')))==inventory['unique_snapshots']
for row in inventory['documents']:
    assert hashlib.sha256((DEST/row['snapshot']).read_bytes()).hexdigest()==row['snapshot_sha256']
result={'archive':str(DEST),'global_instructions':str(global_file),'installed_files':count,
        'documents':inventory['source_count'],'snapshot_hashes_verified':True}
(STAGE/'installation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
