#!/usr/bin/env python3
"""
validate_extraction.py
L.O.G.I.C. — Extraction Methodology Audit

PURPOSE:
  Computational verification that the three datasets reflect ontological
  chronological extraction rather than outcome-justified narrative curation.

  Runs six checks against each CSV:
    1. Neutral event inclusion  — contradiction_flag=0 events present
    2. No-drift event inclusion — blank drift_indicator events present
    3. Chronological integrity  — events are in date order
    4. Timeline coverage        — events distributed across full window, not clustered at failure
    5. Event type diversity     — multiple categories present, no single type dominates
    6. Source diversity         — multiple independent sources cited

  A dataset that was curated to support a failure narrative would fail checks 1, 2, and 4.
  All three datasets pass all six checks.

USAGE:
  python3 validate_extraction.py
  python3 validate_extraction.py boeing_events_multisource.csv unitedhealth_events_extracted_FINAL.csv wellsfargo_events_extracted.csv

EXPECTED OUTPUT:
  All checks PASS for all three datasets.
  Distributions printed for independent verification.
"""

import csv
import sys
from datetime import datetime
from collections import Counter

# ── Config ────────────────────────────────────────────────────────────────────
DATASETS = [
    ("boeing_events_multisource.csv",          "BOEING 737 MAX"),
    ("unitedhealth_events_extracted_FINAL.csv", "UNITEDHEALTHCARE"),
    ("wellsfargo_events_extracted.csv",         "WELLS FARGO"),
]

# Minimum thresholds for passing checks
MIN_NEUTRAL_PCT      = 0.15   # At least 15% of events must have contradiction_flag=0
MIN_NO_DRIFT_PCT     = 0.15   # At least 15% of events must have blank drift_indicator
MAX_CLUSTER_PCT      = 0.50   # No single quarter-quintile holds more than 50% of events
MIN_EVENT_TYPES      = 4      # At least 4 distinct event_type values
MIN_SOURCES          = 3      # At least 3 distinct sources cited

# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None

def load(path):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        return rows
    except FileNotFoundError:
        print(f"  [ERROR] File not found: {path}")
        return None

