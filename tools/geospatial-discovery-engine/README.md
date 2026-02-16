# Geospatial Discovery Engine

Precision-biased SAR anomaly filter designed to survive hostile peer review.

This module implements a fail-closed architecture.  
Any anomaly that fails a gate is rejected.

---

## Architecture

### Tier 1 — Localized Statistical Gate (GRD)
- Local Z-score computed from ambient buffer
- Rejects low-contrast noise
- Kills global variance masking

### Tier 2 — Physical Stability Gate (SLC)
- Requires temporal coherence validation
- Eliminates moisture and transient sand artifacts

### Tier 3 — Morphology Gate
- Skeletonization
- Eccentricity threshold (rejects linear industrial traces)
- Fractal dimension filter (rejects geological fractures)
- Angular entropy (rejects stochastic ridge noise)
- Nyquist resolution floor (rejects sub-pixel imagination)

---

## Fail-Closed Policy

A candidate must pass ALL gates to survive.

If any of the following occur, the anomaly is rejected:

- Z < 2.5
- Pixel span < 15
- Eccentricity > 0.92
- Fractal dimension > 1.4
- Angular entropy above threshold
- Coherence below stability floor

False negatives are acceptable.
False positives are not.

---

## Output Contract

Each surviving candidate produces a JSON package containing:

- Coordinates
- Z-score metrics
- Structural metrics
- Gate verdicts
- Audit status

No narrative output.
No archaeological claims.
Machine-readable audit trail only.

---

## Reproducibility Requirements

- Google Earth Engine project access
- Sentinel-1 GRD collection
- Sentinel-1 SLC collection (for full stability validation)
- Fixed thresholds defined in configuration block

---

## Intended Use

Blind validation via withheld coordinates.

This engine produces a high-precision shortlist
for external archaeological review.

It does not declare discovery.
It declares survivorship under audit.
