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

Write `ai-digest/daily/YYYY-MM-DD.html` using the existing template: the standard
`<!doctype html>` head with `<link rel="stylesheet" href="../styles.css">`, the shared
sidebar with `../` prefixes, and `<h1>AI Digest Log — YYYY-MM-DD</h1>`.

The body is a `<ul>` of four items, then a themes paragraph:

```html
      <ul>
        <li>Newsletters scanned: N — <em>Name (Mon D), Name (Mon D)</em>. Notes on what
            was de-duplicated against earlier runs and what was dropped, and why.</li>
        <li>Distinct stories captured: N</li>
        <li>Topics updated: <a href="../topics/slug.html">Topic name</a>, …</li>
        <li>New topic pages created: none (or: new "Section name" sub-section on Page)</li>
      </ul>
      <h2>Notable themes today</h2>
      <p>One paragraph naming the through-line across the day's stories.</p>
```

Then the standard `<footer>Generated automatically by the AI digest task.</footer>`.

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
