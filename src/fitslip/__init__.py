"""FITSLIP — the fit slip, the paper on the part. Unknown is not a pass."""

from .match import Verdict, match
from .slip import compile_slip

__all__ = ["Verdict", "compile_slip", "match"]
