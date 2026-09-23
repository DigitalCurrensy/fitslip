# FITSLIP

Match a parts list to numeric limits. Fail outranks unknown.

**Owner:** Digital Currensy Inc.
**Copyright:** 2026 Digital Currensy Inc.
**License:** Apache-2.0. The file named LICENSE is the standard license and is not edited. The copyright notice is in NOTICE and at the top of each source file.

## What it decides

Pass, fail, or unknown. A missing number is unknown. Fail beats unknown. Unknown is not a pass. An empty bill is a fail.

## The rule

This does not look up materials. The caller supplies the number and the limits. Each row is a value and a closed interval. A value inside the limits passes. A value outside fails. A missing number or a missing bound is unknown. If the low limit is above the high limit, the row is unknown.

A bill fails when it has no rows, or when any row fails. Otherwise a bill is unknown when any row is unknown. Otherwise the bill passes. One passing row does not save a failing row.

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
