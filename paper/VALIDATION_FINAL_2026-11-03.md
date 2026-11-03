# Final validation of the preprint package (2026-11-03)

Last re-run: release pass on top of `da00bd6` (after the author-footnote edit); every command in the two tables below was re-run in that pass unless marked otherwise.

Environment: Linux x86-64 container, CPython 3.12.8 (analysis venv from the companion lock), system Python 3.13 for
standard-library scripts, TeX Live 2023 (pdfTeX 1.40.25). Author inputs read only from `e29d296`; companion =
`rewardfail-companion.zip` (SHA-256 `2aaf2113…`) extracted with `audit/scripts/safe_unzip.py`.

## Manuscript

| Check | Result |
|---|---|
| `pdflatex → bibtex → pdflatex ×2` on `paper/main.tex` | 23 pages; 0 errors; 0 undefined references/citations; 0 BibTeX warnings; 0 overfull/underfull boxes (final pass, after the policy-section corrections) |
| arXiv package `paper/arxiv/rewardfail-arxiv-source.tar.gz` (`make_arxiv_package.sh`) | contains `main.tex`, `main.bbl`, `refs.bib` (SHA-256 `6bccf07b…`); compiles from a clean directory with pdfLaTeX and the shipped `.bbl` only (BibTeX not run, `refs.bib` removed): 23 pages, no errors; extracted text identical to the full build |
| Fonts | 30 fonts, all embedded and subset (Latin Modern, Type 1) |
| PDF metadata | Title, Author (Yufeiyang Chen), Keywords, Creator, Producer only |
| Source comments | version/build notes only; no paths, credentials or internal discussion |
| Visual check | all 23 pages rendered (contact sheets) and the two new tables at 70 dpi: no clipping, overlap or blank pages |
| `audit/scripts/check_paper_numbers.py` (rewritten, tightened in the fifth pass) | 168/168 checks: each compares a value read from its source file with the number extracted from a specific sentence or an addressed table cell (row labels + column), within half a unit of the printed last digit; for `a\times10^{e}` the tolerance is scaled by `10^e`. The generated table block is parsed strictly: exactly 10 cells per row, every one of the 18 expected rows present, no duplicate, unknown or extra rows, and a missing BEGIN/END marker fails (`audit/results/paper_number_check.json`) |
| `audit/scripts/test_check_paper_numbers.py` | 21/21 counter-tests (each corruption must make the checker fail): tampered source values (policy, supplement, main metric, cross-check), edited sentences, the two old rounding errors, swapped cells and rows, a missing row, a wrong exponent, a wrong mantissa, a dropped last column, an added column, a duplicated row, an unknown policy label, an unknown mechanism label, a removed generated block and a non-numeric cell. The fourth-pass checker (`5d271ea`) fails 8 and errors on 4 of these 21 |
| `make_policy_table.py` | the table block in `main.tex` is byte-identical to a fresh generation from the result files |
| Superseded checker (`superseded_check_paper_numbers_v1.py`) | only searched for hard-coded strings and missed two table cells wrong by double rounding (183.7 → 183.6, 1.5 → 1.4); the new checker rejects the previous manuscript |

## Code and data

| Command | Exit | Result |
|---|---|---|
| `python3 -I -B audit/scripts/test_recount_main_prefix.py` | 0 | 7 tests OK |
| `python3 -I -B audit/scripts/recount_main_prefix.py <author-inputs> <companion>` | 0 | output identical to committed `audit/results/main_prefix_recount.json` (k = 1, u = 9,573; reconciliation true; no corrected rows reconstructed) |
| `python3 -I -B audit/scripts/recount_derived_records.py <companion>` | 0 | all comparisons true |
| `experiments/check_artifacts.py --index package_manifest.json` (companion) | 0 | 724 files, 32 report values |
| `experiments/audit_public_evidence.py` (companion) | 0 | 12/12 |
| `python -m unittest test_offline_policy` | 0 | 9 tests OK |
| `run_offline_policy.py` (OP) | 0 | 72 groups; verl cross-check max difference 2.9e-7 (288 cases); the cross-check was re-run on its own in the final pass with the same result |
| `supplement.py` (same draws) | 0 | exact equality with the main run's means (0 mismatches); exhaustive enumeration of the negative-advantage condition: 131,072 cases, 0 violations |
| `pytest audit/upstream_chain/test_reward_chain.py` on verl `0c4c3d4` | 1 | expected failures (assembly/consumer contracts): 75 failed tests+subtests, 22 passed |
| same on `0c4c3d4` + patches 0001/0002 | 0 | 30 passed, 3 skipped (prototype-only), 66 subtests passed |
| `compare_redacted_json.py` (s2_e3 report) | 0 | path-only differences + one redaction-corrupted hash |

