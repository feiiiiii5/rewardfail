# Claim-to-evidence map (as of 2026-11-03)

Page numbers are for the public `paper.pdf` (12 October 2026). The status labels:

* **Recounted** — re-derived on 2026-11-03 from distributed *derived* records (not raw events).
* **Re-executed (Linux)** — the code was run again on 2026-11-03 on Linux x86-64 / CPython 3.12.8. This is a new verification, not the historical macOS environment.
* **Report-only** — the value exists in a distributed report; no input to rebuild it is public.
* **Source audit** — statement about code; checked by reading, not by running a full configuration.
* **Not checked** — not re-verified in this audit.

Companion paths are relative to the extracted `rewardfail-companion.zip` (audit version, SHA-256 `2aaf2113…`). `audit/…` paths are in this repository.

| # | Paper location | Claim | Data source | Computing code | Rebuildable from original inputs? | Missing | Our verification (2026-11-03) |
|---|---|---|---|---|---|---|---|
| 1 | p.1 abstract; §4 p.3–4 | Moving the same failed row switches lost flag ↔ batch `KeyError`; whole-chunk failures raise assertions; naive manager aborts | `results/c1c/run1`, `run2` (13 cases, ledgers) | `experiments/c1c_chain.py`, `rewardfail/inject.py` | Yes (code + pinned verl) | – | **Re-executed (Linux, real Ray)**: all 13 cases identical to run1 on outcome, exception type, raise site, keys, row scores (`audit/results/c1c_linux/`). `compare_runs.py` on historical runs: pass |
| 2 | §4 p.4 | 21 fixtures: original omits columns in 16, raises in 3; prototype passes 21 | `results/s2_e1/aggregation_contract.json` | `experiments/s2_contract.py` | Yes | – | **Re-executed (Linux)** with the companion's own case list/AST patch: identical source hash, patch hash and all 42 outcomes (`audit/results/contract_fixtures_linux.json`). Note: the archive's `audit_public_evidence.py` only *reads* the saved JSON |
| 3 | §4 p.4 | "downstream acceptance of None … remains untested" | – | – | – | – | **Now tested**: `process_validation_metrics` @0c4c3d4 drops `None` (pass). `RayPPOTrainer._validate` fails across validation batches with sparse keys (AssertionError, `ray_trainer.py:708`); `_merge_validation_results` misaligns silently. Fixed by `audit/upstream_chain/patches/0002` (`audit/results/chain_*.junit.xml`) |
| 4 | §4, §10 | Repair = union-and-fill, proposed upstream (#6545, #7151) | GitHub records | – | – | – | #6545 closed unmerged 2026-06-02; #7151 open (head 96eead6); #8015 open (head 0c4c3d4 unchanged); upstream `main` 2bcc98a still first-row rule. #7151 ported to 0c4c3d4: its tests 21 pass (port) vs 7 fail/6 pass/1 import error (unpatched). Real Ray C1c on port: 11/11 rate_limited cases complete, `error` kept in all 9 with an injected failure; naive still aborts |
| 5 | §4 p.5 | `timeout_score=-7` reached only by outer wait / explicit raise | `results/c1a/run*.json` | `experiments/c1a_timeout_layers.py` | Yes | – | Wrapper branches re-executed in `test_reward_chain.py` (W4 outer timeout → −7 and pool replaced; W6 explicit `TimeoutException` → −7). c1a itself **not re-run** |
| 6 | §5.1 p.5 | Protocol fixed before scoring (snapshot 9a88991) | `plan/*.json`, report `lock` | – | No | Experiment repo history not public | **Not verifiable**: internal freeze only; wording changed to "internally frozen" |
| 7 | §5.1 p.5 | 93,733 problems; one response each; uuid missing 664 / shared by 60 pairs | OpenR1 parquet (not distributed); `plan/sample_map.json` | `plan/sample_map.py` | Yes, with dataset | Dataset (HF blocked in this session) | **Recounted**: 93,733 unique main ids; uuid statistics **not checked** (no dataset access) |
| 8 | Table 2 p.6 | Class counts | `records/main-…/default/rows.jsonl` | `rewardfail/s2/analyze.py::classify` | Derived records only | Raw events | **Recounted**: classes re-derived from step records match the stored labels and the report; 54 event rows (9 score 1); 0 outer timeouts; max wall 5.235 s; 0 multi-attempt rows |
| 9 | §5.2 p.7 | k = 1, u = 18; interval [1.07e-5, 2.03e-4]; bounds 2.97e-4, [2.7e-7, 5.9e-5] | `results/s2_main/report.json` | `rewardfail/s2/report.py::main_metric` | **No** | Corrected main reference-pass rows; raw events; reanalysis code @9a88991 | **Report-only for u = 18 (level A).** Second pass: supplied pre-correction rows (level B) reproduce `k = 1` (same id) and `u = 9,573`; corrected classes need raw events (`audit/MAIN_METRIC.md`). Bound arithmetic re-computed: matches |
| 10 | §5.1 p.6 definition of u | u = reference timed out / interrupted twice / guard-stopped | `report.py::ref_verdict` | same | – | – | **Clarified**: reference errors (12 compare, 4 parse after correction; 12 before) scored 0, not u. Error-inclusive: u = 34, [1/n, 35/n], binomial 4.95e-4; verdict unchanged; post-correction pairing not verifiable |
| 11 | §5.2 | (implicit) u=18 is the corrected value | `reanalysis` block of report | `experiments/s2_main_reanalyze.py` | No | pre-correction rows, 9a88991 | Second pass: 9,866 reclassified rows (9,863 non-warm-up) reconcile exactly with formal totals in aggregate; only 4 guard kill events; final `analyze.py` = `f6e70c6c…` (matches report), old = `a8fa21e2…` (matches run lock); `test_s2_budget` 18/18 on Linux with the old version |
| 12 | §5.3 p.7 | k row: 10× 0 at 5 s alarm, 1 under reference (5.82–7.51 s) | `results/s2_u18/report.json`, `records/u18-…/d3-*` | `experiments/s2_u18_diag.py` | Partly (rows for this diagnostic are distributed) | Input text (needs dataset) | **Not re-executed** (dataset unavailable); hardware dependence flagged |
| 13 | §5.4–5.5 | Heavy inputs, 300 s limits, k300=1/u300=16 | `records/u18-…/d2-ref300` | `s2_u18_diag.py` | Needs dataset | Dataset | **Not re-executed** |
| 14 | §5.6 p.8 | 193,767 answers; 1 + 14 in complement; 2 / 32 pooled; 103 events; 92,287 eligible; 59/42; 103/84 pairs | `records/e2-…/default/rows.jsonl`, `results/s2_e2/report.json` | `experiments/s2_e2.py` | Derived records (default pass) | Complement reference rows (only ids in report) | **Recounted**: every listed count matches; ids disjoint; every complement answer maps to a main question. **New**: 32 unresolved answers = 21 distinct questions; both k answers = 1 question |
| 15 | §5.7 Table 3 | 1,487/43/1,530/3·2 verbatim; 113/91/204/4·3 delimiter; scores identical across limits | `records/e3-…/*/rows.jsonl`, `results/s2_e3/report.json` | `experiments/s2_e3.py` | **Yes** (CSV public, SHA matches) | – | **Re-executed from original input (Linux, new protocol `audit/experiments/e3_linux/PROTOCOL.md`)**: CSV SHA matched; all 22,176 trial scores equal the historical per-row scores; event-row sets identical in all 4 passes (3/4/2/3); Table 3 reproduced exactly (`audit/results/e3_linux/report.json`) |
| 16 | §6 Tables 4, scenes | Shared-pool scenes, batch abort under 60 s/30 s | `results/s2_e1/report*.json`, `records/e1-*` | `experiments/s2_e1.py` | Needs dataset inputs + macOS guard | Heavy input strings (dataset) | Second pass, **re-executed on Linux with substitute controls** (`audit/results/heavy_linux/`): default-limit, rate-limited, pure-control scenes agree; diagnostic naive abort **not reproduced** (0/4), timing explanation recorded |
| 17 | §7 Table 5 | TRL / Ray / verl main / OpenRLHF code paths | upstream sources at pinned commits | `results/s2_e1/normalization_filter.json`, `audits/prime_fallback_check.json` | Source audit | – | **Not re-checked** (source audit, 8–9 Oct) |
| 18 | §8 Table 6 | Advantage values | algebra | – | Yes | – | **Re-computed**: all values match (1.620182, −0.353552, 2.474867, 0, −2.474867, 2.267781, −0.377963) |
| 19 | §10 | Related-work characterisations | arXiv papers | – | – | arXiv unreachable from this session | **Not re-verified**; references left as the author's; GitHub records re-checked and #6830/#6845 added |
| 20 | Appendix A | `check_artifacts.py` verifies 1,572 files / 8 raw dirs / 32 values in the *original* index | `results/artifact_manifest.json` | `experiments/check_artifacts.py` | Original roots not public | Raw directories | Public index: 724 files + 32 values pass; the 1,572-file inventory cannot be checked publicly. Author inputs: 179/179 delivery hashes match (`audit/AUTHOR_INPUTS_AUDIT.md`) |
| 21 | README | "Linux has not been experimentally validated" | – | – | – | – | Superseded in part: mechanism tests, fixtures, E3, heavy scenes and 9 companion tests now run on Linux (with `audit/companion_fixes/`); corpus replays still not |

## Duplicate counting and units (checked)

* Main sample: one answer per exact-text question (93,733 unique ids; no row has more than one attempt; replays/retests are separate passes, not extra rows).
* Complement: 100,034 answers, ids `e2-<question>-<index>`, disjoint from main ids, no duplicate index within a question; question sizes 1–6 reproduce 193,767.
* Pooled extension endpoints count *answers*; the 32 unresolved answers cover 21 questions and both changes are one question — reported now in the paper.
* E3: unit = CSV row; 24 already-boxed rows are aliases, not extra trials.
* C1c / fixtures: unit = scene/fixture; counts are not frequencies.

## Checks that ran and their exit status (2026-11-03)

| Command | Exit | Result |
|---|---|---|
| `check_artifacts.py --index package_manifest.json` (main zip; audit zip) | 0; 0 | main zip 721 files, audit zip 724 files (3 added files); 32 report values each; pass |
| `compare_runs.py` (both zips) | 0 | historical run1 = run2 |
| `audit_public_evidence.py` (audit zip) | 0 | 12/12 comparisons true |
| `audit/scripts/recount_derived_records.py` | 0 | all comparisons true, 0 class mismatches |
| companion `tests/*` on Linux, first pass (unpatched) | mixed | 3 pass; 6 need macOS `libproc.dylib`; `test_s2_stats` 8/9; `test_get_data.sh` was invoked without its required arguments (my error) |
| companion `tests/*` on Linux, second pass (with `audit/companion_fixes/linux-portability.patch`) | mixed | `atype` 56/56, `preprint_extensions` OK, `public_evidence_audit` 7/7, `s2_budget` 18/18, `s2_report` 27/27, `s2_resume` 25/25, `s2_stats` 9/9, `get_data.sh` 17/17 ×2 locales; `s2_stepguard` 12 checks then needs `99b086d`; `s2_flow` needs `42e4d63`; `s2_main_e2e`, `s2_u18_diag` need dataset |
| verl #7151 CPU tests | 0 / 1 | port: 21 pass; unpatched: 7 fail, 6 pass, 1 collection error |
| `audit/upstream_chain/test_reward_chain.py` | 1 / 0 | unpatched: 11 tests fail (75 failed subtests/tests in pytest count), patched: 30 pass, 3 skipped (prototype-only) |
| `run_contract_fixtures_linux.py` | 0 | 21/21 identical to historical |
| `run_e3_linux.py` (E3-L) | 0 | 22,176 trials, 11.9 min, 0 exceptions; identical to historical |
| `c1c_chain.py --all` (unpatched; patched) | 0; 0 | 13/13 identical to historical; patched tree: 11/11 rate_limited cases complete, `error` kept in all 9 with an injected failure |

## Second pass (author inputs, 2026-11-03)

| # | Source | Claim | Evidence level | Our verification |
|---|---|---|---|---|
| 27 | Author-supplied research heavy rows | 4 heavy inputs | B | texts hash-verified; used in Linux heavy scenes |
| 28 | Author LaTeX | source of public PDF | build | compiled unchanged: 18 pages, identical `main.bbl`, same text modulo ligatures/hyphenation/floats |
