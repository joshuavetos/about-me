![8E93F5C3-4637-4D27-AB77-6B92339CFF0F](https://github.com/user-attachments/assets/b0c3ba2b-4fc0-4f58-b57c-fbab8f50cdd7)

# Uncertainty Gatekeeper & Claim Auditor

This artifact is a deterministic boundary layer for interacting with LLMs under ambiguity.
It is designed to **refuse output by default** unless explicit confidence, structure, and grounding requirements are satisfied.

This is not a chatbot.
It is not a reasoning assistant.
It is a control surface that decides whether language is allowed to exit the system.

--------------------------------------------------

## What This Is

A fail-closed execution wrapper around an LLM client that:

- Treats refusal as a correct outcome
- Blocks low-confidence or weakly grounded responses
- Enforces an explicit audit contract before text is released
- Produces machine-readable refusal objects instead of explanations
- Records metrics about failure modes rather than hiding them

The system assumes the model will be confidently wrong unless proven otherwise.

--------------------------------------------------

## Core Components

### UncertaintyGatekeeper

The primary execution boundary.

Responsibilities:
- Pre-flight rejection of low-density or semantically weak prompts
- Confidence threshold enforcement
- Blocking probabilistic or hedging language
- Mandatory citation enforcement when required
- Idempotent execution via SHA-256 prompt caching
- Deterministic refusal with explicit failure codes

If any validation step fails, **no text is returned**.
A structured REFUSED response is emitted instead.

--------------------------------------------------

### AuditContract

An immutable rule set governing what constitutes an acceptable response.

Enforces:
- Minimum confidence threshold
- Disallowed uncertainty language patterns
- Citation requirements
- Non-negotiable validation rules

Contracts are configuration, not behavior.
Changing the contract changes what is allowed to exist.

--------------------------------------------------

### ClaimAuditor

A secondary verifier for comparing claims against reference text.

Responsibilities:
- Normalizes numeric expressions (e.g. 1,000 vs 1000)
- Rejects claims when numeric anchors do not match references
- Returns NULL rather than partial or speculative matches
- Performs strict semantic correspondence checks only

If correspondence is not exact, the claim is rejected.

--------------------------------------------------

## What This Does NOT Do

- It does not explain refusals conversationally
- It does not soften failure modes
- It does not guess, interpolate, or “help”
- It does not optimize for user satisfaction
- It does not recover from uncertainty

Uncertainty terminates execution.

--------------------------------------------------

## Design Principles

- Refusal is success
- Silence is containment
- Confidence must be explicit
- Verification beats completion
- The user is not the optimization target

This artifact exists to prevent bad language from escaping the system,
not to make interaction pleasant.

--------------------------------------------------

## Typical Use

- Wrap any LLM call that must not hallucinate
- Enforce contracts in legal, financial, or policy contexts
- Detect and block confident nonsense early
- Collect metrics on why language was refused
- Serve as a hard boundary between models and downstream systems

--------------------------------------------------

## MULTI-GATE ORCHESTRATION & ESCALATION SEMANTICS (AUTHORITATIVE)

This section defines how multiple failure gates interact.
No gate may redefine these rules locally.

---

## 1. GATE ORDERING (TOTAL, NOT PARTIAL)

Gates are executed in a fixed, total order:

G1 → G2 → G3 → … → Gn

Examples:
- G1: Structural / Schema
- G2: Budget / Quantitative
- G3: Legal / Compliance
- G4: Temporal / Feasibility

Order is immutable per artifact class.

---

## 2. REGENERATION ENTRY RULE (CRITICAL)

If an artifact fails **Gate k**:

- Regeneration re-enters at **Gate k**
- Gates **G1 … G(k−1)** are considered *conditionally passed*
- However: **they are revalidated after regeneration**

This prevents:
- Skipping earlier gates
- Assuming earlier correctness after mutation

---

## 3. PASS INVALIDATION RULE (ANTI-REGRESSION)

After regeneration for Gate k:

- Gates G1 … G(k−1) are automatically rechecked
- If any earlier gate now fails:
  - Control returns to the **earliest failed gate**
  - Retry budget is charged to that gate

This explicitly prevents:
“Fix Gate 2 → silently break Gate 1” loops

---

## 4. RETRY BUDGET SCOPE (LOCKED)

Retry budgets are:

- **Per-gate**
- **Non-transferable**
- **Non-resetting**

Rules:
- Each gate has its own retry counter (e.g. 3–5)
- Passing a gate does **not** reset its budget
- If Gate 2 exhausts retries → permanent ABSTAIN
- Passing Gate 2 does not refund Gate 1 retries

Rationale:
Retries measure instability, not effort.

---

## 5. DOWNSTREAM REFUSAL MODES

Every downstream system MUST declare one of:

### A. HARD REFUSAL
- Any `FORCE_PASS` artifact is rejected automatically
- Used for:
  - Financial execution
  - Legal submission
  - External publication

### B. SOFT REFUSAL
- Artifact is accepted
- Flag is visible and persistent
- Human must explicitly acknowledge flag

### C. CONTEXTUAL
- Policy map determines acceptance
- Example:
  - Allowed for internal review
  - Rejected for final filing

Default mode is **HARD REFUSAL** unless explicitly overridden.

---

## 6. OPERATOR OVERRIDE INTERVENTION LADDER

Override monitoring is not advisory.

Escalation ladder:

1. **Visibility**
   - Override rate
   - Time-to-override
   - ABSTAIN frequency

2. **Threshold Trigger**
   - Exceeds baseline → automatic flag

3. **Constraint**
   - Reduced override privileges
   - Mandatory second reviewer

4. **Suspension**
   - Override disabled pending review

No silent penalties.
All actions are logged.

---

## 7. COLD-START BASELINE PROTOCOL

During initial deployment:

- Overrides are **allowed but labeled**
- No penalties for first N artifacts (configurable)
- Metrics are collected but not enforced

After baseline window:
- Median ABSTAIN rate becomes reference
- Deviations are evaluated relative to baseline, not absolute counts

This prevents:
- Premature rubber-stamping
- Early-stage paralysis

---

## 8. NON-NEGOTIABLE INVARIANTS

- Passed gates are *revalidated*, never trusted
- Retry exhaustion is terminal
- Overrides increase scrutiny, never reduce it
- Silence is always an acceptable output

This section supersedes any conflicting implementation detail.

## Status

This artifact is operational.
It has a single purpose: **decide whether language is allowed to exist**.

If the answer cannot be defended, it does not ship.
