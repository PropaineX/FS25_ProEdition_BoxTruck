"""Stage a searchable migration of the user's first-party Claude notes.

Reads Markdown only from named Claude/profile roots. Does not read credentials,
raw conversations, browser profiles, or vendor/plugin skills. Does not install
global instructions; installation is a separate, reviewable filesystem step.
"""
from pathlib import Path
import collections, hashlib, json, re, subprocess

ROOT=Path(__file__).resolve().parent.parent
PROFILE=ROOT.parent.parent
USER=Path('C:/Users/groov')
OUT=ROOT/'.local/claude-import-2026-10-26'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'snapshots').mkdir(exist_ok=True)
SKIP=['**/plugins/**','**/cache/**','**/skills/**','**/pylib/**','**/node_modules/**',
      '**/.git/**','**/.venv/**','**/site-packages/**','**/backups/**','**/file-history/**',
      '**/.local/**','**/_CodexKnowledge/**','**/previews/detail_v1/work/**','**/previews/detail_v1/before/**']
SCOPES=[('claude',USER/'.claude'),('fs25',PROFILE),('scratch-history',USER/'AppData/Local/Temp/claude')]
files={}; scans=[]
for group,folder in SCOPES:
    args=['rg','--files',str(folder),'--hidden','--no-messages','-g','*.md','-g','*.markdown']
    for skip in SKIP:args+=['-g','!'+skip]
    p=subprocess.run(args,capture_output=True,text=True)
    found=[Path(f).resolve() for f in p.stdout.splitlines()]
    scans.append({'scope':group,'root':str(folder),'returncode':p.returncode,'found':len(found)})
    for f in found: files[f]=group

def scrub(text):
    # Redact recognizable token/key material, leaving environment-variable names,
    # commands using them, and descriptions of credential storage intact.
    patterns=[r'(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})',
              r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
              r'(?i)(?:s?ftp|https?)://[^\s/:]+:[^\s/@]+@']
    redactions=0
    for pattern in patterns:
        text,n=re.subn(pattern,'[REDACTED CREDENTIAL]',text);redactions+=n
    # Literal assignments only; preserve code/env references and placeholders.
    def assignment(m):
        nonlocal redactions
        value=m.group(3)
        if any(s in value for s in ('YOUR_','os.environ','FS25_SFTP_PASSWORD','get_password','<','${','$env:')):
            return m.group(0)
        redactions+=1
        return m.group(1)+m.group(2)+'[REDACTED CREDENTIAL]'+m.group(2)
    text=re.sub(r'''(?im)((?:password|passwd|api_key|access_token|secret)\s*[:=]\s*)(["'`])([^\r\n"'`]{6,})\2''',assignment,text)
    return text,redactions

records=[]; unique={}; total_redactions=0
for f,group in sorted(files.items(),key=lambda it:str(it[0]).lower()):
    raw=f.read_bytes(); text=raw.decode('utf-8-sig',errors='replace')
    safe,redactions=scrub(text);total_redactions+=redactions
    sha=hashlib.sha256(raw).hexdigest()
    content_sha=hashlib.sha256(safe.encode('utf-8')).hexdigest()
    slug=re.sub(r'[^a-zA-Z0-9_.-]+','_',f.stem)[:65]
    snapshot=unique.get(content_sha,f'snapshots/{content_sha[:16]}_{slug}.md')
    unique[content_sha]=snapshot
    (OUT/snapshot).write_bytes(safe.encode('utf-8'))
    title=next((l.strip('# ').strip() for l in safe.splitlines() if l.startswith('# ')),f.stem)
    description=re.search(r'^description:\s*(.+)',safe,re.M)
    if description:title=description.group(1).strip('"')
    headings=[l for l in safe.splitlines() if re.match(r'^#{1,3} ',l)]
    records.append({'source':str(f),'scope':group,'title':title,'source_sha256':sha,
                    'snapshot_sha256':content_sha,'snapshot':snapshot,'lines':len(safe.splitlines()),
                    'redactions':redactions,'headings':headings,'modified_utc_epoch':f.stat().st_mtime})

tool_root=PROFILE/'MOD PROJECTS/Library/_FS25Knowledge/tools'
tools=[str(p) for p in sorted(tool_root.rglob('*')) if p.is_file() and p.suffix.lower() in ('.py','.ps1','.lua','.exe')]
report={'created':'2026-10-26','scopes':scans,'source_count':len(records),'unique_snapshots':len(unique),
        'credential_redactions':total_redactions,'documents':records,'shared_tools':tools,
        'excluded':['Credential/settings files','Raw conversation JSONL','Browser profiles','Vendor/plugin/synced skills','File-history backups','Dependency trees']}
(OUT/'inventory.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
catalog=['# Imported Claude document catalog','',
         'Historical reference only. Read CURRENT_RULES.md before applying any instructions in these snapshots.',
         f'Found {len(records)} source documents; {len(unique)} distinct snapshots. Source attribution is certain for Claude memory files; other project Markdown is related working context, not independently proven Claude authorship.','']
for group,_ in SCOPES:
    catalog+=['## '+group,'']
    for r in records:
        if r['scope']!=group:continue
        catalog += [f"- [{r['title']}]({r['snapshot']}) — {r['lines']} lines",f"  - Original: `{r['source']}`"]
    catalog+=['']
(OUT/'CATALOG.md').write_text('\n'.join(catalog)+'\n',encoding='utf-8')
toc=['# Shared knowledge index: topic map','', 'Consult the original index before searching game files. Snapshot headings below make the 1,850-line reference searchable.','']
for r in records:
    if r['source'].replace('\\','/').endswith('Library/_FS25Knowledge/README.md'):
        toc += [f"[Saved copy]({r['snapshot']})",f"Original: `{r['source']}`",'']+r['headings']+['']
toc+=['## Existing shared command/helper files','']+['- `'+p+'`' for p in tools]
(OUT/'TOPICS_AND_TOOLS.md').write_text('\n'.join(toc)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('source_count','unique_snapshots','credential_redactions','scopes')},indent=2))
