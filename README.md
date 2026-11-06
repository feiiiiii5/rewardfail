# When the Verifier Cannot Decide

**Tracing Math-Verify Failures Through an RLVR Reward Pipeline**

Yufeiyang Chen · preprint version of 3 November 2026

**Current version:** [read the paper (PDF, 23 pages)](paper/rewardfail-preprint-2026-11-03.pdf) ·
[arXiv source package](paper/arxiv/rewardfail-arxiv-source.tar.gz) (`main.tex`, `main.bbl`, `refs.bib`;
LaTeX source also in [`paper/main.tex`](paper/main.tex)) ·
[validation record](paper/VALIDATION_FINAL_2026-11-03.md) ·
[reviewer guide](paper/REVIEWER_GUIDE.md) ·
[companion materials](rewardfail-companion.zip)

This is a publicly available research manuscript. It has not been peer reviewed
and has not been posted to arXiv; [`paper/SUBMISSION_CHECKLIST.md`](paper/SUBMISSION_CHECKLIST.md)
records the author's confirmations (licences, authorship, categories). Posting is not yet authorised. The companion
archive contains code and evidence for inspection; it does not contain model weights,
upstream datasets or the complete original raw-log archive.

**Historical versions (kept unchanged, superseded):** [`paper.pdf`](paper.pdf) is the
manuscript revised 12 October 2026 that this repository first published; earlier
3 November drafts are in [`paper/superseded/`](paper/superseded/) and
[`paper/reconstruction-from-pdf/`](paper/reconstruction-from-pdf/). Cite or review the current version above.

