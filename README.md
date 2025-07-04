# QRZ Logbook Fetch & ADIF to CSV

This project provides scripts to fetch your logbook data from the QRZ Logbook API and convert it from ADIF format to CSV.

## Prerequisites
- Python 3.x
- `requests` library (install with `pip install requests`)

## Usage

### 1. Set your QRZ API Key
Obtain your QRZ Logbook API key from your QRZ.com account.

Set it as an environment variable:

**Linux/macOS:**
```bash
export QRZ_API_KEY=your-key-here
```

**Windows (CMD):**
```cmd
set QRZ_API_KEY=your-key-here
```

**Windows (PowerShell):**
```powershell
$env:QRZ_API_KEY="your-key-here"
```

### 2. Fetch your logbook from QRZ
Run:
```bash
python qrz-fetch.py
```
This will download your logbook as `qrz_logbook_download.adif`.

### 3. Convert ADIF to CSV
Run:
```bash
python adif_to_csv.py qrz_logbook_download.adif qrz_logbook_download.csv
```
This will create a CSV file sorted by QSO date.

### 4. Convert CSV to ADIF
Run:
```bash
python csv_to_adif.py input.csv output.adif
```
This will create an ADIF file from a CSV file.

## Customization
- To change which fields are extracted, edit the `fields` list in `adif_to_csv.py`.
- The CSV is sorted by `qso_date` by default.

## Troubleshooting
- If you get an error about the API key, make sure the environment variable is set in your current shell.
- If the CSV is empty, check the debug output from `adif_to_csv.py` for field extraction issues.

## License
MIT 