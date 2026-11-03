# Proposed licensing for `audit/` (not yet granted)

Status: **proposal only.** The author has not chosen a licence for the files added under `audit/` on
3 November 2026, so none is granted by this repository at present. Nothing below relicenses third-party code or
data. When the author decides, add the two files in the last section (or the author's alternative) in a separate
commit; do not edit the licences of the companion archive, `paper.pdf` or upstream material.

Recommendation: Apache-2.0 for the author-licensable code, matching the companion archive (`rewardfail-companion.zip`,
`LICENSE` + `NOTICE`, copyright Yufeiyang Chen) and upstream verl.

## Inventory

| Path | Origin | Who can license it | Proposed treatment |
|---|---|---|---|
| `audit/scripts/*.py` | written for this audit (standard library; some import companion modules at run time) | author | Apache-2.0 |
| `audit/experiments/offline_policy/*.py`, `e3_linux/run_e3_linux.py`, `heavy_linux/run_heavy_linux.py` | written for this audit; import NumPy, Math-Verify or verl at run time but contain no copied upstream code | author | Apache-2.0 |
| `audit/experiments/e3_linux/e3_child.py` | written for this audit; reproduces the same Math-Verify calls and target configuration as verl PR #8015's `_verify_in_subprocess` | author, with attribution to verl (Apache-2.0) | Apache-2.0; keep the docstring attribution and mention it in NOTICE |
| `audit/upstream_chain/chain_inject.py`, `test_reward_chain.py` | written for this audit; exercise verl functions by import | author | Apache-2.0 |
| `audit/upstream_chain/patches/0001-…7151….patch` | port of open upstream verl PR #7151 (author: keepkeen, head `96eead6`) onto PR #8015 head `0c4c3d4`; contains upstream code and Bytedance copyright headers | upstream contributors under verl's Apache-2.0 | **not** relicensed; distributed under verl's Apache-2.0 with headers kept; NOTICE names the source PR and author |
| `audit/upstream_chain/patches/0002-…patch` | change to verl files written for this audit; context lines are verl code | new lines: author; context: verl contributors | Apache-2.0 (compatible with verl); keep verl attribution |
| `audit/companion_fixes/linux-portability.patch` | change to the author's companion code | author | Apache-2.0 (same as companion) |
| `audit/results/**` (JSON, logs, gz records) | measurement records produced by the scripts above | author, except embedded third-party text | Apache-2.0 for the records, or leave as data under the same terms as the manuscript; excludes the texts below |
| `audit/results/heavy_linux/*/spec.json` (S2–S6, S2f, S5a–S5c, S5f) | contain full answer/response texts of three OpenR1-Math-220k rows | OpenR1 / Hugging Face (data card: Apache-2.0) | keep under the dataset's terms; `audit/results/heavy_linux/NOTICE.md` already says so |
| `audit/results/offline_policy/*`, `e3_linux/*` | statistics and per-id scores derived from the human-label CSV (MIT) and OpenR1 answers; no answer texts | author for the derived numbers | Apache-2.0 for the records; cite the MIT CSV and OpenR1 sources in NOTICE |
| `audit/results/thesis_runs/*` | re-derivations from the author's input archive (`e29d296`) | author | same as other results |
| `audit/*.md`, `paper/*.md` (documentation) | written for this audit | author | CC BY 4.0, like the manuscript, or Apache-2.0 with the code; the author chooses |
| `paper/main.tex`, `paper/refs.bib`, PDFs | manuscript | author | as stated in the manuscript (CC BY 4.0 proposed; see `paper/SUBMISSION_CHECKLIST.md`) |

Not redistributed here and therefore not covered: verl and Math-Verify source trees (linked by fixed revision),
OpenR1-Math-220k beyond the three texts above, and the human-label CSV itself.

## Draft files (to add only after the author decides)

`audit/LICENSE`: the unmodified Apache License 2.0 text (same as the companion's `LICENSE`).

`audit/NOTICE`:

```text
Copyright 2026 Yufeiyang Chen

The original code under audit/ is licensed under the Apache License, Version 2.0; see LICENSE.
Substantial AI assistance (Claude, Codex) is disclosed in the manuscript's author contribution statement.

This licence does not apply to the manuscript, to upstream software or datasets, or to the following:
- audit/upstream_chain/patches/0001-*.patch ports verl pull request #7151 by keepkeen (head 96eead6) and
  contains verl source code; it remains under verl's Apache-2.0 licence and copyright headers.
- audit/upstream_chain/patches/0002-*.patch modifies verl source files; verl's copyright notices apply to the
  unchanged context.
- audit/experiments/e3_linux/e3_child.py follows the Math-Verify call sequence of verl PR #8015
  (verl, Apache-2.0).
- audit/results/heavy_linux/*/spec.json contain texts from OpenR1-Math-220k
  (revision e4e141ec9dea9f8326f4d347be56105859b2bd68), whose data card declares Apache-2.0.
- Results derived from the human-label CSV cite its repository, which declares MIT.
```
