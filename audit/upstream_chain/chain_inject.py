"""Functions executed inside the wrapper's spawned pool workers (fault injection).

They replace ``verl.utils.reward_score.math_verify._verify_in_subprocess`` in the
parent; the pool pickles the function by reference, so the spawned child imports
this module from ``sys.path``. Each function takes the wrapper's two positional
arguments ``(ground_truth_boxed, model_output)``.
"""
import os
import time


def die(ground_truth_boxed, model_output):
    """Persistent worker death on every attempt (as in the paper's C1c injection)."""
    os._exit(17)


def die_once(ground_truth_boxed, model_output):
    """Worker dies on the first attempt only; later attempts run the real verifier."""
    marker = os.environ["RF_DIE_ONCE_MARKER"]
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        from verl.utils.reward_score.math_verify import _verify_in_subprocess as real

        return real(ground_truth_boxed, model_output)
    os.close(fd)
    os._exit(17)


def slow(ground_truth_boxed, model_output):
    """Never-returning (for the test's purposes) task: exercises the outer timeout."""
    time.sleep(float(os.environ.get("RF_SLOW_SECONDS", "20")))
    return 1.0


def raise_value_error(ground_truth_boxed, model_output):
    raise ValueError("injected ordinary exception")


def raise_library_timeout(ground_truth_boxed, model_output):
    from math_verify.errors import TimeoutException

    raise TimeoutException("injected library timeout")


def die_if_marked(ground_truth_boxed, model_output):
    """Die only for responses containing FAIL; otherwise run the real verifier."""
    if "FAIL" in model_output:
        os._exit(17)
    from verl.utils.reward_score.math_verify import _verify_in_subprocess as real

    return real(ground_truth_boxed, model_output)
