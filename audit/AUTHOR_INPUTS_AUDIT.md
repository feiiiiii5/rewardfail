# Audit of `author-inputs/` (branch `author-inputs-20261103`, commit `e29d296c3b08ed6922b4384df438fbfe0650b5c4`)

Read-only: extracted with `git archive` into a separate, write-protected directory; nothing in that branch was
modified, merged or force-pushed. Scripts used: `audit/scripts/compare_redacted_json.py`,
`check_chain_manifest.py`, `rederive_chain_exports.py`, `recount_main_prefix.py`.

## 1. Delivery integrity vs historical provenance

| Question | Result |
|---|---|
| `MANIFEST.sha256` (hash, bytes, path; 179 entries) vs delivered files | **179/179 match** in this environment; the only unlisted file is the manifest itself |
| `paper/main.pdf` vs public `paper.pdf` | byte-identical (`8efbb347…`) |
| `paper/main.tex` + `refs.bib` compiled unchanged | 18 pages; regenerated `main.bbl` byte-identical to the supplied one; text equals the public PDF apart from ligatures/hyphenation/floats |
| `LICENSE`, `NOTICE`, `data_manifest.tsv` | identical to the companion's copies |
| `reanalysis/s2_main_reanalyze.py` | identical to the companion's copy (`dd11c9d7…`) |
| Final `analyze.py` | the companion's copy has SHA-256 `f6e70c6c…`, equal to the formal report's `analysis_env.code_sha256` |
| `history/9a88991`, `history/6c416b2` `analyze.py` | both `a8fa21e2…`, equal to the main run's lock (the pre-correction version) |
| Report JSONs vs companion copies (structural comparison) | `s2_main`, `s2_e1` (2 files), `s2_e2`, `s2_u18`: all differences are path strings only. `c1c/run1`, `run2` summaries: identical. **`s2_e3/report.json`: one SHA-256 value corrupted by the phone-number redaction** (`lock/pre/tasks_sha256/raw` = `2de0481e<PHONE>d55635b9…`; the companion copy has the intact value `2de0481e16387665767d55635b9…`) |
| `main-run/report.json` (raw 10-07 report) | **7 row-id keys corrupted by the phone-number redaction** (e.g. `m-53f<PHONE>cc`); no companion copy exists to restore them. The two raw `rows.jsonl` files contain no placeholder and were not affected |
| `main-run/default/rows.jsonl` vs companion derived default rows | value-identical row by row (different JSON whitespace only) |

So the delivered bytes are intact, but "numeric values not changed" holds only for the rows files and the
fields compared above: the redactor also altered one hash and seven row ids. These were not "fixed" here;
the originals are with the author.

## 2. `new-runs/2026-11-02-chain/manifest-all.json` (81 entries) vs delivery

| Status | Count | Explanation |
|---|---:|---|
| match | 43 | |
| differs, delivered file contains a redaction placeholder and has a different size | 30 | **consistent with** path redaction; not provable without the original bytes |
| self-reference (`manifest-all.json` lists itself) | 1 | `verify_run.py` writes the manifest after hashing the directory, so its own entry is an earlier version (10,296 bytes) of the file (11,086 bytes delivered); the growth cannot be explained by redaction (which shortens) and is **unknown** |
| missing | 7 | see below |

The 7 undelivered files and whether their content is independently available:

| Manifest entry | Evidence | Status |
|---|---|---|
| `driver/c1c_chain.py` | equals companion `experiments/c1c_chain.py` (SHA-256 and size) | reconstructible |
| `driver/fixed_agent_loop.py`, `driver/inject.py`, `driver/reward_fn.py` | equal the companion copies | reconstructible |
| `verl-pr8015-original/reward_loop.py` | equals verl `0c4c3d4` source | reconstructible |
| `verl-pr8015-unionfill/reward_loop.py` | equals `0c4c3d4` + `env/patch.diff` (`82ef9c07…`, 17,160 bytes) | reconstructible |
| `driver/thesis_chain.py` (versions `3b3aa0…` for C0–C4/O4/O6 and `6cce7c…` for C5/C6/C1r/C2r/O5) | not in any public source | **missing; affects verification**: the driver wrote the `scores_match_expected`, `error_set_matches_expected`, export-readback flags and the raise sites that most of the 249 checks read |

## 3. Privacy and licences

* **Local directory names remain** after redaction in 15 text files (path segments after `<LOCAL_USER>` such as
  a Desktop project folder chain). They are already public on the author branch. They were not copied into
  this branch's outputs.
* `context/research-plan-redacted.md` (852 lines) contains planning notes that mention the supervisor and the
  application season. The author's own README flags it as possibly private. It is public on the author branch now;
  nothing from it was copied here. The author may want to move it to a private repository.
* The only e-mail address is the author's published correspondence address (also in the paper).
* No credentials, API tokens or keys were found (pattern search).
* Licences: the Apache-2.0 `LICENSE` covers the original companion code and synthetic fixtures only (per
  `NOTICE`); the manuscript is CC BY 4.0; OpenR1-derived responses in `main-run/*/rows.jsonl` and
  `heavy_rows.json` carry the dataset's Apache-2.0 data-card terms; the human-label CSV is MIT; the thesis
  files carry no stated licence and should not be assumed to be under either code or manuscript licence.
