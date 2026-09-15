# Article update process

This is the methodology Claude should follow when processing a new
batch of article URLs for this project. Point Claude at this file
(`Following docs/PROCESS.md, process these URLs: ...`) rather than
re-explaining the rules each time.

## Goal

Update medical articles for content recency and YMYL (Your Money Your
Life) trust — Google's term for content that can affect health or
financial wellbeing, which needs high accuracy and current sourcing.

## Hard constraints

1. **At most 3 sentence changes or additions per article.** Fewer is
   fine and often better — don't pad to hit 3.
2. **Every edit needs a verified fact, stat, or study** — never
   fabricate or approximate a number. If you can't verify something,
   drop that candidate rather than guess.
3. **Malaysia-specific sourcing first.** Check in this order before
   ever falling back to global data:
   - Malaysia Ministry of Health (MOH/KKM) / National Health and
     Morbidity Survey (NHMS) / Institute for Public Health (IKU)
   - Department of Statistics Malaysia (DOSM)
   - National disease registries: National Renal Registry, National
     Cancer Registry, National Stroke Registry, NCVD (cardiovascular)
   - Malaysian Clinical Practice Guidelines (CPG)
   - Malaysian medical journals (Med J Malaysia, Malaysian Journal of
     Medical Sciences, IIUM Medical Journal Malaysia, etc.)
   - Malaysian university hospital studies (UKM, UM, USM, IIUM, UPM,
     HKL)

   Only fall back to WHO/global/regional data if a genuine, thorough
   search turns up nothing Malaysia-specific for that claim — and when
   you do, say so explicitly (mark it and explain why no local data
   exists). Some topics genuinely have no Malaysian data at all (this
   happened with leg cramps and shingles incidence in the first run) —
   that's a legitimate finding, not something to force around.

4. **If nothing reputable exists for an important claim, flag it and
   move on** — don't block the whole batch on one hard case. Collect
   flagged items and report them at the end.

## Writing style

- **No em dashes anywhere.** They read as an AI tell. Use commas or
  restructure the sentence instead.
- **No filler openers** — avoid "In fact,", "Notably,", "It's worth
  noting that,".
- **Vary the sentence structure.** Attribution can lead the sentence
  ("Data from X show...", "A 2022 study found...", "X's own figures
  indicate...") but don't force literally every sentence into the same
  "According to X, ..." template — that reads mechanically. If an
  article gets more than one edit, make sure each one opens
  differently from the others (a real feedback point from the first
  run: two edits in the same article both starting "The WHO's GLOBOCAN
  2024..." read badly together).
- Match the tone and reading level of the original article. Keep each
  edit to a natural single sentence, or two short sentences if it
  matches an existing list-item (term: definition) pattern in that
  article.

## Cross-article consistency

Before finalizing, check whether a new edit contradicts a stat already
used elsewhere in your own CSV (`$CSV_PATH`) — e.g., don't have one
article say colorectal cancer is Malaysia's #1 cancer in men while
another, using more current GLOBOCAN data, says it's #2. When in
doubt, grep your CSV for the topic first. Each contributor works
against their own CSV and Sheet (see `docs/SETUP.md`), so this check
only needs to cover your own dataset, not everyone else's in the repo.

## Workflow

1. **Dedupe the URL list** the user gives you.
2. **One research agent per article**, launched via the `Agent` tool
   (general-purpose, `run_in_background: true`), so articles are
   researched in parallel. Batch launches in groups of ~8–10 to avoid
   hitting session rate limits; wait for a batch to finish before
   launching the next if you see rate-limit failures.
3. Each agent should return structured JSON: `article_url`, a list of
   `edits` (`before`, `after`, `source_name`, `source_url`,
   `malaysia_specific`, `notes`), and an `unresolved` field for
   anything it couldn't verify.
4. **Compile results into your `$CSV_PATH`** (e.g.
   `data/<your-name>/before_after.csv` — see `docs/SETUP.md`) —
   columns are `Article URL, BEFORE, AFTER, Source, Date Updated,
   Notes`. Leave `BEFORE` blank when an edit is a new addition rather
   than a replacement. Combine `source_name` and `source_url` into one
   `Source` cell separated by ` | `.
5. **Push to your Sheet**: `python3 scripts/push_to_sheet.py` (needs
   `SHEET_ID`, `SHEET_KEY_PATH`, and `CSV_PATH` set — see
   `docs/SETUP.md`). Each contributor has their own Sheet — never
   point your `SHEET_ID` at someone else's.
6. **Commit and push to git** so your CSV (the real source of truth
   for your Sheet) stays in the shared repo alongside everyone else's.
7. **Report flagged items** to the user: anything where no
   Malaysia-specific data exists, any internal-consistency corrections
   made, and any low-confidence calls worth a second look.

## Example research agent prompt

Adapt this per article (see git history around the first ~30 articles
for many real examples if you want more references):

```
You are helping update a medical article on a Malaysian hospital
website for content recency and YMYL trust.

ARTICLE URL: <url>

TASK:
1. Fetch the article content with WebFetch.
2. Identify up to 3 sentences that are the best candidates to update:
   vague claims lacking data, outdated/missing epidemiological stats,
   or claims that would benefit from a concrete, current, verifiable
   statistic. It's fine to ADD a new sentence with a useful stat
   instead of replacing one (then "before" is empty).
3. Strongly prefer Malaysia-specific data (see sourcing hierarchy in
   docs/PROCESS.md). Only fall back to global data if none exists,
   and say so explicitly.
4. If producing more than one edit, make sure each starts differently
   from the others.
5. No em dashes, no filler openers, vary phrasing naturally.
6. Cap: at most 3 edits for this article.

OUTPUT: JSON only —
{
  "article_url": "...",
  "edits": [
    {"before": "...", "after": "...", "source_name": "...",
     "source_url": "...", "malaysia_specific": true/false,
     "notes": "..."}
  ],
  "unresolved": "..."
}
```
