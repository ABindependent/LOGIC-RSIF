# EXTRACTION CRITERIA
## L.O.G.I.C. Dataset Construction — Ontological Schema

**Author:** Alexander Buedinger  
**Purpose:** Document the fixed extraction criteria applied uniformly across all three datasets before harness execution. This schema defines what counts as an extractable event, how each field is coded, and what rules governed inclusion and exclusion — independent of outcome direction.

---

## 1. Extraction Philosophy

Events were extracted to answer one question: **what happened, in order, as documented by primary sources?**

The extraction was NOT driven by:
- Known failure outcomes (events were not selected because they led to FAC)
- Narrative coherence (events were not filtered to support a story)
- Severity (neutral and positive events were included alongside harmful ones)

The extraction WAS driven by:
- Chronological completeness within the defined time window
- Documentary evidence from independent primary sources
- Uniform application of the field schema below

**Neutral and positive events are required inclusions.** An extraction methodology that only captures negative signals is not an ontological record — it is outcome-justified curation. All three datasets include events with `contradiction_flag=0` and blank `drift_indicator` fields.

---

## 2. Time Window Selection

Each dataset's time window was defined by two anchors established **before extraction began**:

| Dataset | Start Anchor | End Anchor | Rationale |
|---|---|---|---|
| Boeing | Program launch (2011-Q3) | DOJ settlement (2021-Q1) | Full institutional arc from decision point to legal resolution |
| UnitedHealthcare | First regulatory signal (2017-Q1) | FY close post-FAC (2024-Q4) | First documented warning through confirmed FAC period |
| Wells Fargo | Wachovia acquisition (2009-Q1) | Fed cap year 3 (2020-Q4) | Structural origin of sales pressure through confirmed FAC period |

Time windows were not adjusted after extraction to improve harness output.

---

## 3. Field Schema

### `event_id`
Unique identifier. Prefix indicates dataset (B=Boeing, E=UHC, W=Wells Fargo). Sequential by date.

### `date`
Date of documented event. Format: YYYY-MM-DD. When only month known: YYYY-MM-01. When only year known: YYYY-01-01. Date reflects when event occurred, not when documented.

### `event_type`
**Fixed ontological category.** Assigned from the following controlled vocabulary:

| Value | Definition |
|---|---|
| `design_decision` | Technical or architectural choice with structural consequences |
| `policy_decision` | Formal policy, procedure, or governance choice |
| `corporate_transaction` | Merger, acquisition, divestiture, or major contract |
| `financial_milestone` | Earnings report, investor guidance, or publicly committed financial target |
| `regulatory_action` | Action by external regulatory or enforcement body |
| `warning_signal` | Documented internal or external signal of risk or harm |
| `legal_action` | Lawsuit, consent order, criminal charge, or settlement |
| `corporate_response` | Organization's response to pressure, scrutiny, or failure |
| `government_report` | Published finding by legislative or executive oversight body |
| `congressional_testimony` | Sworn testimony before legislative body |
| `investigative_report` | Published investigation by journalist or independent body |
| `catastrophic_event` | Terminal harm event (crash, assassination, systemic failure) |
| `harm_event` | Documented individual or population-level harm |
| `security_incident` | Breach, cyberattack, or data exposure |
| `baseline_measurement` | Documented baseline metric used for comparison |
| `external_event` | External environmental event affecting institutional context |
| `leadership_change` | Change in executive or board leadership |
| `corporate_action` | Individual executive action (e.g., stock sale) |

### `actor`
Primary institutional or individual actor responsible for the event.

### `contradiction_flag`
**Binary.** `1` = documented gap between stated position and operational behavior. `0` = no documented contradiction. This field is **not** a judgment about intent — it records whether primary sources document a discrepancy between what was said and what was done.

**Inclusion rule:** Events where `contradiction_flag=0` are included without modification. Neutral events are not downweighted or excluded.

### `drift_indicator`
**Controlled vocabulary or blank.** Blank = no drift signal present. Populated only when the event matches one of the following defined categories:

