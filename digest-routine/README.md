# AI digest routine

Builds `../ai-digest/` — a static AI-news knowledge base — from newsletter email in
Gmail. Runs weekday mornings.

## How it runs

A scheduled task fires a thin prompt: *work in this folder, read `STEP1-ingest.md`
through `STEP5-index.md` in order, follow them exactly, do not modify Gmail.* All the
logic lives in those five files, so **editing the routine never means editing the
scheduled task.**

| File | Does |
|---|---|
| `STEP1-ingest.md` | Finds every connected Gmail account, scans unread + last 7 days, filters, fetches bodies |
| `STEP2-extract.md` | Splits newsletters into discrete stories, applies the quality bar, de-duplicates |
| `STEP3-route.md` | Routes stories to topic pages and rewrites those pages' prose |
| `STEP4-log.md` | Writes `ai-digest/daily/YYYY-MM-DD.html` |
| `STEP5-index.md` | Updates `ai-digest/index.html`, closes out the ledger, verifies |

## Editing what gets picked up

Everything lives in `sources.json`.

- **Tier A** — priority sources, each scanned with its own `from:` query. Entries marked
  `"status": "not-yet-arriving"` are subscriptions that don't reach Gmail yet
  (MarkTechPost, the Substacks, Ona, TLDR AI…). They are queried anyway, so the day one
  of them starts landing it is picked up with no change here.
- **Tier B** — frontier-lab announcements. Kept only when the story clears the bar.
- **Tier C** — vendor product newsletters. Kept only for a genuine release.
- **`drop`** — checked before anything else: invoices, security alerts, GitHub app
  permission mails, Discord pings, event promotion. Matches here are never even fetched.

To add a newsletter, add it to the right tier. To stop one, remove it or move it to
`drop.senders`.

## Sources are never links into a mailbox

The site is published publicly at <https://andresrubio.github.io/ai-digest/> by the
`pages.yml` GitHub Action on every push to `main`. Two consequences, both enforced as
hard gates in STEP 5.3:

- **Newsletter sources are cited as plain text** — `TLDR AI (Sep 11)`, not a link. A
  `mail.google.com` URL leaks the account address *and* points a stranger at a private
  message, so the routine no longer builds one (STEP 1.6). Message ids live only in
  `state/processed.json`, which is all de-duplication ever needed them for.
- **Where a newsletter names a canonical public URL** for the artifact — a vendor blog,
  an arXiv abstract, a model card — link that. It is the better citation regardless: a
  reader can open it.

`digest-routine/sources.json` is **gitignored**, because `accounts[].email` has to hold
the real Gmail address for STEP 1.1's connector cross-check. The full allowlist is
published as `sources.example.json` with the account identity redacted from both the
`accounts[].email` field and the prose `note` fields, so the routine stays reviewable.
Until 2026-09-16 the notes still named the mailboxes; that is what the identity gate in
STEP 5.3 and the `pages.yml` guard now exist to prevent recurring.

## Which inbox this reads

**`<primary-inbox>`, and only that one.** TLDR arrives at the undotted alias
`<undotted alias>`; Gmail treats both as the same mailbox.

A previous account (`<retired-inbox>`) was retired on 2026-09-08 and removed from
`sources.json` on purpose. The routine will not scan it and will not report it as missing.
Stories already ingested from it stay in the wiki, cited by newsletter name. (They
originally carried Gmail permalinks into that mailbox; those were removed site-wide on
2026-09-14 along with every other one — see *Sources are never links into a mailbox*
below.)

## Adding an inbox

The routine still supports several inboxes if you ever want one. **One step, and it's
yours:** in Claude, add another Gmail connector and sign in to that account. Only you can do this — it needs the account's own credentials, so the routine
cannot add an inbox for you.

That's it. You do not need to edit this folder. The next run notices a connector that
isn't in `accounts`, appends it with `"backfill": "30d"` / `"backfillState": "pending"`,
and gives the new inbox **one catch-up pass over its last month** before settling it into
the normal unread + last-7-days window like every other account. The daily log says which
window each account ran on.

If that month exceeds the 25-message-per-run cap, the backfill isn't marked done — the
remainder carries into the next run until the window is exhausted. So a busy new inbox may
take two or three mornings to fully absorb, and each daily log will tell you how many
messages are still outstanding.

Nothing else changes. STEP 1 discovers the available Gmail read tools at run time, scans
every account it finds, and tags each story with the inbox it arrived at. Stories are
cited by newsletter name and date; no mailbox link is ever emitted.

Two behaviours worth knowing about once more than one inbox is connected:

- **A newsletter that reaches both inboxes is de-duplicated.** Message ids are per-account,
  so the same issue arrives twice with different ids. STEP 1 collapses candidates matching
  on sender + subject + date before fetching bodies, and STEP 2 catches any that slip
  through. The issue is cited once, so put the inbox you actually read at the top of
  `accounts`.
- **A de-authorized account is reported, not skipped.** If an entry in `accounts` has no
  live connector, the run says so in the daily log rather than quietly scanning fewer
  inboxes than you think it is.
- **Scope is per account, not per run.** A new inbox on its backfill window and an
  established one on the normal window run side by side in the same morning.

The routine still never writes to any mailbox — see below.

## It never writes to Gmail

No labels, no read-state changes, no archiving, no sending. De-duplication is entirely
local, via `state/processed.json`. Your unread counts are left exactly as they are.

This is enforced at the point of tool loading, not just by instruction: STEP 1 loads only
`search_threads` and `get_thread` by name. A broad tool search for "gmail mail inbox"
returns `trash_message`, `trash_thread`, `mark_thread_spam` and `label_thread` alongside
the read tools, so the destructive tools are deliberately never brought into the run's
context.

## State

- `state/processed.json` — every message id already dealt with, and what became of it.
  Delete it and the routine will re-ingest; if it goes missing the routine falls back to
  de-duplicating against the last 14 days of published timeline entries.
- `state/run-log.md` — one line per run, including quiet days that produced no page.

## Conventions the site depends on

- `ai-digest/styles.css` is never edited. Every class needed already exists.
- Topic pages are **not** append-only: `Current state` and the `<h3>` sections are
  rewritten each run so they read as continuous prose. Only `ul.timeline` is prepend.
- Prose is **paragraphed**, never a single block: `<h3>` sections run 120–250 words per
  `<p>`, and `Current state` shows three to five paragraphs with everything older folded
  into `<details><summary>Earlier cycles</summary>`. See STEP3 §3.2b–c.
- Historical entry text is never touched.
- **No `mail.google.com` URL and no Gmail address appears anywhere in `ai-digest/`.**
- A day with no qualifying stories gets a `run-log.md` line and no page.

## History

The pre-Gmail version of the ingest step is kept at `archive/STEP1-outlook.txt`. Design
rationale is in `../docs/superpowers/specs/2026-09-03-gmail-ai-digest-routine-design.md`.
