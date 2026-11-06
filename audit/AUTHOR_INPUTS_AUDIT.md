# Research input provenance audit (historical verification: 2026-11-03)

The provenance checks below concern the original author-supplied research files. Their retained scientific blobs are unchanged in public research snapshot `4b3ca90bdfa44254594f7d4916540c165bfafcb2`. The current scoped manifest was regenerated; this is not a new execution of the historical measurements. Research comparison scripts: `audit/scripts/compare_redacted_json.py` and `recount_main_prefix.py`.

## 1. Delivery integrity vs historical provenance

| Question | Result |
|---|---|
| `MANIFEST.sha256` (current research snapshot) | **43 entries**; retained original research-file bytes were preserved and the scoped manifest regenerated; the manifest excludes itself |
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

## 2. Retained research snapshot and licences

The public research input snapshot contains 43 manifest-listed files; the original English manuscript, main-run rows, selected reports, historical analysis versions and research row selection remain available. The supplied redacted copies retain the limitations described above. The manifest verifies delivered bytes, not unobserved original event records or scientific correctness.

The Apache-2.0 LICENSE applies to the original companion code and synthetic fixtures subject to NOTICE. The manuscript is CC BY 4.0. OpenR1-derived responses retain the dataset's data-card terms, and the external human-label CSV retains its MIT terms. No licence is extended to unrelated materials.