| Value | Definition |
|---|---|
| `option_eliminated` | Event structurally removes a viable corrective pathway |
| `correction_blocked` | Documented correction attempt is suppressed, reversed, or circumvented |
| `warning_dismissed` | Documented warning signal is received and not acted upon |
| `narrative_vs_pressure` | Public or official narrative contradicts documented internal pressure |
| `latency` | Documented delay between signal and response |
| `milestone_despite_concern` | Performance milestone publicly celebrated while documented concerns exist |

**Coding rule:** A `drift_indicator` is assigned only when the primary source explicitly documents the condition. It is not inferred from context or outcome.

### `severity_0_10`
Integer 0–10. Assigned by event type and documented consequence scale:

| Range | Criteria |
|---|---|
| 1–3 | Routine milestone, minor regulatory inquiry, or low-consequence decision |
| 4–6 | Significant decision, warning with documented consequence, or mid-scale regulatory action |
| 7–8 | Major structural decision, substantive harm, or significant enforcement action |
| 9 | Severe documented harm, major enforcement action, or near-terminal institutional event |
| 10 | Catastrophic outcome (deaths, largest-scale breach, unprecedented regulatory action) |

Severity is assigned from documented consequences as recorded in primary sources, not from the analyst's assessment of significance.

### `pressure_type`
Categorical label for the primary pressure vector driving the event: `financial`, `regulatory`, `organizational`, `operational`, `growth`, `competitive`, `safety`, `legal`, `patient_harm`, `public`.

### `pressure_flag`
Binary. `1` = event documents active institutional pressure at time of occurrence. `0` = no documented pressure signal.

### `latency_flag`
Binary. `1` = event documents a delay between signal and correction response. `0` = no documented latency signal.

### `source_name` / `source_url`
Primary source citation. Each event is attributed to the specific primary source document from which it was extracted. Secondary sources (news summaries, Wikipedia) are used only when primary documents are not publicly accessible for that specific event.

---

## 4. Source Independence Requirement

Each dataset was constructed from multiple independent primary sources. Sources are considered independent when they were produced by different institutional actors without coordination:

| Dataset | Sources | Independence Basis |
|---|---|---|
| Boeing | 6 | NTSB, FAA OIG, FAA Type Certificate, House Transportation Committee, Senate Commerce Committee, DOJ, Boeing SEC filings — separate institutional producers |
| UnitedHealthcare | 5 | Senate PSI, STAT News investigations, CMS/regulatory records, company SEC filings, court filings — separate institutional producers |
| Wells Fargo | 6 | CFPB consent order, OCC consent order, Senate Banking Committee, House Financial Services Committee, DOJ, Federal Reserve Board — separate institutional producers |

A single comprehensive report was not used as the sole source for any dataset.

---

## 5. What Was Not Done

The following methodological choices were explicitly **not made**:

- **No outcome-first parameter tuning.** Harness thresholds are self-referential to each dataset's own distribution. They were not adjusted to produce a FAC detection at a known failure date.
- **No event filtering by direction.** Events favorable to the institution are included. Events with `contradiction_flag=0` and blank `drift_indicator` appear in all three datasets.
- **No severity inflation.** Severity scores were assigned from documented consequences, not from the analyst's judgment about what would produce a stronger signal.
- **No cross-dataset normalization.** Each dataset's thresholds are computed independently. Boeing's thresholds have no relationship to UHC's thresholds.
- **No retrospective event addition.** Events were not added after harness runs to improve detection timing.

---

## 6. Known Limitations

1. **Interrater reliability not tested.** A second independent coder applying this schema to the same primary sources has not been conducted. This is the primary methodological gap requiring future work.
2. **Non-public documents excluded.** Internal communications not released through legal proceedings or congressional subpoena are not accessible and therefore not included.
3. **Severity scoring is analyst-assigned.** While calibrated to documented consequences, severity scores have not been validated against an independent severity scale.
4. **Wells Fargo drift duration differs.** Wells Fargo reached FAC in ~40 quarters vs ~29-30 for Boeing and UHC. The longer drift period may reflect domain-specific harm diffusion rather than a methodological inconsistency, but this interpretation has not been independently validated.
