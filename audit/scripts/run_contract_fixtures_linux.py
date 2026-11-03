"""Re-execute the companion's 21 aggregation fixtures (experiments/s2_contract.py) on Linux.

New verification run (2026-11-03), not a historical-environment replay. The
companion's macOS-only memory helper (rewardfail/s2/mem.py loads libproc.dylib)
is replaced by an inert stub *module* only so that the import chain loads; the
fixtures never sample memory. The case list, the AST prototype and the invocation
are the companion's own functions, executed unchanged against the verl tree on
PYTHONPATH. Output goes to the path given on the command line; the historical
results/s2_e1/aggregation_contract.json is never written.

Usage: PYTHONPATH=<verl tree> python -B run_contract_fixtures_linux.py <companion root> <out.json>
"""
import hashlib
import inspect
import json
import sys
import types
from pathlib import Path

root, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
stub = types.ModuleType("rewardfail.s2.mem")
stub.__doc__ = "inert Linux stub; aggregation fixtures do not read memory"
stub.footprint = lambda *a, **k: None
stub.__file__ = "<inert-mem-stub>"


def _stub_attr(name):
    if name.startswith("__"):
        raise AttributeError(name)
    return lambda *a, **k: None


stub.__getattr__ = _stub_attr
sys.modules["rewardfail.s2.mem"] = stub
sys.path[:0] = [str(root), str(root / "experiments")]
import s2_contract as C  # noqa: E402
from verl.experimental.reward_loop import reward_loop as R  # noqa: E402

original = R.RewardLoopManager.compute_rm_score
src = Path(inspect.getsourcefile(original))
patched, patch_sha = C.local_patch(original)
records = []
for c in C.cases():
    base, prop = (C.invoke(fn, c["outputs"], c["workers"]) for fn in (original, patched))
    keys = sorted({k for r in c["outputs"] for k in r.get("reward_extra_info", {})})
    exp = {"scores": [r["reward_score"] for r in c["outputs"]],
           "columns": {k: [r.get("reward_extra_info", {}).get(k) for r in c["outputs"]] for k in keys}}
    records.append({"name": c["name"], "workers": c["workers"], "n": len(c["outputs"]),
                    "baseline": base, "proposal": prop, "pass": prop == exp})
hist = json.loads((root / "results/s2_e1/aggregation_contract.json").read_text(encoding="utf-8"))
hist_by = {c["name"]: c for c in hist["cases"]}
result = {
    "what": "Linux re-execution of companion s2_contract fixtures (new verification, not historical environment)",
    "source_path_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
    "historical_source_sha256": hist["source_sha256"],
    "local_patch_ast_sha256": patch_sha, "historical_patch_ast_sha256": hist["local_patch_ast_sha256"],
    "n": len(records), "proposal_passed": sum(r["pass"] for r in records),
    "baseline_exceptions": sum("exception" in r["baseline"] for r in records),
    "baseline_omitted_columns": sum("columns" in r["baseline"] and set(r["baseline"]["columns"]) != set(r["proposal"].get("columns", {})) for r in records),
    "baseline_matches_historical": {r["name"]: r["baseline"] == hist_by[r["name"]]["baseline"] for r in records},
    "proposal_matches_historical": {r["name"]: r["proposal"] == hist_by[r["name"]]["proposal"] for r in records},
    "cases": records}
out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "cases"}, ensure_ascii=False, indent=1))
