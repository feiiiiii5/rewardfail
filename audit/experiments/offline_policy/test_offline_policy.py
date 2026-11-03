"""Unit tests for the OP policy arithmetic (NumPy only)."""
import unittest

import numpy as np

import run_offline_policy as op


class PolicyTests(unittest.TestCase):
    def test_grpo_matches_hand_value(self):
        a = op.grpo([1, 1, 0, 0, 0, 0, 0, 0])
        self.assertAlmostEqual(a[0], 1.620182, places=5)

    def test_constant_group_zero(self):
        self.assertTrue(np.allclose(op.grpo([1] * 8), 0))

    def test_single_score_uses_verl_convention(self):
        self.assertAlmostEqual(op.grpo([1.0])[0], 1.0 / (1 + op.EPS))

    def test_zero_fill_keeps_failed_in_loss(self):
        r = np.array([1, 1, 1, 1, 1, 1, 1, 1.0]); f = np.zeros(8, bool); f[0] = True
        adv, m = op.apply_policy(r, f, "P0_zero_fill")
        self.assertTrue(m.all()); self.assertLess(adv[0], -2.4)

    def test_loss_mask_keeps_baseline_shift(self):
        r = np.ones(8); f = np.zeros(8, bool); f[0] = True
        adv, m = op.apply_policy(r, f, "P1_loss_mask_only")
        self.assertFalse(m[0]); self.assertGreater(adv[1], 0.3)

    def test_exclude_restores_constant_group(self):
        r = np.ones(8); f = np.zeros(8, bool); f[0] = True
        adv, m = op.apply_policy(r, f, "P2_exclude")
        self.assertTrue(np.allclose(adv[m], 0))

    def test_exclude_all_failed(self):
        r = np.array([1, 0, 1, 0, 1, 0, 1, 0.0]); f = np.ones(8, bool)
        adv, m = op.apply_policy(r, f, "P2_exclude")
        self.assertFalse(m.any())

    def test_exclude_single_survivor(self):
        r = np.array([1, 0, 0, 0, 0, 0, 0, 0.0]); f = np.ones(8, bool); f[0] = False
        adv, m = op.apply_policy(r, f, "P2_exclude")
        self.assertEqual(int(m.sum()), 1); self.assertAlmostEqual(adv[0], 1.0, places=5)

    def test_correct_only_mechanism(self):
        rng = np.random.default_rng(0)
        r = np.array([0, 0, 0, 0, 1, 1, 1, 1.0])
        f = op.draw_failures(rng, r, "M2_correct_only", 1.0)
        self.assertTrue((f == (r == 1)).all())


if __name__ == "__main__":
    unittest.main()
