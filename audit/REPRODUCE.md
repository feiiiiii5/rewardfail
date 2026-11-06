# Reproducing the 2026-11-03 audit

Pinned states: analysis code and results at commit `da00bd6` (unchanged by later documentation commits); author input
archive at commit `4b3ca90` (branch `author-inputs-20261103`, read only, not merged into `main`).

The original executions used the research files retained byte-for-byte in this input snapshot; the commands now select its current metadata and research-input location. No historical measurement is rerun by this documentation update.

The original audit ran on a **new Linux environment** (`audit/results/environment.json`):
Ubuntu 24.04 container, x86-64, 4 vCPU, 15.7 GiB RAM, no GPU, CPython 3.12.8 (uv-managed).
The historical measurements used macOS arm64 / CPython 3.12.8; nothing here replays that host.

Never run these in a directory holding original measurement records; every command writes
to a fresh output path.

## 0. Extract the companion safely

```bash
mkdir -p /tmp/rf/zip && cp rewardfail-companion.zip /tmp/rf/zip/
mkdir -p /tmp/rf/companion
python3 -I audit/scripts/safe_unzip.py /tmp/rf/zip/rewardfail-companion.zip /tmp/rf/companion
```

`safe_unzip.py` refuses absolute paths, `..`, backslashes and symlinks before extracting.

## 1. Public-package checks (standard library only)

```bash
cd /tmp/rf/companion
python3 -I -B experiments/check_artifacts.py --index package_manifest.json
python3 -I -B experiments/compare_runs.py
python3 -I -B experiments/audit_public_evidence.py
```

Then the stricter derived-record recount from this repository:

```bash
python3 -I -B audit/scripts/recount_derived_records.py /tmp/rf/companion > /tmp/rf/recount.json
```

## 2. Environment for the executed checks

```bash
pip install uv
uv python install 3.12.8
uv venv --python 3.12.8 /tmp/rf/venv
uv pip sync --python /tmp/rf/venv/bin/python /tmp/rf/companion/requirements.lock
uv pip install --python /tmp/rf/venv/bin/python "torch==2.14.1"
```

The second install is needed on Linux only: the lock was generated on macOS and lacks the
CUDA runtime wheels that the Linux `torch` wheel imports (CPU is used throughout).

```bash
git clone --filter=blob:none https://github.com/verl-project/verl.git /tmp/rf/verl
git -C /tmp/rf/verl fetch origin pull/7151/head:pr7151
git -C /tmp/rf/verl worktree add --detach /tmp/rf/companion/third_party/verl-pr8015 0c4c3d40d46d5f47d1918c905641eea969b7fa09
git -C /tmp/rf/verl worktree add -b fixed /tmp/rf/verl-fixed 0c4c3d40d46d5f47d1918c905641eea969b7fa09
git -C /tmp/rf/verl-fixed am audit/upstream_chain/patches/0001-*.patch audit/upstream_chain/patches/0002-*.patch
uv pip install --python /tmp/rf/venv/bin/python --no-deps -e /tmp/rf/companion/third_party/verl-pr8015
```

## 3. Mechanism checks

Companion fixtures (21) on Linux (writes only the given output file):

```bash
PYTHONPATH=/tmp/rf/companion/third_party/verl-pr8015 /tmp/rf/venv/bin/python -B audit/scripts/run_contract_fixtures_linux.py /tmp/rf/companion /tmp/rf/contract_fixtures_linux.json
```

Real-function failure-chain suite, unpatched and patched:

```bash
PYTHONPATH=/tmp/rf/companion/third_party/verl-pr8015:audit/upstream_chain /tmp/rf/venv/bin/python -B -m pytest -q -p no:cacheprovider audit/upstream_chain/test_reward_chain.py
```

```bash
PYTHONPATH=/tmp/rf/verl-fixed:audit/upstream_chain /tmp/rf/venv/bin/python -B -m pytest -q -p no:cacheprovider audit/upstream_chain/test_reward_chain.py
```

Expected: unpatched exits 1 (11 tests with failures, all in batch path, generation path,
prototype and validation consumers); patched exits 0 (30 passed, 3 prototype-only skipped).

C1c injection trace under a real local Ray session (about 6 minutes each):

```bash
cd /tmp/rf/companion && HOME=/tmp/rf/home /tmp/rf/venv/bin/python -B experiments/c1c_chain.py --all --out /tmp/rf/c1c_linux
```

