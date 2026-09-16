# Gmail-sourced AI digest routine — design

Date: 2026-09-03
Status: approved, pending implementation

## Problem

`site/` is a hand-shaped static knowledge base about AI news, built daily from
newsletter email. Its last update was 2026-08-04. The original ingest spec
(`site/STEP1-improved.txt`) targets Outlook; the user is moving to Gmail and may
connect several Gmail accounts over time. The routine needs to be re-expressed against
Gmail, run automatically on weekday mornings, and stay editable as subscriptions change.

## Constraints and decisions

| Decision | Choice |
|---|---|
| Source of truth for mail | Gmail connector(s). Outlook pass dropped. |
| Allowlist scope | Aspirational: includes sources not yet arriving in Gmail, so they are picked up the day they start. |
| Accounts | N Gmail accounts. Discovered at run time, not hardcoded. |
| Backlog | One catch-up run covering 2026-08-05 → 2026-09-03. |
| Schedule | Weekdays 08:00 local. |
| Mailbox writes | None. Dedupe uses a local ledger. |
| Packaging | Markdown STEP files on disk + a thin scheduled-task prompt. |

## Observed inbox reality (45-day scan, 2026-07-21 → 2026-09-03)

Arriving and substantive:
- `hello@ollama.com` — ~2x/week, model availability announcements (GLM 5.3, Kimi K3,
  Qwen 3.8 27B, Muse Glimmer, DeepSeek-V4-Flash-0731, Nemotron 3.5 Lightning)
- `thebatch@deeplearning.ai` — weekly, The Batch
- `no-reply@email.claude.com` — occasional Anthropic product announcements

Arriving but mostly promotional:
- `news@nvidia.com` (GTC passes, livestream invites), `noreply@email.openai.com`
  (consumer tips, policy updates), `team@mail.cursor.com`, `no-reply@mermaid.ai`,
  `hello@rime.ai`, `hello@twelvelabs.io`, `contact@napkin.ai`, `naveen@hey.monologue.to`

Not arriving in Gmail today, but expected later — kept in the allowlist:
MarkTechPost, Substack (Decoding AI / Paul Iusztin, Vanishing Gradients / Hugo
Bowne-Anderson, Sebastian Raschka), Ona / Lou, TLDR AI, Import AI, Ben's Bites,
The Rundown, AlphaSignal, smol.ai.

Recurring non-news noise to hard-drop: Anthropic invoices/receipts, Scaleway invoices,
Google "you shared account data" / security alerts, GitHub app permission requests,
Discord mention notifications, service login alerts.

## Layout

```
mywiki 2/
  site/                  # published static site, shape unchanged
    index.html  styles.css
    topics/*.html  daily/YYYY-MM-DD.html
  digest-routine/
    README.md                 # how it works; how to add a source or an account
    sources.json              # tiered allowlist + drop-list
    STEP1-ingest.md
    STEP2-extract.md
    STEP3-route.md
    STEP4-log.md
    STEP5-index.md
    state/
      processed.json          # ingested message ledger
      run-log.md              # one line per run, incl. no-op days
    archive/STEP1-outlook.txt # superseded original
```

`site/` contains only the site. All machinery is in `digest-routine/`.

## The five steps

### STEP1 — ingest
Discover every available Gmail search tool at run time (ToolSearch over the connector
tools) rather than naming one connector, so newly authorized accounts are included
automatically. For each account:

- Sender pass: one query per Tier A entry in `sources.json`, scoped to
  `newer_than:7d OR is:unread`.
- Keyword pass: `AI`, `LLM`, `GPT|Claude|Gemini|Anthropic|OpenAI`, `agent|agentic`,
  `model release|benchmark|eval|RLHF|fine-tuning`, same scope.
- Union the results, de-duplicate by message id, then subtract every id already in
  `state/processed.json`.
- Apply the drop-list before fetching bodies.
- Cap at 25 messages per run; record any remainder in the daily log.

