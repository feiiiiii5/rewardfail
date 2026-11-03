# OP results (offline, CPU, 2026-11-03; protocol `audit/experiments/offline_policy/PROTOCOL.md`)

72 complete eight-response groups with human labels (26 constant: 9 all-wrong, 17 all-correct); 576 responses;
2,000 synthetic failure draws per (mechanism, rate). Means ± Monte Carlo standard error per draw.
The NumPy estimator matched verl 0c4c3d4 `compute_grpo_outcome_advantage` on 288 groups/sub-groups
(max |difference| 2.9e-7). 9/9 unit tests pass. A first attempt (`offline_policy/`, same code and seed) completed
its computation but failed to write JSON (NumPy integer in the summary); it produced no results and was re-run
unchanged except for that cast.

Columns: failed responses; loss-contributing responses; sign disagreements with the clean advantage among
loss-contributing responses; label-1 responses given a negative advantage; clean non-constant groups left with no
non-zero loss-contributing advantage; mean absolute advantage error over loss-contributing responses.

| Mechanism | p | Policy | Failed | Loss rows | Sign disagreements | Label-1 negative | Groups without signal | Mean abs error |
|---|---|---|---|---|---|---|---|---|
| M1_independent | 0.01 | P0_zero_fill | 5.72 ± 0.05 | 576.00 ± 0.00 | 12.97 ± 0.21 | 3.46 ± 0.04 | 0.04 ± 0.00 | 0.02 ± 0.00 |
| M1_independent | 0.01 | P1_loss_mask_only | 5.72 ± 0.05 | 570.28 ± 0.05 | 9.47 ± 0.18 | 0.00 ± 0.00 | 0.04 ± 0.00 | 0.01 ± 0.00 |
| M1_independent | 0.01 | P2_exclude | 5.72 ± 0.05 | 570.28 ± 0.05 | 0.94 ± 0.06 | 0.00 ± 0.00 | 0.14 ± 0.01 | 0.01 ± 0.00 |
| M1_independent | 0.05 | P0_zero_fill | 28.84 ± 0.11 | 576.00 ± 0.00 | 57.88 ± 0.36 | 17.24 ± 0.09 | 0.19 ± 0.01 | 0.12 ± 0.00 |
| M1_independent | 0.05 | P1_loss_mask_only | 28.84 ± 0.11 | 547.16 ± 0.11 | 40.38 ± 0.31 | 0.00 ± 0.00 | 0.19 ± 0.01 | 0.06 ± 0.00 |
| M1_independent | 0.05 | P2_exclude | 28.84 ± 0.11 | 547.16 ± 0.11 | 4.99 ± 0.13 | 0.00 ± 0.00 | 0.75 ± 0.02 | 0.02 ± 0.00 |
| M1_independent | 0.1 | P0_zero_fill | 57.73 ± 0.16 | 576.00 ± 0.00 | 102.23 ± 0.39 | 34.56 ± 0.12 | 0.43 ± 0.01 | 0.22 ± 0.00 |
| M1_independent | 0.1 | P1_loss_mask_only | 57.73 ± 0.16 | 518.27 ± 0.16 | 66.92 ± 0.31 | 0.00 ± 0.00 | 0.43 ± 0.01 | 0.12 ± 0.00 |
| M1_independent | 0.1 | P2_exclude | 57.73 ± 0.16 | 518.27 ± 0.16 | 9.87 ± 0.17 | 0.00 ± 0.00 | 1.58 ± 0.03 | 0.05 ± 0.00 |
| M1_independent | 0.25 | P0_zero_fill | 143.80 ± 0.23 | 576.00 ± 0.00 | 183.65 ± 0.31 | 85.54 ± 0.18 | 1.26 ± 0.02 | 0.45 ± 0.00 |
| M1_independent | 0.25 | P1_loss_mask_only | 143.80 ± 0.23 | 432.20 ± 0.23 | 94.29 ± 0.22 | 0.00 ± 0.00 | 1.26 ± 0.02 | 0.27 ± 0.00 |
| M1_independent | 0.25 | P2_exclude | 143.80 ± 0.23 | 432.20 ± 0.23 | 22.48 ± 0.21 | 0.00 ± 0.00 | 4.44 ± 0.04 | 0.10 ± 0.00 |
| M2_correct_only | 0.01 | P0_zero_fill | 3.51 ± 0.04 | 576.00 ± 0.00 | 12.91 ± 0.20 | 3.48 ± 0.04 | 0.03 ± 0.00 | 0.02 ± 0.00 |
| M2_correct_only | 0.01 | P1_loss_mask_only | 3.51 ± 0.04 | 572.49 ± 0.04 | 9.40 ± 0.17 | 0.00 ± 0.00 | 0.03 ± 0.00 | 0.01 ± 0.00 |
| M2_correct_only | 0.01 | P2_exclude | 3.51 ± 0.04 | 572.49 ± 0.04 | 0.23 ± 0.03 | 0.00 ± 0.00 | 0.03 ± 0.00 | 0.00 ± 0.00 |
| M2_correct_only | 0.05 | P0_zero_fill | 17.41 ± 0.09 | 576.00 ± 0.00 | 57.73 ± 0.36 | 17.19 ± 0.09 | 0.21 ± 0.01 | 0.12 ± 0.00 |
| M2_correct_only | 0.05 | P1_loss_mask_only | 17.41 ± 0.09 | 558.59 ± 0.09 | 40.32 ± 0.30 | 0.00 ± 0.00 | 0.21 ± 0.01 | 0.06 ± 0.00 |
| M2_correct_only | 0.05 | P2_exclude | 17.41 ± 0.09 | 558.59 ± 0.09 | 1.45 ± 0.07 | 0.00 ± 0.00 | 0.21 ± 0.01 | 0.01 ± 0.00 |
| M2_correct_only | 0.1 | P0_zero_fill | 34.76 ± 0.13 | 576.00 ± 0.00 | 100.88 ± 0.39 | 34.29 ± 0.12 | 0.43 ± 0.01 | 0.22 ± 0.00 |
| M2_correct_only | 0.1 | P1_loss_mask_only | 34.76 ± 0.13 | 541.24 ± 0.13 | 66.12 ± 0.31 | 0.00 ± 0.00 | 0.43 ± 0.01 | 0.11 ± 0.00 |
| M2_correct_only | 0.1 | P2_exclude | 34.76 ± 0.13 | 541.24 ± 0.13 | 3.00 ± 0.09 | 0.00 ± 0.00 | 0.43 ± 0.01 | 0.03 ± 0.00 |
| M2_correct_only | 0.25 | P0_zero_fill | 87.37 ± 0.18 | 576.00 ± 0.00 | 184.17 ± 0.32 | 85.62 ± 0.18 | 1.29 ± 0.02 | 0.45 ± 0.00 |
| M2_correct_only | 0.25 | P1_loss_mask_only | 87.37 ± 0.18 | 488.63 ± 0.18 | 96.80 ± 0.24 | 0.00 ± 0.00 | 1.29 ± 0.02 | 0.26 ± 0.00 |
| M2_correct_only | 0.25 | P2_exclude | 87.37 ± 0.18 | 488.63 ± 0.18 | 8.55 ± 0.14 | 0.00 ± 0.00 | 1.29 ± 0.02 | 0.08 ± 0.00 |
| M3_whole_group | 0.01 | P0_zero_fill | 5.68 ± 0.15 | 576.00 ± 0.00 | 3.66 ± 0.12 | 0.00 ± 0.00 | 0.46 ± 0.02 | 0.01 ± 0.00 |
| M3_whole_group | 0.01 | P1_loss_mask_only | 5.68 ± 0.15 | 570.32 ± 0.15 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.46 ± 0.02 | 0.00 ± 0.00 |
| M3_whole_group | 0.01 | P2_exclude | 5.68 ± 0.15 | 570.32 ± 0.15 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.46 ± 0.02 | 0.00 ± 0.00 |
| M3_whole_group | 0.05 | P0_zero_fill | 28.84 ± 0.33 | 576.00 ± 0.00 | 18.24 ± 0.26 | 0.00 ± 0.00 | 2.28 ± 0.03 | 0.03 ± 0.00 |
| M3_whole_group | 0.05 | P1_loss_mask_only | 28.84 ± 0.33 | 547.16 ± 0.33 | 0.00 ± 0.00 | 0.00 ± 0.00 | 2.28 ± 0.03 | 0.00 ± 0.00 |
| M3_whole_group | 0.05 | P2_exclude | 28.84 ± 0.33 | 547.16 ± 0.33 | 0.00 ± 0.00 | 0.00 ± 0.00 | 2.28 ± 0.03 | 0.00 ± 0.00 |
| M3_whole_group | 0.1 | P0_zero_fill | 57.41 ± 0.46 | 576.00 ± 0.00 | 36.68 ± 0.36 | 0.00 ± 0.00 | 4.58 ± 0.05 | 0.05 ± 0.00 |
| M3_whole_group | 0.1 | P1_loss_mask_only | 57.41 ± 0.46 | 518.59 ± 0.46 | 0.00 ± 0.00 | 0.00 ± 0.00 | 4.58 ± 0.05 | 0.00 ± 0.00 |
| M3_whole_group | 0.1 | P2_exclude | 57.41 ± 0.46 | 518.59 ± 0.46 | 0.00 ± 0.00 | 0.00 ± 0.00 | 4.58 ± 0.05 | 0.00 ± 0.00 |
| M3_whole_group | 0.25 | P0_zero_fill | 143.88 ± 0.67 | 576.00 ± 0.00 | 91.96 ± 0.54 | 0.00 ± 0.00 | 11.49 ± 0.07 | 0.13 ± 0.00 |
| M3_whole_group | 0.25 | P1_loss_mask_only | 143.88 ± 0.67 | 432.12 ± 0.67 | 0.00 ± 0.00 | 0.00 ± 0.00 | 11.49 ± 0.07 | 0.00 ± 0.00 |
| M3_whole_group | 0.25 | P2_exclude | 143.88 ± 0.67 | 432.12 ± 0.67 | 0.00 ± 0.00 | 0.00 ± 0.00 | 11.49 ± 0.07 | 0.00 ± 0.00 |

Reading: advantages are not gradients, the 72 groups are a stratified selection, failures are injected, and none
of these numbers is a training outcome or a natural failure rate.
