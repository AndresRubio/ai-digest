# ai-digest

A self-updating AI-news knowledge base, built each weekday morning from newsletter email
and published as a static site.

**Live:** <https://andresrubio.github.io/ai-digest/>

## Layout

| Path | What it is |
|---|---|
| `site/` | The published site — `index.html`, eleven topic pages, one page per run. Deployed from here by `.github/workflows/pages.yml` on every push to `main`. |
| `digest-routine/` | How a run works: `STEP1`–`STEP5`, the source allowlist, and run state. Start at [`digest-routine/README.md`](digest-routine/README.md). |
| `docs/` | Design specs and implementation plans. |

## How a run works

A scheduled task reads `digest-routine/STEP1-ingest.md` through `STEP5-index.md` in order and
follows them exactly. All the logic lives in those five files, so changing what the routine
does never means changing the task. Briefly: scan the connected Gmail account, split
newsletters into discrete stories, apply a quality bar, route each story to one of eleven
topic pages and rewrite that page's prose, then write a daily log and update the index.

## Two rules the project does not bend

**It never writes to Gmail.** No labels, no read-state changes, no archiving, no sending.
De-duplication is local, via `digest-routine/state/processed.json`. This is enforced at the
point of tool loading, not just by instruction — the routine loads only the two read tools by
name, so the destructive ones never enter its context.

**No mailbox identifier reaches the site.** This repo and the site are both public. Sources
are cited by newsletter name and date, never as a link into a mailbox. `pages.yml` screens
every push for a real Gmail address anywhere in the repo and a mailbox URL anywhere in
`site/`, and fails the deploy rather than publish a violation. A bare mailbox local-part
with no `@gmail.com` or `mail.google.com` attached is a different failure mode that CI
cannot screen for without putting the actual local-parts in a tracked file — so that check
runs locally only, in STEP 5.3, reading its patterns from the gitignored
`digest-routine/sources.json` immediately before every push. It is the sole line of
defence for that failure mode, not a backstop for a CI gate.
