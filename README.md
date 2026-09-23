# FITSLIP

For a payload engineer checking a parts list against a published size, mass, and power limit.

**Owner:** Digital Currensy Inc.
**License:** Apache-2.0. Our code only. Cited data and papers stay with their authors.
**Status:** Private until the owner publishes it.

## What it decides

Pass, fail, or unknown. Fail outranks unknown. Unknown is not a pass.

## The rule

Every line needs a named material and a limit it can be checked against. A missing wattage, a missed lookup, an empty bill, or a line over the cap fails closed. One passing line does not save a failing bill.

## Worked cases

The cases here include a silent pack, a synthetic camera, a published window, a missed lookup, missing watts, the wrong paper, a line that passes while the payload is over the cap, and an empty bill. They are not a flight bill.

## What it will not do

- Treat an unknown property as acceptable.
- Average a passing line with a failing line.
- Sign a materials waiver.

## Run

```
git clone <this repo>
cd fitslip
PYTHONPATH=src python -m unittest tests.test_kernel
```

Python 3.12. No third-party packages. The test is the demo.
