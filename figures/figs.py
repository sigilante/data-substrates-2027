"""Figures for the Substrates 2027 migration study.

Fig 1: three regimes -- protocol-version bumps (breaches) per year in old Ames
        vs. new state versions per year across OS components.
Fig 2: swimlane timeline of state-version landings per component, with events.

Data: version-landings.csv (from substrates-2027-versions.py --first-parent,
patched as noted in its `source` column) and the old-Ames protocol-bump counts
from the subagent census (approximate; see notes).
"""
import csv, datetime as dt
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BLUE, ORANGE = "#2a78d6", "#eb6834"          # categorical slots 1-2 (validated pair)
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
# Titles, labels and annotations in Helvetica; numeric tick labels (years,
# counts) in Computer Modern (matplotlib's bundled cmr10) to match the text.
NUM_FONT = "cmr10"
plt.rcParams.update({
    "font.family": "Helvetica", "font.size": 8, "pdf.fonttype": 42,
    "axes.formatter.use_mathtext": True, "mathtext.fontset": "cm", "axes.edgecolor": MUTED,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
})

rows = [r for r in csv.DictReader(open("../data/version-landings.csv"))]
for r in rows:
    r["date"] = dt.date.fromisoformat(r["date"])
    r["version"] = int(r["version"])

# ---- Fig 1 ---------------------------------------------------------------
years = list(range(2013, 2027))
pb = list(csv.DictReader(open("../data/protocol-bumps.csv")))   # mainline counts, see protocol_bumps.py
bumps = Counter(int(r["date"][:4]) for r in pb)
breach_labelled = Counter(int(r["date"][:4]) for r in pb if r["labelled"] == "1")
newv = Counter(r["date"].year for r in rows)

fig, (a, b) = plt.subplots(2, 1, figsize=(7, 3.6), sharex=True,
                           gridspec_kw={"hspace": 0.35})
other = [bumps.get(y, 0) - breach_labelled.get(y, 0) for y in years]
lab = [breach_labelled.get(y, 0) for y in years]
a.bar(years, lab, width=0.7, color=ORANGE, label="labelled breach / flag day (lower bound)",
      edgecolor="white", linewidth=1)
a.bar(years, other, bottom=lab, width=0.7, color="#f4b49a",
      label="other protocol bumps", edgecolor="white", linewidth=1)
a.set_title("Old Ames: network protocol-version bumps per year on the mainline (%d; ≥%d labelled breaches)" % (sum(bumps.values()), sum(breach_labelled.values())),
            loc="left", fontsize=8.5, color=INK)
a.legend(frameon=False, fontsize=7, loc="center right", bbox_to_anchor=(1.0, 0.45))
b.bar(years, [newv.get(y, 0) for y in years], width=0.7, color=BLUE,
      edgecolor="white", linewidth=1)
b.set_title("New state versions merged to develop per year (Ames, Gall, Clay, Hood, Kiln, Dojo, Drum; n=%d)" % len(rows),
            loc="left", fontsize=8.5, color=INK)
for ax in (a, b):
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    ax.axvspan(2012.5, 2018.5, color="#f6f5f2", zorder=-2)
    ax.axvspan(2018.5, 2020.95, color="#eeede9", zorder=-2)
    ax.axvline(2020.92, color=INK2, linewidth=0.8, linestyle=(0, (3, 2)))
b.set_xticks(years); b.set_xticklabels([str(y) for y in years])
for ax in (a, b):
    ax.tick_params(labelfontfamily=NUM_FONT)
ytop = a.get_ylim()[1]
for x, t in [(2015.5, "breach regime"), (2019.7, "rewrites"), (2023.7, "migration regime")]:
    a.text(x, ytop * 0.92, t, ha="center", va="top", fontsize=7.5, color=INK2, style="italic")
a.text(2021.0, ytop * 0.2, "last breach\n~2020.12", fontsize=6.5, color=INK2, va="center")
fig.savefig("fig-regimes.pdf", bbox_inches="tight"); fig.savefig("fig-regimes.png", dpi=200, bbox_inches="tight")

# ---- Fig 2 ---------------------------------------------------------------
order = ["ames", "gall", "clay", "hood", "kiln", "dojo", "drum"]
names = {"ames": "Ames (vane)", "gall": "Gall (vane)", "clay": "Clay (vane)",
         "hood": "Hood (agent)", "kiln": "  kiln", "dojo": "Dojo (agent)", "drum": "  drum"}
fig, ax = plt.subplots(figsize=(7, 2.9))
for i, c in enumerate(order):
    rs = sorted([r for r in rows if r["component"] == c], key=lambda r: r["version"])
    y = len(order) - 1 - i
    ax.hlines(y, rs[0]["date"], rs[-1]["date"], color=GRID, linewidth=1.2, zorder=1)
    cnt = Counter(r["date"] for r in rs)
    ds = sorted(cnt)
    ax.scatter(ds, [y] * len(ds), s=[14 + 16 * (cnt[d] - 1) for d in ds], color=BLUE,
               edgecolor="white", linewidth=0.8, zorder=3)
    last = rs[-1]
    ax.text(last["date"] + dt.timedelta(days=40), y, "%%%d" % last["version"],
            va="center", fontsize=7, color=INK)
events = [(dt.date(2020, 11, 30), "old migrations pruned\n+ last breach"),
          (dt.date(2025, 10, 31), "type-of-type\nmigration"),
          (dt.date(2026, 1, 20), "408K merged & reverted\n(relanded 2026-04-02)")]
for d, t in events:
    ax.axvline(d, color=INK2, linewidth=0.7, linestyle=(0, (3, 2)), zorder=0)
ax.text(dt.date(2020, 12, 20), len(order) - 0.35, events[0][1], fontsize=6.5, color=INK2, va="top")
ax.text(dt.date(2025, 10, 1), -0.95, events[1][1], fontsize=6.5, color=INK2, ha="right", va="bottom")
ax.text(dt.date(2026, 2, 20), -0.95, events[2][1], fontsize=6.5, color=INK2, va="bottom")
ax.set_yticks(range(len(order))); ax.set_yticklabels([names[c] for c in reversed(order)])
ax.set_ylim(-1.1, len(order) - 0.2)
ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_xlim(dt.date(2019, 6, 1), dt.date(2026, 12, 31))
ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", labelfontfamily=NUM_FONT)
# ax.set_title("State-version merges to develop, 2019–2026 (dot = merge adding versions, area $\\propto$ count; label = current version)",
#              loc="left", fontsize=8.5, color=INK)
fig.savefig("fig-lanes.pdf", bbox_inches="tight"); fig.savefig("fig-lanes.png", dpi=200, bbox_inches="tight")
print("ok")
