# STEP 3 — Route stories and rewrite topic pages

Goal: place each story on the right topic page and integrate it into that page's prose.

## 3.1 The eleven topics

| Slug | Takes |
|---|---|
| `model-releases` | frontier and open-weights launches, MoEs, on-device weights, speech/audio models |
| `agents` | frameworks, MCP, computer-use, harness engineering, memory, orchestration |
| `training-and-rl` | pre-training, post-training, RL methods, distillation, RL environments |
| `infrastructure` | inference economics, KV cache, quantization, serving, enterprise deployment |
| `evals-and-benchmarks` | benchmark results, eval methodology, construct validity |
| `research-papers` | substantive method releases, architecture analysis, notable preprints |
| `safety-and-policy` | alignment, governance, regulation, security models, incidents |
| `tools-and-devex` | coding agents, IDEs, skills/memory patterns, practitioner workflows |
| `applications` | real deployments, case studies, creative media, domain products |
| `industry-and-business` | lab strategy, pricing, funding, partnerships, acquisitions |
| `embodied-and-robotics` | world models, VLA policies, humanoids, physical AI |

One story goes to one page. Where it genuinely spans two, put it on the better fit and
cross-link from the other with a relative `<a href="other-topic.html">` inside the prose,
as the existing pages already do.

**Create a new topic page only** when three or more stories share a theme that fits none
of the eleven. Prefer a new `<h3>` sub-section on an existing page — that is how
"Security benchmarks" and "Product search & e-commerce" were added. On a **converted**
page a sub-section is not a bare `<h3>` — it is a whole
`<section class="topic-section" id="…">`, built as §3.2-new N1 describes. A new page also
needs adding to the sidebar `<ul>` of **every** page in the site and to the index topic
list.

## 3.2 Per touched page, in order

**FIRST, detect which format the page is in.** The site is mid-conversion (started
2026-09-20). Check the page for `<section class="topic-section"`:

- **Present — the page is converted.** Use the story-item instructions in §3.2-new below.
  Do **not** write `<h3>` prose sections onto it; that would undo the conversion and fail
  `digest-routine/check-structure.py`.
- **Absent — the page is not converted yet.** Use the legacy instructions in §3.2-legacy
  below, unchanged from before, and leave the page's structure as you found it.

Never convert a page as a side effect of a daily run. Conversion is its own task.
Run `python3 digest-routine/check-structure.py` before finishing either way; a converted
page must come back clean.

Detect **per page**, not once per run. A single run routinely touches one converted page
and one unconverted page in the same sitting; take the branch that matches the file open
in front of you each time.

**§3.2 is three blocks, and every touched page passes through exactly two of them:**

| Block | Steps | When |
|---|---|---|
| `§3.2-legacy (unconverted pages only)` | **L1**, **L2** | page has **no** `<section class="topic-section"` |
| `§3.2-new (converted pages only)` | **N1**–**N9** | page **has** `<section class="topic-section"` |
| `§3.2-shared (BOTH branches, always)` | **S1**, **S2** | **every** touched page, whichever branch ran |

Pick **one** of the first two blocks by the detection test above, run it end to end, then
run **§3.2-shared** — it is the common tail and it is never optional. A page is not
finished until S1 and S2 have run on it. Skipping them on a converted page leaves its
`Current state` stale and its `Last updated` date wrong, which reads as though the
conversion broke the daily update.

*(Renumbered 2026-09-21 from the old single a–d sequence, which is now split across three
blocks. The old labels map: **a → L1**, **b → L2**, **c → S1**, **d → S2**. Anything
elsewhere in the repo citing §3.2a–d — `digest-routine/README.md` cites "§3.2b–c" — means
L2 and S1 under this numbering.)*

### §3.2-legacy (unconverted pages only)

Run **L1** and **L2** only when the page has **no** `<section class="topic-section"`. On a
converted page skip this whole block and use §3.2-new instead. Either way, continue into
§3.2-shared afterwards.

**L1. Prepend the timeline entry.** Insert at the top of `<ul class="timeline">`:

```html
        <li>
          <span class="date">YYYY-MM-DD</span>
          <span class="label">Label text</span> &mdash; Summary sentences.
          <div class="sources">Sources: Newsletter (Mon D) <a href="PUBLIC_URL">Vendor blog</a></div>
        </li>
```

