"""Compare numbers printed in paper/main.tex with the values in their source files.

Replaces superseded_check_paper_numbers_v1.py, which only searched for hard-coded strings. Each check here
  (1) reads a value from a source file,
  (2) extracts the printed number from a specific location in the manuscript (a table cell addressed by
      row labels and column, or a regular expression anchored on the surrounding sentence), and
  (3) compares them within the rounding tolerance of the printed digits (half a unit in the last place).
Row labels are part of the address, so a swapped table cell fails. stdlib only.

Usage: python3 -I -B check_paper_numbers.py <repo root> <companion root> <author-inputs root>
Exit 0 only if every check passes; the JSON report lists each check with source and printed values.
"""
import json
import re
import sys
from pathlib import Path

POLICY_COLUMNS = ["loss_contributing", "sign_disagreements", "common_zero_to_nonzero", "common_nonzero_to_zero",
                  "common_mean_abs_error", "label1_negative_adv", "nonconstant_groups_without_signal"]
POLICY_SOURCE = {"common_zero_to_nonzero": "supp", "common_nonzero_to_zero": "supp", "common_mean_abs_error": "supp"}
MECH = {"M1 independent": "M1_independent", "M2 correct only": "M2_correct_only", "M3 whole group": "M3_whole_group"}
POL = {"P0": "P0_zero_fill", "P1": "P1_loss_mask_only", "P2": "P2_exclude"}


def load_sources(repo, comp, auth):
    r = lambda p: json.loads((Path(repo) / "audit/results" / p).read_text(encoding="utf-8"))
    return {
        "recount": r("recount_derived_records.json"),
        "prefix": r("main_prefix_recount.json"),
        "e3": r("e3_linux/report.json"),
        "heavy": r("heavy_linux/summary.json"),
        "op": r("offline_policy/results.json"),
        "supp": r("offline_policy/supplement.json"),
        "fixtures": r("contract_fixtures_linux.json"),
        "formal": json.loads((Path(auth) / "reanalysis/s2_main/report.json").read_text(encoding="utf-8")),
        "e2": json.loads((Path(comp) / "results/s2_e2/report.json").read_text(encoding="utf-8")),
    }


def num(text):
    """Parse a printed number: '93,733', '9{,}573', '2.9\\times10^{-7}', '0.007'."""
    t = text.replace("{,}", "").replace(",", "").strip()
    m = re.fullmatch(r"(-?[0-9.]+)\s*\\times\s*10\^\{(-?\d+)\}", t)
    if m:
        return float(m.group(1)) * 10 ** int(m.group(2)), len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
    dec = len(t.split(".")[1]) if "." in t else 0
    return float(t), dec


def close(printed, decimals, value, exponent=0):
    tol = 0.5 * 10 ** (-decimals) * 10 ** exponent + 1e-12
    return abs(printed - value) <= tol


def flat(tex):
    return re.sub(r"\s+", " ", tex)


def policy_table(tex):
    """Return {(mech, p, policy): [cells]} from the generated block, carrying forward blank row labels."""
    a = tex.index("%% BEGIN GENERATED: policy table rows")
    b = tex.index("%% END GENERATED: policy table rows")
    rows, mech, p = {}, None, None
    for line in tex[a:b].splitlines()[1:]:
        line = line.strip()
        if not line.endswith("\\\\"):
            continue
        cells = [c.strip() for c in line[:-2].split("&")]
        mech = cells[0] or mech
        p = cells[1] or p
        rows[(mech, p, cells[2])] = cells[3:]
    return rows


