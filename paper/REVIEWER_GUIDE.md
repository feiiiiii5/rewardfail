# Reviewer guide and remaining release gates

Manuscript-only revision based on PR #1 commit
`9a2fdd56c5844f3f01d285b5e70f98153fc22a12`.

## Scientific center

This is a bounded software-reliability case study of an opt-in RLVR reward path.
Its strongest contribution is the executed composition of a worker failure,
sparse manager metadata, two assembly paths, and a validation consumer, with
regression contracts and a second-platform execution. It is not a discovery of
exception-to-zero behavior, a new union-key algorithm, a universal prevalence
estimate, or a demonstrated improvement in learning.

The corpus measurements and selected heavy-input controls answer different
questions. They should support this case study, not be treated as independent
proof of training harm. The abstract now leads with the reproducible chain,
labels the unresolved-count range as report-conditional, and states the failed
Linux abort reproduction without turning the discrepancy into a causal finding.

## Evidence available and its limits

| Claim | Evidence entry point | What remains outside the evidence |
|---|---|---|
| Row-position failure and repair | `audit/upstream_chain/`, `audit/results/chain_verl-*.txt`; manuscript mechanism section | Full trainer execution and deployment incidence |
| 54 default event rows, one recovered row | `audit/results/recount_derived_records.json`, `audit/results/main_prefix_recount.json` | New full-corpus scoring on another host |
| Corrected unresolved count 18 | `audit/MAIN_METRIC.md`, historical formal report | Corrected event-level reconstruction; report consistency is not replication |
| Labelled replay trial scores | `audit/experiments/e3_linux/` | Independent adjudication or random-population inference |
| Original-host heavy-input abort | historical scenes and `audit/experiments/heavy_linux/` | Matched cross-platform reproduction with identical controls |
| Changed GRPO advantages | declared vectors and arithmetic | Gradients, training trajectories, downstream performance |

## Remaining gates before a stronger public release

1. Rebuild the corrected main-reference classification from complete parent,
   child and guard logs. Until then the main recovery endpoints and pooled
   unresolved endpoints must stay explicitly conditional on historical reports.
   Merely hiding this gap in limitations would be inadequate.
2. If claiming a platform-independent abort mechanism, rerun identical controls
   and heavy inputs with explicit scheduling traces on both platforms. The
   current Linux substitution changes two factors and cannot isolate either.
   This is not necessary for reporting the existing bounded negative replication.
3. Keep sample-selection, reference error policy, and unresolved classification
   visible. Longer limits do not establish correctness; fixed-record completion
   bounds do not bound every future rerun.
4. Have the author verify personal contributions, affiliations, licensing and
   substantive scientific ownership. AI disclosure does not substitute for that
   review. No acceptance or favorable faculty judgment can be guaranteed.
5. On integration, rebuild the PDF and bibliography from the combined source,
   rerun evidence checks, and inspect the new final pages. A standalone writing
   patch cannot certify another concurrently edited manuscript.

## Changes made in this pass

- Rewrote the abstract around the verifiable contribution and conditional evidence.
- Defined “default protocol” as the selected replay baseline, not verl defaults.
- Defined exactly what missing-outcome completions the finite-sample range covers.
- Kept the all-answer unresolved endpoints conditional on the inherited main report.
- Removed causal overinterpretation of the Linux/platform-control discrepancy.
- Corrected Cai v5's relation to GRPO and credited iCoder's actual masking policy.
- Pinned every arXiv link to a checked version; see `LITERATURE_CHECK.md`.

No experiment output, historical count, raw input or scoring code was altered.
No original remote branch was modified during this writing pass; any publication
uses a separate integration branch.

## Status after integration (third pass, 2026-11-03)

- This patch was integrated by fast-forward into `claude/trusting-mccarthy-du7c3t` (commit `06688da`), then extended.
- Gate 5 is done: the combined source was rebuilt (23 pages), the bibliography regenerated, every page inspected, and
  30 manuscript numbers checked against the result files (`VALIDATION_FINAL_2026-11-03.md`).
- The "Changed GRPO advantages" row now also has an offline comparison on 72 complete human-labelled groups (§8.2,
  `audit/results/offline_policy/`); it still says nothing about gradients, trajectories or performance.
- Gates 1, 2 and 4 remain open (`SUBMISSION_CHECKLIST.md`).

## Status after the fourth pass

The independent review's four points (abstract overclaim, string-only checker, two table cells, evaluation sets and
the 500-draw share) are addressed as listed in `VALIDATION_FINAL_2026-11-03.md`. The independent review's revised
`dot` commit was not available on the remote at the time of this pass (branch still at `06688da`); the fixes were
implemented independently and should be compared with it when it is pushed.

## Status after the fifth pass

Final cleanup: the number checker's two boundary defects (unscaled scientific-notation tolerance, silently dropped
table column) are fixed and covered by 21 counter-tests; three policy-analysis sentences were narrowed (M1-only
no-signal increase, $r/(1+\epsilon)$ for a single survivor, partial-group wording). The offline analysis remains a
fixed-sample simulation, not a training result or a natural failure rate; `u = 18` remains a report-only value.