Newsletter names are **plain text, never links** — no `mail.google.com` URLs anywhere on
the site (STEP 1.6). Multiple sources go space-separated inside the one `.sources` div,
with any canonical public URLs as the only `<a>` elements.
Keep the list strictly newest-first. Match the existing indentation (8 spaces for `<li>`).

**L2. Rewrite the relevant `<h3>` section.** These are living prose, not logs. Work the
new story into the existing argument — extend the thread, note where it confirms or
contradicts what the section already claims, and keep the section readable end to end.
Do not append a stranded sentence at the end.

Sections are **multiple `<p>` paragraphs**, one per item or argument, each roughly
120–250 words and none over ~350. A section that has grown into a single long paragraph
is a defect: break it at the sentence that starts the next item. (Fixed site-wide on
2026-09-14 — the pages had accreted paragraphs of up to 1,065 words.)

**End of §3.2-legacy. Now go to §3.2-shared** and run S1 and S2 on this page.

### §3.2-new (converted pages only)

Run **N1**–**N9** when the page **does** contain `<section class="topic-section"`. This
block replaces L1 and L2; it does **not** replace S1 and S2, which run afterwards.
`site/topics/research-papers.html` is a worked example of the finished shape, but
everything you need is written out here — do not go looking in another task file or
another document for markup.

A converted page is built from four moving parts, and this branch touches all four:

1. `<nav class="section-index">` — one chip per section, each carrying a story count.
2. `<section class="topic-section" id="…">` — a heading, one `<p class="lead">`, its
   newest three stories, then an optional `<details>` fold holding the older ones.
3. `<article class="story" id="…">` — one story.
4. `<ul class="timeline index">` at the foot of the page — one line per story on the
   page, newest first, each linking that story's own `#id`.

The old flat `<ul class="timeline">` with `.sources` inside each `<li>` **does not exist
on a converted page** and must not be recreated. Its history now lives in the stories, and
the list at the foot of the page is `<ul class="timeline index">`, which is a different
thing: a bare index of links, no summaries, no sources. Do not be fooled by the substring
match — `<ul class="timeline index">` is not the legacy `<ul class="timeline">`, and
**L1 does not apply to it.**

**N1. Pick the section the story belongs in.** Read the existing `<h3>` headings and place
the story under the one that honestly describes it. Keep every existing heading, its
wording and its order exactly as they are.

**New sections are allowed** where a story genuinely fits no existing heading (user
ruling, 2026-09-20). Add one only when no existing heading honestly describes the story;
prefer a grouping the page's own `Current state` prose already makes. A new section takes
the same `.lead` discipline as every other, gets its own chip in the nav, and goes after
the section it is closest to in subject — or immediately before the `<h2>Timeline</h2>`
heading if nothing is close. Its skeleton, at six spaces of indentation:

```html
      <section class="topic-section" id="kebab-case-of-the-heading">
        <h3>Heading text</h3>
        <p class="lead">What the section is about and what to judge entries on.</p>

        <!-- stories go here, newest first -->
      </section>
```

The section `id` is the kebab-case form of its heading text (`Retrieval-model
architecture` → `retrieval-model-architecture`), lowercase, ASCII, hyphen-separated, no
entities and no punctuation.

**N2. Write the story.** One `<article class="story">` per story, `id` set to the
kebab-case **artifact name** — the model, paper, tool, company or result the story is
about (`PC-ALM` → `pc-alm`, `Dream-RSI` → `dream-rsi`, `LFM2.5 retrieval models` →
`lfm2-5-retrieval`). The `id` must be **unique across the whole page**; the checker fails
on duplicates. If the obvious name is already taken, qualify it rather than reusing it.

Linked form, when the story has a real public URL — eight spaces of indentation:

```html
        <article class="story" id="artifact-name">
          <span class="when">YYYY-MM-DD</span>
          <h4><a href="https://example.com/post">Headline that states the result</a></h4>
          <p>What was released or shown, with the concrete numbers.</p>
          <p>Why it matters, and the limit the authors state.</p>
          <div class="sources"><a href="https://example.com/post">Publisher</a> &middot; <a href="https://arxiv.org/abs/0000.00000">arXiv</a> &middot; <span class="via">via Newsletter (Mon D)</span></div>
        </article>
```

