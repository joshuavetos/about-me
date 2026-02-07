"""
Municipal Capital Improvement Budget Audit Engine v3.3.3
FAIL-CLOSED • CANONICAL-HASHED • DECIMAL-ISOLATED • DoS-HARDENED • DETERMINISTIC
"""

from typing import List, Dict, Any, TypedDict, Iterator, Union
from statistics import median
from pydantic import BaseModel, Field, ValidationError, model_validator
from decimal import Decimal, localcontext, ROUND_HALF_UP, InvalidOperation
from itertools import islice
import hashlib
import json
import unicodedata
import pydantic

# =========================
# VERSION / RUNTIME GUARDS
# =========================
ENGINE_VERSION = "3.3.3"
assert pydantic.VERSION.startswith("2."), "Unsupported Pydantic version"

# =========================
# HARD LIMITS
# =========================
MAX_RECORDS = 10_000
MAX_PROJECT_NAME_LEN = 500
MAX_BUDGET = Decimal("1e12")
MIN_BUDGET = Decimal("0.01")
FISCAL_MIN = 2020
FISCAL_MAX = 2045
Z_CONST = Decimal("0.6745")
Z_THRESHOLD = Decimal("3.5")
MAX_TOTAL_BUDGET = MAX_BUDGET * MAX_RECORDS

# =========================
# SCHEMA (STRICT)
# =========================
class BudgetItem(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=MAX_PROJECT_NAME_LEN)
    budget_allocation: Decimal = Field(..., gt=MIN_BUDGET, le=MAX_BUDGET)
    fiscal_start: int = Field(..., ge=FISCAL_MIN, le=FISCAL_MAX)
    fiscal_end: int = Field(..., ge=FISCAL_MIN, le=FISCAL_MAX)

    @model_validator(mode="after")
    def chronology(self):
        if self.fiscal_end < self.fiscal_start:
            raise ValueError("fiscal_end precedes fiscal_start")
        return self

    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
        "str_strip_whitespace": True
    }

# =========================
# TYPES
# =========================
class AuditRejection(TypedDict):
    index: int
    input: Dict[str, Any]
    errors: list

class AuditResult(TypedDict):
    status: str
    engine_version: str
    records_validated: int
    records_rejected: int
    total_budget: Decimal
    risk_exposure: Decimal
    outlier_count: int
    analysis_records: List[Dict[str, Any]]
    rejection_log: List[AuditRejection]
    audit_hash: str
    input_fingerprint: str

# =========================
# ENGINE
# =========================
def run_financial_audit_streamed(
    input_data: Union[List[Dict[str, Any]], Iterator[Dict[str, Any]]]
) -> AuditResult:

    # -------- INPUT NORMALIZATION --------
    if isinstance(input_data, Iterator):
        input_data = list(islice(input_data, MAX_RECORDS + 1))

    if not isinstance(input_data, list):
        raise TypeError("input_data must be list or iterator")

    if len(input_data) > MAX_RECORDS:
        raise ValueError(f"Record limit exceeded ({MAX_RECORDS})")

    validated: List[Dict[str, Any]] = []
    rejected: List[AuditRejection] = []

    input_hasher = hashlib.sha256()

    # -------- PHASE 1: VALIDATION --------
    for idx, record in enumerate(input_data):
        try:
            # Canonical hash (JSON-stable)
            input_hasher.update(
                json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
            )

            # Unicode normalization
            if "project_name" in record:
                record = dict(record)
                record["project_name"] = unicodedata.normalize("NFC", record["project_name"])

            item = BudgetItem.model_validate(record)
            validated.append(item.model_dump())

        except (ValidationError, InvalidOperation, ValueError) as e:
            rejected.append({
                "index": idx,
                "input": record,
                "errors": [{"loc": err["loc"], "msg": err["msg"]} for err in getattr(e, "errors", lambda: [])()]
            })

    fingerprint = input_hasher.hexdigest()

    if not validated:
        return _abstain(fingerprint, rejected)

    # -------- PHASE 2: PREP --------
    allocations: List[Decimal] = []
    analysis_records: List[Dict[str, Any]] = []

    for rec in validated:
        alloc = rec["budget_allocation"]
        if alloc.is_finite():
            allocations.append(alloc)
            analysis_records.append(dict(rec))
        else:
            analysis_records.append({**rec, "modified_z_score": 0.0, "is_outlier": False})

    if not allocations:
        return _abstain(fingerprint, rejected, len(analysis_records), analysis_records)

    # -------- PHASE 3: STATS (ISOLATED CONTEXT) --------
    with localcontext() as ctx:
        ctx.prec = 18
        ctx.rounding = ROUND_HALF_UP

        allocations.sort()
        med = allocations[len(allocations) // 2]
        deviations = [abs(x - med) for x in allocations]
        mad = deviations[len(deviations) // 2]

        risk_exposure = Decimal("0")
        outlier_count = 0
        alloc_idx = 0

        for rec in analysis_records:
            if "modified_z_score" in rec:
                continue

            alloc = allocations[alloc_idx]
            alloc_idx += 1

            if mad == 0:
                z = Decimal("0")
                is_outlier = False
            else:
                z = (Z_CONST * abs(alloc - med)) / mad
                is_outlier = z > Z_THRESHOLD

            rec["modified_z_score"] = float(z)
            rec["is_outlier"] = is_outlier

            if is_outlier:
                outlier_count += 1
                risk_exposure += alloc

            if risk_exposure > MAX_TOTAL_BUDGET:
                raise ValueError("Aggregate risk exposure overflow")

        total_budget = sum(allocations)
        if total_budget > MAX_TOTAL_BUDGET:
            raise ValueError("Aggregate budget overflow")

    # -------- HASH COMMITMENT --------
    audit_hash = hashlib.sha256(
        repr((
            ENGINE_VERSION,
            analysis_records,
            rejected,
            total_budget,
            risk_exposure,
            outlier_count
        )).encode("utf-8")
    ).hexdigest()

    return {
        "status": "COMPLETE",
        "engine_version": ENGINE_VERSION,
        "records_validated": len(allocations),
        "records_rejected": len(rejected),
        "total_budget": total_budget,
        "risk_exposure": risk_exposure,
        "outlier_count": outlier_count,
        "analysis_records": analysis_records,
        "rejection_log": rejected,
        "audit_hash": audit_hash,
        "input_fingerprint": fingerprint
    }

# =========================
# FAIL-CLOSED RESULT
# =========================
def _abstain(
    fingerprint: str,
    rejected: List[AuditRejection],
    validated_count: int = 0,
    analysis_records: List[Dict[str, Any]] = None
) -> AuditResult:
    return {
        "status": "ABSTAIN",
        "engine_version": ENGINE_VERSION,
        "records_validated": validated_count,
        "records_rejected": len(rejected),
        "total_budget": Decimal("0"),
        "risk_exposure": Decimal("0"),
        "outlier_count": 0,
        "analysis_records": analysis_records or [],
        "rejection_log": rejected,
        "audit_hash": hashlib.sha256(
            repr((ENGINE_VERSION, validated_count, rejected, fingerprint)).encode("utf-8")
        ).hexdigest(),
        "input_fingerprint": fingerprint
    }

# Legacy alias
run_financial_audit = run_financial_audit_streamed
