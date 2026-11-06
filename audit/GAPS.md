# Remaining research gaps (evidence assessment: 2026-11-03)

Ordered by how much they limit the claims. Paths are relative to the original run directory
`stage2/runs/main-20261007-202545/` unless stated otherwise. Details: `audit/MAIN_METRIC.md`.

| # | Gap | Status | Effect | Smallest input that closes it (path / format / use) |
|---|---|---|---|---|
| G1 | Corrected reference-pass classes behind `u = 18` | **partly closed**: pre-correction rows supplied; they reproduce `k = 1` and `u = 9,573`, and the reported changes reconcile in aggregate | `u = 18` remains a reported value (level A); row pairing of the 16 error zeros after correction unverified | `reference/obs-*.jsonl`, `reference/child_logs/child-*.jsonl`, `reference/guard*.jsonl`, `reference/results-*.jsonl`, `reference/warm-*.jsonl` (complete files, JSONL) — to run the final `analyze.py` (`f6e70c6c…`) and derive every corrected class. Run `audit/scripts/inventory_run_dir.py` first to list sizes/hashes |
| G2 | Audit of the budget-attribution correction on real events | **partly closed**: old and new `analyze.py` versions available; synthetic test passes 18/18 on Linux | correction rule verified on synthetic events only | same files as G1 (old vs new `analyze.py` over identical events) |
| G3 | Full eight-pass reproduction | open | limit2s/10s, replays, retest are report-only | all eight pass directories (≈2 GB) + `sample_map.tsv` + OpenR1 shards for re-execution |
| G4 | Original LaTeX source | **closed**: `paper/main.tex`, `refs.bib` supplied and imported; build reproduces the public PDF | – | – |
| G6 | Old test controls for `test_s2_flow.py` / `test_s2_stepguard.py` | open | two companion tests stop before their old-version comparison | `rewardfail/s2/report.py` at `42e4d63`; `rewardfail/s2/stepguard.py` at `99b086d` (single files) |
| G7 | Redaction artifacts in author inputs | open (reported, not altered) | 7 row-id keys in `author-inputs/main-run/report.json` and one hash in `results/s2_e3/report.json` corrupted by the `<PHONE>` pattern | re-export those two files with a redactor that skips hex/id fields |
| G8 | OpenR1-Math-220k not reachable here (Hugging Face blocked) | open | corpus replays, u18 diagnostics and dataset-control shared-pool scenes not re-executed on Linux | network access to `huggingface.co`, or the shards listed in `data_manifest.tsv` |
| G9 | Diagnostic heavy-input abort on Linux | **tested, not reproduced** with substitute controls (0/4) | the abort is timing-dependent; whether it occurs with the paper's 8 dataset controls on Linux is unknown | the 8 dataset control texts of the E1 eight-row matrix (ids, `gt`, `out`), e.g. from `e1-eight-20261008-codex/specs.json` |
| G10 | arXiv and docs sites not reachable from this environment | open | arXiv citations not re-verified here (author's 2 Nov URL audit exists) | access to `arxiv.org` or the author's check |
| G11 | Full trainer never run | open | consumer findings rely on the real `_validate` with stub infrastructure | a small CPU/GPU PPO run with ≥ 2 validation batches and an injected sparse key |
| G12 | Exclusion policy and training effect | open by design | no learning claim; flagged rows still enter statistics as zero | a defined policy and a controlled comparison (see offline-first plan) |
| G13 | `naive` manager aborts on persistent worker death | open upstream | flag contract applies only with `rate_limited` | upstream decision |
| G14 | Missing vs explicit `None` collapse | open | consumers cannot tell "no flag" from "flag = None" | presence mask or typed sentinel, if needed |
| G15 | Validation misalignment not reported upstream | open (author's decision) | patch `0002` exists only here | an upstream issue/PR by the author |

## Not run, and why

* Main-sample and complement re-scoring on Linux — dataset unavailable (G8).
* Training or training-benefit experiments — out of scope here, no GPU; the agreed plan is offline analysis first.
* Paid APIs, model downloads — none used.
