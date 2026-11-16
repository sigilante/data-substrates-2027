"""Count old-Ames network protocol-version changes on the mainline.

Before July 2019 the kernel lived in the separate urbit/arvo repository,
subtree-merged into urbit/urbit at b3901ab42f from arvo commit c20e2a185f.
We follow arvo's first-parent (mainline) history to 2019-06, then urbit/urbit
master's first-parent history until the old Ames was replaced by alef
(f035955a36, 2019-11-27).  A "bump" is any change of the protocol-version
constant between consecutive mainline commits that touch ames.hoon.
`labelled` = the mainline commit's subject mentions breach / flag day /
continuity; merge commits rarely carry such text, so it is a lower bound.

Usage: python3 protocol_bumps.py /path/to/urbit/urbit  -> protocol-bumps.csv
"""
import csv, os, re, subprocess, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("URBIT", "../urbit")
HERE = os.path.dirname(os.path.abspath(__file__))
PATHS = ["arvo/ames.hoon", "base/arvo/ames.hoon", "main/arvo/ames.hoon",
         "sys/vane/ames.hoon", "pkg/arvo/sys/vane/ames.hoon"]
PATS = [re.compile(r"\?>\s*=\((\d+)\s+vez\)"), re.compile(r"protocol-version=(\d+)"),
        re.compile(r"\(\s*(\d+)\s+vez\b"), re.compile(r"vez=(\d+)")]
LABEL = re.compile(r"breach|flag day|continuity", re.I)

def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True,
                          errors="replace").stdout

def mainline(tip, until=None):
    out = git("log", "--first-parent", "--format=%H\t%ad\t%s", "--date=short", tip, "--", *PATHS)
    rows = [l.split("\t", 2) for l in out.splitlines() if l][::-1]
    return [r for r in rows if until is None or r[1] < until]

def version(h):
    for p in PATHS:
        src = git("show", f"{h}:{p}")
        if src:
            for pt in PATS:
                m = pt.search(src)
                if m:
                    return int(m.group(1))
            return None
    return None

rows = mainline("c20e2a185f") + [r for r in mainline("master", "2019-11-27") if r[1] >= "2019-07-01"]
prev, out = None, []
for h, d, s in rows:
    v = version(h)
    if v is None:
        continue
    if prev is not None and v != prev:
        out.append(dict(date=d, commit=h[:10], old=prev, new=v,
                        labelled=int(bool(LABEL.search(s))), subject=s))
    prev = v
with open(os.path.join(HERE, "protocol-bumps.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]))
    w.writeheader(); w.writerows(out)
print(len(out), "bumps;", sum(r["labelled"] for r in out), "labelled")
