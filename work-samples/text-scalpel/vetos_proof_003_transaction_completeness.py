#!/usr/bin/env python3
"""
VETOS-PROOF-003
Transaction Completeness + Conservation Violation

Demonstrates:
- Q2 Completeness: mandatory stage skipped
- Q1 Conservation: value mismatch
"""

import sys
import json
import hashlib
import time

RECEIPT = "receipt.qual.json"
SCHEMA = "exq://spec/v1"


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha(data):
    return hashlib.sha256(json.dumps(data).encode()).hexdigest()


def run_transaction():
    print("[TX] Transaction executed")
    print("[TX] Status: SUCCESS ✅")

    declared_stages = ["validate", "authorize", "settle", "record"]
    executed_stages = ["validate", "authorize", "settle"]  # record skipped

    incoming = 1000
    outgoing = 995  # leaked value

    return declared_stages, executed_stages, incoming, outgoing


def qualify():
    declared, executed, inc, out = run_transaction()
    violations = []

    if set(declared) != set(executed):
        violations.append({
            "id": "Q2_Completeness",
            "evidence": {
                "declared": declared,
                "executed": executed
            }
        })

    if inc != out:
        violations.append({
            "id": "Q1_Conservation",
            "evidence": {
                "expected": inc,
                "observed": out,
                "delta": out - inc
            }
        })

    if violations:
        receipt = {
            "schema": SCHEMA,
            "timestamp": now(),
            "status": "FAILED",
            "violations": [v["id"] for v in violations],
            "evidence": [{
                **v,
                "hash": sha(v)
            } for v in violations]
        }

        with open(RECEIPT, "w") as f:
            json.dump(receipt, f, indent=2)

        print("\n[VETOS] ❌ QUALIFICATION FAILED")
        for v in violations:
            print(f"  Violated Law: {v['id']}")
        print(f"  Receipt written → {RECEIPT}")
        sys.exit(1)

    print("[VETOS] ✅ QUALIFIED")
    sys.exit(0)


if __name__ == "__main__":
    qualify()
