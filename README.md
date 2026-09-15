# Automated Article Updater

Keeps our medical articles current for content recency and YMYL (Your
Money Your Life) trust — Claude researches verified, Malaysia-first
statistics to refresh outdated or unsupported claims, at most 3
sentence changes per article, and tracks every change here.

- **Live sheet** (permanent link, always in sync with this repo):
  https://docs.google.com/spreadsheets/d/10fgkAP5dtrVSs0arpRj_VXO5NFPbpFwaYbrYdVCdaqo/edit
- **Source of truth**: `data/before_after.csv` (columns: Article URL,
  BEFORE, AFTER, Source, Date Updated, Notes)

## For teammates: run this yourself

See [`docs/SETUP.md`](docs/SETUP.md) to get a Google Cloud service
account key and repo access, then in Claude Code:

```
Following docs/PROCESS.md, process these article URLs: <paste URLs>
```

The rules Claude follows (Malaysia-first sourcing, 3-sentence cap,
writing style, workflow) are documented in
[`docs/PROCESS.md`](docs/PROCESS.md) — update that file if the process
needs to change, rather than re-explaining it in chat each time.

## Repo layout

```
data/before_after.csv   - the full dataset (source of truth)
docs/PROCESS.md         - the methodology Claude follows
docs/SETUP.md           - one-time setup for a new contributor
scripts/push_to_sheet.py - syncs the CSV to the live Google Sheet
```
