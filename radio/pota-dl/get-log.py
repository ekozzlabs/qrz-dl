# Adopted from https://github.com/pota-app/pota-hunter-logger/blob/main/pota_hunter_logger.py
# Modified to use argparse for command line arguments instead of click
import argparse
import os
import datetime
import json
import requests
import time
import math


def logbook_page(auth_token, page=1, size=25):
    """Fetches a page of the logbook from the POTA API."""

    url = f'https://api.pota.app/user/logbook?hunterOnly=1&page={page}&size={size}'

    response = requests.get(
        url,
        headers={
            'Authorization': auth_token,
        },
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    return {
        'count': data['count'],
        'page': page,
        'size': size,
        'data': data['entries'],
    }


def retrieve_my_log(qsos, auth_token, page_limit=None, wait_between_pages=2):
    first_page = logbook_page(auth_token, page=1, size=25) #leave this as 25, anything else will result in missing QSOs
    if not first_page:
        print("Failed to fetch first page. Exiting.")
        return qsos
    qsos.extend(first_page['data'])

    total_pages = math.ceil(first_page['count'] / first_page['size'])
    max_pages = page_limit if page_limit else total_pages
    
    print(f'Expecting to fetch {first_page["count"]} QSOs from {total_pages} pages.')
    if page_limit:
        print(f'Limited to fetching {page_limit} pages.')
    
    for page in range(2, min(total_pages + 1, max_pages + 1)):
        if page_limit and page > page_limit:
            print(f"Reached page limit: {page_limit}. Stopping.")
            break

        print(f"..Page {page} of {max_pages}")
        logbook = logbook_page(auth_token, page=page, size=25)
        if logbook and logbook['data']:
            qsos.extend(logbook['data'])
        else:
            print(f"No data for page {page}")

        if page < max_pages:  # Don't wait after the last page
            print(f'  Waiting {wait_between_pages} seconds before retrieving the next page...')
            time.sleep(wait_between_pages)

    return qsos


def write_adif(qsos, filename):
    """
    Write a list of QSO dictionaries to an ADIF file.
    
    Args:
        qsos: List of dictionaries containing QSO data
        filename: Output ADIF file path
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # Write ADIF header
        f.write("ADIF Export\n")
        f.write("<ADIF_VER:5>3.1.0\n")
        f.write("<PROGRAMID:18>POTA Hunter Logger Export Tool\n")
        f.write("<EOH>\n\n")

        # Write each QSO
        for qso in qsos:
            for field, value in qso.items():
                if value is None or value == "":
                    continue

                # Convert value to string and get its length
                value_str = str(value)
                length = len(value_str)

                # Write the field in ADIF format: <FIELDNAME:LENGTH>VALUE
                f.write(f"<{field.upper()}:{length}>{value_str} ")

            # End of record
            f.write("<EOR>\n")

    print(f"Wrote {len(qsos)} QSOs to {filename}")


def main(auth_token, page_limit=None, wait_between_pages=2, keep_json=False, unique_parks_only=False, json_to_adif=False):
    qsos = []

    if not json_to_adif:
        print("Fetching QSOs from POTA API...")
        qsos = retrieve_my_log(qsos, auth_token, page_limit, wait_between_pages)
    else:
        print("Loading QSOs from local JSON file...")
        with open('pota_hunter_log.json', 'r', encoding='utf-8') as f:
            qsos = json.load(f)

    print(f"Total QSOs fetched from API: {len(qsos)}")

    # Filter for unique parks if requested
    if unique_parks_only:
        seen_parks = set()
        unique_qsos = []
        for qso in qsos:
            park_ref = qso.get('reference')  # Adjust field name as needed based on API response
            if park_ref and park_ref not in seen_parks:
                seen_parks.add(park_ref)
                unique_qsos.append(qso)
        qsos = unique_qsos
        print(f"Filtered to {len(qsos)} QSOs with unique parks")
    
    if keep_json:
        with open('pota_hunter_log.json', 'w', encoding='utf-8') as f:
            json.dump(qsos, f, indent=4)
        print("Saved raw JSON data to pota_hunter_log.json")
    
    # modify the structure from POTA API to match ADIF format
    adif_qsos = []
    skipped = 0
    skipped_qsos = []
    for qso in qsos:
        try:
            qso_time = datetime.datetime.fromisoformat(qso['qsoDateTime'])
            adif_qsos.append({
                'call': qso['station_callsign'].upper(),
                'mode': qso['loggedMode'].upper(),
                'qso_date': qso_time.strftime('%Y%m%d'),
                'time_on': qso_time.strftime('%H%M%S'),
                'band': qso['band'],
                'station_callsign': qso['worked_callsign'].upper(),
                'pota_ref': qso['reference'],
            })
        except Exception as e:
            skipped += 1
            skipped_qsos.append(qso)
            print(f"Skipping QSO due to error: {e}\nQSO: {qso}")
    print(f"QSOs written to ADIF: {len(adif_qsos)}")
    if skipped:
        print(f"Skipped {skipped} QSOs due to missing or invalid data.")
        with open('skipped_qsos.json', 'w', encoding='utf-8') as f:
            json.dump(skipped_qsos, f, indent=4)
        print("Saved skipped QSOs to skipped_qsos.json")

    write_adif(adif_qsos, 'pota_hunter_log.adif')


if __name__ == '__main__':
    # Default parameters
    AUTH_TOKEN = os.environ.get('POTA_AUTH_TOKEN', '')  # Read from environment variable
    PAGE_LIMIT = None  # e.g., 5
    WAIT_BETWEEN_PAGES = 2
    KEEP_JSON = False
    UNIQUE_PARKS_ONLY = False
    JSON_TO_ADIF = False

    parser = argparse.ArgumentParser(description='Download and convert POTA logbook data.')
    parser.add_argument('--auth-token', type=str, default=AUTH_TOKEN, help='POTA API authentication token (default: from POTA_AUTH_TOKEN environment variable)')
    parser.add_argument('--page-limit', type=int, default=PAGE_LIMIT, help='Maximum number of pages to fetch (default: fetch all)')
    parser.add_argument('--wait-between-pages', type=float, default=WAIT_BETWEEN_PAGES, help='Seconds to wait between API requests (default: 2)')
    parser.add_argument('--keep-json', action='store_true', default=KEEP_JSON, help='Save raw JSON data to pota_hunter_log.json')
    parser.add_argument('--unique-parks-only', action='store_true', default=UNIQUE_PARKS_ONLY, help='Only include the first QSO for each unique park')
    parser.add_argument('--json-to-adif', action='store_true', default=JSON_TO_ADIF, help='Convert JSON to ADIF format (no HTTP calls)')

    args = parser.parse_args()

    if not args.auth_token:
        print("Error: No POTA API authentication token provided. Set the POTA_AUTH_TOKEN environment variable or use --auth-token.")
        exit(1)

    main(
        args.auth_token,
        args.page_limit,
        args.wait_between_pages,
        args.keep_json,
        args.unique_parks_only,
        args.json_to_adif
    )
