# Main measurement (n = 93,733): what is verified, and what each next step needs

Recomputed 2026-11-03 with `audit/scripts/recount_main_prefix.py` (standard library, read-only), which imports
the companion's frozen `rewardfail/s2/report.py` unchanged. Output: `audit/results/main_prefix_recount.json`.

## Four kinds of evidence (do not mix them)

| Level | Meaning | What it currently covers |
|---|---|---|
| A. Report-level check | Reading or cross-checking numbers inside a report | formal `k = 1`, `u = 18`, bounds, `u_ids`, class totals of the 2026-10-08 report |
| B. Row-record recount | Recomputing from per-row records with the frozen rule | default pass (93,733 rows; Table 2) from both the companion's derived rows and the supplied raw rows; **pre-correction** reference pass (33,487 rows): `k = 1`, `u = 9,573` |
| C. Raw-event reconstruction | Re-running the final `analyze.py` over parent/child/guard event logs | **not possible yet** for the corrected reference classes |
| D. Re-execution | Scoring the inputs again | not done for the main sample (dataset not reachable from this environment) |

## Results of the level-B recount

| Item | Result |
|---|---|
| Default rows (supplied raw) | 93,733 + 1 warm-up; value-identical to the companion's derived default rows |
| Reference rows (supplied raw, pre-correction) | 33,487 + 7 warm-ups = 32,487 default non-one rows + 1,000 default-one controls; ids ⊂ default ids |
| Frozen pairing on pre-correction classes | `k = 1` (`m-377a40b9adf29ef8`, same as the formal report), `u = 9,573` = 9,559 guard-stopped + 11 reference comparison timeouts + 2 interrupted twice + 1 reference-parse timeout |
| Matches the 6c416b2 diagnostic's "official" metric | yes (`k = 1`, `u = 9,573`, identical `u_reasons`) |
| Reported correction | 9,866 reference rows reclassified (9,863 non-warm-up): 9,551 → normal 0, 308 → score 1, 3 → comparison timeout, 3 → comparison error, 1 → answer-parse error |
| Aggregate reconciliation | pre-correction totals + reported changes = formal totals exactly, once the 7 warm-up rows are included in the change counts and excluded from the formal totals |
| Guard events | the reference pass recorded only 4 `budget_kill` events (6c416b2 diagnostic `resynth_stats`); the old rule attached each to every row the killed pool process had scored |
| `ids_sha256` in `pass_spec.json` | not reproducible from file order or sorted order; it hashes the sampling order, which needs `sample_map.tsv` (not supplied) — no evidence of a data problem either way |
| Error-inclusive sensitivity | pre-correction: 12 reference error zeros (row-level). Post-correction: 16 (formal aggregates only) → `u_err = 34`, `[1/n, 35/n] = [1.07e-5, 3.73e-4]`, binomial-model upper bound 4.95e-4, verdict unchanged |

The formal `u_ids` were used **only** as a labelled consistency check (`all_in_uncorrected_u: true`; 15 of 18 have
the same reference class before correction, the other 3 were guard-stopped before correction). They were never used
to fill or alter any row.

## Interval vs bound

* `[k/n, (k+u)/n]` is a **finite-sample identification interval** for the realised 93,733 rows: unresolved rows go to
  either end. No sampling model, no independence assumption, nothing about other corpora.
* The one-sided 95% Clopper–Pearson bound on `(k+u)/n` (2.97e-4) and the two-sided interval for `k/n` are
  **binomial working-model bounds**: they assume independent rows with a common rate. They are used only by the
  pre-declared decision rule.
* Same denominator `n = 93,733` (rows, not questions) for both; the pooled 193,767-answer endpoints use answers
  as the unit and are descriptive only (32 unresolved answers = 21 questions).

## Smallest inputs for each next step

All paths are inside the original run directory `stage2/runs/main-20261007-202545/` (layout read from the
companion's `rewardfail/s2/analyze.py::load_run`).

### ① Verify the corrected k/u row by row (level C for the metric only)

The final `analyze.py` (`f6e70c6c…`) decides a row's reference class from the whole reference pass. Because
`load_run(strict=True)` checks per-file sequence numbers, filtered excerpts would mark rows incomplete; the files
must be complete. Needed, from `reference/`:

| Path / pattern | Format | Used for |
|---|---|---|
| `reference/obs-*.jsonl` | JSONL, parent events (`pool_new`, `submit`, `wait_end`, `proc_exit`, …, `seq`) | attempt outcomes, pool generations, registered pids, `t_wait_end` |
| `reference/child_logs/child-*.jsonl` | JSONL, child events (`task_start`, `step_*`, `task_end`, `fseq`) | `returned_at` (child `t_end`), result matching |
| `reference/guard*.jsonl` | JSONL, guard events incl. 4 `budget_kill` (`pid`, `t`) | which attempts were killed |
| `reference/results-*.jsonl`, `reference/warm-*.jsonl` | JSONL | final results, worker assignment, warm-ups |
| `reference/interrupts.json` | JSON | already supplied |

Plus file-level SHA-256 of each, and (from `default/`) nothing more: default classes are already reproduced.
**Lighter alternative** (weaker, still useful): list only the sizes and hashes of these files first, so that
the transfer can be planned; `audit/scripts/inventory_run_dir.py` (below) prints that list without reading content.

### ② Audit the budget-attribution correction itself

Same files as ①. In addition the pre-correction `analyze.py` is needed to show the before/after difference on
real events; it is now available as `author-inputs/history/9a88991/code.tar.gz` (SHA-256 of `analyze.py`
`a8fa21e2…`, equal to the run lock). With ① this allows re-running both versions over the same events
(`tests/test_s2_budget.py` already does this on synthetic events and now passes 18/18 on Linux).

### ③ Reproduce all eight passes

Complete event directories of every pass, not only `reference/`: `default/`, `reference/`, `limit2s/`,
`limit10s/`, `replay1/`–`replay3/`, `retest/` (each with `obs-*`, `child_logs/`, `guard*`, `results-*`,
`warm-*`, `interrupts.json`, `pass_spec.json`, `pass_done.json`), plus `run.json`, `report.json`, and for
re-*execution* additionally `sample_map.tsv` and the OpenR1-Math-220k shards listed in `data_manifest.tsv`.
This is the ~2 GB tree; it is not needed for ① or ②.
