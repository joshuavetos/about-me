<img width="1024" height="572" alt="D40E277C-2D01-40BC-94FB-42EDA5E17A94" src="https://github.com/user-attachments/assets/2c6b3037-d771-40d7-8c1e-3eacd4a1725c" />

# Coverage Liveness Gate

## Purpose

This gate prevents **silent fail-open** behavior in production security and ML systems by enforcing a single invariant:

> A system is only healthy if it can make evidence-backed decisions.

Accuracy, latency, and availability metrics are meaningless if a system silently stops making decisions and defaults to “safe”.

---

## Core Invariant

**Decision Coverage is a liveness property.**

If events are ingested but not scored, the system is partially blind.  
Blindness is a failure state.

This gate treats coverage loss as a **security incident**, not a performance anomaly.

---

## States

| State       | Meaning |
|------------|--------|
| **ALIVE** | The system is actively making decisions on eligible traffic |
| **DEGRADED** | Decision coverage has fallen below enforceable thresholds |
| **QUARANTINED (segment)** | A segment is removed from active coverage due to persistent failure |
| **PROBATION (segment)** | A quarantined segment is being evaluated for re-entry |

---

## Enforcement Rules

- **Global READY coverage < 95% → DEGRADED**
- **Any READY segment < 90% (min sample size) → DEGRADED**
- DEGRADED state emits a **cryptographically signed receipt**
- Quarantined segments are excluded from READY coverage until they requalify

There is no smoothing, retry logic, or confidence adjustment.

---

## What This Is Not

- Not a model accuracy metric
- Not an AUC or precision proxy
- Not a monitoring dashboard
- Not advisory

This is an **enforceable gate**.

---

## Operational Rule

If this gate reports **DEGRADED**, the system must not claim to be safe.

Fail-closed behavior, escalation, or traffic restriction must occur upstream.

---

## Status

**FROZEN**

This artifact defines a security invariant.  
Any changes require a new file, new gate name, and explicit versioning.
