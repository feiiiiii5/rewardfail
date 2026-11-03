# Manuscript revision log (3 November 2026)

`paper/main.tex` is an **editable reconstruction from the public `paper.pdf`** (12 October 2026,
SHA-256 `8efbb347…c46811`). No original LaTeX source exists in any public branch, commit or
archive (checked: `main`, `audit/public-evidence-2026-11-03`, both companion ZIPs). The companion's
`experiments/package_preprint.py` expects `paper/main.tex`, `refs.bib`, `main.bbl` in the author's
unpublished repository. Layout, float placement and page count therefore differ from the original
(22 vs 18 pages, mostly due to added material).

Transcription: text, equations (§4 permutation equation, §5.1 bounds, §8 advantage formula), all
six tables, Figure 1 (a text table, no images in the PDF) and the 35 references were copied from the
PDF text layer and checked by eye against the rendered pages. The bibliography is now inline
(`thebibliography`) and sorted as in the PDF; the numbering of the two added references shifts
later numbers. This revision was prepared with AI assistance and **needs the author's review**.

## Substantive changes

| Location | Change | Evidence |
|---|---|---|
| Title block | Added "evidence revision 3 November 2026" and the reconstruction notice | – |
| Author footnote | Kept verbatim; appended the AI-assisted-revision disclosure and "awaits the author's review" | user instruction; no invented contributions |
| Abstract | "pre-declared" → "internally frozen"; stated u rule and error-inclusive range 1–35; stated what the public package can and cannot rebuild; added Linux re-execution, #7151 port and validation fix; "unresolved" replaces "undecided" for u | `audit/EVIDENCE_MAP.md` rows 1–4, 6, 9–10 |
| New ¶ "Reading this revision" | Defines historical / recounted / new labels | – |
| §1 | Added #6830/#6845 to the upstream record; RQ1 now includes the validation consumer; contribution 1 rewritten to credit #7151 as the tested repair and to state no mechanism is claimed new | GitHub search API, 2026-11-03 |
| §1 Scope | Added the Linux container description | `audit/results/environment.json` |
| §2 | Noted that no verl code reads `error`/`timeout`; noted other child exceptions propagate; #8015 status re-checked | source @0c4c3d4; test W5 |
| §3 | New Table 2 "How each recorded outcome is counted" reproducing `report.py::ref_verdict` | companion `rewardfail/s2/report.py` |
| §4 Setup | Added Linux real-Ray C1c re-run | `audit/results/c1c_linux/` |
| §4 prototype | Marked historical + re-executed; disclosed that the prototype makes all columns `dtype=object`, sorts keys, covers only the batch path | `audit/results/contract_fixtures_linux.json`; test P2 |
| §4 new ¶ + Table 3 | #7151 port results; `_validate` cross-batch failure and `_merge_validation_results` misalignment; #6830 not reproduced on `process_validation_metrics` at this head; upstream main still affected; patched real-Ray results; missing-vs-None limitation | `audit/upstream_chain/`, `audit/results/chain_*`, `c1c_linux_fixed/` |
| §5.1 | "fixed before" → fixed in an unpublished repository, internal freeze; exact-text identity caveat; u definition now excludes reference errors explicitly | report.py; GAPS G2 |
| Table 4 (old Table 2) caption | Marked recounted with re-derived classes | `audit/results/recount_derived_records.json` |
| §5.2 | Labelled k/u as report-only; new ¶ on what the public record supports, the 9,573 → 18 correction and the 9,863 reclassified rows; new error-inclusive sensitivity (u = 34, 35/n = 3.73e-4, binomial 4.95e-4) | `results/s2_main/report.json` (`reanalysis`, `reference_classes`); `report.upper` |
| §5.3 | Added hardware-dependence caveat for the 0.8 s margin | – |
| §5.6 | Added: both changes are one question; 32 unresolved answers are 21 questions; recount statement | recount script |
| §5.7 | Added `\input{e3_linux_paragraph.tex}` with the new Linux replay | `audit/results/e3_linux/report.json` |
| §6.2 | Stated these scenes were not re-run on Linux | GAPS G7 |
| §7 | Stated source audit dates and that it was not re-read | – |
| §8 | Stated advantage values were re-computed | EVIDENCE_MAP row 18 |
| §9 | Consumer boundary now includes validation batches; flagged rows still receive 0 | patched C1c |
| §10 | Added #6830/#6845; "no new category" wording; dropped implication of priority | GitHub records |
| §11 | New "Public reproducibility" paragraph; execution scope covers Linux checks | GAPS |
| §12 | Conclusion mentions validation accumulation | Table 3 |
| Appendix A | Rewritten as evidence tiers; removed the unverifiable "1,572 files … tested on this host" detail from the main text (still in companion README); commit ids marked as unpublished | `check_artifacts.py` output |
| References | Added verl #6830 and #6845; updated status of #6545, #7151, #8011, #8015 (re-checked 2026-11-03); arXiv entries unchanged and **not re-verified** (arXiv unreachable) | `gh api search/issues` |

## Unchanged on purpose

* All historical numbers, the frozen decision rule and thresholds.
* Licences (CC BY 4.0 manuscript; Apache-2.0 code), affiliation, correspondence, conflict statement.
* §7 framework statements (source audit; not re-checked).
