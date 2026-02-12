# Core Governance & Reliability Stack
    This directory contains production-grade prototypes demonstrating the "Technical Auditor" persona. Each module addresses a specific failure mode in AI and industrial systems.
    
    ### Components:
    - `guardrail_engine.py`: AI Inference Guardrail (Probabilistic refusal).
    - `audit_pipeline.py`: Data Platform Integrity (Transformation receipts).
    - `bounded_agent.py`: Policy-Enforced Agentic AI (Tool-use constraints).
    - `rap_kernel.py`: Action-Scoped Bonding (Capital-backed risk management).
    - `drift_monitor.py`: Model Health & Drift Detection (Statistical validation).
    - `industrial_guard.py`: Predictive Maintenance (Industrial safety states).
## 📊 Performance Audit (v6.0 - Proportional Controller)

The VETOS engine was backtested against the S&P 500 (2005–2026) using recursive GARCH volatility targeting and cross-asset liquidity sensors.

| Metric | S&P 500 (Buy & Hold) | VETOS Proportional |
| :--- | :--- | :--- |
| **Max Drawdown** | -55.19% | **-29.54%** |
| **Sharpe Ratio** | 0.6320 | **0.7994** |
| **Risk Reduction** | Baseline | **+46% Improvement** |

### Systemic Safety Interlocks
- **Recursive Vol-Targeting:** Scales exposure as `target_vol / current_vol` to prevent cliff-edge drawdowns.
- **The Bond Trap:** A deterministic kill-switch that moves to 0% exposure when the Dollar-Equity correlation signals a systemic liquidity collapse.
- **Auditable Lineage:** Every risk-scaling event is cryptographically logged to the `audit_pipeline`.
