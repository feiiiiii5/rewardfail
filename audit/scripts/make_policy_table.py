"""Generate the body of the manuscript's handling-policy table from the OP result files.

Values come from audit/results/offline_policy/results.json (main run) and supplement.json (same draws).
Formatting rule: one decimal for counts, three for mean |delta A|, two for groups without signal; Python's
format() rounding of the stored float (no intermediate rounding).

Usage: python3 -I -B make_policy_table.py <repo root> [--write]   (--write replaces the block in paper/main.tex)
"""
import json
import sys
from pathlib import Path

BEGIN = "%% BEGIN GENERATED: policy table rows (audit/scripts/make_policy_table.py)"
END = "%% END GENERATED: policy table rows"
SETTINGS = [("M1_independent", "M1 independent"), ("M2_correct_only", "M2 correct only"), ("M3_whole_group", "M3 whole group")]
RATES = ("0.05", "0.25")
POLS = [("P0_zero_fill", "P0"), ("P1_loss_mask_only", "P1"), ("P2_exclude", "P2")]
COLUMNS = [  # (source, key, format)
    ("main", "loss_contributing", "{:.1f}"),
    ("main", "sign_disagreements", "{:.1f}"),
    ("supp", "common_zero_to_nonzero", "{:.1f}"),
    ("supp", "common_nonzero_to_zero", "{:.1f}"),
    ("supp", "common_mean_abs_error", "{:.3f}"),
    ("main", "label1_negative_adv", "{:.1f}"),
    ("main", "nonconstant_groups_without_signal", "{:.2f}"),
]


def load(repo):
    base = Path(repo) / "audit/results/offline_policy"
    return (json.loads((base / "results.json").read_text())["results"],
            json.loads((base / "supplement.json").read_text())["results"])


def cells(main, supp):
    """Yield (row label tuple, [formatted cells]) in table order."""
    for mkey, mlabel in SETTINGS:
        for p in RATES:
            key = f"{mkey}|p={p}"
            for pkey, plabel in POLS:
                vals = []
                for src, k, fmt in COLUMNS:
                    v = (main if src == "main" else supp)[key][pkey][k]["mean"]
                    s = fmt.format(v)
                    vals.append("0" if float(s) == 0 else s)
                yield (mlabel, p, plabel), vals


def render(main, supp):
    out, last = [], None
    for (mlabel, p, plabel), vals in cells(main, supp):
        m = mlabel if (mlabel, None) != last and (last is None or last[0] != mlabel) else ""
        pp = p if (last is None or last != (mlabel, p)) else ""
        if last is not None and last[0] != mlabel:
            out.append("\\addlinespace")
        out.append(" & ".join([m, pp, plabel] + vals) + " \\\\")
        last = (mlabel, p)
    return "\n".join(out)


def main():
    repo = Path(sys.argv[1])
    body = render(*load(repo))
    if "--write" in sys.argv:
        tex = (repo / "paper/main.tex").read_text(encoding="utf-8")
        a, b = tex.index(BEGIN) + len(BEGIN), tex.index(END)
        tex = tex[:a] + "\n" + body + "\n" + tex[b:]
        (repo / "paper/main.tex").write_text(tex, encoding="utf-8")
    print(body)


if __name__ == "__main__":
    main()
