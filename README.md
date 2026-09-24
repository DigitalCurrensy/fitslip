# FITSLIP

[![check](https://github.com/DigitalCurrensy/fitslip/actions/workflows/check.yml/badge.svg)](https://github.com/DigitalCurrensy/fitslip/actions/workflows/check.yml)

For someone checking a number against a limit, or the spread of several readings of one part.

One reading is compared with the low and the high. A reading file uses the median. Odd count takes the middle. Even count averages the two middle values. `sd` is the sample standard deviation, divisor n − 1. Clearance is the smaller slack. A blank is unknown, not a pass.

It does not touch the part. A pass is not a measurement.

## Install

```bash
pip install -e .
PYTHONPATH=src python -m unittest tests.test_kernel
```

## First command

```bash
PYTHONPATH=src python -m fitslip examples/readings.csv
```

The rest of this file is the rule that command prints.

## Record

`--json` prints one object. The process exit code is that object's `exit`. 0 is a pass word (`ok`, `pass`, `scored`, `path`). 1 is a refusal. 2 means the file could not be read. `keep` is false. `absent` is what this output does not contain: a stamp, measured basin months, and the points inside a `.laz` file.

This object is not WaterML and it is not a USGS response.

```json
{
  "absent": [
    "stamp",
    "measured_months",
    "laz_points"
  ],
  "desk": "fitslip",
  "exit": 0,
  "formula": "Clearance is the smaller slack. It does not touch the part.",
  "keep": false,
  "rows": [
    {
      "line": "bill pass",
      "word": "pass"
    },
    {
      "line": "washer pass value=5 low=0 high=10 clearance=5 n=3 median=5 sd=2.645751311",
      "word": "pass"
    },
    {
      "line": "spacer pass value=2 low=0 high=4 clearance=2 n=2 median=2 sd=1.414213562",
      "word": "pass"
    }
  ],
  "word": "pass"
}
```


Match a parts list to numeric limits. Fail outranks unknown. One `value` is a number you already have. A `reading` file is different: the value is the median of the readings for that name. An odd count takes the middle reading after sorting. An even count averages the two middle readings. A blank or a non-finite reading makes that part unknown. `clearance` is then the smaller of value minus low and high minus value. A negative clearance is outside the limits. `sd` is the sample standard deviation of those readings. The divisor is n − 1. Washer readings 4, 5, and 9 have `sd=2.645751311`. Two readings have a standard deviation. One does not. This sorts and subtracts. It does not touch the part. A pass is not a measurement.

**Owner:** Digital Currensy Inc.
**Copyright:** 2026 Digital Currensy Inc.
**License:** Apache-2.0. The file named LICENSE is the standard license and is not edited. The copyright notice is in NOTICE and at the top of each source file.

## What it decides

Pass, fail, or unknown. A missing number is unknown. Fail beats unknown. Unknown is not a pass. An empty bill is a fail.

## The rule

This does not look up materials. The caller supplies the number and the limits. Each row is a value and a closed interval. A value inside the limits passes. A value outside fails. A missing number, a non-finite number, or a missing bound is unknown. If the low limit is above the high limit, the row is unknown.

A bill fails when it has no rows, or when any row fails. Otherwise a bill is unknown when any row is unknown. Otherwise the bill passes. One passing row does not save a failing row. Each row line prints the value, the low limit, and the high limit next to pass, fail, or unknown.

Pass two filenames and the first CSV is name and value while the second is name, low, and high. The envelope is a second file the caller wrote. The library does not contain a parts catalog.

An empty field is unknown. A bill that also contains a fail is fail.

## Worked rows

`examples/pass.csv` is all inside the limits. `examples/bill.csv` has an empty value, a row inside the limits, and a row outside them. The empty field is unknown, and the bill is fail. Worked rows are not a flight bill.

## What it will not do

- Look up a material, a wattage, or a published envelope.
- Treat an unknown number as a pass.
- Average a passing row with a failing row.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
PYTHONPATH=src python -m fitslip examples/pass.csv
PYTHONPATH=src python -m fitslip examples/bill.csv
PYTHONPATH=src python -m fitslip examples/values.csv examples/envelope.csv
```

`examples/pass.csv` prints the bill verdict and each line verdict and exits 0. `examples/bill.csv` exits 1. `examples/values.csv` against `examples/envelope.csv` prints the bill verdict and exits 1. A bill that is unknown and has no fail exits 2. An empty cell does not traceback.

Python 3.11 or newer. No third-party packages.

Copyright 2026 Digital Currensy Inc. Apache-2.0.
