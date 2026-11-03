"""Share of P1 (loss-only mask) sign disagreements that fall in clean-constant groups (supplementary to OP).

Usage: python -B p1_breakdown.py <gold.csv>  (500 draws per setting, seed 1; fixed after the main run)
"""
import json
import sys
from pathlib import Path

import numpy as np

import run_offline_policy as op

groups = op.load_groups(Path(sys.argv[1]))
clean = [op.grpo(r) for r in groups]
out = {}
for mech, p in [("M1_independent", 0.05), ("M2_correct_only", 0.05), ("M1_independent", 0.25), ("M2_correct_only", 0.25)]:
    rng = np.random.default_rng(1)
    tot = const = 0
    for _ in range(500):
        for r, a0 in zip(groups, clean):
            f = op.draw_failures(rng, r, mech, p)
            adv, m = op.apply_policy(r, f, "P1_loss_mask_only")
            d = int((op.sign(adv[m]) != op.sign(a0[m])).sum())
            tot += d
            const += d if r.min() == r.max() else 0
    out[f"{mech}|p={p}"] = {"disagreements": tot, "in_clean_constant_groups": const, "share": const / tot}
print(json.dumps(out, indent=1))
