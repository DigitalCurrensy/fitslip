# Copyright 2026 Digital Currensy Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fitslip.__main__ import main  # noqa: E402
from fitslip.match import Verdict, against, bill, match  # noqa: E402
from fitslip.slip import compile_slip  # noqa: E402


class MatchTests(unittest.TestCase):
    def test_pass_fail_unknown(self) -> None:
        self.assertEqual(match(0.0, -20.0, 60.0), Verdict.PASS)
        self.assertEqual(match(-40.0, -20.0, 60.0), Verdict.FAIL)
        self.assertEqual(match(None, -20.0, 60.0), Verdict.UNKNOWN)

    def test_none_bound_is_unknown_and_outside_is_fail(self) -> None:
        self.assertEqual(match(1.0, None, 10.0), Verdict.UNKNOWN)
        self.assertEqual(match(1.0, 0.0, None), Verdict.UNKNOWN)
        self.assertEqual(match(11.0, 0.0, 10.0), Verdict.FAIL)

    def test_reversed_limit_is_unknown(self) -> None:
        self.assertEqual(match(1, 5, 1), Verdict.UNKNOWN)
        self.assertEqual(bill([(1, 5, 1)]), Verdict.UNKNOWN)


class BillTests(unittest.TestCase):
    def test_empty_bill_fails(self) -> None:
        self.assertEqual(bill([]), Verdict.FAIL)

    def test_one_unknown_and_no_fail_is_unknown(self) -> None:
        self.assertEqual(bill([(0.5, 0.0, 1.0), (None, 0.0, 1.0)]), Verdict.UNKNOWN)

    def test_one_fail_plus_a_pass_is_fail(self) -> None:
        self.assertEqual(bill([(0.5, 0.0, 1.0), (5.0, 0.0, 1.0)]), Verdict.FAIL)

    def test_fail_outranks_unknown(self) -> None:
        self.assertEqual(bill([(None, 0.0, 1.0), (5.0, 0.0, 1.0)]), Verdict.FAIL)

    def test_all_inside_is_pass(self) -> None:
        self.assertEqual(bill([(0.5, 0.0, 1.0), (0.2, 0.0, 1.0)]), Verdict.PASS)


class AgainstTests(unittest.TestCase):
    def test_empty_is_fail(self) -> None:
        self.assertEqual(against({}, {}), Verdict.FAIL)

    def test_inside_is_pass(self) -> None:
        self.assertEqual(
            against({"washer": 5.0}, {"washer": (0.0, 10.0)}),
            Verdict.PASS,
        )

    def test_outside_is_fail_and_beats_unknown(self) -> None:
        self.assertEqual(
            against(
                {"washer": 5.0, "bolt": 15.0, "clip": 1.0},
                {"washer": (0.0, 10.0), "bolt": (0.0, 10.0)},
            ),
            Verdict.FAIL,
        )

    def test_missing_value_or_limit_is_unknown(self) -> None:
        self.assertEqual(against({"clip": 1.0}, {}), Verdict.UNKNOWN)
        self.assertEqual(against({}, {"clip": (0.0, 10.0)}), Verdict.UNKNOWN)
        self.assertEqual(against({"washer": None}, {"washer": (0.0, 10.0)}), Verdict.UNKNOWN)

    def test_reversed_limit_stays_unknown(self) -> None:
        self.assertEqual(against({"washer": 1.0}, {"washer": (5.0, 1.0)}), Verdict.UNKNOWN)

    def test_name_only_in_the_envelope_is_unknown(self) -> None:
        self.assertEqual(
            against({"washer": 5.0}, {"washer": (0.0, 10.0), "clip": (0.0, 1.0)}),
            Verdict.UNKNOWN,
        )


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


class CliTests(unittest.TestCase):
    def test_examples(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([str(repo / "examples" / "pass.csv")])
        self.assertEqual(code, 0)
        text = out.getvalue().splitlines()
        self.assertEqual(text[0], "bill pass")
        self.assertEqual(text[1:], [
            "washer pass value=5 low=0 high=10",
            "spacer pass value=1 low=0 high=2",
            "clip pass value=0 low=-20 high=60",
        ])

        out = io.StringIO()
        with redirect_stdout(out):
            code = main([str(repo / "examples" / "bill.csv")])
        self.assertEqual(code, 1)
        text = out.getvalue().splitlines()
        self.assertEqual(text, [
            "bill fail",
            "bracket unknown value=missing low=0 high=10",
            "washer pass value=5 low=0 high=10",
            "bolt fail value=15 low=0 high=10",
        ])

    def test_two_files_exit_1(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([str(repo / "examples" / "values.csv"), str(repo / "examples" / "envelope.csv")])
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue().splitlines(), [
            "bill fail",
            "washer pass value=5 low=0 high=10",
            "bolt fail value=15 low=0 high=10",
            "clip unknown value=1 low=missing high=missing",
        ])



class FiniteMatchTests(unittest.TestCase):
    def test_non_finite_is_unknown(self) -> None:
        self.assertEqual(match(float("nan"), 0.0, 1.0), Verdict.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
