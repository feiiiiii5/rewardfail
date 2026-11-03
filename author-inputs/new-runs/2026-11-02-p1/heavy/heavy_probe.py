"""Natural heavy-input batch propagation probe through the real reward loop.

Uses the four historical D1 heavy rows (IMO 1981 P6 and the power tower),
fixed answers, real AgentLoopManager + RateLimitedRewardManager + Math-Verify.
No fault injection; this is a conditional natural-input propagation test,
not a natural-incidence estimate.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path("<WORKSPACE>/rewardfail")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import c1c_chain
import thesis_chain as tc

HERE = Path(__file__).resolve().parent
HEAVY = json.loads((HERE / "heavy_rows.json").read_text(encoding="utf-8"))["rows"]


def make_config(verl_dir, agent_workers=2):
    cfg = tc.__dict__["_orig_make_config"](verl_dir, agent_workers)
    cfg.actor_rollout_ref.rollout.prompt_length = 128
    cfg.actor_rollout_ref.rollout.response_length = 65536
    return cfg


def build_case(name):
    normal = [list(x) for x in c1c_chain.ROWS]
    if name == "H1":
        rows = normal[:]
        rows[2] = [f"Heavy question {HEAVY[0]['id']}", HEAVY[0]["answer"], HEAVY[0]["generation"]]
        positions = [2]
    elif name == "H3":
        rows = []
        for i in range(3):
            rows.append([f"Heavy question {HEAVY[i]['id']}", HEAVY[i]["answer"], HEAVY[i]["generation"]])
        rows += normal[:5]
        positions = [0, 1, 2]
    else:
        raise SystemExit(name)
    return rows, positions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, choices=["H1", "H3"])
    ap.add_argument("--verl-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", required=True, choices=["original", "fixed"])
    ap.add_argument("--run-id", default="run-01")
    args = ap.parse_args()

    tc._orig_make_config = tc.make_config
    tc.make_config = make_config
    rows, positions = build_case(args.case)
    tc.ROWS = rows
    tc.CASES = {
        args.case: {
            "order": list(range(len(rows))),
            "failing": [],
            "expected": None,
            "rows": len(rows),
            "mode": args.mode,
            "agent_workers": 2,
        }
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {
        "case": args.case,
        "mode": args.mode,
        "heavy_positions": positions,
        "heavy_ids": [HEAVY[i]["id"] for i in range(len(positions))],
        "heavy_generation_chars": [HEAVY[i]["generation_chars"] for i in range(len(positions))],
        "rows_sha256": __import__("hashlib").sha256(json.dumps(rows, ensure_ascii=False).encode()).hexdigest(),
        "note": "natural heavy inputs, no injection; conditional propagation, not incidence",
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    ns = type("Args", (), {})()
    ns.case = args.case
    ns.verl_dir = args.verl_dir
    ns.out = args.out
    ns.run_id = args.run_id
    ns.export = False
    rc = tc.run_case(ns)
    # annotate the case with heavy metadata after the driver has written it
    cj = out / "case.json"
    if cj.exists():
        rec = json.loads(cj.read_text(encoding="utf-8"))
        rec["heavy_meta"] = meta
        cj.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