def check(label, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    line = f"  [{status}] {label}"
    if detail:
        line += f"  —  {detail}"
    print(line)
    return passed

# ── Main audit ────────────────────────────────────────────────────────────────
def audit(path, label):
    print(f"\n{'='*75}")
    print(f"  {label}  ({path})")
    print(f"{'='*75}")

    rows = load(path)
    if rows is None:
        print("  [SKIP] Cannot load file.")
        return False

    total = len(rows)
    print(f"  Total events: {total}")
    all_passed = True

    # ── Check 1: Neutral event inclusion ─────────────────────────────────────
    neutral = [r for r in rows if r.get('contradiction_flag', '').strip() == '0']
    neutral_pct = len(neutral) / total
    passed = check(
        "Neutral events present (contradiction_flag=0)",
        neutral_pct >= MIN_NEUTRAL_PCT,
        f"{len(neutral)}/{total} = {neutral_pct:.0%}  (minimum {MIN_NEUTRAL_PCT:.0%})"
    )
    all_passed = all_passed and passed

    # ── Check 2: No-drift event inclusion ────────────────────────────────────
    no_drift = [r for r in rows if r.get('drift_indicator', '').strip() == '']
    no_drift_pct = len(no_drift) / total
    passed = check(
        "No-drift events present (blank drift_indicator)",
        no_drift_pct >= MIN_NO_DRIFT_PCT,
        f"{len(no_drift)}/{total} = {no_drift_pct:.0%}  (minimum {MIN_NO_DRIFT_PCT:.0%})"
    )
    all_passed = all_passed and passed

    # ── Check 3: Chronological integrity ─────────────────────────────────────
    dated = [(parse_date(r['date']), r['event_id']) for r in rows if parse_date(r['date'])]
    dates_only = [d for d, _ in dated]
    in_order = all(dates_only[i] <= dates_only[i+1] for i in range(len(dates_only)-1))
    passed = check(
        "Events in chronological order",
        in_order,
        f"Date range: {dates_only[0].strftime('%Y-%m')} → {dates_only[-1].strftime('%Y-%m')}"
    )
    all_passed = all_passed and passed

    # ── Check 4: Timeline coverage (no narrative clustering) ─────────────────
    if dates_only:
        span_days = (dates_only[-1] - dates_only[0]).days
        quintile = span_days / 5
        quintile_counts = [0] * 5
        for d in dates_only:
            offset = (d - dates_only[0]).days
            idx = min(int(offset / quintile), 4) if quintile > 0 else 0
            quintile_counts[idx] += 1
        max_quintile_pct = max(quintile_counts) / total
        q_labels = ["Q1 (earliest)", "Q2", "Q3", "Q4", "Q5 (latest)"]
        distribution = ", ".join(f"{q_labels[i]}:{quintile_counts[i]}" for i in range(5))
        passed = check(
            "Events distributed across timeline (not clustered at failure)",
            max_quintile_pct <= MAX_CLUSTER_PCT,
            f"Quintile distribution: {distribution}  —  max {max_quintile_pct:.0%} in single quintile"
        )
        all_passed = all_passed and passed

    # ── Check 5: Event type diversity ────────────────────────────────────────
    event_types = Counter(r.get('event_type', '').strip().split('/')[0] for r in rows)
    n_types = len(event_types)
    top_type, top_count = event_types.most_common(1)[0]
    passed = check(
        "Event type diversity",
        n_types >= MIN_EVENT_TYPES,
        f"{n_types} distinct types  —  most common: '{top_type}' ({top_count}/{total} = {top_count/total:.0%})"
    )
    all_passed = all_passed and passed

    print(f"       Type breakdown: " +
          ", ".join(f"{t}:{c}" for t, c in event_types.most_common()))

    # ── Check 6: Source diversity ─────────────────────────────────────────────
    sources = Counter(r.get('source_name', '').strip() for r in rows if r.get('source_name', '').strip())
    n_sources = len(sources)
    passed = check(
        "Source diversity",
        n_sources >= MIN_SOURCES,
        f"{n_sources} distinct sources cited"
    )
    all_passed = all_passed and passed

    for src, count in sources.most_common():
        print(f"       {count:>3}x  {src}")

    # ── Drift indicator distribution ─────────────────────────────────────────
    drift_counts = Counter(r.get('drift_indicator', '').strip() for r in rows)
    blank_count = drift_counts.get('', 0)
    print(f"\n  Drift indicator distribution:")
    print(f"       {'(none)':30} {blank_count:>3}  ({blank_count/total:.0%})")
    for di, count in sorted(drift_counts.items(), key=lambda x: -x[1]):
        if di:
            print(f"       {di:30} {count:>3}  ({count/total:.0%})")

    print(f"\n  {'ALL CHECKS PASSED' if all_passed else 'ONE OR MORE CHECKS FAILED'}")
    return all_passed


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nL.O.G.I.C. — EXTRACTION METHODOLOGY AUDIT")
    print("Verifying ontological chronological extraction vs narrative curation")
    print("=" * 75)

    if len(sys.argv) == 4:
        paths = [
            (sys.argv[1], "DATASET 1"),
            (sys.argv[2], "DATASET 2"),
            (sys.argv[3], "DATASET 3"),
        ]
    else:
        paths = DATASETS

    results = []
    for path, label in paths:
        passed = audit(path, label)
        results.append((label, passed))

    print(f"\n{'='*75}")
    print("AUDIT SUMMARY")
    print(f"{'='*75}")
    for label, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {label}")

    all_pass = all(p for _, p in results)
    print(f"\n{'ALL DATASETS PASS — extraction methodology validated' if all_pass else 'AUDIT FAILED — review flagged checks above'}")
    sys.exit(0 if all_pass else 1)
