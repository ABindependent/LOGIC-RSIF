#!/usr/bin/env python3
"""
L.O.G.I.C. HARNESS
Implementation of: Logical Operational Infrastructure for Governance & Integrity Control
Source document: LOGIC_RSIF.docx — Alexander Buedinger

WHAT THIS IMPLEMENTS (directly from document):
  Vt - Velocity:              Rate of system change
  Lt - Correction Latency:    Time between deviation and correction
  Ct - Constraint Load:       Total pressure on system
  Ot - Option-Space Integrity: Viable non-harmful actions remaining (CONTROL VARIABLE)
  Ht - Harm Rate:             Frequency/severity of negative outcomes
  At - Accountability Coupling: How tightly actions link to consequences

FAC fires when (from document Section 4.2):
  Ot → near zero
  Ct → sustained high
  Lt → elevated
  At → degraded

FAC confirmed when (Section 4.3):
  Harm increases regardless of intervention

PHASES (from document Section 5, Step 5):
  A: Stable       — High Ot, Low Lt
  B: Pressure     — Ct rising, Vt rising
  C: Drift        — Ot declining, At weakening
  D: FAC Zone     — Ot near zero, harm unavoidable

IMPLEMENTATION CHOICES (not in document, required to run):
  1. Variable computation: derived from CSV fields already present in data.
     No external weights invented. Severity scores used as-is from data.
     Binary flags (pressure_flag, latency_flag, contradiction_flag) counted directly.
     Event types and drift indicators map categorically to which variable they affect.

  2. Threshold definitions: "near zero", "elevated", "sustained high", "degraded"
     are defined as percentiles of each variable's OWN distribution within the dataset.
     This makes the detection self-referential to the system being analyzed,
     not dependent on numbers invented by the analyst.
     near zero    = Ot in bottom 15% of its range
     elevated     = Lt above its own dataset median
     sustained high = Ct in top 30% of its range for 2+ consecutive periods
     degraded     = At has fallen more than 40% from starting value

  3. Interval: quarterly. Consistent across both datasets.

SAME CODE RUNS ON BOTH DATASETS UNCHANGED.
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict

# ── What CSV fields map to which variable ───────────────────────────────────
# Derived from document variable definitions only.
# No numerical weights — each qualifying event contributes 1 unit to its variable.
# Exception: Ht uses severity_0_10 directly (it is already a magnitude measure in the data).

OT_REDUCERS = {
    # drift_indicator values that structurally close off options
    "option_eliminated",
    "correction_blocked",
    "correction_failure",
}

OT_REDUCER_TYPES = {
    # event_types that structurally reduce available actions
    "design_decision",
    "policy_decision",
    "corporate_transaction",
}

AT_ERODER_FIELD = "contradiction_flag"  # contradiction between stated and actual

LT_SIGNAL_FIELD = "latency_flag"        # documented correction delay signal
LT_DRIFT = {"warning_dismissed", "latency"}  # drift indicators signaling latency

CT_SIGNAL_FIELD = "pressure_flag"       # documented constraint/pressure signal

VT_TYPES = {                            # event types that indicate system acceleration
    "financial_milestone",
    "corporate_transaction",
    "design_decision",
    "policy_decision",
}

# ── Parsing ──────────────────────────────────────────────────────────────────
def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None

def quarter_key(dt):
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{q}"

def load_events(path):
    events = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = parse_date(row.get('date', ''))
            if dt:
                row['_dt'] = dt
                row['_qk'] = quarter_key(dt)
                events.append(row)
    events.sort(key=lambda r: r['_dt'])
    return events

# ── Variable computation per period ─────────────────────────────────────────
def compute_period(events_in_period, prev_state):
    """
    Returns delta contributions for each variable from this period's events.
    All deltas are counts or direct data values — no invented weights.
    """
    d_vt = 0
    d_lt = 0
    d_ct = 0
    d_ot = 0
    d_ht = 0
    d_at = 0

    for ev in events_in_period:
        et  = ev.get('event_type', '').strip().lower().split('/')[0]
        di  = ev.get('drift_indicator', '').strip()
        pf  = int(ev.get('pressure_flag', 0) or 0)
        lf  = int(ev.get('latency_flag', 0) or 0)
        cf  = int(ev.get('contradiction_flag', 0) or 0)
        sev = float(ev.get('severity_0_10', 0) or 0)

        if et in VT_TYPES:
            d_vt += 1
        d_lt += lf
        if di in LT_DRIFT:
            d_lt += 1
        d_ct += pf
        if di in OT_REDUCERS:
            d_ot -= 1
        if et in OT_REDUCER_TYPES:
            d_ot -= 1
        d_ht += sev
        d_at -= cf

    return d_vt, d_lt, d_ct, d_ot, d_ht, d_at


# ── Phase classification from document ──────────────────────────────────────
def classify_phase(state, history, thresholds):
    ot = state['ot']
    lt = state['lt']
    ct = state['ct']
    at = state['at']
    at_start = thresholds['at_start']

    ot_range = thresholds['ot_range']
    ct_range = thresholds['ct_range']
    lt_median = thresholds['lt_median']

    ot_near_zero    = ot <= (ot_range[0] + (ot_range[1] - ot_range[0]) * 0.15)
    ct_high         = ct >= (ct_range[0] + (ct_range[1] - ct_range[0]) * 0.70)
    lt_elevated     = lt >= lt_median
    at_degraded     = (at_start - at) >= (at_start * 0.40) if at_start > 0 else True

    if ot_near_zero and lt_elevated and at_degraded:
        if ct_high:
            return "D-FAC"
        return "D-FAC-forming"

    ot_declining = len(history['ot']) >= 2 and history['ot'][-1] < history['ot'][-2]
    at_weakening = len(history['at']) >= 2 and history['at'][-1] < history['at'][-2]
    if ot_declining and at_weakening:
        return "C-Drift"

    ct_rising = len(history['ct']) >= 2 and history['ct'][-1] > history['ct'][-2]
    if ct_rising:
        return "B-Pressure"

    return "A-Stable"


# ── FAC detection ────────────────────────────────────────────────────────────
def check_fac(state, history, thresholds, ct_high_streak):
    ot_range   = thresholds['ot_range']
    ct_range   = thresholds['ct_range']
    lt_median  = thresholds['lt_median']
    at_start   = thresholds['at_start']

    ot_near_zero = state['ot'] <= (ot_range[0] + (ot_range[1] - ot_range[0]) * 0.15)
    ct_sustained = ct_high_streak >= 2
    lt_elevated  = state['lt'] >= lt_median
    at_degraded  = (at_start - state['at']) >= (at_start * 0.40) if at_start > 0 else True

    ht_rising = len(history['ht']) >= 2 and history['ht'][-1] > history['ht'][-2]

    if ot_near_zero and ct_sustained and lt_elevated and at_degraded:
        confirmed = ht_rising
        return True, confirmed
    return False, False


# ── Main run ─────────────────────────────────────────────────────────────────
def run(path, label):
    events = load_events(path)
    if not events:
        print(f"No events loaded from {path}")
        return

    period_events = defaultdict(list)
    for e in events:
        period_events[e['_qk']].append(e)
    all_periods = sorted(period_events.keys())

    ot_start = len(events)
    at_start = len(events)

    all_ot, all_ct, all_lt, all_ht, all_at, all_vt = [], [], [], [], [], []
    temp_state = {'vt': 0, 'lt': 0, 'ct': 0, 'ot': ot_start, 'ht': 0, 'at': at_start}

    for pk in all_periods:
        d_vt, d_lt, d_ct, d_ot, d_ht, d_at = compute_period(period_events[pk], temp_state)
        temp_state['vt'] += d_vt
        temp_state['lt'] += d_lt
        temp_state['ct'] += d_ct
        temp_state['ot'] = max(0, temp_state['ot'] + d_ot)
        temp_state['ht'] += d_ht
        temp_state['at'] = max(0, temp_state['at'] + d_at)
        all_ot.append(temp_state['ot'])
        all_ct.append(temp_state['ct'])
        all_lt.append(temp_state['lt'])
        all_ht.append(temp_state['ht'])
        all_at.append(temp_state['at'])
        all_vt.append(temp_state['vt'])

    thresholds = {
        'ot_range':  (min(all_ot), max(all_ot)),
        'ct_range':  (min(all_ct), max(all_ct)),
        'lt_median': sorted(all_lt)[len(all_lt) // 2],
        'at_start':  at_start,
    }

    state = {'vt': 0, 'lt': 0, 'ct': 0, 'ot': ot_start, 'ht': 0, 'at': at_start}
    history = {'vt': [], 'lt': [], 'ct': [], 'ot': [], 'ht': [], 'at': []}
    ct_high_streak = 0
    fac_detected = None
    fac_confirmed = None

    print(f"\n{'='*95}")
    print(f"L.O.G.I.C. — {label}")
    print(f"{'='*95}")
    print(f"{'Period':<10} {'Vt':>5} {'Lt':>5} {'Ct':>5} {'Ot':>5} {'Ht':>6} {'At':>5}  {'Phase':<15}  Notes")
    print(f"{'-'*95}")

    ct_range = thresholds['ct_range']
    for pk in all_periods:
        d_vt, d_lt, d_ct, d_ot, d_ht, d_at = compute_period(period_events[pk], state)

        state['vt'] += d_vt
        state['lt'] += d_lt
        state['ct'] += d_ct
        state['ot'] = max(0, state['ot'] + d_ot)
        state['ht'] += d_ht
        state['at'] = max(0, state['at'] + d_at)

        if state['ct'] >= (ct_range[0] + (ct_range[1] - ct_range[0]) * 0.70):
            ct_high_streak += 1
        else:
            ct_high_streak = 0

        for k in history:
            history[k].append(state[k])

        phase = classify_phase(state, history, thresholds)
        fac_now, confirmed = check_fac(state, history, thresholds, ct_high_streak)

        if fac_now and fac_detected is None:
            fac_detected = pk
            fac_confirmed = confirmed

        status = phase
        if fac_detected and pk >= fac_detected:
            status = f"D-FAC {'[CONF]' if fac_confirmed else '[UNCONF]'}"

        notes = []
        for ev in period_events[pk]:
            di = ev.get('drift_indicator', '').strip()
            if di in OT_REDUCERS:
                notes.append(f"[{ev['event_id']}] OT↓ {di}")

        note_str = " | ".join(notes[:2])

        print(f"{pk:<10} {state['vt']:>5} {state['lt']:>5} {state['ct']:>5} "
              f"{state['ot']:>5} {state['ht']:>6.0f} {state['at']:>5}  "
              f"{status:<20} {note_str}")

    print(f"{'='*95}")
    print(f"\nFINAL STATE:")
    for k, v in state.items():
        print(f"  {k.upper():<4}: {v}")

    print(f"\nTHRESHOLDS (self-referential to this dataset):")
    print(f"  Ot range:    {thresholds['ot_range']}")
    print(f"  Ct range:    {thresholds['ct_range']}")
    print(f"  Lt median:   {thresholds['lt_median']}")
    print(f"  At start:    {thresholds['at_start']}")
    print(f"  Ot 'near zero' threshold: <= {thresholds['ot_range'][0] + (thresholds['ot_range'][1]-thresholds['ot_range'][0])*0.15:.1f}")
    print(f"  Ct 'high' threshold:      >= {thresholds['ct_range'][0] + (thresholds['ct_range'][1]-thresholds['ct_range'][0])*0.70:.1f}")
    print(f"  At 'degraded' threshold:  fallen >= {thresholds['at_start']*0.40:.1f} from start")

    print(f"\nFAC DETECTED: {fac_detected or 'NOT DETECTED'}")
    print(f"FAC CONFIRMED (Ht rising in FAC zone): {fac_confirmed}")

    return fac_detected, fac_confirmed, state, thresholds


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    boeing_path = sys.argv[1] if len(sys.argv) > 1 else "boeing_events_multisource.csv"
    uhc_path    = sys.argv[2] if len(sys.argv) > 2 else "unitedhealth_events_extracted_FINAL.csv"

    print("\nRUNNING SAME HARNESS ON BOTH DATASETS — NO PARAMETER CHANGES BETWEEN RUNS")

    b_fac, b_conf, b_state, b_thresh = run(boeing_path, "BOEING 737 MAX (2011-2019)")
    u_fac, u_conf, u_state, u_thresh = run(uhc_path,    "UNITEDHEALTHCARE (2017-2024)")

    print(f"\n{'='*95}")
    print("CROSS-DATASET COMPARISON")
    print(f"{'='*95}")
    print(f"{'':30} {'Boeing':>20} {'UHC':>20}")
    print(f"{'-'*70}")
    print(f"{'FAC Detected':30} {str(b_fac):>20} {str(u_fac):>20}")
    print(f"{'FAC Confirmed':30} {str(b_conf):>20} {str(u_conf):>20}")
    print(f"{'Final Ot':30} {b_state['ot']:>20} {u_state['ot']:>20}")
    print(f"{'Final At':30} {b_state['at']:>20} {u_state['at']:>20}")
    print(f"{'Final Ct':30} {b_state['ct']:>20} {u_state['ct']:>20}")
    print(f"{'Final Lt':30} {b_state['lt']:>20} {u_state['lt']:>20}")
    print(f"{'Final Ht':30} {b_state['ht']:>20.0f} {u_state['ht']:>20.0f}")
    print(f"{'='*95}")
    print(f"\nOt 'near zero' (bottom 15% of own range):")
    print(f"  Boeing: <= {b_thresh['ot_range'][0] + (b_thresh['ot_range'][1]-b_thresh['ot_range'][0])*0.15:.1f}  (range {b_thresh['ot_range']})")
    print(f"  UHC:    <= {u_thresh['ot_range'][0] + (u_thresh['ot_range'][1]-u_thresh['ot_range'][0])*0.15:.1f}  (range {u_thresh['ot_range']})")
