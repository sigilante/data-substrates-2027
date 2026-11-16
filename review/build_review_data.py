"""Assemble review-data.json: every step in data/steps.csv with both agents'
judgements, notes, and the diff that introduced it.  Read-only on the repo.

Delta source per step: the develop merge that landed its target version
(diff merge^1..merge), or else its introducing commit (commit^..commit).
Hunks are kept only if they mention the step's version numbers; cut at 240 lines.
"""
import csv, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
REPO = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("URBIT", "../urbit")
def git(*a): return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, errors="replace").stdout
steps = list(csv.DictReader(open(os.path.join(D, "steps.csv"))))
land = {(r["component"], int(r["version"])): r["commit"] for r in csv.DictReader(open(os.path.join(D, "version-landings.csv")))}
opsA = {(r["system"], r["sub"], r["step"]): r for r in csv.DictReader(open(os.path.join(D, "ops-reshape-discard.csv")))}
import glob
B = {}
for f in sorted(glob.glob(os.path.join(D, "second-coder*.csv"))):
    if f.endswith("second-coder-sample.csv"): continue
    for r in csv.DictReader(open(f)):
        B[(r["system"], r["sub"], r["step"])] = dict(r, _src=os.path.basename(f))
INTRO = {  # introducing commits for steps without a reliable develop merge
 ("Ames","old","nest->reset"):"dac62b87e2", ("Ames","old","furt0->fort1"):"bd4f650f5e", ("Ames","old","%0->%1"):"adc9da0b0c",
 ("Clay","","2->3"):"3834860410", ("Clay","","3->4"):"553a9db843", ("Clay","","4->5"):"67c5caada8", ("Clay","","5->6"):"1c8d229fb7",
 ("Gall","","0->1"):"096273cf4a", ("Gall","","1->2"):"4d71c1150c", ("Gall","","2->3"):"df970ed417", ("Gall","","3->4"):"9b0cb85a02",
 ("Gall","","4->5"):"3beb6ee65b", ("Gall","","5->6"):"22aa98e717", ("Gall","","6->7"):"bc929ba6db",
 ("Dojo","","untagged->0"):"5c47efdd29", ("Dojo","","0->1"):"8becbe80a4", ("Dojo","","1->2"):"0964b3fd6d", ("Dojo","","2->3"):"1d4891e4ef",
 ("Dojo","","3->4"):"e82003ec38", ("Dojo","","4->5"):"212276d813", ("Dojo","","5->6"):"6ab3ab7d5c", ("Dojo","","6->7"):"9f89dadc41",
 ("Dojo","","7->8"):"c29108a5f0", ("Dojo","","8->9"):"3120681b2b", ("Dojo","","9->10"):"a7da88f7f9",
 ("Hood","outer","0->1"):"651fb265e4", ("Hood","outer","1->2"):"b14606660a", ("Hood","outer","2->3"):"7fced14cfc", ("Hood","outer","3->4"):"003c4676b1",
 ("Hood","outer","4->5"):"096149713a", ("Hood","outer","5->6"):"eaf523e3c2", ("Hood","outer","6->7"):"3914c0c0dd", ("Hood","outer","7->8"):"47352a06ba",
 ("Hood","outer","8->9"):"7c3d608185", ("Hood","outer","9->10"):"a4e21da3f0", ("Hood","outer","10->11"):"1b8af7d78c", ("Hood","outer","11->12"):"7ffce92c37",
 ("Hood","outer","12->13"):"65c35bb50b", ("Hood","outer","27->28"):"2e654a67f4", ("Hood","outer","28->29"):"d08c6c0b9f",
 ("Hood","drum","0->1"):"651fb265e4", ("Hood","drum","1->2"):"0c8f77d187", ("Hood","helm","0->1"):"3914c0c0dd", ("Hood","helm","1->2"):"970075bbcd",
 ("Hood","kiln","0->1"):"11fa48f57b", ("Hood","kiln","9->10"):"0d757b4436",
 ("Hood","kiln","6->7"):"3b30b67a3e", ("Hood","drum","4->5"):"2c5510db64",  # corrected by the second coder
}
FILES = {"Ames": r"ames\.hoon$", "Gall": r"(gall|lull)\.hoon$", "Clay": r"clay\.hoon$", "Dojo": r"dojo\.hoon$",
         "outer": r"hood\.hoon$|drum\.hoon$", "kiln": r"kiln\.hoon$", "drum": r"drum\.hoon$", "helm": r"helm\.hoon$"}
def first_with(pattern, sub):
    paths = [f"pkg/arvo/lib/hood/{sub}.hoon", f"lib/hood/{sub}.hoon", f"lib/{sub}.hoon"]
    out = git("log", "--all", "--full-history", "--reverse", "--format=%h", "-S", pattern, "--", *paths).split()
    return out[0] if out else None
def nums(step):
    m = re.findall(r"\d+", step); return m[-2:] if len(m) >= 2 else m
