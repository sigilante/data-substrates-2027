# Codebook

This is how each state-migration step is classified. Every **system step** (one `N→N+1` conversion in Ames, Gall, Clay, Dojo or Hood) and every **userspace row** gets three things:

- exactly one **kind**;
- any number of **flags**;
- an **operator sequence**.

A userspace row can span several incoming versions, e.g. `0-4->8`. Rows and steps are reported separately and never added together.

## Kinds: what the step does to the data

| Kind | Definition |
|---|---|
| `none` | Changes only the version tag, often to run a one-time action. |
| `add` | Adds field(s) with a constant or bunt default. |
| `reshape` | Deterministically restructures existing data. |
| `discard` | Drops a field, a cache, queued work, or the whole state, including refusing to load an old version. |
| `derive` | Computes new values from existing state, including by reading other modules. |
| `repair` | Fixes state left wrong by a bug, or infers meaning from content. |
| `re-encode` | Rewrites data because the compiler's type representation changed. |

When a step mixes kinds, it gets the kind that best describes its main purpose. Its operator sequence records the rest.

## Flags: what else the step needs

| Flag | Name | Definition |
|---|---|---|
| `e` | emits-moves | Sends moves during the upgrade: timers, pokes to other agents or to itself, subscription kicks. |
| `o` | outside-read | Reads another vane's or agent's state while loading. `now` alone does not count. |
| `j` | judgement | Encodes an operational decision a schema cannot know, such as dropping in-flight work, inferring from names, or a policy reset. |

## Operators: how the data changes, used forward only

The first ten are Cambria's lens operators (Litt, van Hardenberg and Henry, PaPoC '21; `inkandswitch/cambria-project`, `src/lens-ops.ts`). The last five have no Cambria counterpart.

| Operator | Effect | In Cambria? |
|---|---|---|
| `add` | Add a field with a default | yes |
| `remove` | Drop a field | yes |
| `rename` | Rename a field | yes |
| `hoist` | Move a field out of a nested record into its parent | yes |
| `plunge` | Move a field into a nested record | yes |
| `wrap` | Scalar → one-element list | yes |
| `head` | List → its first element | yes |
| `in(f: …)` | Apply operators to one field | yes |
| `map(…)` | Apply operators to every element of a collection | yes (Cambria: lists only) |
| `convert` | Map values through a fixed, finite lookup table | yes |
| `filter` | Drop the elements of a collection that fail a predicate | no |
| `container` | Change collection type (list, set, map, queue, ordered map, trie) | no |
| `compute` | Produce a value by running code over existing state, `now`, or other values | no |
| `read` | Read another vane's or agent's state | no |
| `re-encode` | Rewrite values under a changed compiler type representation | no |

**Conventions:**
- A version-tag bump is not an operator.
- Setting a field to its bunt or `~` is `remove;add`.
- Setting a constant mode flag is `convert`.
- A wholesale reset removes every field and then adds defaults.

Only vocabulary words count as operators. The coders sometimes wrote arguments, e.g. `add(snub)`; the scripts ignore anything that is not an operator name.

## Composable

A step is **composable** if its operator sequence uses only Cambria's ten operators **and** it carries no flag. This is the `lens` column (`yes` or `no`) in the data files.

The test is lenient in two ways. Report the variants alongside the strict figure:

- **Syntactic only.** It checks that a step *can be written* with Cambria's operators. It constructs no reverse direction and checks no lens laws.
- **`map` over any collection.** It lets `map` apply to Hoon maps, sets and queues as well as lists, and lets `convert` and `wrap` apply to tagged unions and units.

The variants:

| Variant | Rule |
|---|---|
| strict (headline) | Cambria operators only, no flags |
| judgement allowed | Cambria operators only, no `e` or `o` flag |
| operators only | Cambria operators only, flags ignored |
| list-only `map` | strict, and no `map` at all, since every `map` in this corpus is over a Hoon map, set or queue |
| excluding `none` | strict, over the steps whose kind is not `none` |

## Regimes (for the crosstab)

Steps are binned by date:

- **breach:** before 2019
- **rewrite:** 2019–2020
- **migration:** 2021 onward

`date_kind` says whether a date is the step's merge to `develop` or its introducing commit.
