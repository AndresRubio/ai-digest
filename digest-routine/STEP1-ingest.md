# STEP 1 — Ingest from Gmail

Goal: produce a de-duplicated list of qualifying newsletter messages, with full bodies,
across every connected Gmail account. Do not modify Gmail in any way.

## 1.1 Discover the Gmail tools

Do not hardcode a connector id — the user may connect additional Gmail accounts over
time, and each arrives as a separate MCP server with its own tool prefix.

Run `ToolSearch` with query `select:` naming only the two read tools you need, or if you
must search, `+search_threads +get_thread`. **Do not** load with broad terms like
`gmail mail inbox` — that query returns `trash_message`, `trash_thread`,
`mark_thread_spam`, `label_thread` and friends alongside the read tools. This routine
never writes to Gmail, so destructive tools must never be loaded into its context in the
first place. Load only `*__search_threads` and `*__get_thread`.

Each distinct server prefix is one authorized account. For each, determine its address
from the `toRecipients` field of any returned message and record it — permalinks and the
daily log both depend on knowing which inbox a story came from.

Cross-check the prefixes you found against `accounts` in `sources.json`. If an account
listed there produced no tool, it is no longer authorized: say so in the daily log rather
than silently scanning fewer inboxes than the user expects.

If you find a prefix that is **not** in `sources.json`, it is a newly connected inbox.
Add it to `accounts` with `"backfill": "30d"` and `"backfillState": "pending"`. This is
what gives a new inbox one catch-up pass over its recent history before it settles into
the normal rhythm &mdash; the user does not have to edit anything to get it.

If no Gmail tool is available at all, append a line to `state/run-log.md` saying so,
change nothing else, and stop.

## 1.2 Scan scope

Scope is resolved **per account**, not once for the run. Two accounts in the same run can
legitimately be on different windows.

**Normal scope** &mdash; unread messages, plus anything received in the last 7 days whether
read or not. In Gmail syntax: `(is:unread OR newer_than:7d)`.

**Backfill scope** &mdash; if the account's entry in `sources.json` has
`"backfillState": "pending"`, use its `backfill` window instead (`"30d"` &rarr;
`newer_than:30d`) for this account only. Every other account stays on the normal window.

**Explicit catch-up** &mdash; when a run instruction names a backlog window, use
`after:YYYY/MM/DD before:YYYY/MM/DD` for the accounts it names.

A backfill is **not** finished just because one run touched it. The 25-message cap in 1.5
applies per run, and a month of a busy inbox can exceed it. Leave `backfillState` as
`pending` while any message inside the backfill window remains unprocessed, and record the
remaining count; the next run continues where this one stopped. Only when the window is
exhausted does STEP 5 flip the account to `"backfillState": "done"`, after which it uses
the normal window like every other inbox.

## 1.3 Two passes, then union

Read `sources.json`.

**Pass A — sender pass.** One `search_threads` query per `tierA_priority` entry, ORing
that entry's `match` values against `from:`. This guarantees the named priority sources
are caught even when their subject lines carry no obvious AI keyword. Run this pass even
for entries marked `"status": "not-yet-arriving"` — they are in the file precisely so
they are picked up the first day they appear.

**Pass B — keyword pass.** One query per entry in `keyword_pass`, same scope.

Union the two passes. De-duplicate by message id; fall back to normalized subject when
an id is missing.

**Multi-account caveat.** Message ids are per-account, so the *same* newsletter delivered
to two connected inboxes arrives as two different ids and will survive id-based
de-duplication. Before fetching bodies, also collapse candidates that share a normalized
sender plus subject plus send date across accounts — keep one, and note the other
account(s) it also reached. Without this the routine pays twice to read one issue and
STEP 2 has to catch the duplicate later by artifact name.

## 1.4 Filter

Apply in this order:

1. **Drop-list first.** If the sender matches `drop.senders`, or the subject matches any
   `drop.subject_patterns` (case-insensitive substring), discard the message without
   fetching its body. This applies even to Tier A senders — a billing notice from a
   newsletter provider is still a billing notice.
2. **Already-processed.** Discard any message id present in `state/processed.json`.
3. **Tier.** Keep Tier A. Keep Tier B and C only as candidates — whether they survive is
   decided by the quality bar in STEP 2, not here.
4. **Everything else** goes to STEP 2 as a candidate on the strength of the keyword pass
   alone. Personal mail, calendar invites, receipts, and pure marketing blasts are
   dropped.

## 1.5 Cap and fetch

If more than 25 messages qualify, take the 25 most recent and record the remaining count
— it goes in the daily log so the next run can be told to catch up.

Fetch full bodies with `get_thread` for everything retained.

## 1.6 Record

For each retained message, carry forward into STEP 2:

- `messageId`, `threadId`
- `account` (the Gmail address it arrived at)
- `sender`, `subject`, `date`
- the full body text

**Do not build a Gmail permalink, and never put one on the site.** User instruction
2026-09-14: the wiki is published publicly at
<https://andresrubio.github.io/ai-digest/>, and a `mail.google.com` link both exposes
the account address and points a stranger at a private mailbox. Sources are cited by
**display name only** — `TLDR AI (Sep 11)` as plain text, not as a link. The `messageId`
stays in `state/processed.json` for de-duplication, which is the only thing it was ever
needed for. Where the newsletter names a canonical public URL for the artifact, link
*that* instead; it is the more useful citation anyway, since anyone can open it.

### 1.6a Resolving a redirect-only newsletter

Some newsletters emit every link as a tracking redirect — The Batch wraps all of its in
`info.deeplearning.ai`, TLDR wraps some in `links.tldrnewsletter.com`, The Code in
`archive.codenewsletter.ai`. Those are not citations: they carry campaign parameters, they
rot, and the site has never emitted one.

**Where the publisher keeps a public archive of the same issue, resolve the canonical URL
there and link it** (user instruction 2026-09-21). This is a narrow, named exception to
the "do not research the open web for a URL" rule in STEP 3 N2, and it stays narrow:

- It applies only to the **issue you actually ingested**, to recover the address of
  something already in the body. It is never a licence to go looking for a URL the
  newsletter did not carry, or to fill a gap in a story.
- **Verify before linking.** Open the archive, find the issue, and take the URL and any
  heading anchor from the page itself. Never assemble one from a slug pattern. If the
  archive has no page for that issue, use the unlinked form.
- Known archive: **The Batch** publishes at `https://www.deeplearning.ai/the-batch/` with
  one page per issue (`/the-batch/issue-NNN`) and an `id` on each news item's heading, so
  an item is cited as `…/issue-371#how-to-secure-agents-for-the-masses`. The opening
  letter has no anchor; cite the issue page bare.
- TLDR and The Code have **no public archive** of the issues they redirect to, so entries
  sourced only from those redirects still use the unlinked form.

If a query fails, continue with the others and note the gap — STEP 4 reports it in the
daily log rather than failing the run silently.
