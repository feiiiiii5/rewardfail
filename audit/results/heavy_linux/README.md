# HL results (Linux, 2026-11-03; protocol: `audit/experiments/heavy_linux/PROTOCOL.md`)

11 scenes, one at a time, total 7 min 18 s; no memory or time intervention (minimum host MemAvailable 9.3 GiB;
largest scene RSS sum 3.71 GiB, Linux metric). Test batch = 3 heavy rows at positions 0–2 + 5 synthetic controls
(except S1/S7: 8 controls); every scene ends with 8 following controls.

| Scene | Tree | Wrapper | Library / outer | Manager | Test batch scores | Pool resets | Following |
|---|---|---|---|---|---|---|---|
| S1 | base | #8015 | 5 s / 30 s | naive | 8 × 1 | 0 | 8 × 1 |
| S2 | base | #8015 | 5 s / 30 s | naive | 0 0 0 1 1 1 1 1 | 0 | 8 × 1 |
| S3 | base | #8015 | 5 s / 30 s | rate_limited | 0 0 0 1 1 1 1 1 | 0 | 8 × 1 |
| S4 | base | acad987 main | 5 s / 30 s | naive | 0 0 0 1 1 1 1 1 | – | 8 × 1 |
| S5a–c | base | #8015 | 60 s / 30 s | naive | 0 0 0 1 1 1 1 1 (×3) | 3 each | 8 × 1 |
| S6 | base | #8015 | 60 s / 30 s | rate_limited | 0 0 0 1 1 1 1 1 | 3 | 8 × 1 |
| S7 | base | #8015 | 60 s / 30 s | naive | 8 × 1 | 0 | 8 × 1 |
| S2f | fixed | #8015 | 5 s / 30 s | naive | 0 0 0 1 1 1 1 1 | 0 | 8 × 1 |
| S5f | fixed | #8015 | 60 s / 30 s | naive | 0 0 0 1 1 1 1 1 | 3 | 8 × 1 |

At 60 s / 30 s the heavy rows return the integer `timeout_score` 0 from the outer wait; at 5 s the library alarm
returns 0.0 first.

**Agreement with the paper (macOS, 64 dataset controls / 8 dataset controls):** default-limit, rate-limited and
pure-control outcomes agree. **Disagreement:** the paper's naive / #8015 / 60 s / 30 s three-heavy scene raised
`BrokenProcessPool` with no batch return in all traced runs; here 0 of 4 runs aborted. The event timeline
(`S5a/parent.jsonl.gz`) shows why this run could not abort: all five controls returned at ~15 s, and the three
heavy waits expired within 10 ms of each other at ~36 s, so each reset met only already-timed-out futures and no
pending future was broken. The paper's abort needs a reset to break a future that is still pending, which
depends on timing and on how long the controls take; the substituted controls are much shorter than the paper's
dataset responses. This run therefore neither reproduces nor refutes the macOS abort; it shows the abort is not
a property of the heavy inputs alone. The fixed tree (#7151 port + validation patch) does not change the wrapper or
manager and behaves identically, as expected.
