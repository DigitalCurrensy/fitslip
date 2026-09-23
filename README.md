# FITSLIP

FITSLIP matches a bill of materials to a published envelope. A blank cell is not a pass.

**Owner:** Digital Currensy Inc.
**License:** Apache-2.0. Our code only. Cited material data stay with their authors.

## What it decides

Pass, fail, or unknown. Fail outranks unknown. Unknown is not a pass.

## The rule

Every line needs a named material and a limit it can be checked against. A missing wattage, a missing lookup, an empty bill, or a line over the cap fails closed. A line that passes on its own does not save a bill that fails elsewhere.

## Worked cases

The cases in this repository include a silence pack, a synthetic university camera, a published window, a missed lookup, missing watts, a material on the wrong paper, a line that passes while the payload is over the cap, and an empty bill. They prove the rule. They are not a flight bill a customer sent.

## What it will not do

- Treat an unknown property as acceptable.
- Average a passing line with a failing line.
- Sign a materials waiver.

## Run

```
PYTHONPATH=src python -m unittest tests.test_kernel
```

Notes under `docs/` are the build record. This page is the description.
