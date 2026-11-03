"""Path A fixed-output batch-size matrix (no model, no Ray)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe


def main():
    dummy = type("Dummy", (), {"reward_loop_worker_handles": None})()
    fixed_fn, fixed_sha = probe.fixed_postprocess()
    out = {}
    for n in (1, 2, 3, 7, 8, 16):
        cases = {"normal": set()}
        cases["error_first"] = {0}
        cases["error_middle"] = {n // 2}
        cases["error_last"] = {n - 1}
        for name, failing in cases.items():
            inputs = probe.make_input(n, failing)
            rec = {"n": n, "failing": sorted(failing)}
            for label, fn in (("original", probe.AgentLoopWorker._postprocess), ("union_fill", fixed_fn)):
                try:
                    data = fn(dummy, inputs)
                    rec[label] = probe.summarize_result(data, None)
                except Exception as exc:
                    rec[label] = probe.summarize_result(None, exc)
            out[f"n{n}_{name}"] = rec
    env = {"verl_file": probe.verl.__file__, "agent_loop_file": probe.al.__file__,
           "fixed_source_sha256": fixed_sha}
    json.dump({"env": env, "cases": out}, open(HERE / "batch_sizes.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    summary = {}
    for k, v in out.items():
        summary[k] = {
            "original_exception": v["original"]["exception_type"],
            "original_keys": v["original"].get("extract_keys"),
            "union_exception": v["union_fill"]["exception_type"],
            "union_keys": v["union_fill"].get("extract_keys"),
        }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
