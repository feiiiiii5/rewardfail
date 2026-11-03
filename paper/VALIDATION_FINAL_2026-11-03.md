# Final validation of the preprint package (2026-11-03)

Environment: Linux x86-64 container, CPython 3.12.8 (analysis venv from the companion lock), system Python 3.13 for
standard-library scripts, TeX Live 2023 (pdfTeX 1.40.25). Author inputs read only from `e29d296`; companion =
`rewardfail-companion.zip` (SHA-256 `2aaf2113…`) extracted with `audit/scripts/safe_unzip.py`.

## Manuscript

| Check | Result |
|---|---|
| `pdflatex → bibtex → pdflatex ×2` on `paper/main.tex` | 23 pages; 0 errors; 0 undefined references/citations; 0 BibTeX warnings; 0 overfull/underfull boxes (final pass, after the policy-section corrections) |
| arXiv package `paper/arxiv/rewardfail-arxiv-source.tar.gz` (`make_arxiv_package.sh`) | contains `main.tex`, `main.bbl`, `refs.bib` (SHA-256 `ba03dd50…`); compiles from a clean directory with pdfLaTeX and the shipped `.bbl` only (BibTeX not run, `refs.bib` removed): 23 pages, no errors; extracted text identical to the full build |
| Fonts | 30 fonts, all embedded and subset (Latin Modern, Type 1) |
| PDF metadata | Title, Author (Yufeiyang Chen), Keywords, Creator, Producer only |
| Source comments | version/build notes only; no paths, credentials or internal discussion |
| Visual check | all 23 pages rendered (contact sheets) and the two new tables at 70 dpi: no clipping, overlap or blank pages |
| `audit/scripts/check_paper_numbers.py` (rewritten) | 166/166 checks: each compares a value read from its source file with the number extracted from a specific sentence or an addressed table cell (row labels + column), within half a unit of the printed last digit (`audit/results/paper_number_check.json`) |
| `audit/scripts/test_check_paper_numbers.py` | 10/10 counter-tests: tampered source values (policy, supplement, main metric), edited sentences, the two old rounding errors, swapped cells, swapped policy rows and a missing row are all detected |
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
