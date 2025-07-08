import sys
import re
import csv
import html

if len(sys.argv) != 3:
    print(f"Usage: python {sys.argv[0]} input.adif output.csv")
    sys.exit(1)

adif_filename = sys.argv[1]
csv_filename = sys.argv[2]

with open(adif_filename, "r", encoding="utf-8") as f:
    adif_text = f.read()

# Extract only the ADIF portion after 'ADIF='
adif_start = adif_text.find('ADIF=')
if adif_start != -1:
    adif_text = adif_text[adif_start + len('ADIF='):]
adif_text = html.unescape(adif_text)
# Split into records on <eor> (case-insensitive)
qsos = re.split(r'<eor>', adif_text, flags=re.IGNORECASE)
qsos = [qso.strip() for qso in qsos if qso.strip()]

print(qsos[0])
print(f"Total QSO records found: {len(qsos)}")
if qsos:
    print("First QSO record (repr):")
    print(repr(qsos[0]))
    tags = re.findall(r'<([^:>]+):', qsos[0])
    print("Tags found in first QSO:", tags)
    # Use the tags as the fields, in order of appearance
    fields = tags
    print(f"Detected fields for CSV: {fields}")
else:
    fields = []

def extract_field(qso, field):
    # Allow for optional whitespace/newlines after >
    pattern = rf"<{field}:(\d+)[^>]*>\s*([^\n<]*)"
    match = re.search(pattern, qso, re.IGNORECASE)
    if match:
        value = match.group(2).strip()
        print(f"Extracted {field}: {value} (pattern: {pattern})")
        return value
    else:
        print(f"Extracted {field}: NOT FOUND (pattern: {pattern})")
        return ""

with open(csv_filename, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fields)
    all_rows = []
    for idx, qso in enumerate(qsos):
        row = [extract_field(qso, field) for field in fields]
        all_rows.append(row)
        if idx == 0:
            print("Extracted row for first QSO:")
            print(row)
    # Sort by qso_date (index 1)
    all_rows.sort(key=lambda r: r[1])
    for row in all_rows:
        writer.writerow(row)

print(f"CSV saved to {csv_filename}") 