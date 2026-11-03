"""Counter-tests for check_paper_numbers.py: every corruption below must make the checker fail.

Usage: python3 -I -B test_check_paper_numbers.py <repo root> <companion root> <author-inputs root>
"""
import copy
import importlib.util
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cpn", HERE / "check_paper_numbers.py")
cpn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpn)
REPO, COMP, AUTH = (sys.argv.pop(1) for _ in range(3)) if len(sys.argv) >= 4 else (None, None, None)


def failed(tex, src):
    return [r["check"] for r in cpn.run_checks(tex, src) if not r["pass"]]


class CounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tex = (Path(REPO) / "paper/main.tex").read_text(encoding="utf-8")
        cls.src = cpn.load_sources(REPO, COMP, AUTH)

    def test_baseline_passes(self):
        self.assertEqual(failed(self.tex, self.src), [])

    def test_tampered_policy_source_value(self):
        src = copy.deepcopy(self.src)
        src["op"]["results"]["M1_independent|p=0.25"]["P0_zero_fill"]["sign_disagreements"]["mean"] += 0.2
        self.assertIn("Table policies M1 independent p=0.25 P0 sign_disagreements", failed(self.tex, src))

    def test_tampered_supplement_value(self):
        src = copy.deepcopy(self.src)
        src["supp"]["results"]["M2_correct_only|p=0.05"]["P2_exclude"]["common_mean_abs_error"]["mean"] += 0.01
        self.assertTrue(any("common_mean_abs_error" in f for f in failed(self.tex, src)))

    def test_tampered_main_metric_source(self):
        src = copy.deepcopy(self.src)
        src["prefix"]["uncorrected_metric"]["u"] = 9574
        self.assertTrue(any("uncorrected u" in f for f in failed(self.tex, src)))

    def test_old_rounding_errors_detected(self):
        tex = self.tex.replace("& 576.0 & 183.6 &", "& 576.0 & 183.7 &", 1)
        self.assertNotEqual(tex, self.tex)
        self.assertIn("Table policies M1 independent p=0.25 P0 sign_disagreements", failed(tex, self.src))
        line = next(l for l in self.tex.splitlines() if l.strip().startswith("&  & P2 & 558.6 &"))
        tex2 = self.tex.replace(line, line.replace("& 1.4 &", "& 1.5 &", 1), 1)
        self.assertNotEqual(tex2, self.tex)
        self.assertIn("Table policies M2 correct only p=0.05 P2 sign_disagreements", failed(tex2, self.src))

    def test_swapped_cells_detected(self):
        line = next(l for l in self.tex.splitlines() if l.startswith("M1 independent & 0.05 & P0"))
        cells = line[:-2].split("&")
        cells[4], cells[5] = cells[5], cells[4]  # swap two numeric columns
        self.assertNotEqual("&".join(cells) + "\\\\", line)
        tex = self.tex.replace(line, "&".join(cells) + "\\\\", 1)
        self.assertTrue(failed(tex, self.src))

    def test_swapped_policy_rows_detected(self):
        a = next(l for l in self.tex.splitlines() if l.strip().startswith("&  & P1 & 547.2 & 40.4"))
        b = next(l for l in self.tex.splitlines() if l.strip().startswith("&  & P2 & 547.2 & 5.0"))
        tex = self.tex.replace(a, "@@A@@").replace(b, a).replace("@@A@@", b)
        tex = tex.replace(b, b.replace("P2", "P1"), 1).replace(a, a.replace("P1", "P2"), 1)
        self.assertTrue(failed(tex, self.src))

    def test_edited_sentence_detected(self):
        tex = re.sub(r"of which 9,559 are guard-stopped", "of which 9,558 are guard-stopped", self.tex)
        self.assertNotEqual(tex, self.tex)
        self.assertIn("guard-stopped share of uncorrected u", failed(tex, self.src))
        tex = self.tex.replace("it holds for 98--99\\%", "it holds for 99--100\\%")
        self.assertNotEqual(tex, self.tex)
        self.assertIn("98--99% failed correct negative (M1/M2)", failed(tex, self.src))

    def test_overclaim_every_failed_correct_detected(self):
        # the removed abstract claim must not satisfy the condition checks if it returns in place of the qualified text
        tex = self.tex.replace("exhaustive enumeration", "full analysis")
        self.assertIn("enumeration: condition holds", failed(tex, self.src))

    def test_missing_table_row_detected(self):
        line = next(l for l in self.tex.splitlines() if l.strip().startswith("&  & P2 & 432.1"))
        tex = self.tex.replace(line + "\n", "", 1)
        self.assertIn("Table policies has 18 rows", failed(tex, self.src))


if __name__ == "__main__":
    unittest.main()
