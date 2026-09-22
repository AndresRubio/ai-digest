# STEP 4 — Write the daily log

## 4.1 Quiet days

If STEP 2 produced zero stories, **do not create a page.** Append one line to
`state/run-log.md`:

```
2026-09-05  0 stories  |  4 messages scanned, all dropped (3 promo, 1 receipt)  |  no pages touched
```

The daily index then lists only days that have content, which matters because the
routine runs weekdays only.

## 4.2 Otherwise

Write `site/daily/YYYY-MM-DD.html` using the existing template: the standard
`<!doctype html>` head with `<link rel="stylesheet" href="../styles.css">`, the shared
sidebar with `../` prefixes, and `<h1>AI Digest Log — YYYY-MM-DD</h1>`.

The body is a short summary `<ul>`, then the scan notes under their own headings, then
the themes:

```html
      <ul>
        <li><strong>Newsletters scanned: N</strong> — what window this covers.
          <ul><li>Name (Mon D)</li>…</ul></li>
        <li><strong>Distinct stories captured: N, plus M updates.</strong> Per-topic
            counts, then one nested <li> per update saying what it gained.</li>
        <li><strong>Topics updated: N of eleven.</strong> Linked, and a sentence on any
            topic deliberately left untouched.</li>
        <li><strong>New topic pages created: none</strong> (or: the new sub-section and
            why it was opened).</li>
        <li><strong>Backlog:</strong> messages matched, fetched, capped, carried.</li>
      </ul>
      <h2>Scan notes</h2>
      <h3>Sources</h3>              <!-- editions, new senders, sources.json decisions -->
      <h3>Handled without fetching</h3>
      <h3>Dropped</h3>              <!-- a <ul>, grouped by reason -->
      <h3>De-duplication</h3>
      <h3>Link discipline</h3>
      <h3>Out of scope</h3>
      <h2>Notable themes today</h2>
      <p>One or two paragraphs naming the through-line across the day's stories.</p>
```

Then the standard `<footer>Generated automatically by the AI digest task.</footer>`.

**Readability is a hard requirement here, not a preference** (user instruction
2026-09-21: *"when I click on the log entry the block of text is terrible"*). The log is
read, not just archived, and the failure mode is a single `<li>` that absorbs every note
into one unbroken block.

- **No `<p>` or `<li>` over ~150 words.** Anything longer is two items or two paragraphs.
- **Reasons get headings, not run-in bold.** A dense `<li>` with six bolded phrases
  buried inside it is the thing this rule exists to prevent; give each its own `<h3>` or
  its own bullet.
- **Drops are a grouped list** — one bullet per reason (sponsors, outside remit, no
  checkable claim, tutorials), not a paragraph naming thirty items in sequence.
- **No filler.** Every clause states a fact about this run. Cut anything that reads as
  throat-clearing, and do not restate the routine's own rules back at the reader.
- Sub-`<ul>`s inside a summary `<li>` need no CSS — `styles.css` has no rule for plain
  lists and is never edited.

**The log links out** (user instruction 2026-09-21: *"I miss the link for the original
source close to the entry"*). A log that names things the reader cannot reach is a
dead end, so:

- **Each newsletter in the scanned list links to that issue's public archive** — see the
  table in STEP 1.6a. Say so where one genuinely has no public page, rather than leaving
  a bare name that looks like an oversight.
- **Each update bullet links to the entry it updated**, using that story's own `#id` —
  every topic page carries per-story ids, so linking the bare page is never good enough.
- **The first mention of a named artifact links to its entry**, in the scan notes and in
  the themes paragraphs. First mention only — a paragraph where every noun is blue is
  the failure this is trying to avoid.
- Check the links before finishing: every `../topics/…#fragment` must resolve to an `id`
  that exists, which is worth a one-line script rather than an eyeball.

## 4.3 What belongs in the notes

The first `<li>` is where the run is honest about itself. Record:

- which newsletters were read, by name and issue date
- what was de-duplicated against stories already ingested, and against which date
- what was dropped and why ("event promotions dropped")
- any query that failed, and which sources may therefore be missing
- any backlog remainder from the STEP 1 cap: "N further qualifying messages remain
  unprocessed"
- which Gmail account each source arrived at, once more than one account is connected
- whether any account ran on a backfill window rather than the normal one, and whether
  that backfill finished or carries a remainder into the next run
- any account listed in `sources.json` whose connector was missing (de-authorized)
- any newsletter that reached more than one inbox, cited once

## 4.4 Themes paragraph

One paragraph, not a summary list. Name the tension or through-line across the day's
stories the way the existing logs do — "the day's releases split cleanly along 'the thing
announced vs the thing you can run'". If the day's stories genuinely share no theme, say
that plainly in one sentence rather than manufacturing one.
