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

"""FIT SLIP. Paper on the part. Not a certificate. Counsel unsigned."""

from __future__ import annotations

from .match import Verdict, match

TITLE = "FIT SLIP"
AFT = (-20.0, 60.0)
OFFER = "Unsigned. Not a certificate."
PAYLOAD = "SYN-PAY-CAM-3U"


def compile_slip(kind: str, lo: float | None, hi: float | None) -> dict:
    fold = match(0.0, lo, hi) if kind != "undeclared" else Verdict.FAIL
    if kind == "undeclared":
        body = (
            f"No slip issued. {PAYLOAD} identity is off. Undeclared identity is not a payload example. "
            "Not a certificate."
        )
        stamp = "refused"
        issued = False
    elif kind == "passform":
        body = (
            "FIT SLIP. Published window + wrap vs University 3U class. PASS. "
            f"Not {PAYLOAD}. Different bill. Not a certificate. Counsel unsigned."
        )
        stamp = "pass"
        issued = True
        fold = Verdict.PASS
    elif kind == "clip":
        body = (
            f"FIT SLIP. {PAYLOAD} vs ENV-CUBESAT-01. UNKNOWN. Thermal clipped on this payload. "
            "Unknown is not a pass. Not a certificate. Counsel unsigned."
        )
        stamp = "unknown"
        issued = True
        fold = Verdict.UNKNOWN
    else:
        thermal = match(lo if lo is not None else -40.0, AFT[0], AFT[1])
        stamp = "fail" if thermal is Verdict.FAIL else thermal.value
        issued = True
        body = (
            f"FIT SLIP. {PAYLOAD} vs ENV-CUBESAT-01. FAIL. Kapton sits wider than minus 20 to 60 C. "
            "CDS Rev 14.1 is not an operating temperature. Not a certificate. Counsel unsigned."
        )
    return {
        "title": TITLE,
        "issued": issued,
        "stamp": stamp,
        "payload": None if kind == "passform" else PAYLOAD,
        "fold": fold.value if isinstance(fold, Verdict) else fold,
        "body": body,
        "words": len(body.split()),
        "counsel": "unsigned",
        "not_a_certificate": True,
        "cds_is_envelope": False,
        "gevs_is_envelope": False,
        "offer": OFFER,
        "maptis": False,
    }
