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
Console at all.

**Ask David directly for the key** (a JSON file, e.g. `sa-key.json`)
via a secure channel — a password manager's shared vault or an
encrypted note, not Slack/email in plaintext.

Once you have the file, **give it to Claude in your session** the same
way you'll hand over your Sheet ID later — either upload/attach the
file in chat, or tell Claude the path if you've already saved it
locally (e.g. "here's the service account key David sent me:
`~/Downloads/sa-key.json`"). Ask Claude to save it somewhere outside
this repo (e.g. your home directory, not the project folder) so it
never risks being committed:

```
Here's the shared service account key David sent me: [attach the JSON file]
Please save it outside this repo and set it up for scripts/push_to_sheet.py.
```

The service account's email (needed in the next step) is:

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

## 4. Install dependencies

```
pip install -r scripts/requirements.txt
```

**Never commit the key file.** It's already covered by `.gitignore`
patterns (`*-key.json`, `secrets/`), but keep it outside the repo
entirely to be safe.

## 5. Run it

In Claude Code, from the repo root:

```
Following docs/PROCESS.md, process these article URLs: <paste URLs>
```

Claude will research each article, draft verified Malaysia-first
edits, and append them to a CSV. When it's time to sync your Sheet,
run:

```
python3 scripts/push_to_sheet.py
```

The first time you run it, it'll walk you through what it needs and
save your answers so you don't have to repeat this:

- **Your Sheet ID** — paste the full URL of the Sheet you created in
  step 3, or just the ID; either works.
- **Your service account key path** — the local path where you (or
  Claude) saved the JSON file from step 2, e.g. `~/keys/sa-key.json`.
- **Your CSV path** — use something like `data/<your-name>/before_after.csv`
  so your dataset stays separate from everyone else's. If it doesn't
  exist yet, the script offers to create it with the right header row.

After that, `python3 scripts/push_to_sheet.py` on its own will sync
your Sheet using the saved answers. Then commit and push your CSV to
git as usual so its history stays in the shared repo alongside
everyone else's.

## Revoking access

Because the key is shared, removing one person's access means
rotating the key for everyone (Cloud Console → the service account →
Keys → delete the old key, create a new one, redistribute). If you'd
rather avoid that blast radius for someone leaving the project
frequently, switch that person to their own service account instead
(same steps as this doc, but starting from a Cloud Console project of
their own).
