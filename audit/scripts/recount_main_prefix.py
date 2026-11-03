"""Row-level recount of the main measurement from the author's PRE-CORRECTION rows.

Inputs (read-only): author-inputs/main-run/{default,reference}/rows.jsonl (2026-10-07
records), the companion's derived default rows, the companion's frozen
rewardfail/s2/report.py (default_verdict/ref_verdict, imported unchanged), and the
formal 2026-10-08 report. Writes JSON to stdout. stdlib only.

What this establishes and what it does not:
* default and reference classes as written on 2026-10-07 (before the budget-attribution
  correction), paired by id under the frozen rule -> k, u of the UNCORRECTED records;
* whether the companion's derived default rows are value-identical to the raw rows;
* the ids_sha256 values in pass_spec.json;
* which rows the correction must have reclassified, by comparing with the formal
  report's *aggregate* reference_classes (only aggregates; u_ids from the formal report
  are used only for a labelled consistency comparison, never to fill data).
It cannot re-derive the corrected classes: that needs parent/child event timing
(analyze.returned_at, KILL_MARGIN) which the compact rows do not contain.

Usage: python3 -I -B recount_main_prefix.py <author-inputs> <companion>
"""
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


def rows(path):
    out, warm, order, seen = {}, [], [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["id"] in seen:
            raise ValueError("duplicate id " + r["id"])
        seen.add(r["id"])
        if r.get("warm") or str(r["id"]).startswith("warm-"):
            warm.append(r)
            continue
        out[r["id"]] = r
        order.append(r["id"])
    return out, warm, order


def digest(ids):
    return hashlib.sha256("\n".join(ids).encode()).hexdigest()


def apply_changes(counts, changes):
    """Apply aggregate transitions without Counter's silent negative filtering."""
    out = Counter(counts)
    for transition, count in changes.items():
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError("transition count must be a nonnegative integer")
        source, target = transition.split(" → ")
        out[source] -= count
        out[target] += count
    return {key: value for key, value in out.items() if value != 0}


def reconcile_reference(nonwarm_classes, warm_rows, changes, diagnostic, formal):
    """Check all-row report arithmetic, not missing corrected row-level evidence."""
    warm = Counter(row["class"] for row in warm_rows)
    all_before = Counter(nonwarm_classes)
    all_before.update(warm)
    after = apply_changes(all_before, changes)
    reported_after = diagnostic["reference_classes"]["diagnostic"]
    # The residual below comes from two reports, NOT reconstructed warm-up rows.
    residual = {key: after.get(key, 0) - formal.get(key, 0)
                for key in set(after) | set(formal)}
    residual = {key: value for key, value in sorted(residual.items()) if value}
    return {
        "evidence_level": "raw pre-correction counts plus reported aggregate transitions; not corrected per-row reconstruction",
        "pre_correction_warmup_classes": dict(warm),
        "pre_correction_all_row_classes": dict(all_before),
        "pre_correction_all_rows_match_diagnostic_report": dict(all_before) == diagnostic["reference_classes"]["official"],
        "reported_changes_match_diagnostic_report": changes == diagnostic["class_changes"],
        "reconciled_all_row_classes": after,
        "all_row_reconciliation_matches_diagnostic_report": after == reported_after,
        "reported_all_rows_minus_formal_nonwarm_classes": residual,
        "residual_is_nonnegative_and_has_warmup_count": all(value >= 0 for value in residual.values()) and sum(residual.values()) == len(warm_rows),
        "corrected_warmup_classes_independently_reconstructed": False,
        "corrected_nonwarm_classes_independently_reconstructed": False,
    }


def main():
    A, C = Path(sys.argv[1]), Path(sys.argv[2])
    spec = importlib.util.spec_from_file_location("frozen_report", C / "rewardfail/s2/report.py")
    R = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(C))
    spec.loader.exec_module(R)
    d, dwarm, dorder = rows(A / "main-run/default/rows.jsonl")
    r, rwarm, rorder = rows(A / "main-run/reference/rows.jsonl")
    cd, _, _ = rows(C / "records/main-20261007-202545/default/rows.jsonl")
    dspec = json.loads((A / "main-run/default/pass_spec.json").read_text())
    rspec = json.loads((A / "main-run/reference/pass_spec.json").read_text())
    formal = json.loads((A / "reanalysis/s2_main/report.json").read_text(encoding="utf-8"))
    diagnostic_path = A / "reanalysis/budget_attribution_diag.json"
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    def input_label(path):
        root, label = (A, "<author-inputs>") if path.is_relative_to(A) else (C, "<companion>")
        return label + "/" + path.relative_to(root).as_posix()

    out = {"inputs_sha256": {input_label(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        A / "main-run/default/rows.jsonl", A / "main-run/reference/rows.jsonl", C / "rewardfail/s2/report.py",
        C / "rewardfail/s2/analyze.py", A / "reanalysis/s2_main/report.json", diagnostic_path)}}
    out["counts"] = {"default_rows": len(d), "default_warmups": [x["id"] for x in dwarm], "reference_rows": len(r), "reference_warmups": [x["id"] for x in rwarm]}
    out["ids_sha256"] = {
        "default_file_order": digest(dorder) == dspec["ids_sha256"],
        "default_sorted": digest(sorted(dorder)) == dspec["ids_sha256"],
        "reference_file_order": digest(rorder) == rspec["ids_sha256"],
        "reference_sorted": digest(sorted(rorder)) == rspec["ids_sha256"]}
    out["companion_default_value_identical"] = (set(d) == set(cd) and all(d[i] == cd[i] for i in d))
    dcls = {i: x["class"] for i, x in d.items()}
    rcls = {i: x["class"] for i, x in r.items()}
    out["reference_ids_subset_of_default"] = set(r) <= set(d)
    expected_ref = {i for i in d if R.default_verdict(dcls[i]) != 1}
    out["reference_covers_all_default_nonone"] = expected_ref <= set(r)
    out["reference_extra_default_one_controls"] = len(set(r) - expected_ref)
    # frozen rule (imported, unchanged) on the uncorrected classes
    metric, k_ids, u_ids = R.main_metric(dorder, dcls, rcls)
    out["uncorrected_metric"] = {k: metric[k] for k in ("n", "k", "u", "k_by_classes", "u_reasons",
                                                        "lower_one_sided_95_k", "upper_one_sided_95_k_plus_u")}
    out["uncorrected_k_ids"] = k_ids
    out["k_ids_equal_formal"] = sorted(k_ids) == sorted(formal["k_ids"])
    out["uncorrected_reference_classes"] = dict(Counter(rcls.values()))
    out["formal_reference_classes"] = formal["reference_classes"]
    out["formal_class_changes_reported"] = formal["reanalysis"]["class_changes_by_pass"]["reference"]
    # Legacy mixed-scope comparison retained alongside a scoped reconciliation.
    unc = Counter(rcls.values())
    changes = formal["reanalysis"]["class_changes_by_pass"]["reference"]
    rec = apply_changes(unc, changes)
    # A first version (output kept in audit/results/superseded/) compared non-warm-up starting
    # counts with all-row transitions and reported "false". That comparison mixes populations; it
    # is kept only as a labelled diagnostic. The population-consistent result is
    # reference_aggregate_reconciliation below.
    out["legacy_mixed_scope_check"] = {
        "matches": rec == formal["reference_classes"],
        "expected": False,
        "why": "non-warm-up starting counts minus all-row transitions (incl. 3 warm-up rows) cannot equal non-warm-up formal totals; not evidence of a mismatch",
    }
    out["reference_aggregate_reconciliation"] = reconcile_reference(
        unc, rwarm, changes, diagnostic, formal["reference_classes"])
    out["reported_reference_rows_reclassified"] = {
        "all_rows": sum(changes.values()),
        "nonwarm_rows": formal["reanalysis"]["main_rows_changed_by_pass"]["reference"],
        "warm_rows": sum(changes.values()) - formal["reanalysis"]["main_rows_changed_by_pass"]["reference"],
    }
    budget_rows = sorted(i for i, c in rcls.items() if c == "本机预算终止（未裁定）")
    out["uncorrected_budget_killed_reference_rows"] = len(budget_rows)
    out["budget_rows_by_default_class"] = dict(Counter(dcls[i] for i in budget_rows))
    # labelled consistency check only: formal u ids vs uncorrected classes
    fu = formal["u_detail"]
    out["formal_u_ids_check_LABELLED_CONSISTENCY_ONLY"] = {
        "all_in_uncorrected_u": all(i in set(u_ids) for i in fu),
        "uncorrected_reference_class_of_formal_u": dict(Counter(rcls[i] for i in fu)),
        "formal_u_reference_class_equal_uncorrected": sum(rcls[i] == v["reference"] for i, v in fu.items())}
    # error-inclusive sensitivity on the uncorrected records (row-level)
    err_zero = [i for i in dorder if R.default_verdict(dcls[i]) == 0 and rcls.get(i, "").startswith("0 分")
                and "超时" not in rcls[i]]
    out["uncorrected_reference_error_zero_rows"] = len(err_zero)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
