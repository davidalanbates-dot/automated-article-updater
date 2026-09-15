# Setup guide

This lets you run the article-update pipeline in Claude Code: research
agents draft verified BEFORE/AFTER edits, results get written to
`data/before_after.csv`, and pushed live into the shared Google Sheet.

## 1. Get repo access

Ask the repo owner to add you as a collaborator on
`davidalanbates-dot/automated-article-updater` (or clone it if it's
already been transferred to your org). Then, in Claude Code:

```
clone the repo davidalanbates-dot/automated-article-updater and cd into it
```

## 2. Get a Google Cloud service account key

Each person running this pipeline needs their own service account
(don't share keys between people — it's a real credential with write
access to the Sheet).

1. Go to https://console.cloud.google.com/, create a project (or reuse one) — free, no billing/credit card required.
2. Enable the Sheets API: https://console.cloud.google.com/apis/library/sheets.googleapis.com
3. Go to IAM & Admin → Service Accounts, create one (e.g. "sheet-writer").
4. Open it → Keys tab → Add Key → Create new key → JSON. This downloads a key file.
5. Copy the service account's email (looks like `sheet-writer@your-project.iam.gserviceaccount.com`).
6. Open the shared Sheet, click Share, add that email as **Editor**.

Ask whoever owns the Sheet for its link if you don't have it, or run
`ask David for the Medical Article Recency Updates sheet link` — it's
also linked from this repo's README.

## 3. Configure your local environment

Install dependencies once:

```
pip install -r scripts/requirements.txt
```

Set these two environment variables (add them to your shell profile so
they persist):

```
export SHEET_ID=<the sheet's ID, from its URL: /spreadsheets/d/THIS_PART/edit>
export SHEET_KEY_PATH=/path/to/your/downloaded-key.json
```

**Never commit the key file.** It's already covered by `.gitignore`
patterns (`*-key.json`, `secrets/`), but keep it somewhere outside the
repo entirely to be safe (e.g. your home directory or a password
manager's file storage).

## 4. Run it

In Claude Code, from the repo root:

```
Following docs/PROCESS.md, process these article URLs: <paste URLs>
```

Claude will research each article, draft verified Malaysia-first
edits, append them to `data/before_after.csv`, and you (or Claude) run:

```
python3 scripts/push_to_sheet.py
```

to sync the Sheet. Then commit and push the CSV change to git as
usual so the history stays in sync with the team.
