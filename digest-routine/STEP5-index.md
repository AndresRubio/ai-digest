# STEP 5 — Update the index and close the run

## 5.1 `site/index.html`

Four edits, in order:

**a. Meta line** → `<div class="meta">Auto-generated &middot; Last updated: YYYY-MM-DD</div>`

**b. The `changed-today` box.** Replace its entire contents — it describes today only,
not history:

```html
      <div class="changed-today">
        <strong>What changed today (YYYY-MM-DD)</strong>
        <ul>
          <li><a href="topics/slug.html">Topic name</a> &mdash; one line naming the
              concrete thing that changed, with its numbers.</li>
        </ul>
      </div>
```

One `<li>` per topic touched in STEP 3, in the same order the topics appear on the page.

**c. Topic descriptions.** If a topic's remit shifted — a new sub-section, a new recurring
thread — extend that topic's `<li>` description in the `<h2>Topics</h2>` list. Most runs
change nothing here.

**d. Daily logs list.** Prepend `<li><a href="daily/YYYY-MM-DD.html">YYYY-MM-DD</a></li>`
at the top of the `<h2>Daily logs</h2>` list. Skip this on a quiet day, since STEP 4
wrote no page.

## 5.2 Close the run

**Append to `state/processed.json`** every message id STEP 1 retained — including ones
whose stories were rejected in STEP 2, since they have been dealt with and must not be
re-examined. Shape:

```json
{
  "messages": [
    {
      "messageId": "1a06c8cb2ece21ca",
      "account": "primary-inbox",
      "sender": "thebatch@deeplearning.ai",
      "subject": "Software Engineering Fundamentals Remain Essential…",
      "date": "2026-08-27",
      "outcome": "3 stories",
      "processedOn": "2026-09-03"
    }
  ]
}
```

`outcome` is either `"N stories"` or a short reason: `"dropped: event promo"`,
`"dedup: covered 2026-08-26"`.

**Update account state in `sources.json`.** For any account that ran on a backfill window:
if every message inside that window has now been processed, set
`"backfillState": "done"` and add `"backfillCompletedOn": "YYYY-MM-DD"`. If messages
remain (the per-run cap was hit), leave it `pending` and record the remaining count so the
next run continues. Also append any newly discovered account that STEP 1 found.

**Append one line to `state/run-log.md`:**

```
2026-09-03  6 stories  |  5 messages scanned across 1 account  |  model-releases, agents, industry-and-business
```

## 5.3 Verify before finishing

Check and report, rather than assuming:

- every file touched still parses as HTML, and its sidebar matches other pages at the
  same depth once each page's own `class="active"` marker is normalized away
- every timeline entry *added this run* has a date, a label, a summary, and at least one
  source (older entries may legitimately carry a plain-text source with no link — do not
  flag those)
- **no `mail.google.com` URL appears anywhere in `site/`**, and no Gmail address
  appears in any tracked file (`grep -rE 'mail\.google\.com|@gmail\.com' site/`
  must come back empty) — the site is published publicly, so this is a hard gate, not a
  style note
- **no mailbox identifier appears in any tracked file.** Derive the local-parts from
  `digest-routine/sources.json` (gitignored, so the literals never enter the repo) and grep
  the tracked tree for them:
  `python3 -c "import re;s=open('digest-routine/sources.json').read();lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)};lp|={p.replace('.','') for p in lp};print('|'.join(sorted(p for p in lp if len(p)>4)))"`
  then `git grep -InEi "<that pattern>"` must come back empty. This catches what the
  `@gmail.com` gate above cannot: a bare mailbox name with no domain attached, which is how
  20 identifiers reached the public repo before 2026-09-16. If `sources.json` is absent,
  report the check as **skipped**, never as passed.
- **no paragraph is a wall of text**: every touched topic page keeps its `Current state`
  as `<p>` paragraphs with the older cycles inside `<details>`, and no `<p>` anywhere on
  the page runs past ~350 words. A one-line check:
  `python3 -c "import re,sys;[print(f,len(re.sub(r'<[^>]+>','',p).split())) for f in sys.argv[1:] for p in re.findall(r'<p>(.*?)</p>',open(f).read(),re.S) if len(re.sub(r'<[^>]+>','',p).split())>350]" site/topics/*.html`
  should print nothing
- the index date, the `changed-today` box, the daily-log link, and each **touched** page's
  `Last updated` all agree with the run date — untouched topic pages must keep their
  previous date, so a stale-looking meta on a page no story routed to is correct
- `processed.json` grew by exactly the number of messages STEP 1 retained

If any check fails, fix it before reporting the run complete. State plainly what ran and
what did not.
