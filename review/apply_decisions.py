"""Turn the Review Board's decisions into the adjudicated dataset.

Input: a directory of decision documents exported from the Review Board
artifact (one JSON per step, as ArtifactData `list` with `out_dir` writes
them: <dir>/decisions/<id>.json), plus data/steps.csv and
data/second-coder.csv.

Output: data/steps-adjudicated.csv, with the author's final kind, flags, ops
and composable verdict for every step, the decision taken (approve-A,
approve-B, modify, veto), and notes.  Vetoed steps are kept with
kind=vetoed so they can be excluded explicitly.  Prints a summary of how
often each agent's judgement was accepted.

Usage: python3 apply_decisions.py <export_dir>
"""
import csv, json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
C = {"add", "remove", "rename", "hoist", "plunge", "wrap", "head", "in", "map", "convert"}
X = {"filter", "container", "compute", "read", "re-encode"}
def ops(s): return [t for t in re.findall(r"[a-z][a-z-]*", (s or "").lower()) if t in C | X]
def sid(r): return f"{r['system']}-{r['sub'] or 'main'}-{r['step']}".replace("->", "-to-").replace("/", "_").replace("%", "pct").replace(" ", "")

export = sys.argv[1]
dec = {}
for root, _, files in os.walk(export):
    for f in files:
        if f.endswith(".json"):
            doc = json.load(open(os.path.join(root, f)))
            body = doc.get("data", doc)
            dec[os.path.splitext(f)[0]] = body
steps = list(csv.DictReader(open(os.path.join(D, "steps.csv"))))
out, tally, missing = [], Counter(), []
for s in steps:
    d = dec.get(sid(s))
    if not d or not d.get("decision"):
        missing.append(sid(s)); continue
    tally[d["decision"]] += 1
    if d["decision"] == "veto":
        kind, flags, o, comp = "vetoed", "", "", ""
    else:
        kind, flags, o = d.get("kind", ""), "".join(sorted(set(d.get("flags", "")))), d.get("ops", "")
        comp = "yes" if set(ops(o)) <= C and not flags else "no"
    out.append(dict(system=s["system"], sub=s["sub"], step=s["step"], date=s["date"], date_kind=s["date_kind"],
                    kind=kind, flags=flags, ops=o, lens=comp, decision=d["decision"], notes=d.get("notes", ""),
                    agent_kind=s["kind"], agent_flags=s["flags"], agent_ops=s["ops"]))
with open(os.path.join(D, "steps-adjudicated.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]) if out else ["system"]); w.writeheader(); w.writerows(out)
# ---- userspace rows: kept separate, never added to system steps ----
uid = lambda r: f"{r['system']}-main-{r['step']}".replace("->", "-to-").replace("/", "_").replace("(", "").replace(")", "")
UA = os.path.join(D, "userspace-A.csv"); uout = []
if os.path.exists(UA):
    for a in csv.DictReader(open(UA)):
        d = dec.get(uid(a))
        if not d or not d.get("decision"): missing.append(uid(a)); continue
        tally["userspace " + d["decision"]] += 1
        if d["decision"] == "veto": kind, flags, o, comp = "vetoed", "", "", ""
        else:
            kind, flags, o = d.get("kind", ""), "".join(sorted(set(d.get("flags", "")))), d.get("ops", "")
            comp = "yes" if set(ops(o)) <= C and not flags else "no"
        uout.append(dict(system=a["system"], sub="", step=a["step"], date=a.get("date", ""), date_kind=a.get("date_kind", ""),
                         kind=kind, flags=flags, ops=o, lens=comp, decision=d["decision"], notes=d.get("notes", ""),
                         agent_kind=a["kind"], agent_flags=a["flags"], agent_ops=a["ops"]))
    if uout:
        with open(os.path.join(D, "userspace-adjudicated.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(uout[0])); w.writeheader(); w.writerows(uout)
n = len(out)
print(f"{n} of {len(steps)} system steps and {len(uout)} userspace rows decided; {len(missing)} pending")
print("decisions:", dict(tally))
kept = [r for r in out if r["kind"] != "vetoed"]
if kept:
    yes = sum(r["lens"] == "yes" for r in kept)
    print(f"composable (strict): {yes} of {len(kept)} ({100 * yes / len(kept):.0f}%)")
    print("agent A kind accepted:", sum(r["kind"] == r["agent_kind"] for r in kept), "of", len(kept))