Earlier executions retained and not repeated in this pass (results in `audit/results/`): 21 fixtures on Linux, C1c
under real Ray (unpatched and patched), E3-L 22,176 trials, 11 heavy-input scenes, companion tests with the Linux
patch.

## Not executed

Corpus re-scoring on Linux (OpenR1 not reachable), any training, the eight-pass raw-event reconstruction (inputs
not supplied), arXiv re-checks from this environment (arxiv.org not reachable; see `LITERATURE_CHECK.md` for the
author-side check).

## Independent-review items and what this pass did with them

| Item raised by the author's independent review | Status here |
|---|---|
| Abstract overclaimed ("every failed correct answer" gets a negative advantage) | corrected in abstract, §8.2, §12; condition verified by exhaustive enumeration and stated with its M1/M2 scope; M3 stated separately |
| Number checker only searched hard-coded text | replaced; counter-tests added; it found nothing beyond the two cells below once the table was generated from the sources |
| M1 p=.25 P0 disagreement and M2 p=.05 P2 disagreement | 183.6 and 1.4 (were 183.7 and 1.5) |
| Policies evaluated on different row sets; "sign disagreement" includes zero changes | caption and text now say so; added a common evaluation set and a flip / zero→non-zero / non-zero→zero decomposition (same draws); text no longer calls lower error alone "better" |
| 91–96% came from a separate 500-draw sample | the manuscript now uses the same-draw decomposition (91–97%); the 500-draw file is labelled as separate |
| Author's independent re-run of OP (CSV hash, 72 groups, 9 tests, 2,000-draw means and standard errors) | not repeated here; consistent with this environment's results. The real-verl torch cross-check was run here (not by the independent review) |

## Fifth pass (final cleanup)

| Item | Status here |
|---|---|
| Checker: exponent tolerance not scaled; `zip` silently dropped a deleted last column | fixed (see table above); 11 new counter-tests; old checker fails or errors on 12 of 21 |
| "Exclusion leaves more groups without signal" | now stated only for independent failures (M1); for M2/M3 the no-signal count is identical across policies (asserted by the checker from the result file) |
| Single surviving response | stated as advantage $r/(1+\epsilon)$ (raw score divided by $1+10^{-6}$), verl's mean 0 / std 1 convention; checker asserts the formula |
| Partial groups | "the statistics of their original eight-response groups cannot be reconstructed" |
| Author's independent recheck (original label CSV obtained and checked, 72 complete groups, 720 means and Monte Carlo standard errors recomputed with an independent algorithm, max difference about `1.11e-16`) | reported by the author; **not repeated here**. It supports the offline simulation on fixed samples only — not a training gain and not a natural failure rate |
| Main experiment `u = 18` | unchanged: historical report value only (pre-correction rows reproduce `k = 1`, `u = 9,573`) |

## Release pass (before merging into `main`)

Re-run on the release tree: LaTeX build (23 pages; 0 errors, undefined references, box warnings or BibTeX
warnings; `main.bbl` byte-identical to the committed one), arXiv package build from a clean directory (23 pages, text
identical to the full build), fonts all embedded, title page inspected; number checker 168/168; counter-tests 21/21;
table regeneration identical; offline unit tests 9/9; verl cross-check 288 cases, max difference 2.9e-7; recount
tests 7/7 and recount output identical to the committed file; derived recount identical to the previous run;
companion `check_artifacts` (724 files, 32 report values) and `audit_public_evidence` (status unchanged); redacted
report comparison; author-input manifest 179/179; chain suite 30 passed / 3 skipped on the patched tree and the
expected 75 failed / 22 passed on the base tree; all relative README links resolve. The same checks were repeated
from `main` after the merge (see the pull request).

Taken from earlier records, not re-run: 21 fixtures and C1c under real Ray on Linux, E3-L (22,176 trials), the 11
heavy-input scenes, companion tests with the Linux patch, the 2,000-draw offline runs themselves (their outputs are
checked, not regenerated), and the author's independent recheck of the offline statistics.

Not executable here: corpus re-scoring (OpenR1 not reachable), training of any kind, reconstruction of the corrected
`u = 18` from reference-pass events (not supplied), arXiv/metadata re-checks of citations (unreachable).

## Author-confirmation pass

After the author confirmed CC BY 4.0, Apache-2.0 for `audit/`, a public correspondence address and cs.SE + cs.LG,
one appendix sentence changed ("Original companion and audit code is licensed under Apache-2.0"). Re-run: LaTeX
build (23 pages; 0 errors, undefined references, box or BibTeX warnings; `main.bbl` unchanged), arXiv package
(SHA-256 `6bccf07b…`, builds from a clean directory, text identical to the full build), fonts embedded, number
checker 168/168 with output identical to the committed `paper_number_check.json`, counter-tests 21/21, offline unit
tests 9/9, recount tests 7/7. Analysis code and results unchanged since `da00bd6`.
