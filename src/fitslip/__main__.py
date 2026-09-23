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
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from fitslip.match import Verdict, bill, match


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


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python -m fitslip CSV", file=sys.stderr)
        return 2
    names, rows = load(Path(args[0]))
    overall = bill(rows)
    print(f"bill {overall.value}")
    for name, row in zip(names, rows):
        print(f"{name} {match(*row).value}")
    if overall == Verdict.PASS:
        return 0
    if overall == Verdict.FAIL:
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
