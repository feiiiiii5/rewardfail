"""Failure-chain regression suite for the verl tree on ``PYTHONPATH``.

Math-Verify -> PR #8015 wrapper -> reward manager -> batch aggregation
(reward-loop batch path and agent-loop generation path) -> consumers
(``extract_reward``, ``RayPPOTrainer._validate``, ``process_validation_metrics``).

All verl functions under test are the real ones from the imported tree. The
substitutes are: fixed response texts and a text tokenizer instead of a model,
in-process stand-ins for Ray ``.remote``/``ray.get``, and stub trainer
attributes (dataloader, config) around the real ``_validate``. This is therefore
a minimal integration of real functions, NOT a full Ray trainer run.

Run (see ../REPRODUCE.md):
    PYTHONPATH=<verl tree>:<this dir> python -B -m pytest -q test_reward_chain.py
Each test is a *contract*: failures on the unpatched tree are the expected,
recorded evidence that the test distinguishes the old and the fixed behaviour.
"""
import asyncio
import ast
import inspect
import itertools
import os
import random
import tempfile
import textwrap
import unittest
from collections import Counter
from concurrent.futures.process import BrokenProcessPool
from types import SimpleNamespace

import numpy as np
import torch
from omegaconf import OmegaConf

import chain_inject
import verl.utils.reward_score.math_verify as MV
from verl.experimental.reward_loop import reward_loop as R
from verl.experimental.reward_loop.reward_manager.limited import RateLimitedRewardManager
from verl.experimental.reward_loop.reward_manager.naive import NaiveRewardManager
from verl.protocol import DataProto
from verl.trainer.ppo.metric_utils import process_validation_metrics
from verl.trainer.ppo.reward import extract_reward

OUTER = float(os.environ.get("RF_OUTER_TIMEOUT", "30"))


# ----------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------
def fresh_pool():
    """Drop the wrapper's module-level pool so each test starts from a clean state."""
    pool = MV._pool
    MV._pool = None
    if pool is not None:
        for proc in list((getattr(pool, "_processes", None) or {}).values()):
            proc.kill()
        pool.shutdown(wait=False, cancel_futures=True)


class Injected:
    def __init__(self, fn):
        self.fn = fn

    def __enter__(self):
        fresh_pool()
        self.saved = MV._verify_in_subprocess
        MV._verify_in_subprocess = self.fn

    def __exit__(self, *exc):
        MV._verify_in_subprocess = self.saved
        fresh_pool()


def make_batch(texts, gts):
    n = len(texts)
    return DataProto.from_dict(
        tensors={"responses": torch.arange(n).reshape(n, 1), "prompts": torch.zeros(n, 1, dtype=torch.long),
                 "attention_mask": torch.ones(n, 2, dtype=torch.long)},
        non_tensors={"data_source": np.array(["chain"] * n, dtype=object),
                     "reward_model": np.array([{"ground_truth": g} for g in gts], dtype=object),
                     "extra_info": np.array([{"rid": i} for i in range(n)], dtype=object)})


class TextTokenizer:
    def __init__(self, texts):
        self.texts = texts

    def decode(self, ids, **kw):
        return self.texts[int(ids[0])]


def wrapper_score(data_source, solution_str, ground_truth, extra_info, **kw):
    return MV.compute_score(solution_str, ground_truth, timeout=OUTER)


def run_manager(cls, texts, gts, score_fn=wrapper_score, timeout=300):
    config = OmegaConf.create({"reward": {"max_concurrent": 1, "timeout": timeout,
                                         "custom_reward_function": {"path": "local"}}})
    from verl.utils.ray_utils import get_event_loop

    loop = get_event_loop()  # the manager binds this loop at construction, as in a reward worker
    mgr = cls(config, TextTokenizer(texts), score_fn)
    worker = object.__new__(R.RewardLoopWorker)
    worker.config, worker.reward_manager = config, mgr
    return loop.run_until_complete(worker.compute_score_batch(make_batch(texts, gts)))


