# Author inputs for the rewardfail thesis

This directory is an isolated input archive on branch author-inputs-20261103. It does not modify the existing reconstructed manuscript, paper.pdf, companion zip, or main branch.

## Contents

| Path | What it is | Source |
| --- | --- | --- |
| paper/ | main.tex, refs.bib, main.bbl, main.pdf | rewardfail/paper |
| thesis/ | main.md, proposal.md, proposal_final.md, figures, PDFs | thesis |
| context/ | redacted research-plan background | rewardfail-候选研究方案.md |
| main-run/default/ | raw default rows.jsonl (49,088,377 bytes), pass_spec, pass_done | original 2026-10-07 run |
| main-run/reference/ | raw reference rows.jsonl (18,475,478 bytes), pass_spec, pass_done, interrupts | original 2026-10-07 run |
| main-run/report.json | raw 2026-10-07 report | original run |
| reanalysis/ | 2026-10-08 formal s2_main report, reanalysis driver, legacy recheck, budget attribution | results/s2_main, experiments |
| results/ | selected formal reports for s2_e2, s2_e3, s2_u18, s2_e1, c1c | rewardfail/results |
| history/9a88991/ | commit metadata, README snapshot, code snapshot, path-filtered diff | local git |
| history/6c416b2/ | commit metadata, README snapshot, code snapshot, path-filtered diff | local git |
| new-runs/ | 2026-11-02-chain and 2026-11-02-p1 protocols, manifests, verification, results, logs | thesis-runs |
| LICENSE, NOTICE, data_manifest.tsv | upstream license/permission and data manifest | rewardfail root |

## Provenance

- Public repository: https://github.com/feiiiiii5/rewardfail
- This archive was created from the local working copy on 2026-11-03.
- Main-run raw data comes from stage2/runs/main-20261007-202545; the formal 2026-10-08 reanalysis is in reanalysis/. Do not assume the raw 10-07 report is the final result.
- History commits: 9a88991 (2026-10-07, second revision evidence; main sample not scored) and 6c416b2 (2026-10-07, main measurement result; unvetted). Code snapshots and diffs are under history/.
- New runs: 2026-11-02-chain (12 real-chain runs) and 2026-11-02-p1 (path A probe, four heavy-input runs, None arithmetic, batch matrix, static audits).

## Sanitization

- 58 text files had local paths replaced with placeholders: the local user path became WORKSPACE, REWARDfail_LOCAL, or LOCAL_USER. Token/email/phone patterns were redacted if present. Numeric values, scores, class labels, and timestamps were not changed.
- The two raw rows.jsonl files were copied byte-for-byte and contain no /Users/ path or token-like strings. Their SHA-256 values are in MANIFEST.sha256.
- Original local records are unchanged. The uploaded copies are for reading, not a replacement for the originals.
- Some manifest/verification hash fields refer to pre-sanitization originals. The sanitized P1 summary has refreshed hashes; chain manifest-all.json may still contain original hashes. Use values and paths together; do not treat a hash mismatch caused by path redaction as a data change.

## Excluded

- Full stage2/runs tree is about 2.0 GB; not uploaded.
- default/child_logs (316 MB+), reference/child_logs, obs/task/result rows other than the requested rows.jsonl; not uploaded.
- .venv, .git, .claude, .pytest_cache, __pycache__, .DS_Store, third_party checkouts, full dataset, caches; not uploaded.
- The paper source zips (arxiv-source.zip, rewardfail-companion.zip) are not duplicated here; paper.tex/refs.bib/main.bbl/main.pdf and the companion content already exist in the public repository. main.bbl was extracted from arxiv-source.zip; if main.tex changed after that zip, regenerate main.bbl before compiling.

## How to read it

1. Start with paper/main.tex and refs.bib for the original English manuscript.
2. Use thesis/main.md and proposal.md for the Chinese thesis/proposal source.
3. Read main-run/report.json and reanalysis/s2_main/report.json together; use the raw rows.jsonl to recompute k=1/u=18.
4. Read history/9a88991 and 6c416b2 for the analysis-version provenance.
5. Read new-runs/README.md in each run directory for the 2026-11-02 experiments; do not rerun them by default.

## Privacy and license

- This is a public repository. The archive contains math-problem responses derived from OpenR1-Math-220k and third-party public code snapshots; check the upstream licenses before redistribution.
- No passwords, API tokens, private keys, or full home directory are included. Local paths were sanitized.
- If raw responses or internal planning notes must remain private, move this directory to a private repository or remove context/ before sharing.

## Checksums

MANIFEST.sha256 lists every file in this archive with its SHA-256 and byte size. It is a delivery manifest, not a claim that every numeric result is correct.
