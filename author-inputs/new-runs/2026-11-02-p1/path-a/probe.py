"""Path A fixed-output probe: AgentLoopWorker._postprocess and extract_reward.

No model, no Ray, no reward manager. The goal is to check whether path A's
agent-loop aggregation has the same first-row key behaviour as batch path B,
and whether a local union-and-fill prototype preserves the error column.

Writes only under this directory.
"""
import hashlib
import inspect
import json
import os
import platform
import sys
import textwrap
import traceback
import types
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
OUT = HERE
VERL_DIR = Path(os.environ["VERL_DIR"]).resolve()

import verl
import verl.experimental.agent_loop.agent_loop as al
from verl.experimental.agent_loop.agent_loop import (
    AgentLoopWorker,
    AgentLoopMetrics,
    _InternalAgentLoopOutput,
)
from verl.protocol import DataProto
from verl.trainer.ppo.reward import extract_reward


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_input(n, failing, mixed=False):
    inputs = []
    order = list(range(n))
    for i in order:
        score = 0.0 if i in failing else (1.0 if i % 2 == 0 else 0.0)
        extra = {"acc": score}
        if i in failing:
            extra["error"] = "injected-failure"
            if mixed and i % 2 == 0:
                extra["timeout"] = True
        prompt = torch.tensor([[1, 2]], dtype=torch.long)
        response = torch.tensor([[3, 4]], dtype=torch.long)
        inputs.append(
            _InternalAgentLoopOutput(
                prompt_ids=prompt,
                response_ids=response,
                input_ids=torch.tensor([[1, 2, 3, 4]], dtype=torch.long),
                position_ids=torch.arange(4, dtype=torch.long).unsqueeze(0),
                response_mask=torch.ones(1, 2, dtype=torch.long),
                attention_mask=torch.ones(1, 4, dtype=torch.long),
                reward_score=score,
                num_turns=1,
                metrics=AgentLoopMetrics(),
                extra_fields={"reward_extra_info": extra},
            )
        )
    return inputs


def fixed_postprocess():
    """Build a local union-and-fill copy of the exact _postprocess function."""
    src = textwrap.dedent(inspect.getsource(AgentLoopWorker._postprocess))
    src = src.replace(
        "reward_extra_keys = list(reward_extra_infos[0].keys())",
        "reward_extra_keys = sorted({k for info in reward_extra_infos for k in info})",
    )
    src = src.replace(
        "non_tensor_batch[key] = np.array([info[key] for info in reward_extra_infos])",
        "non_tensor_batch[key] = np.array([info.get(key, None) for info in reward_extra_infos], dtype=object)",
    )
    ns = dict(vars(al))
    ns.update({"np": np, "torch": torch, "DataProto": DataProto})
    exec(src, ns)
    fn = ns["_postprocess"]
    return fn, hashlib.sha256(src.encode()).hexdigest()


def summarize_result(out, exc):
    rec = {"exception": None, "exception_type": None, "non_tensor_keys": None,
           "meta_reward_extra_keys": None, "extract": None, "reward_sum": None}
    if exc is not None:
        rec["exception"] = repr(exc)
        rec["exception_type"] = type(exc).__name__
        return rec
    rec["non_tensor_keys"] = sorted(out.non_tensor_batch.keys())
    rec["meta_reward_extra_keys"] = list(out.meta_info.get("reward_extra_keys", []))
    rec["reward_sum"] = float(out.batch["rm_scores"].sum().item())
    try:
        rt, extra = extract_reward(out)
        rec["extract"] = {k: [x.item() if hasattr(x, "item") else x for x in np.asarray(v).tolist()]
                          if isinstance(v, np.ndarray) else v for k, v in extra.items()}
        rec["extract_keys"] = sorted(extra.keys())
        rec["extract_reward_shape"] = list(rt.shape)
    except Exception as e:
        rec["extract"] = {"exception": repr(e)}
    return rec


def main():
    dummy = types.SimpleNamespace(reward_loop_worker_handles=None)
    fixed_fn, fixed_src_sha = fixed_postprocess()
    cases = {
        "normal": (8, set(), False),
        "error_pos_2": (8, {2}, False),
        "error_pos_0": (8, {0}, False),
        "mixed_error_timeout": (8, {1, 4}, True),
        "all_error": (4, {0, 1, 2, 3}, False),
        "empty_extras": (4, set(), False),
    }
    results = {}
    for name, (n, failing, mixed) in cases.items():
        inputs = make_input(n, failing, mixed)
        rec = {"n": n, "failing": sorted(failing), "mixed": mixed}
        for label, fn in (("original", AgentLoopWorker._postprocess), ("union_fill", fixed_fn)):
            try:
                out = fn(dummy, inputs)
                rec[label] = summarize_result(out, None)
            except Exception as e:
                rec[label] = summarize_result(None, e)
                rec[label]["traceback_tail"] = traceback.format_exc().splitlines()[-3:]
        results[name] = rec

    env = {
        "time": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "verl_dir": str(VERL_DIR),
        "verl_file": getattr(verl, "__file__", None),
        "agent_loop_file": getattr(al, "__file__", None),
        "verl_head": os.popen(f"git -C {VERL_DIR} rev-parse HEAD").read().strip(),
        "verl_status": os.popen(f"git -C {VERL_DIR} status --porcelain").read().strip(),
        "agent_loop_sha256": sha(Path(al.__file__)),
        "fixed_source_sha256": fixed_src_sha,
    }
    json.dump({"env": env, "cases": results},
              open(OUT / "results.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps({"env": env, "summary": {
        k: {"original_exception": v["original"]["exception_type"],
            "original_extract_keys": v["original"].get("extract_keys"),
            "union_fill_exception": v["union_fill"]["exception_type"],
            "union_fill_extract_keys": v["union_fill"].get("extract_keys")}
        for k, v in results.items()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
