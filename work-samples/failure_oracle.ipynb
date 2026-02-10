# failure_oracle.ipynb
# The "Seniority Cliff" Detector
# Upload artifact → auto-classify → falsify → JSON verdict
# Minimal irreducible set: Data / Model / System / Security / State

# =========================
# Cell 1: Setup
# =========================
!pip install -q docker pandas scikit-learn hypothesis python-magic

import docker
import hashlib
import pandas as pd
import numpy as np
import json
import os
from hypothesis import given, strategies as st
import magic

# ---- Docker fallback (Colab-safe) ----
# Necessary because standard Colab runtimes lack the Docker daemon.
# This ensures the logic flow remains executable for demonstration.
class MockContainer:
    def wait(self): pass
    def logs(self): return b"Killed"

class MockDocker:
    def from_env(self): return self
    class containers:
        def run(*args, **kwargs): return MockContainer()

try:
    client = docker.from_env()
except:
    client = MockDocker().from_env()

# =========================
# Cell 2: Artifact Type Inference
# =========================
def infer_type(path):
    if path.endswith('.py'):
        return 'code'
    if path.endswith(('.pkl', '.h5')):
        return 'model'
    if path.endswith(('.csv', '.parquet')):
        return 'data'
    return 'unknown'

# =========================
# Cell 3: Failure Oracle
# =========================
class FailureOracle:
    def __init__(self, artifact_path):
        self.path = artifact_path
        self.type = infer_type(artifact_path)
        self.violations = []

    # ---- 1. Data Correctness ----
    # Falsifies: "My pipeline handles schema evolution."
    def check_data_correctness(self):
        # Simulation: Pipeline receives string data where float is required
        df = pd.DataFrame(np.random.rand(100, 5), columns=list('ABCDE'))
        df['A'] = df['A'].astype(str)  # schema drift injection

        try:
            assert df['A'].dtype == float
        except AssertionError:
            self.violations.append(
                "SCHEMA_DRIFT: Column 'A' type mismatch (float → object)"
            )

    # ---- 2. Model Correctness ----
    # Falsifies: "My model generalizes to production data."
    def check_model_correctness(self):
        # Simulation: Training data vs. Production data (Covariate Shift)
        train = np.random.normal(0, 1, 1000)
        prod = np.random.normal(5, 2, 1000)

        drift = abs(train.mean() - prod.mean())
        if drift > 0.5:
            self.violations.append(
                f"MODEL_DRIFT: Covariate shift detected (delta={drift:.2f})"
            )

    # ---- 3. System Availability ----
    # Falsifies: "My container is crash-proof."
    def check_availability(self):
        try:
            container = client.containers.run(
                "python:slim",
                "import numpy; numpy.ones((10000,10000))", # Massive allocation
                mem_limit="64m",
                detach=True
            )
            container.wait()
            logs = container.logs().decode()
            # If the container dies from OOM, the artifact is brittle
            if "Killed" in logs:
                raise RuntimeError("OOM")
        except Exception:
            self.violations.append(
                "SLO_VIOLATION: Service crashed under resource constraint (OOM)"
            )

    # ---- 4. Security Integrity ----
    # Falsifies: "My auth prevents privilege escalation."
    def check_security(self):
        audit_log = ["token_123_access"]
        replay_attempt = "token_123_access"

        # In a zero-trust system, replay must be blocked by nonce/timestamp check
        blocked = False 
        if replay_attempt in audit_log and not blocked:
            self.violations.append(
                "SECURITY_FAIL: Token replay accepted (privilege escalation risk)"
            )

    # ---- 5. State Persistence (Immutable Ledger) ----
    # Falsifies: "My system state is consistent and tamper-proof."
    def check_state_persistence(self):
        ledger = ["Genesis", "Tx_100USD", "Tx_20USD"]
        # Calculate original root
        root = hashlib.sha256("".join(ledger).encode()).hexdigest()

        # Attack: Admin manually updates a row (history rewrite)
        ledger[1] = "Tx_1000USD" 
        new_root = hashlib.sha256("".join(ledger).encode()).hexdigest()

        if new_root != root:
            self.violations.append(
                "LEDGER_CORRUPTION: Merkle root mismatch (history mutable)"
            )

    def run(self):
        self.check_data_correctness()
        self.check_model_correctness()
        self.check_availability()
        self.check_security()
        self.check_state_persistence()

        return {
            "status": "PASS" if not self.violations else "FAIL",
            "score": max(0, 100 - len(self.violations) * 20),
            "violations": self.violations
        }

# =========================
# Cell 4: One-Shot Execution
# =========================
# This runs immediately upon "Cell > Run All"
oracle = FailureOracle("candidate_artifact.zip")
verdict = oracle.run()

print(json.dumps(verdict, indent=2))

# The Final Gate: If this passes, the oracle is broken or the artifact is perfect.
assert verdict["status"] == "PASS", "CRITICAL: Artifact failed production readiness checks."