Unlinked form, when no real URL is available:

```html
        <article class="story unlinked" id="artifact-name">
          <span class="when">YYYY-MM-DD</span>
          <h4>Headline that states the result</h4>
          <p>What was released or shown, with the concrete numbers.</p>
          <div class="sources"><span class="via">via Newsletter (Mon D) &mdash; no public URL given</span></div>
        </article>
```

Rules the checker enforces on this markup, all of them hard:

- **`<span class="when">` is required** and must be exactly `YYYY-MM-DD`. It is the date
  of the story, the same date the timeline line carries — not the run date.
- **The headline link must be a real absolute URL**, lowercase `https://` or `http://`
  followed by a host. A relative link does not count as linked. **Never fabricate a URL
  and never research the open web for one.** No URL in the source material → use the
  unlinked form: `class="story unlinked"`, a plain-text `<h4>` with no `<a>`, and the
  words `no public URL given` inside `.sources`. Those three go together; a story that is
  linked *and* marked `unlinked`, or unlinked with no stated reason, fails the checker.
  A commentary or analysis page is an acceptable headline link when it is the only real
  URL an entry carries (user ruling, 2026-09-20) — a reader getting somewhere real beats
  an unlinked story, and `.sources` should still make plain what kind of page it is.
- **Body: one to three `<p>`, 2–4 sentences in total.** No `<p>` anywhere on the
  page may run past 350 words.
- **No nesting.** A story body must never contain another `<article`, and a
  `topic-section` body must never contain another `<section`. The checker's parser assumes
  a flat structure and fails loudly if it is broken.
- **No mailbox identifier may ever reach the site.** No `mail.google.com`, no
  `outlook.office365.com`, no `/owa/?ItemID`, no Gmail address — not in an `href`, not in
  `.sources`, not in a comment. Newsletter names are **plain text** inside
  `<span class="via">`, never links. The only `<a>` elements in a `.sources` div are
  canonical public URLs. This is the project's second unbendable rule and `.sources` is
  exactly where it gets broken.
- Cross-links to another topic page stay relative (`<a href="agents.html">`). A cross-link
  to another story *on this page* uses that story's `#id` and the id must exist — every
  `#fragment` anywhere on the page is checked, including ones inside story prose.

**N3. Prepend the story to its section.** It goes immediately after that section's
`<p class="lead">`, above the existing stories, because sections run newest-first.
If the story is *older* than stories already in the section — a backfill — insert it in
date order rather than at the top, so the section stays newest-first; if that puts it
below the newest three it belongs inside the `<details>` fold from the start (N4).

**N4. Fold anything past the newest three.** A section shows its **newest 3** stories
directly; every older one lives inside a `<details>` that is the **last** child of the
section, after the visible stories and still inside `</section>`. Adding a fourth story
therefore pushes the oldest visible one down into the fold.

If the section already has a fold, move the displaced story to the **top** of it (the
fold is newest-first too) and increment the number in the `<summary>`. If it has none,
create one — eight spaces for `<details>`, ten for the articles inside it:

```html
        <details>
          <summary>Earlier in this section (1)</summary>

          <article class="story unlinked" id="older-artifact-name">
            <span class="when">YYYY-MM-DD</span>
            <h4>Headline of the displaced story</h4>
            <p>Its existing text, moved unchanged.</p>
            <div class="sources"><span class="via">via Newsletter (Mon D) &mdash; no public URL given</span></div>
          </article>
        </details>
```

Moving a story into the fold is a **move, not a rewrite**: its wording, date, id and
sources travel with it untouched. The count in the `<summary>` is the number of articles
inside that `<details>`, and nothing else.

**N5. Update the `.lead` only if the through-line actually changed.** One `<p class="lead">`
per section, **60 words maximum**, directly under the `<h3>`. It says what the section is
about and what to judge entries on — it is not a summary of today's story. Most runs leave
every lead alone. Rewrite one only when the new story genuinely changes what the section
is about; then keep it under 60 words. A section with zero leads, two leads, or a lead
over 60 words fails the checker.

**N6. Rebuild the `<nav class="section-index">` chips.** One `<li>` per section, in the
same order the sections appear on the page, ten spaces of indentation:

```html
          <li><a href="#section-id">Section heading <span class="n">3</span></a></li>
```

