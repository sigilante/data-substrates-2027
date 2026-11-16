"""Trace state-version molds and ?=(%N -.old) tags through one file's history.

Usage: python3 versions.py <urbit-repo> <path> <out.json> [--first-parent]
Prints one line per change point; writes the change points as JSON.
"""
import subprocess, re, sys, json
repo, start = sys.argv[1], sys.argv[2]
def git(*a): return subprocess.run(['git','-C',repo,*a],capture_output=True,text=True,errors='replace').stdout
log = git('log',*([] if '--first-parent' not in sys.argv else ['--first-parent']),'--follow','--name-only','--format=@@%H|%ad|%an|%s','--date=short','--',start)
rows=[]; cur=None
for line in log.splitlines():
    if line.startswith('@@'): cur=line[2:].split('|',3)
    elif line.strip() and cur: rows.append((*cur,line.strip())); cur=None
rows.reverse()
pat = re.compile(r'^\s*\+\$\s+([a-z][a-z0-9-]*?)-(\d+)\b', re.M)
prev=None; out=[]
for h,d,a,s,path in rows:
    if path.endswith('behn.hoon'): continue
    src = git('show',f'{h}:{path}')
    names = sorted(set(f'{m[0]}-{m[1]}' for m in pat.findall(src)))
    tags = sorted(set(int(x) for x in re.findall(r'\?=\(%(\d+)\s+-\.old', src)))
    key=(tuple(names),tuple(tags))
    if key!=prev:
        out.append(dict(h=h[:10],d=d,a=a,s=s[:70],path=path,names=names,tags=tags))
        prev=key
json.dump(out,open(sys.argv[3],'w'),indent=1)
for o in out: print(o['d'],o['h'],o['path'].split('/')[-1],'| tags',o['tags'][-3:] if o['tags'] else '-','| names',len(o['names']),(o['names'][-3:]),'|',o['s'][:50])
