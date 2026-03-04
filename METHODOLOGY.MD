# Methodology — L.O.G.I.C. Detection Harness

## How Variables Are Computed

Variables are derived directly from the event CSV.
No external weights are applied. No parameters differ between datasets.

- Vₜ: Count of acceleration events per period
- Lₜ: Cumulative latency flags and drift indicators
- Cₜ: Cumulative pressure flags
- Oₜ: Starts at event count, decremented by option_eliminated
      and correction_blocked events [CONTROL VARIABLE]
- Hₜ: Cumulative sum of severity_0_10 scores from raw data
- Aₜ: Starts at event count, decremented by contradiction_flag events

## How Thresholds Are Set

All thresholds are self-referential to each dataset's own distribution:

- "Near zero" Oₜ = bottom 15% of that dataset's Oₜ range
- "Elevated" Lₜ = above that dataset's median
- "Sustained high" Cₜ = top 30% for 2+ consecutive periods
- "Degraded" Aₜ = fallen more than 40% from starting value

No threshold is set by looking at outcomes first.
The same rules apply to all three datasets unchanged.

## FAC Detection Criteria

FAC fires when all four conditions are simultaneously met:
1. Oₜ near zero
2. Cₜ sustained high
3. Lₜ elevated
4. Aₜ degraded

FAC is confirmed when Hₜ rises in the FAC zone regardless of intervention.

## Interval

Quarterly. Consistent across all three datasets.

## What Was Not Done

- No weights were invented and applied to amplify signals
- No thresholds were chosen after seeing outcomes
- No parameters were changed between datasets
- No events were selected knowing they would produce FAC

## Known Limitations

Event extraction involves human judgment about which events qualify
as option-space reducers versus noise. Two analysts extracting the same
dataset independently may produce slightly different CSVs.
Interrater reliability testing is the next methodological step before
formal publication.
