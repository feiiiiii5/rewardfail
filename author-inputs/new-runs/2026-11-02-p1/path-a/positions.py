"""Expanded position matrix for the path A fixed-output probe."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe


def main():
    dummy = type("Dummy", (), {"reward_loop_worker_handles": None})()
    fixed_fn, fixed_src_sha = probe.fixed_postprocess()
    results = {}
    for kind in ("error", "timeout"):
        for pos in range(8):
            n, failing = 8, {pos}
            inputs = probe.make_input(n, failing, mixed=False)
            if kind == "timeout":
                # make_input only adds error; move it to timeout for this case
                for i in failing:
                    extra = inputs[i].extra_fields["reward_extra_info"]
                    extra.pop("error", None)
                    extra["timeout"] = True
            rec = {"n": n, "kind": kind, "position": pos}
            for label, fn in (("original", probe.AgentLoopWorker._postprocess), ("union_fill", fixed_fn)):
                try:
                    out = fn(dummy, inputs)
                    rec[label] = probe.summarize_result(out, None)
                except Exception as e:
                    rec[label] = probe.summarize_result(None, e)
            results[f"{kind}_pos_{pos}"] = rec
    env = {
        "time": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "verl_file": probe.verl.__file__,
        "agent_loop_file": probe.al.__file__,
        "fixed_source_sha256": fixed_src_sha,
    }
    json.dump({"env": env, "cases": results}, open(HERE / "positions.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    summary = {}
    for k, v in results.items():
        summary[k] = {
            "original_exception": v["original"]["exception_type"],
            "original_extract_keys": v["original"].get("extract_keys"),
            "union_fill_exception": v["union_fill"]["exception_type"],
            "union_fill_extract_keys": v["union_fill"].get("extract_keys"),
        }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
