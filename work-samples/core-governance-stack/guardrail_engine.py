import hashlib
import json
import time
from typing import Dict, Any, Optional
import numpy as np
from pydantic import BaseModel, Field, validator
from scipy.special import softmax

# --- Configuration ---
CONFIDENCE_THRESHOLD = 0.92  # High bar for "Fail-Closed"
DOMAIN_WHITELIST = ["financial", "industrial", "audit"]

class InputSchema(BaseModel):
    query: str
    context: str
    domain: str
    timestamp: float = Field(default_factory=time.time)

    @validator("domain")
    def domain_must_be_whitelisted(cls, v):
        if v not in DOMAIN_WHITELIST:
            raise ValueError(f"Domain '{v}' not in whitelist: {DOMAIN_WHITELIST}")
        return v

class DecisionReceipt(BaseModel):
    receipt_id: str
    input_hash: str
    confidence_score: float
    decision: str  # "EXECUTE" or "HALT"
    timestamp: float

class GuardrailEngine:
    def __init__(self):
        self._last_hash = "0" * 64  # Genesis hash for lineage chaining

    def _compute_hash(self, data: Dict) -> str:
        """Structural hashing of dictionary content."""
        serialized = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()

    def _mock_inference_logits(self, text: str) -> np.ndarray:
        """
        In production, this comes from the LLM. 
        Here, we simulate logits based on input length/entropy to be deterministic.
        """
        seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        # Simulate 3 classes: [Safe, Ambiguous, Unsafe]
        return np.random.normal(0, 1.5, 3)

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution gate. 
        Returns valid output OR raises FailClosedError.
        """
        # 1. Validation Gate (Pydantic)
        try:
            clean_input = InputSchema(**payload)
        except Exception as e:
            return {"error": f"Schema Validation Failed: {str(e)}", "status": "HALT"}

        # 2. Epistemic Confidence Check (Softmax)
        logits = self._mock_inference_logits(clean_input.query)
        probs = softmax(logits)
        confidence = float(np.max(probs))

        # 3. Fail-Closed Logic
        decision = "HALT"
        if confidence >= CONFIDENCE_THRESHOLD:
            decision = "EXECUTE"

        # 4. Cryptographic Receipt Emission
        input_hash = self._compute_hash(payload)
        receipt = DecisionReceipt(
            receipt_id=hashlib.sha256(f"{input_hash}{time.time()}".encode()).hexdigest(),
            input_hash=input_hash,
            confidence_score=confidence,
            decision=decision,
            timestamp=time.time()
        )

        # 5. Output
        if decision == "HALT":
            return {
                "status": "HALT",
                "reason": f"Insufficient Confidence ({confidence:.4f} < {CONFIDENCE_THRESHOLD})",
                "receipt": receipt.dict()
            }
        
        return {
            "status": "EXECUTE",
            "payload": f"Processed: {clean_input.query}",
            "receipt": receipt.dict()
        }

# --- Quick Test ---
if __name__ == "__main__":
    engine = GuardrailEngine()
    
    # Test 1: Safe Query
    print(engine.process({
        "query": "Calculate net liquidity for Q3", 
        "context": "Banking audit", 
        "domain": "financial"
    }))

    # Test 2: Invalid Domain (Should Validation Fail)
    print(engine.process({
        "query": "Generate meme", 
        "context": "social", 
        "domain": "entertainment"
    }))
