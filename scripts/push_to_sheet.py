#!/usr/bin/env python3
"""Push data/before_after.csv to the shared Google Sheet, in place.

Requires a Google Cloud service account with the Sheets API enabled,
shared as an Editor on the target Sheet. See docs/SETUP.md for how to
create one.

Usage:
    python3 scripts/push_to_sheet.py

Configuration (env vars, or edit the defaults below):
    SHEET_ID       - the Google Sheet's ID (from its URL)
    SHEET_KEY_PATH - path to the service account JSON key
    CSV_PATH       - path to the CSV to push (defaults to data/before_after.csv)
"""
import csv
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHEET_ID = os.environ.get("SHEET_ID")
SHEET_KEY_PATH = os.environ.get("SHEET_KEY_PATH")
CSV_PATH = os.environ.get("CSV_PATH", os.path.join(REPO_ROOT, "data", "before_after.csv"))


def main():
    if not SHEET_ID or not SHEET_KEY_PATH:
        sys.exit(
            "Set SHEET_ID and SHEET_KEY_PATH environment variables first.\n"
            "  export SHEET_ID=<your sheet id from its URL>\n"
            "  export SHEET_KEY_PATH=/path/to/your/service-account-key.json\n"
            "See docs/SETUP.md for how to obtain these."
        )

    creds = service_account.Credentials.from_service_account_file(SHEET_KEY_PATH, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    meta = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    sheet_title = meta["sheets"][0]["properties"]["title"]

    # Clear first so a shrinking dataset doesn't leave stale rows behind
    service.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID,
        range=sheet_title,
        body={},
    ).execute()

    result = service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"{sheet_title}!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    print(f"Updated {result.get('updatedCells')} cells across {result.get('updatedRows')} rows in sheet '{sheet_title}'")


if __name__ == "__main__":
    main()
