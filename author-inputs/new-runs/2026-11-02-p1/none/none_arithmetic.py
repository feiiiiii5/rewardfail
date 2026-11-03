"""Offline GRPO advantage arithmetic for three treatments of one failed sample.

This is not a training experiment. It fixes a group of eight rewards and shows
how the same failure, coerced to 0, excluded, or coerced to 1, changes the
group mean/std and the advantages of the remaining rows.
"""
import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent
EPS = 1e-8
base = np.array([1.0] * 8)
fail = 2

def grpo(rewards, mask=None):
    r = rewards.astype(float)
    if mask is None:
        mask = np.ones_like(r, dtype=bool)
    used = r[mask]
    mean = float(used.mean()) if used.size else 0.0
    std = float(used.std(ddof=0)) if used.size else 0.0
    adv = np.zeros_like(r)
    if std > EPS:
        adv[mask] = (r[mask] - mean) / std
    return {"rewards": r.tolist(), "mask": mask.tolist(), "n_used": int(mask.sum()),
            "mean": mean, "std": std, "advantages": [round(float(x), 6) for x in adv]}

policies = {}
# A: include the failed sample as 0 (the current default symptom)
r0 = base.copy(); r0[fail] = 0.0
policies["include_as_0"] = grpo(r0)
# B: exclude the failed sample and renormalise over the remaining seven
mask = np.ones(8, dtype=bool); mask[fail] = False
policies["exclude_failed_sample"] = grpo(r0, mask=mask)
# C: include the failed sample but coerce it to 1 (counterfactual)
r1 = base.copy(); r1[fail] = 1.0
policies["include_as_1"] = grpo(r1)
# D: keep the failed sample but mask its loss only; advantages still computed over 8 with 0
policies["keep_0_mask_loss"] = grpo(r0)
# E: exclude and compute the group only over the remaining correct rows -> zero std
policies["exclude_only_correct"] = grpo(base, mask=mask)

result = {
    "note": "offline fixed-reward arithmetic; not training, not model evidence; GRPO population std",
    "failure_index": fail,
    "policies": policies,
    "different_from_include_as_0": {
        k: {"mean_delta": round(v["mean"] - policies["include_as_0"]["mean"], 6),
            "std_delta": round(v["std"] - policies["include_as_0"]["std"], 6),
            "max_adv_delta_remaining": round(max(abs(a - b) for a, b in zip(
                v["advantages"][:fail] + v["advantages"][fail+1:],
                policies["include_as_0"]["advantages"][:fail] + policies["include_as_0"]["advantages"][fail+1:])), 6),
            "n_used": v["n_used"]}
        for k, v in policies.items() if k != "include_as_0"
    },
}
(OUT / "none_arithmetic.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
