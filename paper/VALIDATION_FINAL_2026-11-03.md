# Final validation of the preprint package (2026-11-03)

Environment: Linux x86-64 container, CPython 3.12.8 (analysis venv from the companion lock), system Python 3.13 for
standard-library scripts, TeX Live 2023 (pdfTeX 1.40.25). Author inputs read only from `e29d296`; companion =
`rewardfail-companion.zip` (SHA-256 `2aaf2113…`) extracted with `audit/scripts/safe_unzip.py`.

## Manuscript

| Check | Result |
|---|---|
| `pdflatex → bibtex → pdflatex ×2` on `paper/main.tex` | 23 pages; 0 errors; 0 undefined references/citations; 0 BibTeX warnings; 0 overfull/underfull boxes |
| arXiv package `paper/arxiv/rewardfail-arxiv-source.tar.gz` (`make_arxiv_package.sh`) | contains `main.tex`, `main.bbl`, `refs.bib`; compiles from a clean directory with pdfLaTeX and the shipped `.bbl` only (BibTeX not run, `refs.bib` removed): 23 pages, no errors; extracted text identical to the full build |
| Fonts | 27 fonts, all embedded Type 1 (Latin Modern) |
| PDF metadata | Title, Author (Yufeiyang Chen), Keywords, Creator, Producer only |
| Source comments | version/build notes only; no paths, credentials or internal discussion |
| Visual check | all 23 pages rendered (contact sheets) and the two new tables at 70 dpi: no clipping, overlap or blank pages |
| `audit/scripts/check_paper_numbers.py` | 30/30 manuscript numbers equal the committed result files (`audit/results/paper_number_check.json`) |

## Code and data

| Command | Exit | Result |
|---|---|---|
| `python3 -I -B audit/scripts/test_recount_main_prefix.py` | 0 | 7 tests OK |
| `python3 -I -B audit/scripts/recount_main_prefix.py <author-inputs> <companion>` | 0 | output identical to committed `audit/results/main_prefix_recount.json` (k = 1, u = 9,573; reconciliation true; no corrected rows reconstructed) |
| `python3 -I -B audit/scripts/recount_derived_records.py <companion>` | 0 | all comparisons true |
| `experiments/check_artifacts.py --index package_manifest.json` (companion) | 0 | 724 files, 32 report values |
| `experiments/audit_public_evidence.py` (companion) | 0 | 12/12 |
| `python -m unittest test_offline_policy` | 0 | 9 tests OK |
| `run_offline_policy.py` (OP) | 0 | 72 groups; verl cross-check max difference 2.9e-7 (288 cases) |
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
