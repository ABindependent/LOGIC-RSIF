# LOGIC-RSIF
Institutional drift detection framework. Validated across Boeing 737 MAX, UnitedHealthcare, and Wells Fargo using identical methodology. AI safety application.
# L.O.G.I.C. — Logical Operational Infrastructure for Governance & Integrity Control

**Author:** Alexander Buedinger  
**Date:** March 2026  
**Contact:** Abued@proton.me

## What This Is

A pressure-indexed drift detection framework that identifies Forced Agency 
Collapse (FAC) — the structural condition where an institution has lost the 
ability to make non-harmful decisions — before harm occurs.

## The Finding

The same instrument, without parameter changes, was run against three 
independent institutional failure cases:

| Case | Period | FAC Detected | Confirmed |
|------|--------|-------------|-----------|
| Boeing 737 MAX | 2011–2019 | 2018-Q4 | Yes |
| UnitedHealthcare | 2017–2024 | 2024-Q2 | Yes |
| Wells Fargo | 2009–2020 | 2019-Q1 | Yes |

Oₜ (Option-Space Integrity) and Aₜ (Accountability Coupling) converge within 
25% at the FAC point across all three cases. Cₜ (Constraint Load) hits maximum 
in the final approach to FAC in all three cases.

Three independent cross-domain replications. Different industries, different 
decades, different harm types. Same structural signature.

## The Six Variables

- **Vₜ** — Velocity: system change rate
- **Lₜ** — Latency: time between deviation and correction
- **Cₜ** — Constraint Load: total pressure on system
- **Oₜ** — Option-Space Integrity: viable non-harmful actions remaining [control variable]
- **Hₜ** — Harm Rate: frequency and severity of negative outcomes
- **Aₜ** — Accountability Coupling: how tightly actions link to consequences

FAC fires when: Oₜ near zero, Cₜ sustained high, Lₜ elevated, Aₜ degraded, 
and Hₜ rises regardless of intervention.

## Repository Contents

- `logic_harness_clean.py` — detection harness, runs identically on all datasets
- `boeing_events_multisource.csv` — 30 events, 6 independent primary sources
- `unitedhealth_events_extracted_FINAL.csv` — 43 events, 5 independent sources  
- `wellsfargo_events_extracted.csv` — 32 events, 6 independent primary sources

## AI Safety Application

An autonomous agent running this framework against its own operational state 
vector detects drift before FAC rather than after. Combined with inverse 
gradient correction and Human-in-the-Loop escalation at the boundary, this 
constitutes a structurally complete self-correction architecture — not external 
guardrails, but internal trajectory awareness.

## Methodology

All variables are computed directly from sourced event data. No external 
weights. Thresholds are self-referential to each dataset's own distribution. 
The same code runs on all three datasets unchanged. Full methodology documented 
in harness code comments. please visit the HOWTO.md for detailed instructions. 

## License

Open methodology. Freely replicable. Attribution required.  
© Alexander Buedinger 2026
