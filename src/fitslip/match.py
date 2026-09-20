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