def assemble_batch_path(outputs, workers=1, method=None):
    """Run the real RewardLoopManager.compute_rm_score on fixed per-row outputs.

    Rows are split into ``workers`` contiguous padded chunks exactly as the real
    method pads/chunks; each stand-in worker returns the scorer outputs for its chunk.
    """
    method = method or R.RewardLoopManager.compute_rm_score
    n = len(outputs)
    control = object.__new__(R.RewardLoopManager)
    control.reward_model_manager, control.reward_manager_cls = None, NaiveRewardManager
    pad = (-n) % workers if n else 0
    padded = outputs + outputs[:pad]
    size = len(padded) // workers if workers else 0
    chunks = [padded[i * size:(i + 1) * size] for i in range(workers)]
    control.reward_loop_workers = [SimpleNamespace(compute_score_batch=SimpleNamespace(remote=lambda c, rows=rows: rows))
                                   for rows in chunks]
    saved = R.ray.get
    R.ray.get = lambda values: values
    try:
        batch = make_batch(["x"] * n, ["1"] * n) if n else DataProto.from_dict(
            tensors={"responses": torch.zeros(0, 1, dtype=torch.long), "prompts": torch.zeros(0, 1, dtype=torch.long),
                     "attention_mask": torch.ones(0, 2, dtype=torch.long)})
        result = method(control, batch)
    finally:
        R.ray.get = saved
    scores, extras = extract_reward(result)
    return scores.sum(dim=-1).tolist(), {k: v for k, v in extras.items()}


def expected(outputs):
    keys = []
    for o in outputs:
        for k in o.get("reward_extra_info", {}):
            if k not in keys:
                keys.append(k)
    cols = {k: [o.get("reward_extra_info", {}).get(k) for o in outputs] for k in keys}
    return [o["reward_score"] for o in outputs], cols


def normal(n=8):
    return [{"reward_score": 1.0, "reward_extra_info": {"acc": 1.0}} for _ in range(n)]


def flagged(kind):
    value = {"error": "A process in the process pool was terminated abruptly", "timeout": True}[kind]
    return {"reward_score": 0.0, "reward_extra_info": {kind: value, "acc": 0.0}}


class ContractMixin:
    def assertContract(self, outputs, got):
        scores, cols = got
        exp_scores, exp_cols = expected(outputs)
        self.assertEqual(scores, exp_scores, "reward vector changed")
        self.assertEqual(sorted(cols), sorted(exp_cols), "metadata keys lost or invented")
        for k, v in exp_cols.items():
            self.assertEqual(len(cols[k]), len(outputs), f"column {k} misaligned")
            self.assertEqual(list(cols[k].tolist()), v, f"column {k} values")


