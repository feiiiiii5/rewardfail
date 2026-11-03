"""Re-derive the 2026-11-02 chain results from raw outputs, without the driver's own flags.

For each case: scores and error-bearing rows are read from export/1.jsonl (the real
_write_generations output) and injected rows from ledger.jsonl (written by the injector in the
scoring subprocess) and from the injection marker in the exported response text. These are
compared with the expected vectors declared in verify_run.py (imported read-only) and with the
values the driver wrote to case.json. Aborted cases have no export; their raise site is read
from case.json only (driver-reported). stdlib only.

Usage: python3 -I rederive_chain_exports.py <chain dir>
"""
import json
import runpy
import sys
from pathlib import Path

chain = Path(sys.argv[1])
g = runpy.run_path(str(chain / "verify_run.py"), run_name="not_main")
expected = {**g["EXPECTED"], **g["ORIG_EXPECTED"]}
MARK = "[[INJECT_WORKER_DEATH]]"
out = {}
for case, exp in expected.items():
    d = chain / "run-01" / case
    rec = json.loads((d / "case.json").read_text(encoding="utf-8"))
    led = [json.loads(x) for x in (d / "ledger.jsonl").read_text().splitlines() if x.strip()] if (d / "ledger.jsonl").exists() else []
    led_rows = sorted({int(x["row"]) for x in led})
    r = {"outcome_case_json": rec.get("outcome"), "ledger_rows": led_rows, "ledger_entries": len(led)}
    order = rec.get("order")  # position -> original id, when the driver permuted rows
    if (d / "export/1.jsonl").exists():
        rows = [json.loads(x) for x in (d / "export/1.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        scores = [x["score"] for x in rows]
        err_pos = [i for i, x in enumerate(rows) if x.get("error") is not None]
        marked_pos = [i for i, x in enumerate(rows) if MARK in x["output"]]
        orig = (lambda i: order[i]) if isinstance(order, list) and len(order) == len(rows) else (lambda i: i)
        r.update({"export_rows": len(rows), "export_scores": scores, "export_error_positions": err_pos,
                  "export_marked_positions": marked_pos,
                  "export_error_original_ids": sorted(orig(i) for i in err_pos),
                  "has_error_key_in_export": any("error" in x for x in rows)})
        r["scores_equal_expected"] = scores == [float(s) for s in exp["scores"]]
        r["scores_equal_case_json"] = scores == rec.get("row_scores")
        if case in g["EXPECTED"]:
            r["error_rows_equal_planned"] = r["export_error_original_ids"] == sorted(exp["fail"])
        else:
            r["error_flag_lost_in_export"] = not err_pos
        r["error_rows_equal_marked"] = err_pos == marked_pos if case in g["EXPECTED"] else None
        r["ledger_equals_planned"] = led_rows == sorted(exp["fail"])
    else:
        r["raise_site_case_json"] = rec.get("raise_site")
        r["ledger_equals_planned"] = led_rows == sorted(exp["fail"])
    out[case] = r
summary = {
    "cases": len(out),
    "fixed_cases_scores_and_error_rows_from_export_ok": all(v.get("scores_equal_expected") and v.get("error_rows_equal_planned")
                                                           and v.get("error_rows_equal_marked") for k, v in out.items() if k in g["EXPECTED"]),
    "original_completed_cases_lose_flag_in_export": all(v.get("error_flag_lost_in_export") for k, v in out.items()
                                                        if k in g["ORIG_EXPECTED"] and "export_rows" in v),
    "ledgers_equal_planned": all(v["ledger_equals_planned"] for v in out.values()),
}
print(json.dumps({"summary": summary, "cases": out}, ensure_ascii=False, indent=1))