out = []
for s in steps:
    k = (s["system"], s["sub"], s["step"]); comp = {"Ames":"ames","Gall":"gall","Clay":"clay","Dojo":"dojo"}.get(s["system"]) if not s["sub"] else s["sub"] if s["sub"] in ("kiln","drum") else None
    n = nums(s["step"]); tgt = int(n[-1]) if n else None
    if k in INTRO: c, rng, how = INTRO[k], None, "introducing commit"
    elif comp in ("kiln", "drum"):
        c = first_with(f"state-{tgt}", comp) or land.get((comp, tgt)); rng, how = None, "introducing commit"
    elif comp and (comp, tgt) in land: c = land[(comp, tgt)]; rng, how = (c + "^1", c), "develop merge"
    else: c, rng, how = None, None, "none found"
    if c and rng is None: rng = (c + "^", c)
    diff = ""; msg = ""; nk = tot = 0; trunc = False; url = ""
    if c:
        msg = git("log", "-1", "--format=%h %ad %an: %s", "--date=short", c).strip()
        url = "https://github.com/urbit/urbit/commit/" + git("rev-parse", c).strip()
        pathre = re.compile(FILES.get(s["sub"] or s["system"], r"\.hoon$"))
        files = [f for f in git("diff", "--name-only", *rng).splitlines() if pathre.search(f)]
        if files:
            d = git("diff", "-U2", *rng, "--", *files)
            hunks = re.split(r"(?m)^(?=@@)", d); head, hunks = hunks[0], hunks[1:]; tot = len(hunks)
            pat = re.compile("|".join(rf"(%|-|\b){x}\b" for x in n) + r"|-to-|prep|load") if n else re.compile(r"prep|load|old")
            keep = [h for h in hunks if pat.search(h)] or hunks; nk = len(keep)
            lines = "".join(keep).split("\n"); trunc = len(lines) > 240; diff = "\n".join(lines[:240])
    a_notes = "; ".join(x for x in [s.get("note", ""), (opsA.get(k) or {}).get("notes", "")] if x)
    b = B.get(k)
    out.append(dict(
        id=f"{s['system']}-{s['sub'] or 'main'}-{s['step']}".replace("->", "-to-").replace("/", "_").replace("%", "pct").replace(" ", ""),
        system=s["system"], sub=s["sub"], step=s["step"], date=s["date"], dateKind=s["date_kind"],
        A=dict(kind=s["kind"], flags=s["flags"], ops=s["ops"], notes=a_notes, confidence=(opsA.get(k) or {}).get("confidence", "")),
        B=dict(kind=b["kind"].strip(), flags=b["flags"].strip(), ops=b["ops"], notes=b["notes"], sample=b["_src"] == "second-coder.csv") if b else None,
        evidence=(opsA.get(k) or b or {}).get("evidence", ""),
        delta=dict(how=how, commit=msg, url=url, hunks=f"{nk} of {tot}", truncated=trunc, diff=diff)))
for o in out: o["layer"] = "system"
# ---- userspace rows (Agent A: data/userspace-A.csv; Agent B: second-coder-userspace.csv) ----
UA = os.path.join(D, "userspace-A.csv")
UPATH = {"metadata-store": r"metadata-store\.hoon$", "graph-store": r"graph-store\.hoon$", "azimuth": r"app/azimuth\.hoon$",
         "eth-watcher": r"eth-watcher\.hoon$", "roller": r"app/roller\.hoon$", "chat-cli": r"chat-cli\.hoon$"}
if os.path.exists(UA):
    for a in csv.DictReader(open(UA)):
        k = (a["system"], a["sub"], a["step"]); b = B.get(k); c = (a.get("commit") or "").strip()[:10]
        diff = msg = url = ""; nk = tot = 0; trunc = False
        if c:
            msg = git("log", "-1", "--format=%h %ad %an: %s", "--date=short", c).strip()
            url = "https://github.com/urbit/urbit/commit/" + git("rev-parse", c).strip()
            files = [f for f in git("diff", "--name-only", c + "^", c).splitlines() if re.search(UPATH.get(a["system"], r"\.hoon$"), f)]
            if files:
                d = git("diff", "-U2", c + "^", c, "--", *files)
                hunks = re.split(r"(?m)^(?=@@)", d)[1:]; tot = len(hunks)
                n = re.findall(r"\d+", a["step"])
                pat = re.compile("|".join(rf"(%|-|\b){x}\b" for x in n) + r"|on-load|prep|load") if n else re.compile(r"on-load|load")
                keep = [h for h in hunks if pat.search(h)] or hunks; nk = len(keep)
                lines = "".join(keep).split("\n"); trunc = len(lines) > 240; diff = "\n".join(lines[:240])
        out.append(dict(
            id=f"{a['system']}-main-{a['step']}".replace("->", "-to-").replace("/", "_").replace("(", "").replace(")", ""),
            system=a["system"], sub="", step=a["step"], date=a.get("date", ""), dateKind=a.get("date_kind", "intro"), layer="userspace",
            A=dict(kind=a["kind"].strip(), flags=a["flags"].strip(), ops=a["ops"], notes=a.get("notes", ""), confidence=a.get("confidence", "")),
            B=dict(kind=b["kind"].strip(), flags=b["flags"].strip(), ops=b["ops"], notes=b["notes"], sample=False) if b else None,
            evidence=a.get("evidence", ""),
            delta=dict(how="develop merge" if a.get("date_kind") == "develop" else "introducing commit", commit=msg, url=url,
                       hunks=f"{nk} of {tot}", truncated=trunc, diff=diff)))
json.dump(out, open(os.path.join(HERE, "review-data.json"), "w"))
print(len(out), "steps;", sum(1 for o in out if o["delta"]["diff"]), "with diffs;", sum(1 for o in out if o["B"]), "with coder B")
for o in out:
    if not o["delta"]["diff"]: print("  no diff:", o["id"], o["delta"]["how"], o["delta"]["commit"][:60])
