# HL: Linux heavy-input batch scenes (protocol fixed before running, 2026-11-03)

Input-location note (2026-11-06): the selected research rows are retained byte-for-byte at the location below; the original measurement protocol and results are unchanged.

New verification on a different platform (Linux x86-64 container, 4 vCPU, 15.7 GiB, no swap,
CPython 3.12.8). It is **not** a replay of the macOS E1 runs and **not** a frequency estimate.

| Item | Fixed value |
|---|---|
| Heavy inputs | `author-inputs/research-inputs/heavy_rows.json` (SHA-256 `297c3deb…`); rows `m-8364284f555502b7`, `m-ac45c2e3c4109182`, `m-2a2cbb703cd7d47a` ("three-IMO-first", positions 0–2) — the answer/response text pairs of the paper's D1 rows, each verified against its stored SHA-256 |
| Controls (**substitution**) | 8 synthetic score-one rows `\boxed{n}` vs `n` (n = 2…9) instead of the paper's 64 dataset rows (dataset unavailable here); 4 synthetic warm-up rows; a following batch of the same 8 controls |
| Code | companion `experiments/s2_e1.py::scene` unchanged (real wrapper, real pool constructor with the companion's limit-setting initializer, real `naive`/`rate_limited` managers, real `compute_rm_score`); companion `rewardfail/s2/mem.py`/`guard.py` with the Linux port (`audit/companion_fixes/`) |
| Wrappers | `pr` = verl PR #8015 `math_verify.py` @0c4c3d4 (SHA `f04f57d5…`); `main` = verl `acad987` copy (SHA `1242011c…`) |
| verl trees | `base` = 0c4c3d4; `fixed` = 0c4c3d4 + `audit/upstream_chain/patches/0001,0002` |
| Scenes | S1 pr/5 s/naive/normal; S2 pr/5 s/naive/three; S3 pr/5 s/limited/three; S4 main/5 s/naive/three; S5 pr/60 s/naive/three ×3; S6 pr/60 s/limited/three; S7 pr/60 s/naive/normal; S2f, S5f = S2, S5 on the `fixed` tree (×1 each). Outer wait 30 s everywhere. `main` is not run at 60 s (it never kills its children; three would exceed this host's memory) |
| Order | as listed; one scene at a time, each in a fresh subprocess and fresh scene directory |
| Repeats | S5 three times; all others once |
| Stop conditions | scene wall time > 600 s → kill process tree, record `timeout`; host MemAvailable < 2.0 GiB → kill the scene's descendants, record `memory intervention` (scene excluded from interpretation); two interventions → stop the campaign |
| Recorded | scene result.json (scores/extras or exception + traceback per batch), parent.jsonl events, watchdog samples (MemAvailable, scene RSS sum) every 0.5 s, wall time, exit code |
| Interpretation | compare with paper Table 4 qualitatively (abort vs completion, zeros/ones); memory numbers use the Linux metric and are not comparable to macOS footprint |
