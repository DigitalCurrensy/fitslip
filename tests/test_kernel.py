from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fitslip.match import Verdict, match  # noqa: E402
from fitslip.slip import compile_slip  # noqa: E402


class MatchTests(unittest.TestCase):
    def test_pass_fail_unknown(self) -> None:
        self.assertEqual(match(0.0, -20.0, 60.0), Verdict.PASS)
        self.assertEqual(match(-40.0, -20.0, 60.0), Verdict.FAIL)
        self.assertEqual(match(None, -20.0, 60.0), Verdict.UNKNOWN)


class SlipTests(unittest.TestCase):
    def test_fail_issues_refused_does_not(self) -> None:
        fail = compile_slip("declared", -40.0, 80.0)
        self.assertTrue(fail["issued"])
        self.assertEqual(fail["stamp"], "fail")
        self.assertTrue(fail["not_a_certificate"])
        self.assertFalse(fail["cds_is_envelope"])
        self.assertLessEqual(fail["words"], 80)
        off = compile_slip("undeclared", -20.0, 60.0)
        self.assertFalse(off["issued"])
        self.assertEqual(off["stamp"], "refused")
        other = compile_slip("passform", -20.0, 60.0)
        self.assertTrue(other["issued"])
        self.assertIsNone(other["payload"])


if __name__ == "__main__":
    unittest.main()
