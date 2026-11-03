# Linux portability patch for the companion archive

`linux-portability.patch` applies with `git apply` to an extracted `rewardfail-companion.zip`
(checked 2026-11-03). The distributed archive itself is unchanged.

| File | Change | Effect on macOS | Effect on Linux |
|---|---|---|---|
| `rewardfail/s2/mem.py` | `usage()` per platform; new `METRIC` constant | unchanged (libproc `phys_footprint`) | reads `/proc/<pid>/status`: `VmRSS + VmSwap` (current), `VmHWM + VmSwap` (lifetime proxy), `VmRSS` |
| `rewardfail/s2/guard.py` | `sysctl_int` returns `None` without `sysctlbyname`; `PRESSURE_AVAILABLE`; guard start record uses `mem.METRIC` | unchanged | no pressure level exists, so its absence is not a monitoring failure and the red-pressure (4) intervention never fires |
| `tests/test_s2_stats.py` | closed form `-expm1(log(a)/n)`; tolerance 1e-9 relative for the zero-event check | test only | the old reference `1 - a**(1/n)` lost ~12 digits to cancellation; the frozen `report.upper` (accurate to ~5e-11 relative here) is unchanged |
| `tests/test_s2_budget.py` | `RF_OLD_ANALYZE=<path>` may supply the pre-correction `analyze.py` (must hash to the run lock `a8fa21e2…`) instead of `git show 9a88991` | test only | runs with the snapshot from `author-inputs/history/9a88991/code.tar.gz` |
| `tests/test_get_data.sh` | BSD `sed -i ''` replaced by a portable temp-file rewrite | test only | runs |

**Metrics are not equivalent.** macOS `phys_footprint` counts compressed and swapped pages; Linux
`VmRSS + VmSwap` does not count compressed memory and the lifetime value can under-read the true peak. Budgets,
the 1.5 GiB stack-capture endpoint and every frozen classification were calibrated on macOS and are not
re-calibrated. Records carry `metric` so the two are never pooled silently. No frozen rule, budget, denominator or
classification was changed.

## Companion tests on Linux after the patch (2026-11-03)

| Test | Result | Note |
|---|---|---|
| `test_atype.py` | 56/56 | |
| `test_preprint_extensions.py` | OK | previously failed on `libproc.dylib` |
| `test_public_evidence_audit.py` | 7/7 | |
| `test_s2_budget.py` | 18/18 | with `RF_OLD_ANALYZE` from the 9a88991 snapshot |
| `test_s2_report.py` | 27/27 | |
| `test_s2_resume.py` | 25/25 | previously failed on `libproc.dylib` |
| `test_s2_stats.py` | 9/9 | |
| `test_get_data.sh` | 17/17 (`C.UTF-8`, `zh_CN.UTF-8`) | the earlier failure was partly a wrong invocation on my side (the script needs `<locale> <script>` arguments) |
| `test_s2_stepguard.py` | 12 checks pass, then stops | needs `99b086d:rewardfail/s2/stepguard.py` (not supplied) for its old-version control |
| `test_s2_flow.py` | not run | needs `42e4d63:rewardfail/s2/report.py` and `99b086d:rewardfail/s2/stepguard.py` (not supplied) |
| `test_s2_main_e2e.py`, `test_s2_u18_diag.py` | not run | need `stage2/sample_map.tsv` and the OpenR1 shards |

Outputs: `audit/results/companion_tests_linux/`.
