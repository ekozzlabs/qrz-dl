import csv

# File paths
pota_file = "pota-dl/pota_hunter_log.csv"
qrz_file = "qrz-dl/qrz_logbook_download.csv"

# Read QRZ logbook into a set of tuples for fast lookup
qrz_set = set()
with open(qrz_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Only match on call and qso_date
        key = (
            row.get('call', '').strip().upper(),
            row.get('qso_date', '').strip(),
        )
        qrz_set.add(key)

# Read POTA log and find entries not in QRZ
missing = []
fieldnames = None
with open(pota_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        key = (
            row.get('CALL', '').strip().upper(),
            row.get('QSO_DATE', '').strip(),
        )
        if key not in qrz_set:
            missing.append(row)

# Output results
print(f"Found {len(missing)} entries in POTA log not in QRZ logbook.")
if not fieldnames:
    if missing:
        fieldnames = list(missing[0].keys())
    else:
        raise ValueError("No fieldnames found and no missing entries to infer from.")
with open("missing_from_qrz.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(missing)
print("Wrote missing entries to missing_from_qrz.csv") 