The number is that section's **real** story count — **visible stories plus folded ones**.
Adding a story raises its section's count by one even when the story lands in the fold.
Add a chip when you added a section; never drop one. Every section must have a chip and
every chip must point at a section that exists.

**N7. Add one line to `<ul class="timeline index">`.** The list sits under
`<h2>Timeline</h2>` at the foot of `<main>`, is strictly newest-first, and carries exactly
one line per story on the page — folded stories included. Eight spaces of indentation:

```html
        <li><span class="date">YYYY-MM-DD</span><span class="label"><a href="#artifact-name">Headline text</a></span></li>
```

The date matches the story's `<span class="when">`. The link is the story's own `#id`, and
a fragment that does not resolve fails the checker. The label is the headline as plain
text (it may be trimmed if the headline is long); there is **no** `.sources` div and no
summary on these lines — the sources live in the story. Insert the new line in date order,
above any line with an older date. Never rewrite an existing line's wording or date.

**N8. End of §3.2-new. Now go to §3.2-shared** and run S1 and S2 on this page — rewrite
the `Current state` div and update the meta line. A converted page has both and is not
finished without them.

**N9. Run the checker.** `python3 digest-routine/check-structure.py`. Any failure naming a
page you touched is yours to fix before finishing. Lines reading
`… not converted yet (no topic-section)` for pages you did not touch are the expected
mid-conversion state and are not your run's failure.

### §3.2-shared (BOTH branches, always)

**These two steps run on every touched page, whichever branch above applied.** A
converted page and an unconverted page both carry a `<div class="current-state">` block
and a `<div class="meta">` line, in the same place, with the same rules. Do not skip this
block because you came out of §3.2-new; nothing here is legacy.

**S1. Rewrite the `Current state` div.** Same discipline, one level up: it opens with the
most recent cycle and narrates backwards. Lead it with today's stories and their
through-line, then compress what was previously leading. Every run should leave it
coherent rather than accreted.

Its structure is fixed, and a run must preserve it:

```html
      <div class="current-state">
        <p>Today's cycle: the lead story and its through-line.</p>
        <p>The rest of this cycle, one paragraph per thread.</p>
        <details>
          <summary>Earlier cycles</summary>
          <p>Everything older, still newest-first, one paragraph per cycle or thread.</p>
        </details>
      </div>
```

The div as a whole is allowed to be long, but what shows **before** `<details>` is the
budget that matters: three to five paragraphs, roughly 500–900 words. When today's
material pushes an older paragraph out of that budget, move it inside `<details>` —
do not let the visible part grow. Never emit the div as one unbroken run of text.

On a converted page this `<details>` is the one inside `<div class="current-state">`, and
it is a different thing from the per-section `Earlier in this section (N)` fold in N4.
Do not merge them and do not move stories into this one.

**S2. Update the meta line** to `<div class="meta">Last updated: YYYY-MM-DD</div>`.

That date is the **run date**, on every page this run touched — converted or not. Pages
no story routed to keep their previous date.

**The page is now finished.** Move to the next touched page and start again at the
detection test at the top of §3.2.

## 3.3 Constraints

- Never edit `styles.css`. Every class you need already exists: `timeline`, `date`,
  `label`, `sources`, `current-state`, `changed-today`, `meta` — and, on a converted page,
  `topic-section`, `story`, `unlinked`, `lead`, `when`, `via`, `section-index`, `n` and
  `timeline index`. (It was last changed on
  2026-09-14, on user instruction, to add paragraph and `<details>` rules inside
  `.current-state`. Use those elements; do not add more.)
- Never rewrite historical timeline entries. Their wording and dates stay. (The one
  sanctioned exception was 2026-09-14, when every Gmail link site-wide was stripped to
  plain-text source names on user instruction; entry text was untouched.)
- Sidebar rules, which are easy to get wrong: the index links topics as `topics/slug.html`,
  topic pages link their siblings bare (`agents.html`), and daily pages use `../topics/`.
  Each topic page additionally marks its **own** entry `class="active"`. So the blocks are
  *not* byte-identical across the site — compare a page only against others at the same
  depth, with the active marker normalized away. (Note: daily pages written before
  `embodied-and-robotics.html` existed are missing it from their sidebar. Leave them alone;
  do not backfill historical pages.)
