"""OP supplement (specified after the main run; same data, seed, streams and draws).

Adds metrics that the main run did not report, without new sampling:
  * common evaluation set: responses that did NOT fail, identical across policies, so policies are compared on
    the same rows (the main run's metrics use each policy's own loss-contributing rows);
  * decomposition of sign disagreements into true flips (+ <-> -), zero -> nonzero and nonzero -> zero;
  * failed label-1 responses with a negative advantage under P0, split by whether a non-failed label-1
    response remains in the group.
It first re-derives the main run's per-draw means and checks they equal the committed results.json exactly,
which shows the draws are identical. A separate exhaustive enumeration verifies the condition under which a
failed correct response receives a negative advantage under P0.

Usage: python -B supplement.py <gold.csv> <committed results.json> <out.json>
"""
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

import run_offline_policy as op


def enumerate_condition():
    """All 2^8 label vectors x 2^8 failure masks: under P0, a failed label-1 response has a negative advantage
    iff at least one non-failed label-1 response remains in the group; otherwise its advantage is 0."""
    checked = violations = 0
    for labels in itertools.product((0, 1), repeat=8):
        r = np.array(labels, float)
        for fails in itertools.product((False, True), repeat=8):
            f = np.array(fails)
            adv, _ = op.apply_policy(r, f, "P0_zero_fill")
            other_correct = bool(((r == 1) & ~f).any())
            for i in np.flatnonzero(f & (r == 1)):
                checked += 1
                neg = adv[i] < -1e-9
                zero = abs(adv[i]) < 1e-9
                if (other_correct and not neg) or (not other_correct and not zero):
                    violations += 1
    return {"failed_label1_cases": checked, "violations": violations}


def main():
    csv_path, committed, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    groups = op.load_groups(csv_path)
    clean = [op.grpo(r) for r in groups]
    ref = json.loads(committed.read_text())["results"]
    res, mismatches = {}, []
    for mi, mech in enumerate(op.MECHS):
        for pi, p in enumerate(op.RATES):
            rng = np.random.default_rng([op.SEED, mi, pi])
            acc = {pol: defaultdict(list) for pol in op.POLICIES}
            for _ in range(op.DRAWS):
                fails = [op.draw_failures(rng, r, mech, p) for r in groups]
                for pol in op.POLICIES:
                    c = defaultdict(float)
                    for r, f, a0 in zip(groups, fails, clean):
                        adv, m = op.apply_policy(r, f, pol)
                        # main-run metric (own loss rows) for the identity check
                        c["main_sign_disagreements"] += int((op.sign(adv[m]) != op.sign(a0[m])).sum())
                        # common evaluation set: non-failed responses
                        keep = ~f
                        s_new, s_old = op.sign(adv[keep]), op.sign(a0[keep])
                        c["common_rows"] += int(keep.sum())
                        c["common_flip"] += int(((s_new * s_old) < 0).sum())
                        c["common_zero_to_nonzero"] += int(((s_old == 0) & (s_new != 0)).sum())
                        c["common_nonzero_to_zero"] += int(((s_old != 0) & (s_new == 0)).sum())
                        c["common_abs_error_sum"] += float(np.abs(adv[keep] - a0[keep]).sum())
                        # decomposition on the policy's own loss rows
                        s_new, s_old = op.sign(adv[m]), op.sign(a0[m])
                        c["own_flip"] += int(((s_new * s_old) < 0).sum())
                        c["own_zero_to_nonzero"] += int(((s_old == 0) & (s_new != 0)).sum())
                        c["own_nonzero_to_zero"] += int(((s_old != 0) & (s_new == 0)).sum())
                        if pol == "P0_zero_fill":
                            fc = f & (r == 1)
                            other = bool(((r == 1) & ~f).any())
                            c["p0_failed_label1"] += int(fc.sum())
                            c["p0_failed_label1_negative"] += int((fc & (adv < -1e-9)).sum())
                            c["p0_failed_label1_with_surviving_correct"] += int(fc.sum()) if other else 0
                    c["common_mean_abs_error"] = c["common_abs_error_sum"] / c["common_rows"] if c["common_rows"] else 0.0
                    for k, v in c.items():
                        acc[pol][k].append(v)
            key = f"{mech}|p={p}"
            res[key] = {}
            for pol in op.POLICIES:
                got = float(np.mean(acc[pol]["main_sign_disagreements"]))
                want = ref[key][pol]["sign_disagreements"]["mean"]
                if got != want:
                    mismatches.append([key, pol, got, want])
                res[key][pol] = {k: {"mean": float(np.mean(v)), "mc_se": float(np.std(v, ddof=1) / np.sqrt(len(v)))}
                                 for k, v in acc[pol].items() if k != "common_abs_error_sum"}
    report = {"what": "OP supplement; same draws as results.json (identity checked)",
              "identity_check_mismatches": mismatches, "enumeration": enumerate_condition(), "results": res}
    out.write_text(json.dumps(report, indent=1))
    print(json.dumps({"identity_check_mismatches": len(mismatches), "enumeration": report["enumeration"]}, indent=1))
    return 1 if mismatches or report["enumeration"]["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
