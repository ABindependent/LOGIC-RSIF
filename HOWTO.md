# HOW TO RUN THIS

## Requirements
- Python 3.6 or higher
- No additional packages needed

## Step 1 — Get the files
git clone https://github.com/ABindependent
cd ABindependent

Or download the ZIP from the green "Code" button on GitHub and unzip it:
https://github.com/ABindependent

---

## Step 2 — Run the detection harness
python3 logic_harness_clean.py boeing_events_multisource.csv unitedhealth_events_extracted_FINAL.csv

This runs the Boeing and UHC datasets through the harness and prints the full quarterly state vector, phase classification, FAC detection, and cross-dataset comparison.

To also run Wells Fargo, open `logic_harness_clean.py` in any text editor, scroll to the bottom, and add:
```python
run("wellsfargo_events_extracted.csv", "WELLS FARGO (2009-2020)")
```

---

## Step 3 — Verify the extraction methodology
python3 validate_extraction.py

This runs six computational checks against all three CSV files and confirms the datasets reflect chronological extraction rather than narrative curation. Expected output: all checks PASS.

---

## Step 4 — Inspect the data directly
The three CSV files are plain text. Open them in Excel, Google Sheets, or any text editor. Every event has a source URL in the final column — click through to verify against the original document.

---

## What you're looking at

| File | What it does |
|---|---|
| `logic_harness_clean.py` | Runs the detection engine |
| `validate_extraction.py` | Audits the extraction methodology |
| `METHODOLOGY.md` | Explains the framework |
| `EXTRACTION_CRITERIA.md` | Documents the coding schema |
| `boeing_events_multisource.csv` | Boeing dataset — 30 events, 6 sources |
| `unitedhealth_events_extracted_FINAL.csv` | UHC dataset — 43 events, 5 sources |
| `wellsfargo_events_extracted.csv` | Wells Fargo dataset — 32 events, 6 sources |

---

## Questions or issues
Contact: abued@proton.me
