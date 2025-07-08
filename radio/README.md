# QRZ & POTA Logbook Tools

This project provides scripts to fetch, convert, and compare your logbook data from the QRZ Logbook API and the POTA (Parks on the Air) API.

## Prerequisites
- Python 3.x
- `requests` library (install with `pip install requests`)

## Overview of Workflow
1. **Fetch your POTA logbook and export to ADIF/CSV**
2. **Fetch your QRZ logbook and convert to CSV**
3. **Compare the two logs to find missing entries**

---

## 1. Fetch Your POTA Logbook

### Get Your POTA API Token
1. Go to [https://pota.app](https://pota.app) and log in.
2. Open the network console and navigate to somewhere like your hunter log.
3. Look for the XHR request for hunter log and find the Authorization in the headers. Copy that value (make sure there are no ...'s in it)
4. That will be used as your POTA_AUTH_TOKEN.

(Honestly I don't think it changes that much...)

### Set Your POTA API Token
**Linux/macOS:**
```bash
export POTA_AUTH_TOKEN=your-pota-api-key-here
```
**Windows (CMD):**
```cmd
set POTA_AUTH_TOKEN=your-pota-api-key-here
```
**Windows (PowerShell):**
```powershell
$env:POTA_AUTH_TOKEN="your-pota-api-key-here"
```

### Download and Export Your POTA Logbook
Run:
```bash
python pota-dl/get-log.py --keep-json
```
- This will fetch your POTA logbook and save it as `pota_hunter_log.json` and `pota_hunter_log.adif`.
- You can adjust options (see `--help` for all):
  - `--page-limit` to limit the number of pages fetched
  - `--unique-parks-only` to only include the first QSO for each unique park

---

## 2. Fetch Your QRZ Logbook

### Set Your QRZ API Key
Obtain your QRZ Logbook API key from your QRZ.com account.

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

### Download Your QRZ Logbook
Run:
```bash
cd qrz-dl
python qrz-fetch.py
```
- This will download your logbook as `qrz_logbook_download.adif`.

### Convert QRZ ADIF to CSV
Run:
```bash
python adif_to_csv.py qrz_logbook_download.adif qrz_logbook_download.csv
```
- This will create a CSV file sorted by QSO date.

---

## 3. Compare POTA and QRZ Logs

### Find Entries in POTA Log Not in QRZ Logbook
Run:
```bash
python find_missing_qrz.py
```
- This will compare `pota-dl/pota_hunter_log.csv` and `qrz-dl/qrz_logbook_download.csv` (by CALL and QSO_DATE) and output missing entries to `missing_from_qrz.csv`.

---

## 4. Run everything
```bash
python pota-dl/get-log.py && python qrz-dl/qrz-fetch.py && python adif_to_csv.py pota-dl/pota_hunter_log.adif pota-dl/pota_hunter_log.csv && adif_to_csv.py qrz-dl/qrz_logbook_download.adif qrz-dl/qrz_logbook_download.csv && python find_missing_qrz.csv
```
- Now you will have CSV files for both systems and a comparison that you can use to find out what is missing from QRZ that exists in POTA. 

---

## Script Reference

### pota-dl/get-log.py
- Downloads your POTA logbook using your API token.
- Outputs: `pota_hunter_log.json`, `pota_hunter_log.adif`, and optionally CSV.
- Run with `--help` for all options.

### qrz-dl/qrz-fetch.py
- Downloads your QRZ logbook as ADIF using your QRZ API key.

### adif_to_csv.py
- Converts an ADIF file (e.g., from QRZ) to CSV.
- Usage: `python adif_to_csv.py input.adif output.csv`

### find_missing_qrz.py
- Compares your POTA and QRZ logs (CSV) and outputs QSOs in POTA not found in QRZ (by CALL and QSO_DATE).
- Outputs: `missing_from_qrz.csv`

---

## Troubleshooting
- If you get an error about a missing API key, make sure the environment variable is set in your current shell.
- If the CSV is empty, check the debug output from `adif_to_csv.py` for field extraction issues.
- For more options, run each script with `--help` (where available).

## Todos and notes
- Do not hammer the API endpoints. These are run by volunteers and I'm sure those servers are not meant to handle tons of requests
- There is very little error handling on the endpoints. Inspect your outputs.

## Shout outs
https://github.com/adamfast/pota-hunter-log-adif -- This guy provided a great way for me to get started with the help of Cursor.

## License
MIT 