**Reproduction snapshot.** The analysis code, result files and number checker used for the
current manuscript are at commit
[`da00bd6`](https://github.com/feiiiiii5/rewardfail/tree/da00bd6dfcad86526b81b5352384a23ae1731752);
later commits change only documentation, front matter and release notes (see
[`paper/CHANGES.md`](paper/CHANGES.md)). Some re-checks additionally read the author's
research input archive at the fixed commit
[`4b3ca90`](https://github.com/feiiiiii5/rewardfail/tree/4b3ca90bdfa44254594f7d4916540c165bfafcb2)
(branch `author-inputs-20261103`, not merged into `main`): the pre-correction main-run rows
(recount of `k = 1`, `u = 9,573`), the heavy-input rows used in the Linux scenes. That archive does not contain the reference-pass event files, so the reported
`u = 18` remains a historical report value; it has not been independently rebuilt from raw
events. See [`audit/REPRODUCE.md`](audit/REPRODUCE.md).

## Study

The study traces failure information from Math-Verify through a pinned verl
reward wrapper, manager and batch aggregation. Controlled worker-failure tests
reproduce a known sparse-metadata problem: the position of a failed row can
determine whether its flag is lost or the batch raises an exception.
The manuscript cites the related upstream proposals
[#6545](https://github.com/verl-project/verl/pull/6545) and
[#7151](https://github.com/verl-project/verl/pull/7151).
Its contribution is the specific wrapper-to-consumer failure trace and the
paired corpus and timeout/recovery measurements. The local aggregation
prototype supplies 21 regression fixtures, not a new repair algorithm.

A pre-declared replay covers 93,733 stored mathematical responses. Longer
checking limits recover one zero-to-one verdict and leave 18 responses
undecided. A separate extension covers all 193,767 stored answers. Matched
shared-pool tests and a fixed-source comparison distinguish the behavior of
wrappers and execution settings.

These results are conditional on the fixed corpora and declared protocols.
Longer checking is not mathematical ground truth. Controlled failure injections
and shared-pool diagnostics do not measure failure rates in training, and no
training benefit has been measured. The paper states the sampling assumptions,
comparison units and limits of inference.

## Inspect the evidence

Extract the companion archive into a fresh directory. From its root, run:

```sh
python3 -B experiments/check_artifacts.py --index package_manifest.json
python3 -B experiments/compare_runs.py
```

These commands inspect the distributed snapshot without installing packages
or downloading data. The archive includes compact reports, derived score records,
selected event traces, synthetic checks, exact upstream source revisions and a
file manifest. Its README explains which records are included and which are
omitted.

Replaying the measurements requires the documented dependencies, upstream
sources and separately obtained datasets. The measured environment was macOS
arm64 with CPython 3.12.8. A fresh installation and Linux have not been
experimentally validated. Follow the archive's instructions in a fresh environment;
do not overwrite retained original records or an existing measurement environment.

## Public evidence clarification (3 November 2026)

The manuscript PDF and its reported measurements are unchanged. The companion
now includes EVIDENCE_STATUS.md and a read-only, standard-library audit:

```sh
python3 -B experiments/audit_public_evidence.py
```

This independently counts the distributed default-pass derived records and
checks recorded regression outcomes. It is not a new scoring experiment or an
independent raw-event replication. The corrected main reference records and
complete historical reanalysis inputs remain unavailable in the public package,
so k=1 and u=18 are reported values, not independently reconstructed by this audit.
The note also distinguishes reference-protocol unresolved rows from all library
execution failures and lists the evidence still needed. No training benefit or
fresh-machine replication has been added.

## Evidence audit and revision (3 November 2026)

The audit adds, without changing the historical `paper.pdf` or the companion archive:

- [`audit/EVIDENCE_MAP.md`](audit/EVIDENCE_MAP.md): claim-to-evidence table and every check run.
- [`audit/GAPS.md`](audit/GAPS.md): what still cannot be verified and the smallest input that would close each gap.
- [`audit/REPRODUCE.md`](audit/REPRODUCE.md): commands, environment and stored results.
- [`audit/upstream_chain/`](audit/upstream_chain/): real-function failure-chain tests and two patches
  for verl `0c4c3d4` (a port of the open upstream PR #7151, and a validation-accumulation fix).
- [`audit/experiments/e3_linux/`](audit/experiments/e3_linux/): a new, pre-specified Linux replay of the labelled answer set.
- [`paper/`](paper/): the author's original LaTeX source, revised ([`paper/CHANGES.md`](paper/CHANGES.md)),
  with build notes, the compiled preprint and the arXiv source package; an earlier editable
  reconstruction from the public PDF is kept in `paper/reconstruction-from-pdf/`.
- [`audit/experiments/offline_policy/`](audit/experiments/offline_policy/): the offline handling-policy
  comparison of §8.2 (synthetic failures on 72 human-labelled groups; a mechanism analysis, not a
  training result or a natural failure rate).
- [`audit/scripts/check_paper_numbers.py`](audit/scripts/check_paper_numbers.py): checks manuscript numbers
  against their source files, with counter-tests.

New executions ran on Linux x86-64 (CPython 3.12.8); they are additional verification, not a replay
of the historical macOS environment. Recounting the distributed derived records is not an independent
reproduction from raw data. The author's pre-correction rows reproduce k = 1 and the uncorrected u = 9,573; the corrected u = 18 remains a report-only value.

## Contribution and assistance

The author selected the research topic, research route and methods. AI agents
provided substantial assistance with implementation, experiment execution,
code analysis and manuscript drafting. The manuscript contains the full
contribution and AI-use statement. Human answer labels in the supplementary
analysis were supplied by the cited dataset authors.

## Licences and fixed files

- Manuscript: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (confirmed by the author).
- Original companion code and synthetic fixtures: Apache-2.0; see LICENSE and
  NOTICE inside the archive.
- Original code, records and documentation under `audit/`: Apache-2.0; see
  [`audit/LICENSE`](audit/LICENSE) and [`audit/NOTICE`](audit/NOTICE). The NOTICE lists the parts that keep
  third-party terms (verl code in the two patches, OpenR1 texts in the heavy-scene specs, the MIT human-label
  CSV); see [`audit/LICENSING_PLAN.md`](audit/LICENSING_PLAN.md).
- Third-party sources and datasets retain their own licences and notices.

SHA-256 of the distributed files (historical `paper.pdf` and companion archive):

```text
8efbb3471d23a8b5396bc1605fb5cf29d4769ee6e0214ede8e63e76f69c46811  paper.pdf
2aaf2113ebc11a5396dc17408a40534419bb14b70589de30a832c146a1381ae4  rewardfail-companion.zip
```
