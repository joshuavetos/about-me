import re
import json
import logging
import hashlib
import time
from enum import Enum
from functools import wraps
from typing import List, Dict, Tuple, Optional, Any, Protocol, runtime_checkable, Set
from dataclasses import dataclass, field
from datetime import date
from pydantic import BaseModel, Field, field_validator

# --------------------------------------------------
# 1. LOGGING & METRICS
# --------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("FilingAuditor")

@dataclass
class AuditMetrics:
    total_requests: int = 0
    refusals: int = 0
    cache_hits: int = 0
    failures_by_type: Dict[str, int] = field(default_factory=dict)

# --------------------------------------------------
# 2. SCHEMAS & UTILITIES
# --------------------------------------------------

class InferenceFailure(Enum):
    INSUFFICIENT_GROUNDING = "insufficient_grounding"
    CONTRADICTORY_SOURCES = "contradictory_sources"
    AMBIGUOUS_SCOPE = "ambiguous_scope"
    OUT_OF_BOUNDS = "out_of_bounds"

@dataclass(frozen=True)
class AuditContract:
    min_confidence: float = 0.9
    required_citations: bool = True
    uncertainty_patterns: Tuple[str, ...] = (
        r"\bi think\b", r"\bprobably\b", r"\bperhaps\b",
        r"\bnot sure\b", r"\bmight be\b", r"\bmaybe\b"
    )

class LLMResponse(BaseModel):
    text: str
    confidence: float = Field(default=0.0)

    @field_validator('confidence')
    @classmethod
    def confidence_range(cls, v):
        if not (0.0 <= v <= 1.0): raise ValueError("Confidence 0.0-1.0")
        return v

class ErrorResponse(BaseModel):
    error_code: str
    point_of_failure: Optional[str] = None
    status: str = "REFUSED"

@runtime_checkable
class LLMClient(Protocol):
    def __call__(self, prompt: str) -> Dict[str, Any]: ...

class PreconditionError(Exception):
    pass

def retry_with_backoff(max_retries=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1: raise
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt+1}/{max_retries} in {delay}s: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

# --------------------------------------------------
# 3. CORE GATEKEEPER
# --------------------------------------------------

class UncertaintyGatekeeper:
    def __init__(self, llm_client: LLMClient, contract: AuditContract):
        self.llm_client = llm_client
        self.contract = contract
        self.metrics = AuditMetrics()
        self._cache: Dict[str, LLMResponse] = {}

    def _heuristic_check(self, prompt: str):
        tokens = prompt.strip().split()
        if len(tokens) < 10: raise PreconditionError("Density failure")
        if not re.search(r"\b\w+(?:ed|es|s|ing)?\s+\w+\b", prompt):
            raise PreconditionError("Semantic structure failure")

    def _validate(self, res: LLMResponse) -> Tuple[Optional[InferenceFailure], Optional[str]]:
        if res.confidence < self.contract.min_confidence:
            return InferenceFailure.INSUFFICIENT_GROUNDING, f"conf={res.confidence}"
        for pat in self.contract.uncertainty_patterns:
            match = re.search(pat, res.text, re.IGNORECASE)
            if match: return InferenceFailure.INSUFFICIENT_GROUNDING, match.group(0)
        if self.contract.required_citations and not re.search(r"\[\d+\]", res.text):
            return InferenceFailure.OUT_OF_BOUNDS, "missing_citation"
        return None, None

    @retry_with_backoff()
    def execute(self, prompt: str) -> str:
        self.metrics.total_requests += 1
        cache_key = hashlib.sha256(prompt.encode()).hexdigest()
        
        if cache_key in self._cache:
            self.metrics.cache_hits += 1
            res = self._cache[cache_key]
        else:
            self._heuristic_check(prompt)
            raw = self.llm_client(prompt)
            res = LLMResponse(**raw)
            self._cache[cache_key] = res

        failure, snippet = self._validate(res)
        if failure:
            self.metrics.refusals += 1
            self.metrics.failures_by_type[failure.value] = self.metrics.failures_by_type.get(failure.value, 0) + 1
            return ErrorResponse(error_code=failure.value, point_of_failure=snippet).model_dump_json()

        return res.text

# --------------------------------------------------
# 4. CLAIM AUDITOR
# --------------------------------------------------

class ClaimAuditor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def _normalize_numbers(self, text: str) -> Set[str]:
        return {n.replace(",", "") for n in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?%?", text)}

    @retry_with_backoff()
    def audit(self, claim: str, reference: str) -> str:
        prompt = f"REF:\n{reference}\n\nCLAIM:\n{claim}\n\nStrict semantic match only. Else NULL."
        raw = self.llm_client(prompt)
        output = raw.get("text", "").strip()
        if re.fullmatch(r"(?i)null", output): return "NULL"
        
        c_nums, r_nums = self._normalize_numbers(claim), self._normalize_numbers(reference)
        if c_nums and not (c_nums & r_nums): return "NULL"
        return output

# --------------------------------------------------
# 5. TEST RUN
# --------------------------------------------------
if __name__ == "__main__":
    mock_client = lambda p: {"text": "Revenue: 500M [1]", "confidence": 0.98}
    gate = UncertaintyGatekeeper(mock_client, AuditContract())
    print(f">> Result: {gate.execute('Identify the specific revenue for the current fiscal period.')}")
    print(f">> Metrics: {gate.metrics}")
