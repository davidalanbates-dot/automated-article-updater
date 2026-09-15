# Setup guide

This lets you run the article-update pipeline in Claude Code: research
agents draft verified BEFORE/AFTER edits, results get written to a
CSV, and pushed live into your own Google Sheet.

## 1. Get repo access

Ask the repo owner to add you as a collaborator on
`davidalanbates-dot/automated-article-updater` (or clone it if it's
already been transferred to your org). Then, in Claude Code:

```
clone the repo davidalanbates-dot/automated-article-updater and cd into it
```

## 2. Get the shared service account key

The team reuses one existing Google Cloud service account rather than
everyone setting up their own — you don't need to touch Google Cloud
Console at all. Ask David for the key file (`sa-key.json`) via a
secure channel (password manager, not Slack/email in plaintext) and
save it somewhere outside the repo, e.g. your home directory.

The service account's email is:

```
automated-article-json@automated-article-updater.iam.gserviceaccount.com
```

## 3. Create your own Google Sheet for your project

**Each person's project should live in its own Sheet — don't add your
articles into someone else's.** To set yours up:

1. Create a new, blank Google Sheet in your own Drive, named
   something like "Medical Article Recency Updates — <your name>".
2. Click **Share**, add the service account email above, and set its
   role to **Editor**.
3. Copy the Sheet's ID from its URL: `.../spreadsheets/d/THIS_PART/edit`.

## 4. Configure your local environment

Install dependencies once:

```
pip install -r scripts/requirements.txt
```

Set these environment variables (add them to your shell profile so
they persist):

```
export SHEET_ID=<your new sheet's ID>
export SHEET_KEY_PATH=/path/to/sa-key.json
export CSV_PATH=$(pwd)/data/<your-name>/before_after.csv
```

`CSV_PATH` keeps your dataset separate from everyone else's in the
shared repo — use a folder named after you or your project (e.g.
`data/jane/before_after.csv`), and create it with just the header row
(`Article URL,BEFORE,AFTER,Source,Date Updated,Notes`) before your
first run.

**Never commit the key file.** It's already covered by `.gitignore`
patterns (`*-key.json`, `secrets/`), but keep it outside the repo
entirely to be safe.

## 5. Run it

In Claude Code, from the repo root:

```
Following docs/PROCESS.md, process these article URLs: <paste URLs>
```

Claude will research each article, draft verified Malaysia-first
edits, append them to your `CSV_PATH`, and you (or Claude) run:

```
python3 scripts/push_to_sheet.py
```

to sync your Sheet. Then commit and push your CSV to git as usual so
its history stays in the shared repo alongside everyone else's.

## Revoking access

Because the key is shared, removing one person's access means
rotating the key for everyone (Cloud Console → the service account →
Keys → delete the old key, create a new one, redistribute). If you'd
rather avoid that blast radius for someone leaving the project
frequently, switch that person to their own service account instead
(same steps as this doc, but starting from a Cloud Console project of
their own).
