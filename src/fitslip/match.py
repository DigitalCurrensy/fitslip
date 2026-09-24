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

import math
from enum import Enum

class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


def match(value: float | None, lo: float | None, hi: float | None) -> Verdict:
    if value is None or lo is None or hi is None:
        return Verdict.UNKNOWN
    if not math.isfinite(value) or not math.isfinite(lo) or not math.isfinite(hi):
        return Verdict.UNKNOWN
    if lo > hi:
        return Verdict.UNKNOWN
    if lo <= value <= hi:
        return Verdict.PASS
    return Verdict.FAIL


def clearance(value: float | None, lo: float | None, hi: float | None) -> float | None:
    """Smaller distance to a limit. Negative means the value is outside.

    The part size is still the caller's. This only subtracts.
    """
    if match(value, lo, hi) == Verdict.UNKNOWN:
        return None
    assert value is not None and lo is not None and hi is not None
    return min(value - lo, hi - value)


def median(readings: list[float | None]) -> float | None:
    """Middle reading. An even count averages the two middle readings.

    A blank or a non-finite reading is not a number. This is not a caliper.
    """
    if not readings:
        return None
    clean: list[float] = []
    for value in readings:
        if value is None or not math.isfinite(value):
            return None
        clean.append(value)
    clean.sort()
    mid = len(clean) // 2
    if len(clean) % 2:
        return clean[mid]
    return (clean[mid - 1] + clean[mid]) / 2.0


def sample_sd(readings: list[float | None]) -> float | None:
    """Sample standard deviation. The divisor is n − 1. Under two readings is missing.

    This is the spread of the readings. It is not a caliper.
    """
    if median(readings) is None or len(readings) < 2:
        return None
    clean = [float(value) for value in readings if value is not None]
    mean = sum(clean) / len(clean)
    var = sum((value - mean) ** 2 for value in clean) / (len(clean) - 1)
    return var ** 0.5


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


def against(
    values: dict[str, float | None],
    limits: dict[str, tuple[float | None, float | None]],
) -> Verdict:
    """Score every name in either dict with the bill rank.

    A name with no value, or no limit, is unknown. A reversed limit stays
    unknown because match() sees it. An empty pair of dicts fails.
    """
    names: list[str] = []
    seen: set[str] = set()
    for name in values:
        if name not in seen:
            seen.add(name)
            names.append(name)
    for name in limits:
        if name not in seen:
            seen.add(name)
            names.append(name)
    rows: list[tuple[float | None, float | None, float | None]] = []
    for name in names:
        if name not in values or name not in limits:
            rows.append((None, None, None))
            continue
        lo, hi = limits[name]
        rows.append((values[name], lo, hi))
    return bill(rows)