# ----------------------------------------------------------------------------------------------
# 1. wrapper (real Math-Verify in the wrapper's real spawned ProcessPoolExecutor)
# ----------------------------------------------------------------------------------------------
class WrapperTests(unittest.TestCase):
    def tearDown(self):
        fresh_pool()

    def test_w1_correct_and_wrong_answers(self):
        fresh_pool()
        self.assertEqual(MV.compute_score("The answer is \\boxed{42}", "42"), 1.0)
        self.assertEqual(MV.compute_score("The answer is \\boxed{41}", "42"), 0.0)

    def test_w2_transient_worker_death_is_retried(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ["RF_DIE_ONCE_MARKER"] = os.path.join(d, "died")
            with Injected(chain_inject.die_once):
                self.assertEqual(MV.compute_score("\\boxed{42}", "42"), 1.0)

    def test_w3_persistent_worker_death_propagates(self):
        with Injected(chain_inject.die):
            with self.assertRaises(BrokenProcessPool):
                MV.compute_score("\\boxed{42}", "42")

    def test_w4_outer_timeout_returns_timeout_score_and_replaces_pool(self):
        os.environ["RF_SLOW_SECONDS"] = "20"
        with Injected(chain_inject.slow):
            first = MV._get_pool()
            self.assertEqual(MV.compute_score("\\boxed{42}", "42", timeout_score=-7, timeout=2), -7)
            self.assertIsNot(MV._pool, first)

    def test_w5_ordinary_worker_exception_propagates_unchanged(self):
        with Injected(chain_inject.raise_value_error):
            with self.assertRaisesRegex(ValueError, "injected ordinary exception"):
                MV.compute_score("\\boxed{42}", "42")

    def test_w6_library_timeout_exception_maps_to_timeout_score(self):
        with Injected(chain_inject.raise_library_timeout):
            self.assertEqual(MV.compute_score("\\boxed{42}", "42", timeout_score=-7), -7)


# ----------------------------------------------------------------------------------------------
# 2. reward managers (real run_single through the real RewardLoopWorker.compute_score_batch)
# ----------------------------------------------------------------------------------------------
class ManagerTests(unittest.TestCase):
    def tearDown(self):
        fresh_pool()

    def test_m1_rate_limited_flags_persistent_worker_death(self):
        texts = ["\\boxed{1}", "FAIL \\boxed{2}", "\\boxed{3}"]
        with Injected(chain_inject.die_if_marked):
            outs = run_manager(RateLimitedRewardManager, texts, ["1", "2", "3"])
        self.assertEqual([o["reward_score"] for o in outs], [1.0, 0.0, 1.0])
        self.assertEqual([sorted(o["reward_extra_info"]) for o in outs], [["acc"], ["acc", "error"], ["acc"]])

    def test_m2_rate_limited_flags_manager_timeout(self):
        def slow_score(**kw):
            import time
            time.sleep(1.0)
            return 1.0
        outs = run_manager(RateLimitedRewardManager, ["a"], ["1"], score_fn=slow_score, timeout=0.2)
        self.assertEqual(outs[0]["reward_extra_info"], {"timeout": True, "acc": 0.0})

    def test_m3_naive_manager_aborts_batch_on_worker_death(self):
        with Injected(chain_inject.die_if_marked):
            with self.assertRaises(BrokenProcessPool):
                run_manager(NaiveRewardManager, ["\\boxed{1}", "FAIL"], ["1", "2"])


# ----------------------------------------------------------------------------------------------
# 3. reward-loop batch path aggregation (RewardLoopManager.compute_rm_score)
# ----------------------------------------------------------------------------------------------
class BatchPathTests(unittest.TestCase, ContractMixin):
    def test_a01_flag_at_every_position(self):
        for kind, pos in itertools.product(("error", "timeout"), range(8)):
            with self.subTest(kind=kind, pos=pos):
                rows = normal()
                rows[pos] = flagged(kind)
                self.assertContract(rows, assemble_batch_path(rows))

    def test_a02_several_sparse_keys_in_different_rows(self):
        rows = normal(6)
        rows[1] = flagged("error")
        rows[4] = flagged("timeout")
        rows[5] = {"reward_score": 1.0, "reward_extra_info": {"acc": 1.0, "pred": "42"}}
        self.assertContract(rows, assemble_batch_path(rows))

    def test_a03_all_rows_without_extra_info(self):
        rows = [{"reward_score": 1.0} for _ in range(4)]
        self.assertContract(rows, assemble_batch_path(rows))

    def test_a04_all_rows_flagged(self):
        rows = [flagged("error") for _ in range(4)]
        self.assertContract(rows, assemble_batch_path(rows))

    def test_a05_single_row(self):
        for row in (normal(1)[0], flagged("error")):
            with self.subTest(row=row):
                self.assertContract([row], assemble_batch_path([row]))

    def test_a06_empty_batch_rejected_before_scoring(self):
        """Observed on both trees: DataProto.chunk rejects a zero-length batch first."""
        with self.assertRaisesRegex(RuntimeError, "split_size"):
            assemble_batch_path([], workers=1)

    def test_a06b_empty_extra_info_list_assembles(self):
        """The assembly step itself must not index row 0 of an empty list."""
        src = inspect.getsource(R.RewardLoopManager.compute_rm_score)
        if "reward_extra_infos[0]" in src:
            self.fail("compute_rm_score indexes reward_extra_infos[0] (IndexError on an empty list)")
        from verl.utils.reward_score.reward_extra_info import assemble_reward_extra_info
        self.assertEqual(assemble_reward_extra_info([]), {})

    def test_a07_row_permutation_equivariance(self):
        base = normal(8)
        base[2], base[5] = flagged("error"), flagged("timeout")
        base[6] = {"reward_score": 1.0, "reward_extra_info": {"acc": 1.0, "pred": "7"}}
        rng = random.Random(20261103)
        for t in range(40):
            perm = list(range(8))
            rng.shuffle(perm)
            rows = [base[i] for i in perm]
            with self.subTest(trial=t, perm=perm):
                self.assertContract(rows, assemble_batch_path(rows))

    def test_a08_chunks_and_padding_across_workers(self):
        for n, workers, pos in [(7, 2, 6), (7, 3, 0), (5, 4, 4), (9, 2, 8)]:
            rows = normal(n)
            rows[pos] = flagged("error")
            with self.subTest(n=n, workers=workers, pos=pos):
                self.assertContract(rows, assemble_batch_path(rows, workers=workers))

    def test_a09_schema_split_between_workers(self):
        rows = normal(4) + [flagged("error") for _ in range(4)]
        self.assertContract(rows, assemble_batch_path(rows, workers=2))
        rows = [flagged("error") for _ in range(4)] + normal(4)
        self.assertContract(rows, assemble_batch_path(rows, workers=2))

    def test_a10_fully_populated_column_keeps_numeric_dtype(self):
        rows = normal(4)
        rows[3] = flagged("error")
        _, cols = assemble_batch_path(rows)
        self.assertEqual(cols["acc"].dtype, np.float64)

    def test_a11_missing_and_explicit_none_are_indistinguishable(self):
        """Documented limitation of None-fill (both #7151 and the paper's prototype)."""
        rows = normal(3)
        rows[0] = {"reward_score": 0.0, "reward_extra_info": {"acc": 0.0, "error": None}}
        rows[1] = flagged("error")
        _, cols = assemble_batch_path(rows)
        self.assertIsNone(cols["error"][0])
        self.assertIsNone(cols["error"][2])  # absent key: same representation as explicit None


# ----------------------------------------------------------------------------------------------
# 4. the paper's local prototype (AST replacement used by companion experiments/s2_contract.py)
# ----------------------------------------------------------------------------------------------
def paper_prototype():
    original = R.RewardLoopManager.compute_rm_score
    tree = ast.parse(textwrap.dedent(inspect.getsource(original)))
    hits = 0

    class Replace(ast.NodeTransformer):
        def visit_Assign(self, node):
            nonlocal hits
            src = ast.unparse(node.value)
            if src == "list(reward_extra_infos[0].keys())":
                hits += 1
                return ast.copy_location(ast.parse(
                    "reward_extra_keys = sorted({key for info in reward_extra_infos for key in info})").body[0], node)
            if src == "np.array([info[key] for info in reward_extra_infos])":
                hits += 1
                return ast.copy_location(ast.parse(
                    "non_tensor_batch[key] = np.array([info.get(key, None) for info in reward_extra_infos], dtype=object)"
                ).body[0], node)
            return node

    tree = ast.fix_missing_locations(Replace().visit(tree))
    if hits != 2:
        return None
    ns = dict(original.__globals__)
    exec(compile(tree, "<paper-prototype>", "exec"), ns)
    return ns[original.__name__]


class PaperPrototypeTests(unittest.TestCase, ContractMixin):
    """Only meaningful on the unpatched tree (the prototype rewrites its two lines)."""

    def setUp(self):
        self.method = paper_prototype()
        if self.method is None:
            self.skipTest("tree no longer contains the two first-row-key assignments")

    def test_p1_keys_and_rewards_preserved(self):
        rows = normal()
        rows[0] = flagged("error")
        scores, cols = assemble_batch_path(rows, method=self.method)
        exp_scores, exp_cols = expected(rows)
        self.assertEqual(scores, exp_scores)
        self.assertEqual(sorted(cols), sorted(exp_cols))

    def test_p2_full_column_dtype(self):
        rows = normal(4)
        rows[3] = flagged("error")
        _, cols = assemble_batch_path(rows, method=self.method)
        self.assertEqual(cols["acc"].dtype, np.float64, "prototype turns every column into dtype=object")

    def test_p3_empty_batch(self):
        try:
            assemble_batch_path([], method=self.method)
        except IndexError as exc:
            self.fail(f"IndexError: {exc}")


# ----------------------------------------------------------------------------------------------
# 5. agent-loop generation path (_postprocess per worker + AgentLoopManager.generate_sequences)
# ----------------------------------------------------------------------------------------------
from verl.experimental.agent_loop import agent_loop as AL  # noqa: E402


def internal(info, score):
    t = lambda x: torch.tensor([x], dtype=torch.long)  # noqa: E731
    return AL._InternalAgentLoopOutput(
        prompt_ids=t([101]), response_ids=t([11]), response_mask=t([1]), attention_mask=t([1, 1]),
        input_ids=t([101, 11]), position_ids=t([0, 1]), reward_score=score, num_turns=1,
        metrics=AL.AgentLoopMetrics(), extra_fields={"reward_extra_info": info} if info is not None else {})


def generation_path(outputs, workers):
    """Real _postprocess on each worker chunk, then the real manager concat/finalize."""
    dummy = type("_W", (), {"reward_loop_worker_handles": None, "distillation_enabled": False})()
    n = len(outputs)
    size = -(-n // workers)
    chunks = [outputs[i * size:(i + 1) * size] for i in range(workers)]

    class FakeWorker:
        def __init__(self, rows):
            async def remote(chunk, rows=rows):
                return AL.AgentLoopWorker._postprocess(
                    dummy, [internal(o.get("reward_extra_info"), o["reward_score"]) for o in rows])
            self.generate_sequences = SimpleNamespace(remote=remote)

    mgr = object.__new__(AL.AgentLoopManager)
    mgr.agent_loop_workers = [FakeWorker(c) for c in chunks]
    prompts = DataProto.from_dict(tensors={"dummy": torch.zeros(n, 1)},
                                  non_tensors={"uid": np.array([str(i) for i in range(n)], dtype=object)})
    out = AL.AgentLoopManager.generate_sequences(mgr, prompts)
    if inspect.iscoroutine(out):
        out = asyncio.run(out)
    scores, extras = extract_reward(out)
    return scores.sum(dim=-1).tolist(), extras


class GenerationPathTests(unittest.TestCase, ContractMixin):
    def test_g1_flag_at_every_position_single_worker(self):
        for pos in range(4):
            rows = normal(4)
            rows[pos] = flagged("error")
            with self.subTest(pos=pos):
                self.assertContract(rows, generation_path(rows, workers=1))

    def test_g2_flag_only_in_second_worker(self):
        rows = normal(4)
        rows[3] = flagged("timeout")
        self.assertContract(rows, generation_path(rows, workers=2))

    def test_g3_flag_only_in_first_worker(self):
        rows = normal(4)
        rows[0] = flagged("error")
        self.assertContract(rows, generation_path(rows, workers=2))


# ----------------------------------------------------------------------------------------------
# 6. consumers: real RayPPOTrainer._validate and process_validation_metrics
# ----------------------------------------------------------------------------------------------
from verl.trainer.ppo.ray_trainer import RayPPOTrainer  # noqa: E402


class FakeRollout:
    """Returns rewards already computed in the agent loop (the generation path)."""

    def __init__(self, per_batch):
        self.per_batch = list(per_batch)

    def generate_sequences(self, batch):
        rows = self.per_batch.pop(0)
        n = len(rows)
        out = DataProto.from_dict(tensors={"responses": torch.arange(n).reshape(n, 1),
                                           "prompts": torch.zeros(n, 1, dtype=torch.long),
                                           "rm_scores": torch.tensor([[r["reward_score"]] for r in rows])})
        keys = []
        for r in rows:
            keys += [k for k in r.get("reward_extra_info", {}) if k not in keys]
        for k in keys:
            values = [r.get("reward_extra_info", {}).get(k) for r in rows]
            out.non_tensor_batch[k] = np.array(values, dtype=object if None in values else None)
        out.meta_info["reward_extra_keys"] = keys
        return out


def run_validate(per_batch, merged=False):
    """Call the real RayPPOTrainer._validate with stubbed infrastructure attributes."""
    me = object.__new__(RayPPOTrainer)
    me.val_dataloader = [{"input_ids": torch.zeros(len(b), 1, dtype=torch.long),
                          "data_source": np.array(["chain"] * len(b), dtype=object),
                          "uid": np.array([f"b{i}u{j}" for j in range(len(b))], dtype=object),
                          "reward_model": np.array([{"ground_truth": "1"}] * len(b), dtype=object)}
                         for i, b in enumerate(per_batch)]
    me.config = OmegaConf.create({"actor_rollout_ref": {"rollout": {"val_kwargs": {"n": 1, "do_sample": False},
                                                                    "agent": {"num_workers": 1}}},
                                  "trainer": {"validation_data_dir": None, "log_val_generations": 0}})
    me.tokenizer = SimpleNamespace(eos_token_id=0, pad_token_id=0, decode=lambda ids, **k: "r")
    me.global_steps, me.use_rm = 1, False
    me.async_rollout_manager = FakeRollout(per_batch)
    me._maybe_log_val_generations = lambda **kw: None
    return RayPPOTrainer._validate(me, merged=merged)


class ConsumerTests(unittest.TestCase):
    def test_c1_validate_single_batch_with_sparse_flag(self):
        b = normal(4)
        b[0] = flagged("error")
        metrics = run_validate([b])
        self.assertIn("val-core/chain/acc/mean@1", metrics)

    def test_c2_validate_flag_appears_only_in_later_batch(self):
        b2 = normal(4)
        b2[1] = flagged("error")
        metrics = run_validate([normal(4), b2])
        self.assertAlmostEqual(metrics["val-core/chain/acc/mean@1"], 7 / 8)

    def test_c3_validate_flag_only_in_earlier_batch(self):
        b1 = normal(4)
        b1[1] = flagged("timeout")
        metrics = run_validate([b1, normal(4)])
        self.assertAlmostEqual(metrics["val-core/chain/acc/mean@1"], 7 / 8)

    def test_c4_merge_validation_results_keeps_alignment(self):
        b1 = normal(2)
        b2 = [flagged("error"), normal(1)[0]]
        ra = run_validate([b1], merged=True)
        rb = run_validate([b2], merged=True)
        me = object.__new__(RayPPOTrainer)
        merged = {}
        me._val_metrics_update = lambda ds, uids, infos, turns: merged.update(infos) or {}
        RayPPOTrainer._merge_validation_results(me, ra, rb)
        self.assertEqual(merged["error"], [None, None, flagged("error")["reward_extra_info"]["error"], None])

    def test_c5_process_validation_metrics_with_none_filled_flags(self):
        infos = {"reward": [1.0, 0.0, 1.0, 0.0], "acc": [1.0, 0.0, 1.0, 0.0],
                 "error": [None, "boom", None, None], "timeout": [None, None, None, True]}
        out = process_validation_metrics(["chain"] * 4, ["a", "a", "b", "b"], infos)
        self.assertAlmostEqual(out["chain"]["acc"]["mean@2"], 0.5)
        self.assertNotIn("error", out["chain"])  # string column is skipped, not averaged

    def test_c6_flag_does_not_change_reward_or_acc(self):
        """Observability only: an error flag is not an exclusion policy (zero still counted)."""
        b = normal(4)
        b[0] = flagged("error")
        metrics = run_validate([b])
        self.assertAlmostEqual(metrics["val-core/chain/reward/mean@1"] if "val-core/chain/reward/mean@1" in metrics
                               else metrics["val-aux/chain/reward/mean@1"], 3 / 4)


if __name__ == "__main__":
    unittest.main()
