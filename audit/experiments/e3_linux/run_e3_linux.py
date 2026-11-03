"""E3-L driver (see PROTOCOL.md). New Linux run; writes only to --out.

Usage:
  PYTHONPATH=<verl 0c4c3d4>:<this dir> python -B run_e3_linux.py --csv gold.csv \
      --historical <companion>/records/e3-20261008-codex --out <new dir>
"""
import argparse
import csv
import hashlib
import io
import json
import os
import time
from collections import Counter
from pathlib import Path

import e3_child
import verl.utils.reward_score.math_verify as MV

CSV_SHA = "90fca106cb07f031a7ac169e009e6ab9cc0839126912218d0763b0ab6e037005"
WRAPPER_SHA = "f04f57d5cdc08d80197577c77d0bb9d47c2ddc6b4f8e80389ddf7ad3c71c8713"
CONDITIONS = {"L5": (5, 30.0), "L60": (60, 300.0)}


def rows_from(path):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CSV_SHA, "input CSV differs from the fixed source"
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))
    for n, r in enumerate(rows):
        r["id"] = f"e3-{n:05d}"
    groups = {r["group_id"] for r in rows}
    assert (len(rows), len(groups), sum(r["human_label"] == "1" for r in rows)) == (5556, 3041, 2822)
    return rows


def run_pass(rows, presentation, cond, out):
    limit, outer = CONDITIONS[cond]
    os.environ["RF_LIB_LIMIT"] = str(limit)  # inherited by the spawned pool workers
    MV._pool = None
    MV._verify_in_subprocess = e3_child.verify_instrumented
    MV.compute_score("\\boxed{1}", "1", timeout=outer)  # warm-up, discarded
    gen0 = id(MV._pool)
    res, t_pass = {}, time.time()
    with (out / f"{presentation}-{cond}.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            ans = r["raw_answer"]
            if presentation == "boxed" and "\\boxed" in ans:
                continue
            text = ans if presentation == "raw" else "\\boxed{" + ans + "}"
            t = time.time()
            exc, steps = None, []
            try:
                got = MV.compute_score(text, r["gt_answer"], timeout_score=0, timeout=outer)
                score, steps = (got if isinstance(got, tuple) else (got, None))
                outcome = "score" if isinstance(got, tuple) else "outer_timeout_or_timeout_score"
            except Exception as e:  # recorded, never converted to a score
                score, outcome, exc = None, "exception", type(e).__name__
            rec = {"id": r["id"], "presentation": presentation, "condition": cond, "score": score,
                   "outcome": outcome, "exc": exc, "wall": round(time.time() - t, 4), "steps": steps,
                   "pool_replaced": id(MV._pool) != gen0}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            res[r["id"]] = rec
    MV._pool = None
    return res, round(time.time() - t_pass, 1)


def event(rec):
    if rec is None:
        return None
    if rec["outcome"] != "score":
        return True
    return any(c for s in rec["steps"] for c in s[2])


def table(rows, res, alias):
    c = Counter()
    for r in rows:
        rec = res.get(r["id"]) or alias.get(r["id"])
        lab, s, ev = int(r["human_label"]), rec["score"], event(rec)
        c["n"] += 1
        c["label_pos_score0"] += lab == 1 and s == 0
        c["label_neg_score1"] += lab == 0 and s == 1
        c["event_zero"] += bool(ev) and s == 0
        c["event_zero_label_pos"] += bool(ev) and s == 0 and lab == 1
        c["incomplete"] += rec["outcome"] != "score"
    c["disagreement"] = c["label_pos_score0"] + c["label_neg_score1"]
    return dict(c)


def hist_rows(path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if not r.get("warm"):
            out[r["id"]] = r
    return out


def hist_event(r):
    return any(c.startswith(("Timeout", "Error")) for a in r["attempts"] for s in a["steps"] for c in s[3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--historical", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    assert hashlib.sha256(Path(MV.__file__).read_bytes()).hexdigest() == WRAPPER_SHA
    rows = rows_from(a.csv)
    hist_name = {"L5": "observe", "L60": "reference"}
    report = {"protocol": "PROTOCOL.md", "csv_sha256": CSV_SHA, "wrapper_sha256": WRAPPER_SHA,
              "passes": {}, "tables": {}, "historical_agreement": {}}
    for cond in ("L5", "L60"):
        raw, t_raw = run_pass(rows, "raw", cond, a.out)
        boxed, t_box = run_pass(rows, "boxed", cond, a.out)
        alias = {i: raw[i] for i in raw if i not in boxed}
        report["passes"][cond] = {"raw_trials": len(raw), "boxed_trials": len(boxed), "aliases": len(alias),
                                  "seconds": {"raw": t_raw, "boxed": t_box}}
        for pres, res, al in (("raw", raw, {}), ("boxed", boxed, alias)):
            report["tables"][f"{pres}-{cond}"] = table(rows, res, al)
            h = hist_rows(a.historical / f"{pres}-{hist_name[cond]}" / "rows.jsonl")
            merged = {**al, **res}
            same_score = sum(merged[i]["score"] == h[i]["score"] for i in h if i in merged)
            diff = [i for i in h if i in merged and merged[i]["score"] != h[i]["score"]]
            ev_new = {i for i in merged if event(merged[i])}
            ev_old = {i for i in h if hist_event(h[i])}
            report["historical_agreement"][f"{pres}-{cond}"] = {
                "compared_rows": sum(i in merged for i in h), "same_score": same_score, "score_differs": diff,
                "event_rows_new": len(ev_new), "event_rows_historical": len(ev_old),
                "event_only_new": sorted(ev_new - ev_old), "event_only_historical": sorted(ev_old - ev_new),
                "max_wall_new": max(r["wall"] for r in res.values())}
    (a.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
