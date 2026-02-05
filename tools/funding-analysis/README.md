![0CFAA5F8-5F94-4612-BEBC-4F1D2C746152](https://github.com/user-attachments/assets/0f0af82c-2d0f-42d3-b64c-604c3db5845e)

# Funding / Allocation Analysis Tool

This directory contains **one specific tool** within the repository:
a deterministic engine for extracting and validating financial allocations
across time from planning, regulatory, or disclosure documents.

It does **not** describe the entire repository.
It describes **only the allocation extraction and gap detection mechanism**.

---

## Purpose

The purpose of this tool is narrow and mechanical:

To determine **where funding is explicitly disclosed**,  
**where it is not**, and  
**where claims fail basic validation**.

It is intentionally not a summarization or interpretation system.

---

## What This Tool Does

- Extracts year references and monetary amounts from document text
- Normalizes values (e.g. millions vs. billions, signed amounts)
- Applies hard sanity bounds to reject implausible data
- Logs every rejection with evidence instead of hiding failures
- Computes coverage across a target year horizon
- Identifies years with no associated funding (“gaps”)

All outputs are derived strictly from explicit disclosures in the input text.

---

## What This Tool Explicitly Does NOT Do

- It does not infer intent
- It does not assume missing data is zero
- It does not fill gaps
- It does not narrate or summarize findings
- It does not claim correctness when inputs are incomplete
- It does not evaluate ethics, legality, or compliance

Absence, partial coverage, and refusal are valid outcomes.

---

## How It Works (High Level)

1. Parse candidate year and currency tokens from text
2. Normalize units and signs
3. Apply explicit validation bounds
4. Reject and log invalid or ambiguous values
5. Build a coverage vector across the target horizon
6. Report funded vs. unfunded years and data quality telemetry

Rejection is treated as a first-class result.

---

## How To Use This Tool

- Provide document text as input (text extraction happens upstream)
- Run the allocation extraction and validation logic
- Review:
  - accepted allocations
  - rejected values and rejection reasons
  - coverage across the target year range

If rejection rates are high, the document should be flagged
for manual review rather than trusted.

---

## Design Principle

This tool prefers **observable absence** and **explicit refusal**
over speculative completeness.

It exists to answer one question only:

> “What funding is explicitly disclosed for which years — and where does that disclosure stop?”
