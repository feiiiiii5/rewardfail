# E3-L: Linux replay of the human-labelled extracted-answer set (protocol fixed before running)

Written 2026-11-03 before any E3-L row was scored. This is a **new verification run
on a different platform**, not a reproduction of the historical macOS arm64 run and
not a ground-truth measurement.

| Item | Fixed value |
|---|---|
| Input | `gold_set_1p5b_manual_labeled.csv` from `ethxin0011/rlvr_group_correlation@ccb3302` (MIT); SHA-256 `90fca106cb07f031a7ac169e009e6ab9cc0839126912218d0763b0ab6e037005`; must contain 5,556 rows / 3,041 groups / 2,822 positive labels |
| Sample unit | one CSV row (one extracted answer); id `e3-%05d` in file order (same rule as companion `s2_e3.py`) |
| Selection | all rows; no filtering |
| Presentations | `raw` = `raw_answer` verbatim; `boxed` = `\boxed{raw_answer}` unless `raw_answer` already contains `\boxed` (those 24 rows reuse the raw result, as in the paper) |
| Reference | `gt_answer`, passed to the wrapper unchanged |
| Scorer | PR #8015 wrapper `verl/utils/reward_score/math_verify.py` at `0c4c3d4` (SHA-256 `f04f57d5…`), Math-Verify 0.9.0, SymPy 1.14.0; the child function is an instrumented copy of `_verify_in_subprocess` executing the same `parse`/`verify` calls and capturing Math-Verify log records |
| Conditions | `L5`: library parse/compare limits 5 s, outer 30 s (shipped defaults); `L60`: 60 s / 60 s, outer 300 s (diagnostic) ; `timeout_score = 0` |
| Order | raw-L5, boxed-L5, raw-L60, boxed-L60; rows in file order; one controller, sequential calls, one wrapper pool per pass, warmed with one discarded trivial row |
| Repeats / seed | 1 / none (deterministic order) |
| Resource limits | container 4 vCPU, ~15 GiB, no swap; no memory guard; no intervention planned |
| Recorded per row | id, presentation, condition, score, wall seconds, exception type, log categories per step, pool generation |
| Metrics | Table 3 cells: label-positive/score-0, label-negative/score-1, disagreement, failure-event zeros; row-level agreement of score and event flag with historical `records/e3-20261008-codex/*-observe|*-reference/rows.jsonl` |
| Interpretation limits | event = Math-Verify logged timeout/error; it is not a training failure rate; label disagreement is not verifier error rate (labels not re-adjudicated); Linux results do not validate the macOS timing claims |
| Output | `audit/results/e3_linux/` (new directory); historical records are read-only |
