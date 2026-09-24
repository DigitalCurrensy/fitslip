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

"""Print a bill verdict and each line verdict.

An empty field is unknown. A bill that also contains a fail is fail.
Exit 0 for pass, exit 1 for fail, exit 2 for unknown.
Two filenames score a name,value file against a name,lo,hi envelope and print the bill verdict.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

from fitslip.match import Verdict, against, bill, clearance, match, median, sample_sd


def cell(text: str | None) -> float | None:
    """An empty field is unknown. Unreadable text is unknown, not a traceback."""
    if text is None:
        return None
    stripped = text.strip()
    if stripped == "":
        return None
    try:
        return float(stripped)
    except ValueError:
        return None


def load(path: Path) -> tuple[list[str], list[tuple[float | None, float | None, float | None]]]:
    names: list[str] = []
    rows: list[tuple[float | None, float | None, float | None]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for record in reader:
            names.append((record.get("name") or "").strip())
            rows.append((cell(record.get("value")), cell(record.get("lo")), cell(record.get("hi"))))
    return names, rows


def load_readings(path: Path) -> list[tuple[str, float | None, float | None, float | None, list[float | None]]]:
    """Group rows of name,reading,lo,hi. The value is the median of the readings."""
    grouped: dict[str, tuple[list[float | None], list[tuple[float | None, float | None]]]] = {}
    order: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for record in reader:
            name = (record.get("name") or "").strip()
            if name not in grouped:
                grouped[name] = ([], [])
                order.append(name)
            grouped[name][0].append(cell(record.get("reading")))
            grouped[name][1].append((cell(record.get("lo")), cell(record.get("hi"))))
    rows: list[tuple[str, float | None, float | None, float | None, list[float | None]]] = []
    for name in order:
        readings, limits = grouped[name]
        value = median(readings)
        low, high = limits[0]
        if any(item != (low, high) for item in limits):
            low, high = None, None
        rows.append((name, value, low, high, readings))
    return rows


def load_values(path: Path) -> dict[str, float | None]:
    """name,value. Limits are not in this file."""
    values: dict[str, float | None] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for record in reader:
            name = (record.get("name") or "").strip()
            values[name] = cell(record.get("value"))
    return values


def load_limits(path: Path) -> dict[str, tuple[float | None, float | None]]:
    """name,lo,hi. An envelope the caller wrote. Not a parts catalog."""
    limits: dict[str, tuple[float | None, float | None]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
        for record in reader:
            name = (record.get("name") or "").strip()
            limits[name] = (cell(record.get("lo")), cell(record.get("hi")))
    return limits



def _show(value: float | None) -> str:
    if value is None:
        return "missing"
    if not math.isfinite(value):
        return "bad"
    return f"{value:.10g}"


def _row_line(
    name: str,
    row: tuple[float | None, float | None, float | None],
    n: int | None = None,
    readings: list[float | None] | None = None,
) -> str:
    word = match(*row).value
    line = (
        f"{name} {word} value={_show(row[0])} low={_show(row[1])} high={_show(row[2])} "
        f"clearance={_show(clearance(*row))}"
    )
    if n is None:
        return line
    return f"{line} n={n} median={_show(row[0])} sd={_show(sample_sd(readings or []))}"


def _exit_for(overall: Verdict) -> int:
    if overall == Verdict.PASS:
        return 0
    if overall == Verdict.FAIL:
        return 1
    return 2


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 1:
        path = Path(args[0])
        with path.open(newline="", encoding="utf-8") as handle:
            header = next(csv.reader(handle), [])
        header = [name.strip() for name in header]
        if "reading" in header:
            packed = load_readings(path)
            overall = bill([(value, low, high) for _, value, low, high, _ in packed])
            print(f"bill {overall.value}")
            for name, value, low, high, readings in packed:
                print(_row_line(name, (value, low, high), len(readings), readings))
            return _exit_for(overall)
        names, rows = load(path)
        overall = bill(rows)
        print(f"bill {overall.value}")
        for name, row in zip(names, rows):
            print(_row_line(name, row))
    elif len(args) == 2:
        values = load_values(Path(args[0]))
        limits = load_limits(Path(args[1]))
        overall = against(values, limits)
        print(f"bill {overall.value}")
        names = list(dict.fromkeys([*values, *limits]))
        for name in names:
            value = values.get(name)
            low, high = limits.get(name, (None, None))
            print(_row_line(name, (value, low, high)))
    else:
        print("usage: python -m fitslip CSV [ENVELOPE]", file=sys.stderr)
        return 2
    return _exit_for(overall)


if __name__ == "__main__":
    raise SystemExit(main())
