"""Cumulative migration steps by kind over time, one panel per system,
plus the matching count table (tbl-categories.tex).  Source: ../data/steps-adjudicated.csv (author-adjudicated; Agent A labels remain in steps.csv).
"""
import csv, datetime as dt, os
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, "..", "data", "steps-adjudicated.csv"))))
SYSTEMS = ["Ames", "Gall", "Clay", "Dojo", "Hood"]
KINDS = ["none", "add", "reshape", "discard", "derive", "repair", "re-encode"]
# Lines: four main kinds + "computed" (derive, repair, re-encode) = 5 series.
GROUP = {"add": "add", "reshape": "reshape", "discard": "discard", "none": "none",
         "derive": "computed", "repair": "computed", "re-encode": "computed"}
SERIES = ["add", "reshape", "discard", "none", "computed"]
COLOR = dict(zip(SERIES, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]))  # slots 1-5, validated
LABEL = {"computed": "derive / repair / re-encode"}
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 7.5, "axes.edgecolor": MUTED,
                     "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})

for r in rows:
    r["d"] = dt.date.fromisoformat(r["date"])
x0, x1 = dt.date(2014, 1, 1), dt.date(2026, 12, 31)

fig, axes = plt.subplots(1, 5, figsize=(7, 2.2), sharey=True)
ymax = max(Counter((r["system"], GROUP[r["kind"]]) for r in rows).values())
for ax, s in zip(axes, SYSTEMS):
    rs = sorted([r for r in rows if r["system"] == s], key=lambda r: r["d"])
    for k in SERIES:
        ds = [r["d"] for r in rs if GROUP[r["kind"]] == k]
        if not ds:
            continue
        xs = ds + [x1]                      # start at first occurrence
        ys = list(range(1, len(ds) + 1)) + [len(ds)]
        ax.plot([ds[0]], [1], marker="o", markersize=2.5, color=COLOR[k])
        ax.step(xs, ys, where="post", color=COLOR[k], linewidth=1.6, solid_capstyle="round")
    ax.set_title("%s (%d)" % (s, len(rs)), loc="left", fontsize=8, color=INK)
    ax.axvline(dt.date(2020, 12, 1), color=INK2, linewidth=0.6, linestyle=(0, (3, 2)))
    ax.yaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.set_xlim(x0, x1); ax.set_ylim(0, ymax + 1)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    ax.xaxis.set_major_locator(mdates.YearLocator(4)); ax.xaxis.set_major_formatter(mdates.DateFormatter("'%y"))
axes[0].set_ylabel("cumulative steps", color=INK2)
handles = [plt.Line2D([], [], color=COLOR[k], linewidth=1.6) for k in SERIES]
fig.legend(handles, [LABEL.get(k, k) for k in SERIES], loc="lower center", ncol=5,
           frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.06))
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(os.path.join(HERE, "fig-kinds-time.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(HERE, "fig-kinds-time.png"), dpi=200, bbox_inches="tight")

# ---- table view (doubles as the accessible table for the figure) ----
c = Counter((r["system"], r["kind"]) for r in rows)
lines = [r"\begin{tabular}{@{}l" + "r" * (len(SYSTEMS) + 1) + "@{}}", r"\toprule",
         "Kind & " + " & ".join(SYSTEMS) + r" & Total \\", r"\midrule"]
for k in KINDS:
    vals = [c[(s, k)] for s in SYSTEMS]
    lines.append(k + " & " + " & ".join(str(v) if v else "--" for v in vals) + " & %d \\\\" % sum(vals))
tot = [sum(c[(s, k)] for k in KINDS) for s in SYSTEMS]
lines += [r"\midrule", "Total & " + " & ".join(map(str, tot)) + " & %d \\\\" % sum(tot), r"\bottomrule", r"\end{tabular}"]
open(os.path.join(HERE, "tbl-categories.tex"), "w").write("\n".join(lines) + "\n")
print("ok", sum(tot))
