"""OP driver (see PROTOCOL.md): offline advantage-level consequences of failure-handling policies.

Usage: python -B run_offline_policy.py --csv gold.csv --out <new dir> [--verl <verl tree> to cross-check]
NumPy only for the analysis; the optional cross-check imports verl's real GRPO estimator (needs torch).
"""
import argparse
import csv
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

CSV_SHA = "90fca106cb07f031a7ac169e009e6ab9cc0839126912218d0763b0ab6e037005"
EPS = 1e-6
RATES = (0.01, 0.05, 0.10, 0.25)
MECHS = ("M1_independent", "M2_correct_only", "M3_whole_group")
POLICIES = ("P0_zero_fill", "P1_loss_mask_only", "P2_exclude")
DRAWS = 2000
SEED = 20261103


def load_groups(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CSV_SHA:
        raise SystemExit("CSV differs from the fixed source")
    g = defaultdict(dict)
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        g[r["group_id"]][int(r["cid"])] = int(r["human_label"])
    full = {k: np.array([v[i] for i in range(8)], float) for k, v in g.items() if sorted(v) == list(range(8))}
    return [full[k] for k in sorted(full)]


def grpo(scores):
    """verl 0c4c3d4 compute_grpo_outcome_advantage for one group (outcome reward, std-normalised)."""
    s = np.asarray(scores, float)
    if len(s) == 0:
        return s
    if len(s) == 1:
        mean, std = 0.0, 1.0
    else:
        mean, std = s.mean(), s.std(ddof=1)
    return (s - mean) / (std + EPS)


def apply_policy(r, failed, policy):
    """Return (advantage array over all 8, loss mask)."""
    obs = np.where(failed, 0.0, r)
    if policy == "P0_zero_fill":
        return grpo(obs), np.ones(8, bool)
    if policy == "P1_loss_mask_only":
        return grpo(obs), ~failed
    adv = np.zeros(8)
    keep = ~failed
    adv[keep] = grpo(obs[keep])
    return adv, keep


def draw_failures(rng, r, mech, p):
    if mech == "M1_independent":
        return rng.random(8) < p
    if mech == "M2_correct_only":
        return (rng.random(8) < p) & (r == 1)
    return np.full(8, rng.random() < p)


def sign(x):
    return np.where(np.abs(x) < 1e-9, 0, np.sign(x))


def run(groups):
    clean = [grpo(r) for r in groups]
    nonconst = [r.min() != r.max() for r in groups]
    out = {}
    for mi, mech in enumerate(MECHS):
        for pi, p in enumerate(RATES):
            rng = np.random.default_rng([SEED, mi, pi])
            acc = {pol: defaultdict(list) for pol in POLICIES}
            for _ in range(DRAWS):
                fails = [draw_failures(rng, r, mech, p) for r in groups]
                n_failed = sum(int(f.sum()) for f in fails)
                for pol in POLICIES:
                    flips = err = neg_correct = contrib = lost = single = 0
                    for r, f, a0, nc in zip(groups, fails, clean, nonconst):
                        adv, mask = apply_policy(r, f, pol)
                        m = mask
                        contrib += int(m.sum())
                        flips += int((sign(adv[m]) != sign(a0[m])).sum())
                        err += float(np.abs(adv[m] - a0[m]).sum())
                        neg_correct += int(((adv < -1e-9) & (r == 1) & m).sum())
                        if nc and m.any() and np.all(np.abs(adv[m]) < 1e-9):
                            lost += 1
                        if nc and not m.any():
                            lost += 1
                        if pol == "P2_exclude" and int(m.sum()) == 1:
                            single += 1
                    d = acc[pol]
                    d["failed_responses"].append(n_failed)
                    d["loss_contributing"].append(contrib)
                    d["sign_disagreements"].append(flips)
                    d["mean_abs_adv_error"].append(err / contrib if contrib else 0.0)
                    d["label1_negative_adv"].append(neg_correct)
                    d["nonconstant_groups_without_signal"].append(lost)
                    d["single_survivor_groups"].append(single)
            out[f"{mech}|p={p}"] = {pol: {k: {"mean": float(np.mean(v)), "mc_se": float(np.std(v, ddof=1) / np.sqrt(len(v)))}
                                          for k, v in acc[pol].items()} for pol in POLICIES}
    return out


def crosscheck(groups, verl_path):
    """Compare grpo() with the real verl estimator on the clean groups and on random sub-groups."""
    import sys
    import torch
    sys.path.insert(0, verl_path)
    from verl.trainer.ppo.core_algos import compute_grpo_outcome_advantage
    rng = np.random.default_rng(7)
    worst = 0.0
    cases = [r for r in groups] + [r[rng.random(8) < 0.6] for r in groups for _ in range(3)]
    cases = [c for c in cases if len(c)]
    for c in cases:
        n = len(c)
        rew = torch.zeros(n, 4)
        rew[:, -1] = torch.tensor(c, dtype=torch.float32)
        adv, _ = compute_grpo_outcome_advantage(rew, torch.ones(n, 4), np.array(["g"] * n, dtype=object))
        worst = max(worst, float(np.abs(adv[:, -1].numpy() - grpo(c)).max()))
    return {"cases": len(cases), "max_abs_difference": worst}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--verl")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    groups = load_groups(a.csv)
    pos = [int(r.sum()) for r in groups]
    summary = {"protocol": "PROTOCOL.md", "csv_sha256": CSV_SHA, "groups": len(groups),
               "positives_per_group": {str(k): pos.count(k) for k in range(9)},
               "constant_groups": int(sum(r.min() == r.max() for r in groups)), "draws": DRAWS, "seed": SEED}
    if a.verl:
        summary["verl_crosscheck"] = crosscheck(groups, a.verl)
    summary["results"] = run(groups)
    (a.out / "results.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=1))


if __name__ == "__main__":
    main()
