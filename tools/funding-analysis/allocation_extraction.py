import hashlib
import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import date

# --------------------------------------------------
# 1. Global State Registries
# --------------------------------------------------

REJECTED_YEARS_LOG: List[Dict] = []
EXTRACTION_STATS: Dict[str, Dict] = {}
FILING_STATS: Dict[str, Dict] = {}
FILING_QUALITY_ALERTS: Dict[str, Dict] = {}

# --------------------------------------------------
# 2. System Constants
# --------------------------------------------------

MIN_VALID_YEAR = 1900
MAX_VALID_YEAR = 2100

CURRENCY_SANITY_BOUNDS = {
    "min": 0.0,
    "max": 10_000_000_000.0,  # 10B baseline
}

CONTEXT_SANITY_BOUNDS = {
    "ANNUAL_REPORT": {"min": 1800, "max": 2100},
    "PRESS_RELEASE": {"min": 1900, "max": 2100},
    "DEFAULT": {"min": 1900, "max": 2100},
}

REJECTION_THRESHOLDS = {
    "ANNUAL_REPORT": 0.3,
    "PRESS_RELEASE": 0.5,
    "DEFAULT": 0.3,
}

# --------------------------------------------------
# 3. Utility Functions
# --------------------------------------------------

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonicalize_text(text: str) -> str:
    return " ".join(text.split())

def hash_canonical_text(text: str) -> str:
    return sha256_bytes(canonicalize_text(text).encode("utf-8"))

def get_context_snippet(text: str, start: int, end: int, window: int = 25) -> str:
    s = max(0, start - window)
    e = min(len(text), end + window)
    return text[s:e]

def preprocess_temporal_metadata(text: str) -> str:
    if not text:
        return ""
    token_pattern = r"\b\d{4}(?:[-/]\d{2,4})?\b"

    def replacer(match):
        token = match.group(0)
        if "-" in token or "/" in token:
            return f"period {token}"
        return f"year {token}"

    return re.sub(token_pattern, replacer, text)

# --------------------------------------------------
# 4. Data Model
# --------------------------------------------------

@dataclass
class Filing:
    filing_type: str
    source_class: str
    identifier: str
    accepted_date: date
    raw_bytes: bytes
    text: Optional[str]

    raw_hash: str = field(init=False)
    canonical_hash: str = field(init=False)

    def __post_init__(self):
        if self.raw_bytes is None:
            raise ValueError("raw_bytes must not be None")

        self.raw_hash = sha256_bytes(self.raw_bytes)

        if self.text:
            self.text = preprocess_temporal_metadata(self.text)

        self.canonical_hash = hash_canonical_text(self.text or "")

# --------------------------------------------------
# 5. Extraction Logic
# --------------------------------------------------

def extract_currency_amounts(text: str) -> List[Dict]:
    pattern = (
        r"(?i)"
        r"(?<![\w.])"
        r"(?P<sign>-?)\$"
        r"(?P<value>\d{1,3}(?:,\d{3})*(?:\.\d+)?)"
        r"(?:\s*(?P<unit>million|billion|m|b))?"
    )

    multipliers = {
        "m": 1e6,
        "million": 1e6,
        "b": 1e9,
        "billion": 1e9,
    }

    results = []
    for m in re.finditer(pattern, text):
        try:
            amt = float(m.group("value").replace(",", ""))
            if m.group("sign") == "-":
                amt = -amt
            if m.group("unit"):
                amt *= multipliers[m.group("unit").lower()]
            results.append(
                {"amount": amt, "start": m.start(), "end": m.end()}
            )
        except ValueError:
            continue

    return results

def expand_year_range(range_str: str, min_year: int, max_year: int) -> List[int]:
    match = re.match(r"(\d{4})[-/](\d{2,4})", range_str)
    if not match:
        return []

    start_year = int(match.group(1))
    end_raw = match.group(2)

    if len(end_raw) == 2:
        end_year = (start_year // 100) * 100 + int(end_raw)
        if end_year < start_year:
            end_year += 100
    else:
        end_year = int(end_raw)

    return [y for y in range(start_year, end_year + 1)
            if min_year <= y <= max_year]

def r3_classify(
    filing: Filing,
    required_years: List[int],
) -> Tuple[str, Dict[int, bool]]:

    if not filing.text:
        return "R3_NON_PARSABLE", {y: False for y in required_years}

    f_id = filing.identifier
    f_type = filing.filing_type

    FILING_STATS.setdefault(f_id, {"total": 0})
    EXTRACTION_STATS.setdefault(f_type, {"total": 0})

    found_years = set()

    year_pattern = (
        r"\b"
        r"(?:year|period)\s+"
        r"(?P<yr>\d{4}|\d{4}[-/]\d{2,4})"
        r"\b"
    )

    bounds = CONTEXT_SANITY_BOUNDS.get(f_type, CONTEXT_SANITY_BOUNDS["DEFAULT"])
    min_y, max_y = bounds["min"], bounds["max"]

    for m in re.finditer(year_pattern, filing.text):
        token = m.group("yr")
        FILING_STATS[f_id]["total"] += 1
        EXTRACTION_STATS[f_type]["total"] += 1

        if "-" in token or "/" in token:
            years = expand_year_range(token, min_y, max_y)
            found_years.update(years)
        else:
            y = int(token)
            if min_y <= y <= max_y:
                found_years.add(y)
            else:
                REJECTED_YEARS_LOG.append(
                    {"value": y, "filing": f_id, "context": "year"}
                )

    for info in extract_currency_amounts(filing.text):
        FILING_STATS[f_id]["total"] += 1
        EXTRACTION_STATS[f_type]["total"] += 1
        amt = info["amount"]
        if not (CURRENCY_SANITY_BOUNDS["min"] <= amt <= CURRENCY_SANITY_BOUNDS["max"]):
            REJECTED_YEARS_LOG.append(
                {"value": amt, "filing": f_id, "context": "currency"}
            )

    year_map = {y: y in found_years for y in required_years}

    if all(year_map.values()):
        status = "R3_PARSABLE_COMPLETE"
    elif any(year_map.values()):
        status = "R3_PARSABLE_PARTIAL"
    else:
        status = "R3_NON_PARSABLE"

    return status, year_map

# --------------------------------------------------
# 6. Null Identifier Engine
# --------------------------------------------------

def null_identifier_engine(
    issuer_name: str,
    target_years: List[int],
    primary: Filing,
    supplements: List[Filing],
) -> Dict:

    coverage = {y: 0 for y in target_years}

    _, primary_map = r3_classify(primary, target_years)
    for y, ok in primary_map.items():
        if ok:
            coverage[y] = 1

    for f in supplements:
        _, year_map = r3_classify(f, target_years)
        for y, ok in year_map.items():
            if ok:
                coverage[y] = 1

    null_years = [y for y, v in coverage.items() if v == 0]

    return {
        "issuer": issuer_name,
        "coverage_vector": coverage,
        "null_years": null_years,
    }

# --------------------------------------------------
# Load Confirmation
# --------------------------------------------------

if __name__ == "__main__":
    print("Filing Analysis System (MVP v1.0) loaded successfully.")
