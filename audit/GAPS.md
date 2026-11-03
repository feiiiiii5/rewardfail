# Remaining gaps (2026-11-03)

Ordered by how much they limit the paper's claims. "Needs" lists the smallest thing that would close the gap.

| # | Gap | Effect on claims | Needs |
|---|---|---|---|
| G1 | Corrected main **reference-pass row records** (33,487 rows) are not public | k = 1 and u = 18 are report-only; the error-inclusive alternative (u = 34) cannot be row-verified | Release `main-20261007-202545/reference/rows.jsonl` (post-correction) or a row ledger `id, default_class, reference_class` |
| G2 | **Reanalysis history** (`9a88991`, `6c416b2`, pre-correction rows) is not public | The 9,573 → 18 correction cannot be audited; `test_s2_budget.py` cannot run | Publish the experiment repository history or a diff of `analyze.py` before/after plus the pre-correction class ledger |
| G3 | **Raw parent/child events** for changed and unresolved rows | Recounts are of derived records only, not an independent reproduction from raw data | Raw events for the 1 k row, 18 u rows, 16 reference error rows |
| G4 | **Original LaTeX source** (`paper/main.tex`, `refs.bib`, `main.bbl`) | The editable source here is a reconstruction from the PDF | Author supplies the original source; then diff against `paper/main.tex` |
| G5 | **OpenR1-Math-220k** not reachable from this session (Hugging Face blocked) | Main/complement replays, u18 diagnostics, shared-pool scenes not re-executed | Network access to `huggingface.co` (dataset is Apache-2.0); then run `get_data.sh` and the drivers in fresh directories |
| G6 | **arXiv** not reachable from this session | Related-work characterisations not re-verified; no new arXiv citations added | Network access to `arxiv.org`, or the author re-checks |
| G7 | Shared-pool scenes (§6) and heavy-input diagnostics (§5.4–5.5) **not re-run** on Linux | Timing/concurrency claims remain single-host (macOS) | Dataset access + porting the macOS memory guard (`rewardfail/s2/mem.py` uses `libproc.dylib`) |
| G8 | Companion tests are **macOS-specific** in 6 scripts; `test_get_data.sh` uses BSD sed; `test_s2_stats` uses exact float equality | Linux users cannot run the full self-test | Platform-neutral memory sampling (e.g. psutil fallback), GNU/BSD-neutral sed, tolerance in the closed-form check |
| G9 | **Full trainer** never run; generation always substituted | Consumer findings rely on the real `_validate` method with stub infrastructure, and on real Ray for reward workers only | A small CPU/GPU PPO run with validation over ≥2 batches and an injected sparse key |
| G10 | **Exclusion policy** for flagged rows is undefined upstream | Preserving the flag changes no reward; no learning benefit can be claimed | A stated policy (mask / impute / keep zero) and a controlled training comparison |
| G11 | `naive` manager still aborts the batch on a persistent worker death | The flagging contract applies only with `rate_limited` | Upstream decision; out of scope of the ported patches |
| G12 | Missing key vs explicit `None` collapse after union-and-fill | A consumer cannot tell "no flag emitted" from "flag value None" | A presence mask or typed sentinel, if a consumer needs the distinction |
| G13 | Cross-batch validation misalignment has not been reported upstream (limited search) | Patch `0002` exists only here | Author decides whether to open an upstream issue/PR (not done by this audit) |
| G14 | Torch on Linux needed the CUDA runtime wheels (unused) because the lock is macOS-only | Environment differs from the lock by those extra wheels | A Linux lock file |

## New experiments that were **not** run, and why

* Main-sample and complement re-scoring on Linux — dataset unreachable (G5).
* Shared-pool heavy-input scenes — dataset inputs and macOS guard (G5, G7).
* Any training run or training-benefit comparison — out of scope, no GPU, and the user asked not to default to long training.
* Paid APIs — none used.
