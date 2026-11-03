"""Independent recount of the companion's *derived* default-pass records.

Standard library only; read-only. Run with ``python3 -I -B`` and pass the root of
an extracted companion archive. This script was written on 2026-11-03 for the
evidence audit; it is separate from, and stricter than, the archive's own
``experiments/audit_public_evidence.py``:

* it re-derives each row's outcome class from the stored step records instead of
  trusting the stored ``class`` label, and reports any disagreement;
* it checks that main and complement ids are disjoint and that every complement
  answer belongs to a main question (the 193,767 denominator);
* it reconstructs per-question answer counts, the 92,287 eligible questions and
  the 103 directed event pairs from row ids;
* it checks rows with more than one attempt (retries) are counted once;
* it cross-checks the k/u row ids published in the formal reports against the
  default-pass records (this is a consistency check, NOT a reconstruction of k
  or u: the corrected main reference-pass rows are not in the archive).

Nothing here re-runs a verifier. Results describe derived records only.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

SIDE = {"gold_parse": "标准答案侧解析", "pred_parse": "回答侧解析", "compare": "比较"}


def derive_class(row):
    """Mirror of rewardfail/s2/analyze.py::classify restricted to fields kept in rows.jsonl."""
    if row.get("undetermined"):
        return "未裁定（" + row["undetermined"] + "）"
    atts = row["attempts"]
    if any(a.get("budget_killed") for a in atts):
        return "本机预算终止（未裁定）"
    if row.get("problems"):
        return "观测不完整（未裁定）"
    if row.get("exc"):
        return "最终异常（" + row["exc"] + "）"
    outs = [a.get("outcome") for a in atts]
    last = atts[-1]["steps"] if atts else []
    any_timeout = any(c.startswith("Timeout") for a in atts for s in a["steps"] for c in s[3])
    if row["score"] == 1:
        return "1 分" + ("（重试后）" if len(outs) > 1 else "") + ("，有库超时日志" if any_timeout else "")
    if "outer_timeout" in outs:
        return "0 分：外层超时"
    if "lib_timeout_exc" in outs:
        return "0 分：库超时异常（壳层）"
    tags = sorted({SIDE[s[0]] + ("超时" if c.startswith("Timeout") else "出错")
                   for s in last for c in s[3] if c.startswith(("Timeout", "Error"))})
    return "0 分：" + "、".join(tags) if tags else "正常 0"


def load(path):
    rows, warm = {}, 0
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("warm"):
                warm += 1
                continue
            if r["id"] in rows:
                raise ValueError("duplicate id " + r["id"])
            rows[r["id"]] = r
    return rows, warm


def has_event(r):
    return any(c.startswith(("Error", "Timeout")) for a in r["attempts"] for s in a["steps"] for c in s[3])


def summarise(rows):
    stored, derived, mism = Counter(), Counter(), []
    multi_attempt = 0
    for i, r in rows.items():
        stored[r["class"]] += 1
        d = derive_class(r)
        derived[d] += 1
        if d != r["class"]:
            mism.append((i, r["class"], d))
        multi_attempt += len(r["attempts"]) > 1
    return {"n": len(rows), "stored_classes": dict(stored), "derived_classes": dict(derived),
            "class_mismatches": mism[:20], "n_class_mismatches": len(mism),
            "rows_with_multiple_attempts": multi_attempt,
            "event_rows": sum(map(has_event, rows.values())),
            "event_rows_score_one": sum(has_event(r) and r["score"] == 1 for r in rows.values()),
            "max_wall": max((r["wall"] or 0) for r in rows.values())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    a = ap.parse_args()
    root = a.root.resolve()
    main_rows, mw = load(root / "records/main-20261007-202545/default/rows.jsonl")
    comp_rows, cw = load(root / "records/e2-complement-20261008-codex/default/rows.jsonl")
    out = {"input_sha256": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in (
        "records/main-20261007-202545/default/rows.jsonl",
        "records/e2-complement-20261008-codex/default/rows.jsonl",
        "results/s2_main/report.json", "results/s2_e2/report.json")},
        "warmups_excluded": {"main": mw, "complement": cw},
        "main": summarise(main_rows), "complement": summarise(comp_rows)}
    # --- identity and denominators
    mkeys = {i[2:] for i in main_rows}
    assert all(i.startswith("m-") and len(i) == 18 for i in main_rows)
    per_q = defaultdict(list)
    bad = []
    for i in comp_rows:
        p, key, idx = i.split("-")
        if p != "e2" or key not in mkeys:
            bad.append(i)
        per_q[key].append(int(idx))
    dup_idx = [k for k, v in per_q.items() if len(v) != len(set(v))]
    sizes = Counter(len(per_q.get(k, [])) + 1 for k in mkeys)
    out["identity"] = {
        "main_ids_unique_16hex_prefixes": len(mkeys) == len(main_rows),
        "main_complement_id_overlap": len(set(main_rows) & set(comp_rows)),
        "complement_ids_not_matching_a_main_question": len(bad),
        "questions_with_duplicate_complement_index": len(dup_idx),
        "max_complement_index_exceeds_size": sum(max(v) >= len(v) + 1 for v in per_q.values()),
        "question_sizes": dict(sorted(sizes.items())),
        "n_answers": len(main_rows) + len(comp_rows),
        "eligible_multi_answer_questions": sum(v for s, v in sizes.items() if s >= 2)}
    # --- directed event pairs (paper §5.6)
    ev = defaultdict(list)
    for i, r in main_rows.items():
        ev[i[2:]].append(has_event(r))
    for i, r in comp_rows.items():
        ev[i.split("-")[1]].append(has_event(r))
    pairs = both = 0
    eq = mq = 0
    for k, flags in ev.items():
        if len(flags) < 2:
            continue
        ne = sum(flags)
        eq += ne > 0
        mq += ne > 1
        for f in flags:
            if f:
                pairs += len(flags) - 1
                both += ne - 1
    out["pairs"] = {"event_questions_among_eligible": eq, "multiple_event_questions": mq,
                    "directed_pairs": pairs, "both_event_pairs": both}
    # --- consistency of published k/u ids with default records
    mr = json.loads((root / "results/s2_main/report.json").read_text(encoding="utf-8"))
    er = json.loads((root / "results/s2_e2/report.json").read_text(encoding="utf-8"))
    ud = mr["u_detail"]
    out["published_ids_vs_default_records"] = {
        "main_k_ids_default_class": {i: main_rows[i]["class"] for i in mr["k_ids"]},
        "main_u_ids_default_class_matches_report": all(main_rows[i]["class"] == d["default"] for i, d in ud.items()),
        "main_u_ids_all_default_zero": all(main_rows[i]["score"] == 0 for i in ud),
        "main_u_count": len(ud),
        "ext_k_ids_default_score": {i: comp_rows[i]["score"] for i in er["extension"]["k_ids"]},
        "ext_u_ids_all_default_zero": all(comp_rows[i]["score"] == 0 for i in er["extension"]["u_ids"]),
        "ext_u_count": len(er["extension"]["u_ids"]),
        "reference_classes_sum": sum(mr["reference_classes"].values()),
        "expected_reference_rows": out["main"]["derived_classes"].get("正常 0", 0) + sum(
            v for c, v in out["main"]["derived_classes"].items() if c.startswith("0 分")) + 1000,
    }
    # --- report-aggregate-only sensitivity (not row-verified)
    rc = mr["reference_classes"]
    err_zero = sum(v for c, v in rc.items() if c.startswith("0 分") and "超时" not in c)
    n = mr["main_metric"]["n"]
    out["error_inclusive_sensitivity_from_report_aggregates"] = {
        "reference_error_zero_rows_counted_as_score_0_by_frozen_rule": err_zero,
        "premise": "all 1,000 default-1 control rows were 1 under reference, so these error zeros are default-0 rows and are disjoint from k and u (one reference class per row)",
        "row_pairing_verified": False,
        "k": mr["main_metric"]["k"], "u_frozen": mr["main_metric"]["u"],
        "u_error_inclusive": mr["main_metric"]["u"] + err_zero,
        "upper_endpoint_frozen": (mr["main_metric"]["k"] + mr["main_metric"]["u"]) / n,
        "upper_endpoint_error_inclusive": (mr["main_metric"]["k"] + mr["main_metric"]["u"] + err_zero) / n}
    rep = er["question_descriptions"]
    out["agreement_with_e2_report"] = {
        "question_sizes": {str(k): v for k, v in out["identity"]["question_sizes"].items()} == rep["question_sizes"],
        "eligible": out["identity"]["eligible_multi_answer_questions"] == rep["eligible_multi_answer_questions"],
        "event_questions": eq == rep["event_questions_among_eligible"],
        "multiple_event_questions": mq == rep["multiple_event_questions"],
        "directed_pairs": pairs == rep["directed_other_answer_pairs"],
        "both_event_pairs": both == rep["observed_both_event_pairs"],
        "combined_classes": dict(Counter(out["main"]["derived_classes"]) + Counter(out["complement"]["derived_classes"])) == rep["default_classes"],
        "main_table2": out["main"]["derived_classes"] == mr["default_classes"]}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    ok = all(out["agreement_with_e2_report"].values()) and out["main"]["n_class_mismatches"] == 0 \
        and out["complement"]["n_class_mismatches"] == 0 and out["identity"]["main_complement_id_overlap"] == 0 \
        and out["identity"]["complement_ids_not_matching_a_main_question"] == 0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
