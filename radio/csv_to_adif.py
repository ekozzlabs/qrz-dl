import sys
import csv

if len(sys.argv) != 3:
    print(f"Usage: python {sys.argv[0]} input.csv output.adif")
    sys.exit(1)

csv_filename = sys.argv[1]
adif_filename = sys.argv[2]

with open(csv_filename, "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    qsos = list(reader)
    fields = reader.fieldnames if reader.fieldnames is not None else []
    if not fields:
        print("Warning: No fields detected in CSV header.")
    else:
        print(f"Detected fields: {fields}")

with open(adif_filename, "w", encoding="utf-8") as f:
    for qso in qsos:
        for field in fields:
            value = qso.get(field, "").strip()
            if value:
                f.write(f"<{field}:{len(value)}>{value}\n")
        f.write("<eor>\n\n")

print(f"ADIF saved to {adif_filename}") 