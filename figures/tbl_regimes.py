"""Kind-by-regime crosstab (tbl-regimes.tex) from ../data/steps-adjudicated.csv.

Regimes are cut by the step's date (date_kind says whether it is a develop
merge or an introducing commit): breach before 2019, rewrite 2019--2020,
migration 2021 onward.
"""
import csv, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, "..", "data", "steps-adjudicated.csv"))))
KINDS = ["none", "add", "reshape", "discard", "derive", "repair", "re-encode"]
REGIMES = [("breach", "Breach", "${\\le}2018$"), ("rewrite", "Rewrite", "2019--20"), ("migration", "Migration", "2021--")]

def regime(d):
    return "breach" if d < "2019" else "rewrite" if d < "2021" else "migration"

c = Counter((r["kind"], regime(r["date"])) for r in rows)
n = Counter(regime(r["date"]) for r in rows)
def share(pred):
    k = Counter(regime(r["date"]) for r in rows if pred(r))
    return [f"{k[g]} ({round(100 * k[g] / n[g])}\\%)" for g, _, _ in REGIMES]

L = [r"\begin{tabular}{@{}lrrrr@{}}", r"\toprule",
     "Kind & " + " & ".join(f"{t}" for _, t, _ in REGIMES) + r" & Total \\",
     " & " + " & ".join(f"\\footnotesize {y}" for _, _, y in REGIMES) + r" & \\", r"\midrule"]
for k in KINDS:
    v = [c[(k, g)] for g, _, _ in REGIMES]
    L.append(f"\\texttt{{{k}}} & " + " & ".join(str(x) if x else "--" for x in v) + f" & {sum(v)} \\\\")
L += [r"\midrule", "Steps & " + " & ".join(str(n[g]) for g, _, _ in REGIMES) + f" & {len(rows)} \\\\",
      "Composable & " + " & ".join(share(lambda r: r["lens"] == "yes")) + r" & \\",
      "Emit moves & " + " & ".join(share(lambda r: "e" in r["flags"])) + r" & \\",
      "Judgement & " + " & ".join(share(lambda r: "j" in r["flags"])) + r" & \\",
      r"\bottomrule", r"\end{tabular}"]
open(os.path.join(HERE, "tbl-regimes.tex"), "w").write("\n".join(L) + "\n")
dk = Counter((regime(r["date"]), r["date_kind"]) for r in rows)
print("ok;", dict(n), "; intro-dated:", {g: dk[(g, "intro")] for g, _, _ in REGIMES})
