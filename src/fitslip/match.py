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

from enum import Enum

class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


def match(value: float | None, lo: float | None, hi: float | None) -> Verdict:
    if value is None or lo is None or hi is None:
        return Verdict.UNKNOWN
    if lo <= value <= hi:
        return Verdict.PASS
    return Verdict.FAIL


def bill(rows: list[tuple[float | None, float | None, float | None]]) -> Verdict:
    """Fold a parts bill. An empty bill fails. Fail outranks unknown."""
    if not rows:
        return Verdict.FAIL
    verdicts = [match(value, lo, hi) for value, lo, hi in rows]
    if any(item == Verdict.FAIL for item in verdicts):
        return Verdict.FAIL
    if any(item == Verdict.UNKNOWN for item in verdicts):
        return Verdict.UNKNOWN
    return Verdict.PASS