For the patched tree, copy the companion to a second directory whose
`third_party/verl-pr8015` is a symlink to `/tmp/rf/verl-fixed`, and prefix the command with
`PYTHONPATH=<that copy>/third_party/verl-pr8015` so the driver and the Ray workers import the
patched tree.

## 4. E3-L labelled replay (new experiment; protocol in `audit/experiments/e3_linux/PROTOCOL.md`)

```bash
mkdir -p /tmp/rf/e3data && curl -sSo /tmp/rf/e3data/gold.csv https://raw.githubusercontent.com/ethxin0011/rlvr_group_correlation/ccb330209370ddbbd76717658074abd54a7c45d0/data/gold/gold_set_1p5b_manual_labeled.csv
```

```bash
PYTHONPATH=/tmp/rf/companion/third_party/verl-pr8015:audit/experiments/e3_linux /tmp/rf/venv/bin/python -B audit/experiments/e3_linux/run_e3_linux.py --csv /tmp/rf/e3data/gold.csv --historical /tmp/rf/companion/records/e3-20261008-codex --out /tmp/rf/e3_linux_new
```

The script refuses a CSV whose SHA-256 is not `90fca106…` and a wrapper whose SHA-256 is not
`f04f57d5…`, and refuses an existing output directory.

## Results stored in this repository

| Path | Content |
|---|---|
| `audit/results/environment.json` | OS, Python, package versions, verl heads |
| `audit/results/companion_selfchecks/` | outputs of the three public checks and the tail of every companion test |
| `audit/results/recount_derived_records.json` | derived-record recount |
| `audit/results/contract_fixtures_linux.json` | 21 fixtures on Linux vs historical |
| `audit/results/chain_verl-pr8015.*`, `chain_verl-fixed.*` | real-function suite (text + JUnit XML) |
| `audit/results/c1c_linux/`, `c1c_linux_fixed/` | C1c per-case JSON and injection ledgers |
| `audit/results/e3_linux/` | E3-L per-row records and report |

## Second pass (author inputs, 2026-11-03)

Fetch the author inputs read-only into a fresh directory (never into the working tree):

```bash
mkdir -p /tmp/rf/author && git archive 4b3ca90bdfa44254594f7d4916540c165bfafcb2 author-inputs | tar -x -C /tmp/rf/author && chmod -R a-w /tmp/rf/author
```

Delivery manifest (hash, bytes, path):

```bash
cd /tmp/rf/author/author-inputs && python3 -I -c "import hashlib,os;r=[l.rstrip('\n').split('  ',2) for l in open('MANIFEST.sha256',encoding='utf-8')];print(sum(os.path.isfile(p) and hashlib.sha256(open(p,'rb').read()).hexdigest()==h and os.path.getsize(p)==int(n) for h,n,p in r),'/',len(r))"
```

Main metric from the supplied pre-correction rows (frozen `report.py` imported unchanged):

```bash
python3 -I -B audit/scripts/recount_main_prefix.py /tmp/rf/author/author-inputs /tmp/rf/companion
```

Report copies vs companion copies:

```bash
python3 -I audit/scripts/compare_redacted_json.py /tmp/rf/companion/results/s2_e3/report.json /tmp/rf/author/author-inputs/results/s2_e3/report.json
```

Companion tests on Linux with the portability patch (in a copy of the extracted companion):

```bash
cd /tmp/rf/companion && git apply <repo>/audit/companion_fixes/linux-portability.patch
```

```bash
mkdir -p /tmp/rf/hist && tar -xzf /tmp/rf/author/author-inputs/history/9a88991/code.tar.gz -C /tmp/rf/hist
```

```bash
cd /tmp/rf/companion && RF_OLD_ANALYZE=/tmp/rf/hist/rewardfail/s2/analyze.py /tmp/rf/venv/bin/python -I -B tests/test_s2_budget.py
```

```bash
cd /tmp/rf/companion && bash tests/test_get_data.sh C.UTF-8 get_data.sh
```

Heavy-input scenes (protocol `audit/experiments/heavy_linux/PROTOCOL.md`; about 7 minutes; needs ≥ 12 GiB free):

```bash
/tmp/rf/venv/bin/python -B audit/experiments/heavy_linux/run_heavy_linux.py --companion /tmp/rf/companion --heavy /tmp/rf/author/author-inputs/research-inputs/heavy_rows.json --base-verl /tmp/rf/companion/third_party/verl-pr8015 --fixed-verl /tmp/rf/verl-fixed --python /tmp/rf/venv/bin/python --out /tmp/rf/heavy_linux_new
```

Manuscript: see `paper/BUILD.md`.
