![EAD252D1-08CC-4BCE-B2E7-A980AFC4C242](https://github.com/user-attachments/assets/7de1787d-0ab4-4a3d-a9fb-a552cb30a158)

# Structural Integrity Audit

A deterministic audit engine that inspects real artifacts and fails closed.

## Inputs
- CSV files
- Images
- PyTorch checkpoints
- Raw text

## Outputs
- JSON audit reports
- Evidence files
- Optional PDF certificates

## Guarantees
- No heuristics without observables
- Evidence emitted on failure
- Machine-enforceable verdicts

## Interfaces
- REST API (FastAPI)
- Batch mode
- CI/CLI gate

This tool does not explain outcomes.
It records them.
