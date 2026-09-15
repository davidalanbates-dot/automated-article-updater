# Automated Article Updater

Keeps our medical articles current for content recency and YMYL (Your
Money Your Life) trust — Claude researches verified, Malaysia-first
statistics to refresh outdated or unsupported claims, at most 3
sentence changes per article, and tracks every change here.

- **David's sheet** (permanent link, always in sync with `data/before_after.csv`):
  https://docs.google.com/spreadsheets/d/10fgkAP5dtrVSs0arpRj_VXO5NFPbpFwaYbrYdVCdaqo/edit
- Each contributor runs their own batches into their own Sheet and
  their own `data/<name>/before_after.csv` — see `docs/SETUP.md`. This
  repo hosts everyone's dataset and the shared tooling/process, but
  Sheets are kept one-per-project rather than shared.

## For teammates: run this yourself

See [`docs/SETUP.md`](docs/SETUP.md) to get the shared service account
key and repo access, then in Claude Code:

```
Following docs/PROCESS.md, process these article URLs: <paste URLs>
```

The rules Claude follows (Malaysia-first sourcing, 3-sentence cap,
writing style, workflow) are documented in
[`docs/PROCESS.md`](docs/PROCESS.md) — update that file if the process
needs to change, rather than re-explaining it in chat each time.

## Repo layout

```
data/before_after.csv    - David's dataset (source of truth for his Sheet)
data/<name>/before_after.csv - each other contributor's own dataset
docs/PROCESS.md          - the methodology Claude follows
docs/SETUP.md            - one-time setup for a new contributor
scripts/push_to_sheet.py - syncs a CSV to its Google Sheet (reads
                           SHEET_ID / SHEET_KEY_PATH / CSV_PATH from env)
```
