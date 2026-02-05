# Comparative Analysis: Standard Z-Score vs. Modified Z-Score

| Metric | Standard Z-Score (Mean-Based) | Modified Z-Score (Median-Based) |
|---|---|---|
| Statistical Center | Arithmetic Mean | Median |
| Sensitivity | High (Drifted by Outliers) | Low (Resistant to Outliers) |
| Fail Mode | Normalizes massive projects | Anchors to typical projects |
| Application | Bell-curve distributions | Power-law distributions (Budgets) |

**Result**

In testing, a single $100M project moved the arithmetic mean enough to hide
$5M-scale infrastructure risks.

The Modified Z-Score maintained a stable median and successfully flagged
the $100M project with a modified_z > 14, preserving visibility of capital
concentration risk.
