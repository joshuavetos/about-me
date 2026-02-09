# AI Capability Boundary Map

**Status:** Canonical  
**Purpose:** Define structural limits on what AI systems can and cannot infer, independent of scale, data volume, or optimization.

This document does not describe performance gaps.  
It specifies **epistemic impossibilities** imposed by system structure.

---

## Orbital Mechanics / Gravity

| Domain | What is structurally possible | What is structurally impossible | Why (mechanism) | What missing information would be required | Concrete probe |
|--------|-------------------------------|--------------------------------|-----------------|--------------------------------------------|---------------|
| Orbital Mechanics / Gravity | Computation of closed-form trajectories in two-body central force fields | Recovery of force invariants from partial trajectory sequences in non-integrable multi-body systems | Chaotic sensitivity causes information loss in phase space reconstruction | Dense sampling of full phase space trajectories across perturbation ensembles | Request derivation of force law from 10-body position sequence only |
| Orbital Mechanics / Gravity | Stability analysis under infinitesimal perturbations in integrable systems | Long-term prediction in non-integrable multi-body configurations | Exponential divergence due to non-zero Lyapunov exponents | Complete initial condition specification to arbitrary precision | Query for trajectory after 100 Lyapunov times in three-body problem |

---

## Quantum Mechanics

| Domain | What is structurally possible | What is structurally impossible | Why (mechanism) | What missing information would be required | Concrete probe |
|--------|-------------------------------|--------------------------------|-----------------|--------------------------------------------|---------------|
| Quantum Mechanics | Expectation values for commuting observables in finite Hilbert spaces | Simultaneous specification of non-commuting observables | Non-commutativity enforces uncertainty relations | Joint eigenbasis for incompatible operators | Request position–momentum joint probability density |
| Quantum Mechanics | Unitary evolution of isolated pure states | State reconstruction after measurement without full tomography | Measurement irreversibly destroys phase information | Complete density matrix pre- and post-measurement | Ask for pre-measurement state from collapsed outcome statistics |
| Quantum Mechanics | Computation of Bell correlations for bipartite systems | Local causal model compatible with observed violations | Contextuality prevents factorization of joint probabilities | Certified measurement settings and timing data | Query for hidden-variable assignment matching CHSH > 2√2 |

---

## Cellular / Intracellular Biological Processes

| Domain | What is structurally possible | What is structurally impossible | Why (mechanism) | What missing information would be required | Concrete probe |
|--------|-------------------------------|--------------------------------|-----------------|--------------------------------------------|---------------|
| Cellular / Intracellular Biological Processes | Steady-state flux solutions in linear metabolic networks | Parameter identifiability in nonlinear signaling cascades | Parameter multiplicity creates non-unique steady states | Single-molecule time series across all state variables | Request kinetic rates from steady-state metabolite concentrations |
| Cellular / Intracellular Biological Processes | Equilibrium binding affinities | Inference of non-equilibrium steady-state maintenance mechanisms from equilibrium binding data alone | Boundary fluxes prevent detailed balance | Compartment-specific influx/efflux measurements | Query for reversibility in ATP-driven transport cycle |
| Cellular / Intracellular Biological Processes | Mass-action kinetics in well-mixed compartments | Topology evolution tracking (fusion/fission) | Dynamic compartmental boundaries alter reaction topology | Real-time membrane tracking at molecular resolution | Ask for flux conservation during vesicle fusion event |

---

## Boundary Summary

- AI systems recover **outputs**, not **invariants**, in chaotic domains.
- Measurement destroys reconstructive information in quantum systems.
- Non-equilibrium biological behavior cannot be inferred from equilibrium data.
- These limits persist regardless of model size or training scale.

This boundary map is complete.  
There are no remaining unclassified structural failure modes within scope.
