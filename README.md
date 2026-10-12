# When the Verifier Cannot Decide

**Tracing Math-Verify Failures Through an RLVR Reward Pipeline**

Yufeiyang Chen · manuscript revised 12 October 2026

[Read the paper](paper.pdf) · [Download companion materials](rewardfail-companion.zip)

This is a publicly available research manuscript. It has not been peer reviewed
or posted to arXiv. The companion archive contains code and evidence for
inspection; it does not contain model weights, upstream datasets or the complete
original raw-log archive.

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

## Contribution and assistance

The author selected the research topic, research route and methods. AI agents
provided substantial assistance with implementation, experiment execution,
code analysis and manuscript drafting. The manuscript contains the full
contribution and AI-use statement. Human answer labels in the supplementary
analysis were supplied by the cited dataset authors.

## Licences and fixed files

- Manuscript: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Original companion code and synthetic fixtures: Apache-2.0; see LICENSE and
  NOTICE inside the archive. Third-party sources and datasets retain their own
  licences and notices.

SHA-256 of the distributed files:

```text
8efbb3471d23a8b5396bc1605fb5cf29d4769ee6e0214ede8e63e76f69c46811  paper.pdf
32cdea7d19181eff030707d96db360715231eff058c5add80133c6b1e0fdabdf  rewardfail-companion.zip
```
