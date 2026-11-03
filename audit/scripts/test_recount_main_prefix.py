"""Regression tests for population-scoped aggregate reconciliation (stdlib)."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('recount', Path(__file__).with_name('recount_main_prefix.py'))
recount = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(recount)

class ReconciliationTests(unittest.TestCase):
    def test_all_rows_not_nonwarm_transitions(self):
        before = {'guard': 4, 'one': 1}
        warm = [{'id': 'warm-a', 'class': 'guard'}, {'id': 'warm-b', 'class': 'one'}]
        changes = {'guard → one': 4}
        diag = {'reference_classes': {'official': {'guard': 5, 'one': 2}, 'diagnostic': {'guard': 1, 'one': 6}}, 'class_changes': changes}
        result = recount.reconcile_reference(before, warm, changes, diag, {'guard': 1, 'one': 4})
        self.assertTrue(result['all_row_reconciliation_matches_diagnostic_report'])
        self.assertEqual(result['reported_all_rows_minus_formal_nonwarm_classes'], {'one': 2})
        self.assertTrue(result['residual_is_nonnegative_and_has_warmup_count'])
        self.assertFalse(result['corrected_nonwarm_classes_independently_reconstructed'])
        self.assertNotEqual(recount.apply_changes(before, changes), {'guard': 1, 'one': 4})

    def test_negative_counts_not_silently_discarded(self):
        self.assertEqual(recount.apply_changes({'guard': 1}, {'guard → one': 2}), {'guard': -1, 'one': 2})

    def test_invalid_transition_counts_rejected(self):
        for value in [-1, 1.5, True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                recount.apply_changes({'a': 2}, {'a → b': value})

    def test_mismatch_is_detected(self):
        result = recount.reconcile_reference({'a': 1}, [], {}, {'reference_classes': {'official': {'a': 1}, 'diagnostic': {'a': 2}}, 'class_changes': {}}, {'a': 2})
        self.assertFalse(result['all_row_reconciliation_matches_diagnostic_report'])
        self.assertFalse(result['residual_is_nonnegative_and_has_warmup_count'])

    def test_duplicate_warm_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rows.jsonl'
            path.write_text('\n'.join(json.dumps(row) for row in [{'id': 'warm-a', 'class': 'one'}] * 2))
            with self.assertRaisesRegex(ValueError, 'duplicate id'):
                recount.rows(path)

    def test_warm_classes_retained_both_detection_forms(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rows.jsonl'
            source = [{'id': 'warm-a', 'class': 'one'}, {'id': 'b', 'warm': True, 'class': 'guard'}, {'id': 'c', 'class': 'zero'}]
            path.write_text('\n'.join(json.dumps(row) for row in source))
            rows, warm, order = recount.rows(path)
            self.assertEqual(warm, source[:2])
            self.assertEqual(order, ['c'])
            self.assertEqual(rows, {'c': source[2]})

    def test_committed_recount_population_regression(self):
        root = Path(__file__).resolve().parents[1] / 'results'
        historical = json.loads((root / 'superseded' / 'main_prefix_recount_9a2fdd5.json').read_text())
        revised = json.loads((root / 'main_prefix_recount.json').read_text())
        for key, value in historical.items():
            if key == 'aggregate_reconciliation_matches_formal':
                self.assertEqual(revised['legacy_mixed_scope_check']['matches'], value)
                self.assertFalse(revised['legacy_mixed_scope_check']['expected'])
            elif key != 'inputs_sha256':
                self.assertEqual(revised[key], value, key)
        self.assertNotIn('aggregate_reconciliation_matches_formal', revised)
        self.assertEqual(revised['uncorrected_budget_killed_reference_rows'], 9864)
        self.assertEqual(revised['reported_reference_rows_reclassified'], {'all_rows': 9866, 'nonwarm_rows': 9863, 'warm_rows': 3})
        result = revised['reference_aggregate_reconciliation']
        self.assertTrue(result['all_row_reconciliation_matches_diagnostic_report'])
        self.assertTrue(result['pre_correction_all_rows_match_diagnostic_report'])
        self.assertTrue(result['reported_changes_match_diagnostic_report'])
        self.assertEqual(result['reported_all_rows_minus_formal_nonwarm_classes'], {'1 分': 6, '本机预算终止（未裁定）': 1})
        self.assertFalse(result['corrected_warmup_classes_independently_reconstructed'])

if __name__ == '__main__':
    unittest.main()
