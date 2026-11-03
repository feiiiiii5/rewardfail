"""Instrumented child function for E3-L (runs inside the wrapper's spawned pool worker).

Same parse/verify calls and target configs as verl PR #8015 `_verify_in_subprocess`;
adds per-step wall time and Math-Verify log categories. Limits come from RF_LIB_LIMIT.
Returns (score, steps) through the unchanged wrapper `compute_score`.
"""
import logging
import os
import time

CATS = ("Timeout during parsing", "Error parsing", "Timeout during comparison", "Error during comparison")


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records = []

    def emit(self, record):
        msg = record.getMessage()
        for c in CATS:
            if msg.startswith(c):
                self.records.append(("Timeout" if c.startswith("Timeout") else "Error"))


def verify_instrumented(ground_truth_boxed, model_output):
    from math_verify.grader import verify
    from math_verify.parser import ExprExtractionConfig, LatexExtractionConfig, parse

    limit = int(os.environ.get("RF_LIB_LIMIT", "5"))
    cap = _Capture()
    lg = logging.getLogger("math_verify")
    lg.setLevel(logging.DEBUG)
    lg.addHandler(cap)
    steps = []

    def step(kind, fn):
        start, n0 = time.perf_counter(), len(cap.records)
        out = fn()
        steps.append([kind, round(time.perf_counter() - start, 6), sorted(set(cap.records[n0:]))])
        return out

    try:
        gold_targets = (LatexExtractionConfig(),)
        pred_targets = (ExprExtractionConfig(), LatexExtractionConfig())
        g = step("gold_parse", lambda: parse(ground_truth_boxed, gold_targets, parsing_timeout=limit))
        p = step("pred_parse", lambda: parse(model_output, pred_targets, parsing_timeout=limit))
        score = 0.0
        if g and p:
            best = 0.0
            for pp in p:
                hit = any(step("compare", lambda gg=gg: verify(gg, pp, timeout_seconds=limit)) for gg in g)
                best = max(best, 1.0 if hit else 0.0)
            score = best
        return score, steps
    finally:
        lg.removeHandler(cap)
