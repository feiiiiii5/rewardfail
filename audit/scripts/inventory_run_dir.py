"""List the files a k/u re-verification would need from a stage-two run directory (author runs this locally).

Prints JSON with relative path, byte size and SHA-256 for the reference-pass event files listed in
audit/MAIN_METRIC.md (step 1/2), plus totals per pattern. It does not print file contents, so the output
can be shared to plan a transfer. Add --all-passes for the eight-pass inventory (step 3).

Usage: python3 -I inventory_run_dir.py <stage2/runs/main-20261007-202545> [--all-passes] > inventory.json
"""
import hashlib
import json
import sys
from pathlib import Path

PATTERNS = ["obs-*.jsonl", "child_logs/child-*.jsonl", "guard*.jsonl", "results-*.jsonl", "warm-*.jsonl",
            "interrupts.json", "pass_spec.json", "pass_done.json"]
PASSES = ["default", "reference", "limit2s", "limit10s", "replay1", "replay2", "replay3", "retest"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    run = Path(sys.argv[1])
    passes = PASSES if "--all-passes" in sys.argv else ["reference"]
    out = {"run_dir_name": run.name, "passes": {}}
    for ps in passes:
        files, totals = [], {}
        for pat in PATTERNS:
            for p in sorted((run / ps).glob(pat)):
                n = p.stat().st_size
                files.append({"path": f"{ps}/{p.relative_to(run / ps)}", "bytes": n, "sha256": sha(p)})
                totals[pat] = totals.get(pat, 0) + n
        out["passes"][ps] = {"files": files, "bytes_by_pattern": totals, "bytes_total": sum(totals.values()),
                             "n_files": len(files)}
    for extra in ("run.json", "report.json"):
        p = run / extra
        if p.exists():
            out[extra] = {"bytes": p.stat().st_size, "sha256": sha(p)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