def run_checks(tex, src):
    F = flat(tex)
    out = []

    def add(name, ok, printed=None, source=None):
        out.append({"check": name, "pass": bool(ok), "printed": printed, "source": source})

    def sentence(name, pattern, value, group=1, exponent=0):
        m = re.search(pattern, F)
        if not m:
            add(name, False, None, value)
            return
        printed, dec = num(m.group(group))
        add(name, close(printed, dec, value, exponent if "times" not in m.group(group) else 0), m.group(group), value)

    rc, pf, fm = src["recount"], src["prefix"], src["formal"]
    mm = fm["main_metric"]
    # --- main replay
    sentence("Table default: score 1", r"Score 1 & ([\d,]+) \\\\", rc["main"]["derived_classes"]["1 分"])
    sentence("Table default: normal 0", r"Score 0, no verifier event & ([\d,]+) \\\\", rc["main"]["derived_classes"]["正常 0"])
    sentence("Table default: comparison timed out", r"comparison timed out \(library\) & ([\d,]+)", rc["main"]["derived_classes"]["0 分：比较超时"])
    sentence("Table default: comparison raised", r"comparison raised \(library\) & ([\d,]+)", rc["main"]["derived_classes"]["0 分：比较出错"])
    sentence("abstract: library-event rows", r"records ([\d,]+) library-event rows", rc["main"]["event_rows"])
    sentence("abstract: responses", r"fixed-response replay of ([\d,]+) responses", mm["n"])
    sentence("formal u (abstract)", r"corrected report leaves (\d+) rows unresolved", mm["u"])
    sentence("uncorrected u (abstract)", r"uncorrected count of ([\d,{}]+)", pf["uncorrected_metric"]["u"])
    sentence("k (§5.2)", r"they give \$k=(\d+)\$", pf["uncorrected_metric"]["k"])
    sentence("uncorrected u (§5.2)", r"\$u=(9\{?,\}?573)\$", pf["uncorrected_metric"]["u"])
    sentence("guard-stopped share of uncorrected u", r"of which ([\d,]+) are guard-stopped rows", pf["uncorrected_metric"]["u_reasons"]["参照：本机预算终止（未裁定）"])
    rec = pf["reference_aggregate_reconciliation"]
    sentence("originally marked, all rows", r"contain ([\d,]+) guard-stopped reference rows", rec["pre_correction_all_row_classes"]["本机预算终止（未裁定）"])
    sentence("originally marked, non-warm-up", r"guard-stopped reference rows \(([\d,]+) excluding warm-ups\)", pf["uncorrected_budget_killed_reference_rows"])
    sentence("reclassified, all rows", r"the report records ([\d,]+) reclassifications", pf["reported_reference_rows_reclassified"]["all_rows"])
    sentence("reclassified, non-warm-up", r"reclassifications \(([\d,]+) excluding warm-ups\)", pf["reported_reference_rows_reclassified"]["nonwarm_rows"])
    add("reconciliation true and no rows reconstructed",
        rec["all_row_reconciliation_matches_diagnostic_report"] and not rec["corrected_nonwarm_classes_independently_reconstructed"]
        and "not reconstruction of the corrected" in F)
    sentence("reference rows", r"contain [\d,]+ default and ([\d,]+) reference rows", pf["counts"]["reference_rows"])
    sentence("193,767 answers", r"(\d{3},\d{3}) in total", rc["identity"]["n_answers"])
    sentence("92,287 eligible", r"Of the ([\d,]+) questions with at least two answers", rc["identity"]["eligible_multi_answer_questions"])
    sentence("directed pairs", r"There are (\d+) such pairs", rc["pairs"]["directed_pairs"])
    sentence("both-event pairs", r"such pairs, of which (\d+) have events", rc["pairs"]["both_event_pairs"])
    e2 = src["e2"]["all_answers"]
    add("pooled endpoints 2/n and 34/n", "$2/n$ and $34/n$" in F and e2["k"] == 2 and e2["k"] + e2["u"] == 34)
    # --- E3, fixtures, heavy
    e3 = src["e3"]
    trials = sum(v["raw_trials"] + v["boxed_trials"] for v in e3["passes"].values())
    sentence("E3 trials (abstract)", r"A ([\d,]+)-trial replay", trials)
    add("E3 every score equal historical", all(not v["score_differs"] for v in e3["historical_agreement"].values()))
    fx = src["fixtures"]
    add("fixtures: 21, 16 omitted, 3 raised", fx["n"] == 21 and fx["baseline_omitted_columns"] == 16 and fx["baseline_exceptions"] == 3
        and "omits columns in 16 fixtures and raises in three" in F)
    s5 = [h for h in src["heavy"] if h["scene"].startswith("S5")]
    add("heavy: diagnostic naive scenes, none aborted (4)", len(s5) == 4 and all(not any(b.get("exception") for b in h["batches"]) for h in s5)
        and "did \\emph{not} abort in any of four runs" in F)
    # --- offline policy analysis
    op, supp = src["op"], src["supp"]
    sentence("groups", r"we used the (\d+) groups of the labelled set", op["groups"])
    sentence("constant groups", r"(\d+) groups are constant", op["constant_groups"])
    sentence("verl cross-check", r"maximum difference \$([0-9.]+\\times10\^\{-?\d+\})\$", op["verl_crosscheck"]["max_abs_difference"])
    table = policy_table(tex)
    for (mech, p, pol), cells in sorted(table.items()):
        key = f"{MECH[mech]}|p={p}"
        for col, cell in zip(POLICY_COLUMNS, cells):
            source = (supp if POLICY_SOURCE.get(col) == "supp" else op)["results"]
            value = source[key][POL[pol]][col]["mean"]
            printed, dec = num(cell)
            add(f"Table policies {mech} p={p} {pol} {col}", close(printed, dec, value), cell, value)
    add("Table policies has 18 rows", len(table) == 18)
    keys = [f"{a}|p={p}" for a in MECH.values() for p in ("0.05", "0.25")]
    max_se = max(max(op["results"][k][pp][c]["mc_se"] for pp in POL.values() for c in POLICY_COLUMNS if c in op["results"][k][pp])
                 for k in keys)
    max_se = max(max_se, max(supp["results"][k][pp][c]["mc_se"] for k in keys for pp in POL.values()
                             for c in ("common_zero_to_nonzero", "common_nonzero_to_zero", "common_mean_abs_error")))
    m = re.search(r"standard errors at most ([0-9.]+)\)", F)
    add("caption: max Monte Carlo SE bound", bool(m) and max_se <= float(m.group(1)), m.group(1) if m else None, max_se)
    shares = [supp["results"][k]["P0_zero_fill"]["p0_failed_label1_negative"]["mean"] / supp["results"][k]["P0_zero_fill"]["p0_failed_label1"]["mean"]
              for k in keys if not k.startswith("M3")]
    m = re.search(r"it holds for (\d+)--(\d+)\\% of failed correct responses", F)
    add("98--99% failed correct negative (M1/M2)", bool(m) and int(m.group(1)) <= round(100 * min(shares)) and round(100 * max(shares)) <= int(m.group(2)),
        m.group(0) if m else None, [min(shares), max(shares)])
    m3 = [supp["results"][k]["P0_zero_fill"]["p0_failed_label1_negative"]["mean"] for k in keys if k.startswith("M3")]
    add("M3: no failed correct negative", all(v == 0 for v in m3) and "no correct response receives a negative advantage" in F)
    enum = supp["enumeration"]
    add("enumeration: condition holds", enum["violations"] == 0 and enum["failed_label1_cases"] > 0 and "exhaustive enumeration" in F)
    p1 = [supp["results"][k]["P1_loss_mask_only"]["own_zero_to_nonzero"]["mean"] / op["results"][k]["P1_loss_mask_only"]["sign_disagreements"]["mean"]
          for k in keys if not k.startswith("M3")]
    m = re.search(r"\((\d+)--(\d+)\\% of P1's disagreements on the same draws", F)
    add("P1 zero-to-nonzero share", bool(m) and int(m.group(1)) <= round(100 * min(p1)) and round(100 * max(p1)) <= int(m.group(2)),
        m.group(0) if m else None, [min(p1), max(p1)])
    flips = max(supp["results"][k][pp]["common_flip"]["mean"] for k in supp["results"] for pp in POL.values())
    add("no sign flip among surviving responses", flips == 0 and "No surviving response" in F, None, flips)
    z = max(v["P2_exclude"]["common_zero_to_nonzero"]["mean"] for v in supp["results"].values())
    m = re.search(r"at most ([0-9.]+) such\s+changes per draw", F)
    add("P2 new signal bound", bool(m) and z <= float(m.group(1)), m.group(1) if m else None, z)
    k05 = "M1_independent|p=0.05"
    m = re.search(r"\(([0-9.]+) versus ([0-9.]+) per draw at \$p=0.05\$\)", F)
    add("P2 vs P0/P1 zeroed survivors at p=0.05", bool(m) and close(float(m.group(1)), 1, supp["results"][k05]["P2_exclude"]["common_nonzero_to_zero"]["mean"])
        and close(float(m.group(2)), 1, supp["results"][k05]["P1_loss_mask_only"]["common_nonzero_to_zero"]["mean"]), m.group(0) if m else None)
    k25 = "M1_independent|p=0.25"
    m = re.search(r"\(([0-9.]+) versus ([0-9.]+) at \$p=0.25\$\)", F)
    add("groups without signal at p=0.25", bool(m) and close(float(m.group(1)), 2, op["results"][k25]["P2_exclude"]["nonconstant_groups_without_signal"]["mean"])
        and close(float(m.group(2)), 2, op["results"][k25]["P1_loss_mask_only"]["nonconstant_groups_without_signal"]["mean"]), m.group(0) if m else None)
    single = max(v["P2_exclude"]["single_survivor_groups"]["mean"] for v in op["results"].values())
    m = re.search(r"occurred in at most ([0-9.]+) groups per draw", F)
    add("single-survivor bound", bool(m) and single <= float(m.group(1)) + 0.005, m.group(1) if m else None, single)
    return out


def main():
    repo, comp, auth = sys.argv[1:4]
    tex = (Path(repo) / "paper/main.tex").read_text(encoding="utf-8")
    res = run_checks(tex, load_sources(repo, comp, auth))
    failed = [r for r in res if not r["pass"]]
    print(json.dumps({"checks": len(res), "failed": failed, "all": res}, ensure_ascii=False, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
