# OP: offline consequence analysis of failure-handling policies (fixed before running, 2026-11-03)

**What this is:** an advantage-level calculation on real, complete response groups with human labels and
*synthetic* verification failures. **What it is not:** training, gradients, model quality, or a natural
failure rate.

| Item | Fixed value |
|---|---|
| Data | `gold_set_1p5b_manual_labeled.csv` (SHA-256 `90fca106…`, ethxin0011/rlvr_group_correlation @ccb3302, MIT) |
| Unit | the 72 groups that contain all eight responses `cid` 0–7 of one prompt (all 5,556 rows are qwen2.5-1.5b). The other 2,969 groups are partial and are **not** used: their missing members are unknown, so GRPO statistics cannot be formed |
| Clean reward | `human_label` (0/1); labels were not re-adjudicated; the 72 groups come from a stratified sampler, so results describe these groups only |
| Advantage | verl 0c4c3d4 `compute_grpo_outcome_advantage`: group mean, `torch.std` (sample, n−1), ε = 1e-6, `norm_adv_by_std_in_grpo=True`; a group with exactly one score uses mean 0 and std 1 (verl's convention). The NumPy implementation is checked against the real verl function |
| Failure mechanisms | M1 independent: each response fails with probability p. M2 correctness-correlated: only label-1 responses fail, with probability p. M3 group-level: a whole group fails with probability p (reference-side trigger) |
| Rates | p ∈ {0.01, 0.05, 0.10, 0.25} |
| Policies | P0 zero-fill: failed reward 0, failed row in statistics and loss (verl `rate_limited` behaviour). P1 loss-mask only: failed reward 0 in statistics, failed row excluded from loss (NeMo RL `include` with a masked row). P2 exclude: failed rows excluded from statistics and loss (NeMo RL `exclude`; iCoder-27B) |
| Metrics (per draw, over loss-contributing responses) | (a) sign disagreement with the clean advantage; (b) mean absolute advantage error; (c) label-1 responses given negative advantage; (d) clean non-constant groups whose loss-contributing advantages are all zero; (e) loss-contributing responses; (f) single-survivor groups under P2 (verl's std = 1 convention) |
| Replicates | 2,000 draws per (mechanism, p), NumPy `default_rng(20261103)`, one stream per (mechanism, p) in the order listed |
| Output | means and Monte Carlo standard errors; `audit/results/offline_policy/` |
| Interpretation limits | advantage changes are not gradients (PPO clipping, token weighting and optimiser state are absent); the 72 groups are selected and small; failure injection is synthetic |