Every retained message is recorded with: message id, thread id, account email, sender,
subject, date. The Gmail permalink is
`https://mail.google.com/mail/u/?authuser=<account>#all/<messageId>`.

> **Superseded 2026-09-14.** Permalinks were dropped entirely when the wiki began
> publishing to GitHub Pages: a mailbox URL exposes the account address and points a
> stranger at a private message. Sources are now cited by newsletter name as plain text,
> with canonical public URLs as the only links. Message ids survive only in
> `state/processed.json`, for de-duplication. See STEP 1.6.

### STEP2 — extract
Fetch full bodies for retained messages. Break each into discrete stories.

Quality bar (this is what keeps new entries consistent with the existing pages): a story
must name a specific artifact — a model, paper, tool, release, or company action — and
carry at least one concrete claim: a benchmark number, price, license, parameter count,
date, or named architectural detail. Event invitations, "book your pass", generic
product tips, and pricing-page marketing are not stories.

De-duplicate stories across messages by artifact name. When two newsletters cover the
same release, emit one story with both sources.

### STEP3 — route and rewrite
Assign each story to one of the eleven existing topic pages (create a new page only when
three or more stories share a theme that fits nowhere). For each touched page:

- Prepend a `<li>` to `ul.timeline` — `<span class="date">`, `<span class="label">`,
  an em-dash summary, and a `<div class="sources">` with Gmail permalinks.
- **Rewrite**, not append, the `Current state` div and the relevant `<h3>` section so
  the new item is absorbed into the running narrative. These sections are living prose
  in the existing pages; appending would break their voice.
- Update the page's `<div class="meta">Last updated: YYYY-MM-DD</div>`.

Cross-link between topic pages with relative hrefs where a story spans two topics, as
the existing pages already do.

### STEP4 — daily log
Write `site/daily/YYYY-MM-DD.html` following the existing template: sidebar, a
`<ul>` of run stats (newsletters scanned with names, distinct stories captured, topics
updated as links, new pages or sub-sections created, plus any de-duplication or backlog
notes), then a `Notable themes today` paragraph.

If a run yields zero stories, write no page — append a line to `state/run-log.md`
instead. The daily index then lists only days that have content.

### STEP5 — index
Update `site/index.html`: the `Last updated` meta, the yellow `changed-today` box
(one `<li>` per touched topic, linked, with a one-line summary), the topic descriptions
if a topic's remit changed, and prepend the new date to the daily-log list.

Finally, append the run's message ids to `state/processed.json` and a summary line to
`state/run-log.md`.

## Scheduling

A weekday 08:00 scheduled task whose prompt is thin:

> Work in `/Users/autobot/Desktop/projects/ai-digest`. Read `digest-routine/STEP1-ingest.md`
> through `STEP5-index.md` in order and follow them exactly. Do not modify Gmail.

All logic stays in the files, so editing the allowlist never means editing the cron job.

## Error handling

- No Gmail tool available → write a run-log line saying so, change nothing, stop.
- A Gmail query fails → continue with the other queries, note the gap in the daily log.
- Zero qualifying messages → run-log line, no page, no index change.
- `processed.json` missing or corrupt → fall back to de-duplicating against the last 14
  days of timeline entries already on the topic pages, and rebuild the ledger.
- More than 25 qualifying messages → process the 25 most recent, record the remainder
  count in the daily log so the next run can be told to catch up.

## Verification

The routine is verified by reading its output, since there is no test suite for a static
site:
- Every touched HTML file parses and its sidebar/nav matches the others.
- Every new timeline entry has a `date`, a `label`, a summary, and at least one source.
- Every Gmail permalink is well-formed and carries the right `authuser`.
- The index's daily list, the `changed-today` box, and the touched pages' `Last updated`
  dates all agree with the run date.
- `processed.json` grew by exactly the number of messages ingested.

## Out of scope

- Migrating existing Outlook permalinks in the historical pages. They stay as they are.
- Any Gmail write: no labels, no read-state changes, no archiving.
- Re-styling the site. `styles.css` is unchanged.
