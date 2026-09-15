#!/usr/bin/env python3
"""Push a before/after CSV to its Google Sheet, in place.

Requires a Google Cloud service account with the Sheets API enabled,
shared as an Editor on the target Sheet. See docs/SETUP.md for how to
get one.

Usage:
    python3 scripts/push_to_sheet.py

Configuration, checked in this order:
    1. Environment variables: SHEET_ID, SHEET_KEY_PATH, CSV_PATH
    2. Values saved from a previous run (scripts/.push_config.json,
       not committed to git)
    3. If still missing, you'll be prompted for them interactively,
       with the option to save your answers for next time.
"""
import csv
import json
import os
import re
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CSV_PATH = os.path.join(REPO_ROOT, "data", "before_after.csv")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".push_config.json")

SHEET_ID_EXAMPLE = "1aBcDeFGhiJKLmnoPQRstuVwxYZ1234567890abcdEFghij"
SHEET_URL_EXAMPLE = f"https://docs.google.com/spreadsheets/d/{SHEET_ID_EXAMPLE}/edit"


def load_saved_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print(f"(Could not save config for next time: {e})")


def extract_sheet_id(raw):
    """Accept either a bare Sheet ID or a full Sheet URL and return the ID."""
    raw = raw.strip()
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", raw)
    return match.group(1) if match else raw


def prompt_for_value(name, example, help_text):
    print(f"\n{name} is not set.")
    print(help_text)
    print(f"  Example: {example}")
    value = input(f"Enter your {name}: ").strip()
    if not value:
        sys.exit(f"{name} is required. Set it as an environment variable, or re-run and enter it when prompted.")
    return value


def prompt_with_default(name, default, help_text):
    print(f"\n{name} is not set.")
    print(help_text)
    print(f"  Default (press Enter to accept): {default}")
    value = input(f"Enter your {name} [{default}]: ").strip()
    return value or default


def resolve_config():
    saved = load_saved_config()
    changed = False

    sheet_id = os.environ.get("SHEET_ID") or saved.get("SHEET_ID")
    if not sheet_id:
        raw = prompt_for_value(
            "SHEET_ID",
            f"{SHEET_ID_EXAMPLE}\n  (this is the long ID in your Sheet's URL, e.g. {SHEET_URL_EXAMPLE}"
            " -- you can also just paste the full URL and it'll be extracted for you)",
            "The ID of the Google Sheet you want to push to.",
        )
        sheet_id = extract_sheet_id(raw)
        changed = True

    key_path = os.environ.get("SHEET_KEY_PATH") or saved.get("SHEET_KEY_PATH")
    if not key_path:
        key_path = prompt_for_value(
            "SHEET_KEY_PATH",
            "/Users/yourname/keys/sa-key.json",
            "Path to the shared service account JSON key file (see docs/SETUP.md).",
        )
        changed = True

    csv_path = os.environ.get("CSV_PATH") or saved.get("CSV_PATH")
    if not csv_path:
        csv_path = prompt_with_default(
            "CSV_PATH",
            DEFAULT_CSV_PATH,
            "The CSV file to push. If this isn't your own project's CSV\n"
            "  (e.g. data/<your-name>/before_after.csv), make sure to change it --\n"
            "  the default below is the shared repo's main dataset, and pushing your\n"
            "  own edits there would push them into someone else's Sheet by mistake.",
        )
        changed = True

    if changed:
        answer = input("\nSave these values so you don't have to re-enter them next time? [Y/n] ").strip().lower()
        if answer in ("", "y", "yes"):
            save_config({"SHEET_ID": sheet_id, "SHEET_KEY_PATH": key_path, "CSV_PATH": csv_path})
            print(f"Saved to {CONFIG_PATH} (not committed to git).")

    return sheet_id, key_path, csv_path


CSV_HEADER = ["Article URL", "BEFORE", "AFTER", "Source", "Date Updated", "Notes"]


def main():
    sheet_id, sheet_key_path, csv_path = resolve_config()

    if not os.path.exists(csv_path):
        answer = input(
            f"\n{csv_path} doesn't exist yet. Create it now with just the header row? [Y/n] "
        ).strip().lower()
        if answer not in ("", "y", "yes"):
            sys.exit("Nothing to push -- create the CSV first, or point CSV_PATH at an existing file.")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADER)
        print(f"Created {csv_path} with header row.")

    if not os.path.exists(sheet_key_path):
        sys.exit(
            f"Can't find a key file at {sheet_key_path}.\n"
            "Double check the path, or ask David for the shared service account key if you don't have it yet\n"
            "(see docs/SETUP.md). Delete scripts/.push_config.json if you need to re-enter your settings."
        )

    try:
        creds = service_account.Credentials.from_service_account_file(sheet_key_path, scopes=SCOPES)
    except (ValueError, KeyError) as e:
        sys.exit(f"{sheet_key_path} doesn't look like a valid service account key file: {e}")
    service = build("sheets", "v4", credentials=creds)

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    meta = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheet_title = meta["sheets"][0]["properties"]["title"]

    # Clear first so a shrinking dataset doesn't leave stale rows behind
    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range=sheet_title,
        body={},
    ).execute()

    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{sheet_title}!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    print(f"Updated {result.get('updatedCells')} cells across {result.get('updatedRows')} rows in sheet '{sheet_title}'")


if __name__ == "__main__":
    main()
