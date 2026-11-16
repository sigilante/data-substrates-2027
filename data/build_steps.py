"""Build data/steps.csv: one row per migration step, five systems.

Kinds use the paper's 7-kind scheme (none, add, reshape, discard, derive,
repair, re-encode); flags are e (emits-moves), o (outside-read),
j (judgement).  Classifications transcribe the census in
~/Code/urbit/substrates-2027-notes.md (subagent-classified, spot-checked;
second-coder pass still TODO).

Dates: `date` is the merge of the step's target version to develop (the integration branch) where
version-landings.csv has it (date_kind=develop); otherwise the introducing
commit on any branch (date_kind=intro).  Pre-2019 steps are intro dates.
"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
land = {}
for r in csv.DictReader(open(os.path.join(HERE, "version-landings.csv"))):
    land[(r["component"], int(r["version"]))] = r["date"]

def L(comp, v, fallback=None):
    """Master landing date of version v, else the fallback intro date."""
    if (comp, v) in land:
        return land[(comp, v)], "develop"
    return fallback, "intro"

rows = []
def add(system, sub, step, kind, flags, date, date_kind, note=""):
    rows.append(dict(system=system, sub=sub, step=step, kind=kind, flags=flags,
                     date=date, date_kind=date_kind, note=note))

# ---- Gall (0->20) -------------------------------------------------------
gall = {1: ("none", ""), 2: ("add", ""), 3: ("none", ""), 4: ("discard", "j"),
        5: ("discard", "j"), 6: ("discard", "j"), 7: ("add", ""), 8: ("reshape", ""),
        9: ("reshape", ""), 10: ("discard", "j"), 11: ("reshape", ""), 12: ("add", ""),
        13: ("add", ""), 14: ("add", ""), 15: ("add", ""), 16: ("reshape", "j"),
        17: ("discard", "j"), 18: ("add", ""), 19: ("repair", ""), 20: ("re-encode", "")}
for v, (k, f) in gall.items():
    d, dk = L("gall", v)
    add("Gall", "", f"{v-1}->{v}", k, f, d, dk,
        {6: "live core replaced by on-save vase", 16: "namespace migration #6852",
         17: "buggy; repaired by 18->19 (#7271)"}.get(v, ""))

# ---- Ames: old lineage (breach era) then 1->31 --------------------------
add("Ames", "old", "nest->reset", "discard", "", "2014-04-11", "intro", "dac62b87e2 ~&(%ames-reset ..^$)")
add("Ames", "old", "furt0->fort1", "add", "", "2017-05-16", "intro", "bd4f650f5e adds bad")
add("Ames", "old", "%0->%1", "add", "", "2018-04-25", "intro", "adc9da0b0c adds ten; later reverted")
ames = {2: ("add", ""), 3: ("reshape", ""), 4: ("discard", "j"), 5: ("repair", ""),
        6: ("derive", "o"), 7: ("add", ""), 8: ("add", "e"), 9: ("add", ""), 10: ("add", ""),
        11: ("add", ""), 12: ("reshape", ""), 13: ("re-encode", "o"), 14: ("reshape", ""),
        15: ("derive", "o"), 16: ("repair", ""), 17: ("reshape", "eo"), 18: ("none", "e"),
        19: ("reshape", "j"), 20: ("add", "e"), 21: ("discard", "j"), 22: ("add", "e"),
        23: ("reshape", "e"), 24: ("derive", "j"), 25: ("add", "j"), 26: ("add", ""),
        27: ("none", "eo"), 28: ("add", ""), 29: ("none", "eo"), 30: ("derive", ""),
        31: ("discard", "j")}
for v, (k, f) in ames.items():
    d, dk = L("ames", v)
    add("Ames", "", f"{v-1}->{v}", k, f, d, dk)

# ---- Clay (2->16) -------------------------------------------------------
clay = {3: ("reshape", "ej"), 4: ("reshape", ""), 5: ("discard", ""), 6: ("none", ""),
        7: ("discard", ""), 8: ("add", ""), 9: ("discard", ""), 10: ("add", "e"),
        11: ("reshape", "j"), 12: ("add", ""), 13: ("add", "j"), 14: ("reshape", ""),
        15: ("add", "j"), 16: ("re-encode", "")}
clay_intro = {3: "2020-06-03", 4: "2020-07-22", 5: "2020-08-28", 6: "2020-11-09"}
for v, (k, f) in clay.items():
    d, dk = L("clay", v, clay_intro.get(v))
    add("Clay", "", f"{v-1}->{v}", k, f, d, dk, "relabelled none: removes pun already emptied by 4->5" if v == 6 else "")

# ---- Dojo (untagged->10); intro dates, since early tags predate the idiom --
dojo = [("untagged->0", "reshape", "", "2015-09-03"), ("0->1", "discard", "", "2015-09-09"),
        ("1->2", "discard", "", "2015-09-11"), ("2->3", "discard", "", "2015-09-29"),
        ("3->4", "add", "", "2015-11-25"), ("4->5", "discard", "", "2016-11-30"),
        ("5->6", "add", "", "2020-05-06"), ("6->7", "discard", "j", "2021-09-23"),
        ("7->8", "discard", "j", "2021-10-06"), ("8->9", "reshape", "ej", "2022-02-20"),
        ("9->10", "re-encode", "j", "2025-10-31")]
for s, k, f, d in dojo:
    add("Dojo", "", s, k, f, d, "intro", {"7->8": "replay of 6->7", "1->2": "relabelled discard: arm only resets poy; reshape went into the %0 arm via hotfix a5f5e08d70"}.get(s, ""))

# ---- Hood: outer (non-delegated steps) + kiln, drum, helm ---------------
hood_outer = [("0->1", "none", "", "2016-05-02"), ("1->2", "none", "e", "2019-12-13"),
              ("2->3", "none", "e", "2020-02-14"), ("3->4", "none", "e", "2020-04-27"),
              ("4->5", "none", "", "2020-05-22"), ("5->6", "none", "e", "2020-06-17"),
              ("6->7", "reshape", "", "2020-06-17"), ("7->8", "none", "e", "2020-06-24"),
              ("8->9", "none", "e", "2020-07-28"), ("9->10", "none", "e", "2020-08-19"),
              ("10->11", "none", "e", "2020-11-02"), ("11->12", "none", "e", "2021-01-19"),
              ("12->13", "none", "e", "2021-05-18"), ("27->28", "none", "eo", "2025-06-26"),
              ("28->29", "add", "", "2026-02-19")]
for s, k, f, d in hood_outer:
    add("Hood", "outer", s, k, f, d, "intro")
kiln = {1: ("discard", "ej"), 2: ("add", ""), 3: ("discard", ""), 4: ("add", ""),
        5: ("reshape", ""), 6: ("add", ""), 7: ("reshape", ""), 8: ("derive", "o"),
        9: ("none", ""), 10: ("discard", "ej"), 11: ("add", "")}
for v, (k, f) in kiln.items():
    d, dk = L("kiln", v)
    add("Hood", "kiln", f"{v-1}->{v}", k, f, d, dk)
drum = [("0->1", "repair", "j", "2016-05-02", "intro"), ("1->2", "reshape", "", "2016-10-19", "intro")]
for v, (k, f) in {4: ("discard", ""), 5: ("reshape", ""), 6: ("add", "e")}.items():
    d, dk = L("drum", v)
    drum.append((f"{v-1}->{v}" if v != 4 else "2/3->4", k, f, d, dk))
for s, k, f, d, dk in drum:
    add("Hood", "drum", s, k, f, d, dk)
add("Hood", "helm", "0->1", "discard", "", "2020-06-17", "intro")
add("Hood", "helm", "1->2", "none", "e", "2021-12-17", "intro")

# ---- operator sequences (ops) and lens expressibility -----------------
# Vocabulary: Cambria's ten operators, used forward-only, plus five additions
# that Cambria cannot express.  Mechanical marking: add -> add; none -> (empty,
# identity); derive/repair -> compute (+ read if outside-read); re-encode ->
# re-encode.  reshape/discard steps need their code re-read: ops = TODO.
CAMBRIA = {"add", "remove", "rename", "hoist", "plunge", "wrap", "head", "in", "map", "convert"}
EXTRA = {"filter", "container", "compute", "read", "re-encode"}
OPS_OVERRIDE = {}   # (system, sub, step) -> "op;op;..." once re-read
_ovr = os.path.join(HERE, "ops-reshape-discard.csv")
if os.path.exists(_ovr):
    for o in csv.DictReader(open(_ovr)):
        OPS_OVERRIDE[(o["system"], o["sub"], o["step"])] = o["ops"]
import re
def op_names(seq):
    """All operator names in a (possibly nested) sequence like in(f: map(add;filter))."""
    return re.findall(r"[a-z][a-z-]*(?=\(|;|\)|$)", re.sub(r"\b[\w-]+:", "", seq))
for r in rows:
    key = (r["system"], r["sub"], r["step"])
    if key in OPS_OVERRIDE:
        r["ops"] = OPS_OVERRIDE[key]
    elif r["kind"] == "none":
        r["ops"] = ""
    elif r["kind"] == "add":
        r["ops"] = "add"
    elif r["kind"] in ("derive", "repair"):
        r["ops"] = "compute;read" if "o" in r["flags"] else "compute"
    elif r["kind"] == "re-encode":
        r["ops"] = "re-encode"
    else:
        r["ops"] = "TODO"
    ops = op_names(r["ops"]) if r["ops"] else []
    assert all(o in CAMBRIA | EXTRA | {"TODO"} for o in ops), (key, ops)
    if "TODO" in ops:
        r["lens"] = "?"
    elif r["flags"] or any(o in EXTRA for o in ops):
        r["lens"] = "no"
    else:
        r["lens"] = "yes"

missing = [r for r in rows if not r["date"]]
assert not missing, missing
with open(os.path.join(HERE, "steps.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
from collections import Counter
for sysname in ["Ames", "Gall", "Clay", "Dojo", "Hood"]:
    c = Counter(r["kind"] for r in rows if r["system"] == sysname)
    print(sysname, sum(c.values()), dict(c))
print("total", len(rows))
