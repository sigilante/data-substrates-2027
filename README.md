# Data for "Schema Change in the Wild" (Substrates 2027)

This repository holds the data and scripts behind N. E. Davis, *Schema Change in the Wild*, Substrates 2027 at ⟨Programming⟩ 2027. The paper is a census of state migrations in [Urbit](https://github.com/urbit/urbit) over 2013–2026:

- **111 system steps** in five components: Ames, Gall, Clay, Dojo, and Hood with its Kiln, Drum and Helm sub-cores.
- **38 userspace rows** in six agents: `%metadata-store`, `%graph-store`, `%azimuth`, `%eth-watcher`, `%roller` and `%chat-cli`.

Each step and row is classified by kind, flags and operator sequence. The definitions are in [`CODEBOOK.md`](CODEBOOK.md).

Every count in the paper comes from these files.

## Layout

```
data/       classifications, version histories, and the scripts that build and check them
review/     the adjudication interface, its inputs, and the author's exported decisions
figures/    scripts that draw the paper's figures and generate its tables, with their outputs
```

| File | What it is |
|---|---|
| `data/steps-adjudicated.csv` | **Final labels for the 111 system steps.** The paper's counts come from here. |
| `data/userspace-adjudicated.csv` | **Final labels for the 38 userspace rows.** |
| `data/steps.csv` | Agent A's labels for the system steps, written by `data/build_steps.py`. |
| `data/ops-reshape-discard.csv` | Agent A's operator decompositions for the reshape and discard steps, with evidence lines. |
| `data/second-coder-full.csv` | Agent B's labels for all 111 system steps. The `second-coder*.csv` files are its passes. `second-coder.csv` is its first, a 31-step stratified sample (`second-coder-sample.csv`). |
| `data/userspace-A.csv`, `data/second-coder-userspace.csv` | Agent A and Agent B labels for the userspace rows. |
| `data/version-landings.csv` | Date each state version merged to `develop`, by component. The `source` column records how each date was obtained. |
| `data/protocol-bumps.csv` | Old-Ames network protocol-version changes on the mainline, 2013–2019. |
| `review/export/decisions/*.json` | The author's 149 decisions, as exported from the review board. |
| `review/review-data.json` | Every item with both agents' labels and the diff that introduced it. |
| `review/migration-review-board.html` | The adjudication interface. Opened locally it is a read-only browser of `review-data.json`. |

### Columns in the adjudicated files

| Column | Meaning |
|---|---|
| `system`, `sub`, `step` | Component, sub-core (Hood only) and conversion, e.g. `Gall`, `""`, `16->17` |
| `date`, `date_kind` | Date of the merge to `develop` (`develop`) or of the introducing commit (`intro`) |
| `kind`, `flags`, `ops` | Final classification (see the codebook) |
| `lens` | Final composable verdict, `yes` or `no` (strict rule) |
| `decision` | `approve-A`, `approve-B`, `modify` or `veto` |
| `notes` | The author's note, if any |
| `agent_kind`, `agent_flags`, `agent_ops` | Agent A's original labels, for comparison |

## Sources

| Repository | Used for |
|---|---|
| [`urbit/urbit`](https://github.com/urbit/urbit) at `2a6d5dd226` (`develop`, 2026-04-13) | All code, history and dates. Its history includes the [`urbit/arvo`](https://github.com/urbit/arvo) repository, subtree-merged at `b3901ab42f` (2019-06-28) from arvo commit `c20e2a185f`. Kernel history before July 2019 is followed along arvo's mainline. |
| `urbit/urbit` pull requests and issues | Developer rationale quoted in the paper, read with `gh`. |
| [`inkandswitch/cambria-project`](https://github.com/inkandswitch/cambria-project) | The definitions of Cambria's ten operators (`src/lens-ops.ts`, `src/reverse.ts`). |

**Not used:**
- **[`urbit/archaeology`](https://github.com/urbit/archaeology)** (2013-08-15 to 2014-08-29). It preserves the pre-split repository with different commit hashes. The history here starts on 2013-09-28.
- **[`urbit/vere`](https://github.com/urbit/vere)**, the runtime, including its own on-disk epoch migrations.
- **[`tloncorp/tlon-apps`](https://github.com/tloncorp/tlon-apps)**, the current Groups. The userspace agents studied are the legacy Landscape agents in `urbit/urbit`'s `pkg/landscape`, plus the `%azimuth`, `%eth-watcher` and `%roller` agents in `pkg/arvo`.

## How the labels were made

1. **Agent A.** The first classification was assembled from several passes by Claude Opus 5.5 agents: per-component census passes, an operator-decomposition pass for reshape and discard steps, and mechanical rules for the `none`, `add`, `derive`, `repair` and `re-encode` kinds. The author spot-checked them.
2. **Agent B.** A second Claude Opus 5.5 agent classified every step and row from the code and its history. It never saw Agent A's labels.
3. **Author adjudication.** The author reviewed every item against the diff that introduced it, using the review board, and approved one agent's labels, modified them, or vetoed the item. All 149 were resolved by approval: Agent A 40 times and Agent B 109 times. On the 31 system steps where the agents disagreed about kind or verdict, the author sided with Agent B 30 times.

**Agreement between the agents** on the system steps (`python3 data/reliability.py data/second-coder-full.csv`):

| Measure | Agreement | Cohen's κ (95% bootstrap CI) |
|---|---|---|
| kind | 86% | 0.82 (0.74–0.90) |
| composable verdict | 86% | 0.71 (0.57–0.84) |
| judgement flag | — | 0.48 (0.28–0.67), the weakest |

Both agents are the same model family, so their errors are unlikely to be independent.

## Reproducing

```sh
make            # rebuild steps.csv, the adjudicated files, the tables, and the figures; print reliability
make check      # the same, then fail if any tracked output changed
```

These targets need only Python 3 and matplotlib.

Some targets also need a full clone of `urbit/urbit`, with history and the `develop` branch, checked out at or containing commit `2a6d5dd226` (2026-04-13):

```sh
git clone https://github.com/urbit/urbit ../urbit
make board URBIT=../urbit    # rebuild review-data.json and the review board (diffs per item)
make traces URBIT=../urbit   # recount protocol bumps; trace one component's state versions
```

**Two git pitfalls:**
- Paths before 2016, such as `arvo/ames.hoon`, are visible only with `git log --full-history`.
- Commit `7956adedee` (2020-11-25) pruned old migrations from seven vanes. Read them from its parent.

**Two inputs are not rebuilt by `make`:**
- `version-landings.csv` was assembled from `data/versions.py --first-parent` runs per component, patched where first-parent tracing gave artefactual dates. Its `source` column records each patch.
- The agent labels are coded by hand: Agent A's inline in `data/build_steps.py` and `data/ops-reshape-discard.csv`, and Agent B's in the `second-coder*.csv` files. They are data, not computation.

## Where the paper's numbers come from

| Paper element | Script | Input |
|---|---|---|
| Kinds by system (table) | `figures/fig_kinds.py` → `tbl-categories.tex` | `steps-adjudicated.csv` |
| Kinds by regime (table) | `figures/tbl_regimes.py` → `tbl-regimes.tex` | `steps-adjudicated.csv` |
| Cumulative kinds over time (figure) | `figures/fig_kinds.py` | `steps-adjudicated.csv` |
| Protocol churn and state migrations (figure) | `figures/figs.py` | `protocol-bumps.csv`, `version-landings.csv` |
| Version merges to `develop` (figure) | `figures/figs.py` | `version-landings.csv` |
| Composable shares (41–54%, 76%, and the variants) | `review/apply_decisions.py` and the codebook rules | `steps-adjudicated.csv`, `userspace-adjudicated.csv` |
| Inter-agent agreement | `data/reliability.py` | `steps.csv`, `second-coder-full.csv` |

## Licences

- **Code** (all `*.py`, `Makefile`, and `review/*.html`): MIT. See [`LICENSE`](LICENSE).
- **Data** (all `*.csv`, `*.json`, and the documentation): CC BY 4.0. See [`LICENSE-DATA.md`](LICENSE-DATA.md).

The quoted commit messages, PR text and code excerpts belong to their authors in `urbit/urbit`, which is MIT-licensed.

## Citation

Davis, N. E. 2027. *Schema Change in the Wild.* In Companion Proceedings of the 11th International Conference on the Art, Science, and Engineering of Programming (Substrates '27). ACM. DOI to be added.
