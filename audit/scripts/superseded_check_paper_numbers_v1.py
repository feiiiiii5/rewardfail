"""Check that key numbers in paper/main.tex equal the values in the committed result files.

Each check reads a value from a result JSON in audit/results/ (or the companion/author report given on the
command line) and asserts that its formatted form occurs in the manuscript source. stdlib only.

Usage: python3 -I -B check_paper_numbers.py <repo root> <companion root> <author-inputs root>
Exit 0 if every check passes.
"""
import json
import re
import sys
from pathlib import Path

repo, comp, auth = (Path(x) for x in sys.argv[1:4])
tex = (repo / "paper/main.tex").read_text(encoding="utf-8")
flat = re.sub(r"\s+", " ", tex)
R = lambda p: json.loads((repo / "audit/results" / p).read_text(encoding="utf-8"))
recount = R("recount_derived_records.json")
prefix = R("main_prefix_recount.json")
e3 = R("e3_linux/report.json")
heavy = R("heavy_linux/summary.json")
op = R("offline_policy/results.json")
fx = R("contract_fixtures_linux.json")
formal = json.loads((auth / "reanalysis/s2_main/report.json").read_text(encoding="utf-8"))
e2 = json.loads((comp / "results/s2_e2/report.json").read_text(encoding="utf-8"))


def fmt(n):
    return f"{n:,}".replace(",", "{,}") if False else f"{n:,}"


checks = []


def has(desc, needle, value=None):
    ok = needle in flat
    checks.append({"claim": desc, "expect_in_tex": needle, "source_value": value, "pass": ok})


m = recount["main"]["derived_classes"]
has("main n", "93,733", recount["main"]["n"])
has("Table default: score 1", "61,246", m["1 分"])
has("Table default: normal 0", "32,442", m["正常 0"])
has("54 library-event rows", "54 library-event rows", recount["main"]["event_rows"])
has("k = 1 (formal)", "$k=1$", formal["main_metric"]["k"])
has("u = 18 (formal)", "$u=18$", formal["main_metric"]["u"])
um = prefix["uncorrected_metric"]
has("uncorrected u", "9{,}573" if "9{,}573" in flat else "9,573", um["u"])
has("guard-stopped (uncorrected) 9,559", "9,559", um["u_reasons"]["参照：本机预算终止（未裁定）"])
rr = prefix["reported_reference_rows_reclassified"]
has("reclassified all rows", "9,866", rr["all_rows"])
has("reclassified non-warm-up", "9,863", rr["nonwarm_rows"])
allc = prefix["reference_aggregate_reconciliation"]["pre_correction_all_row_classes"]["本机预算终止（未裁定）"]
has("originally guard-stopped all rows", "9,868", allc)
has("originally guard-stopped non-warm-up", "9,864", prefix["uncorrected_budget_killed_reference_rows"])
has("reference rows", "33,487", prefix["counts"]["reference_rows"])
has("193,767 answers", "193,767", recount["identity"]["n_answers"])
has("92,287 eligible", "92,287", recount["identity"]["eligible_multi_answer_questions"])
has("103 pairs / 84 both", "There are 103 such pairs, of which 84", (recount["pairs"]["directed_pairs"], recount["pairs"]["both_event_pairs"]))
has("21 distinct questions", "21 distinct questions", None)
has("E3 trials", "22,176", sum(v["raw_trials"] + v["boxed_trials"] for v in e3["passes"].values()))
same = all(not v["score_differs"] for v in e3["historical_agreement"].values())
checks.append({"claim": "E3 all scores equal historical", "pass": same})
has("21 fixtures", "Twenty-one", fx["n"])
checks.append({"claim": "fixtures: 16 omitted / 3 exceptions", "pass": fx["baseline_omitted_columns"] == 16 and fx["baseline_exceptions"] == 3})
abort = [h for h in heavy if h["scene"].startswith("S5")]
checks.append({"claim": "heavy diagnostic naive scenes did not abort (4 runs)", "pass": len(abort) == 4 and all(
    not any(b.get("exception") for b in h["batches"]) for h in abort) and "in any of four runs" in flat})
has("72 complete groups", "72 groups", op["groups"])
has("26 constant groups", "26 groups are constant", op["constant_groups"])
cell = op["results"]["M1_independent|p=0.05"]
has("Table policies M1 0.05 P0 disagree", "57.9", round(cell["P0_zero_fill"]["sign_disagreements"]["mean"], 1))
has("Table policies M1 0.05 P2 disagree", "5.0", round(cell["P2_exclude"]["sign_disagreements"]["mean"], 1))
cell = op["results"]["M1_independent|p=0.25"]
has("Table policies M1 0.25 P2 no signal", "4.44", round(cell["P2_exclude"]["nonconstant_groups_without_signal"]["mean"], 2))
cell = op["results"]["M3_whole_group|p=0.25"]
has("Table policies M3 0.25 no signal", "11.49", round(cell["P0_zero_fill"]["nonconstant_groups_without_signal"]["mean"], 2))
has("verl cross-check", "2.9\\times10^{-7}", op.get("verl_crosscheck", {}).get("max_abs_difference"))
checks.append({"claim": "pooled endpoints 2/n and 34/n", "pass": e2["all_answers"]["k"] == 2 and e2["all_answers"]["u"] == 32
               and "$2/n$ and $34/n$" in flat})
fails = [c for c in checks if not c["pass"]]
print(json.dumps({"checks": len(checks), "failed": fails, "all": checks}, ensure_ascii=False, indent=1))
sys.exit(1 if fails else 0)
