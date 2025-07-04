import os
import requests

# Read QRZ Logbook API access key from environment variable
QRZ_API_KEY = os.getenv("QRZ_API_KEY")
if not QRZ_API_KEY:
    print("Error: QRZ_API_KEY environment variable not set.")
    exit(1)
# Example: QRZ_API_KEY = "ABCD-0A0B-1C1D-2E2F"

# Set your callsign and script name for the User-Agent header
USER_AGENT = "MyQrzFetchScript/1.0.0 (YOURCALLSIGN)"

# API endpoint
API_URL = "https://logbook.qrz.com/api"

# Prepare POST data for fetching all records (see docs for more options)
post_data = {
    "KEY": QRZ_API_KEY,
    "ACTION": "FETCH",
    "OPTION": "ALL,TYPE:ADIF"  # Fetch up to 10 records as ADIF
}

headers = {
    "User-Agent": USER_AGENT
}

response = requests.post(API_URL, data=post_data, headers=headers)

adif_filename = "qrz_logbook_download.adif"
csv_filename = "qrz_logbook_download.csv"

if response.status_code == 200:
    print("Saving ADIF to file...")
    with open(adif_filename, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"ADIF saved to {adif_filename}")
    print("To convert ADIF to CSV, run: python adif_to_csv.py qrz_logbook_download.adif qrz_logbook_download.csv")
else:
    print(f"Error: HTTP {response.status_code}")
    print(response.text)