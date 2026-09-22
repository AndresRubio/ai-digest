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
of the eleven. Prefer a new sub-section on an existing page — that is how
"Security benchmarks" and "Product search & e-commerce" were added. A sub-section is not a
bare `<h3>`: it is a whole `<section class="topic-section" id="…">`, built as §3.2-story
**N1** describes. A new page also needs adding to the sidebar `<ul>` of **every** page in
the site and to the index topic list, and it is born in the story-item shape — there is no
other shape on this site.

## 3.2 Per touched page, in order

**Every topic page carries the story-item structure.** The conversion ran 2026-09-21 to
2026-09-22 (planned, and the 192 mailbox permalinks stripped, on 2026-09-20): all eleven
pages are built from
`<section class="topic-section">` and `<article class="story">`. The legacy `<h3>`
living-prose branch that ran beside it for those three days is gone from this document.
Never write an `<h3>` prose section onto a topic page. `check_no_legacy_prose` fails the
run on any `<h3>` that is not inside a `<section class="topic-section">` — added
2026-09-22 for exactly this, because until then an injected legacy section passed every
other check with exit 0.

**If a page you are about to touch has no `<section class="topic-section"`, stop.** That is
not a page awaiting conversion; every page was converted. It is a page that has *lost* its
structure, through a bad edit or a bad merge. Say so plainly and restore the structure
before routing any story into it. Do not fall back to prose sections, and do not convert a
page as a side effect of a daily run — recovering a page is its own task, exactly as
conversion was.

**§3.2 is two blocks, and every touched page runs both, in order:**

| Block | Steps | Covers |
|---|---|---|
| `§3.2-story` | **N1**–**N9** | placing, writing and indexing the story itself |
| `§3.2-page` | **S1**, **S2** | the page tail: `Current state`, `Last updated` |

Run §3.2-story end to end, then run §3.2-page. The tail is never optional: a page is not
finished until S1 and S2 have run on it, and skipping them leaves the `Current state` stale
and the `Last updated` date wrong — which reads to a visitor as though the daily update
stopped working.

*(Label history, for anything citing older names. The original a–d sequence was split on
2026-09-21 into three blocks: **a → L1**, **b → L2**, **c → S1**, **d → S2**. On 2026-09-22
the legacy branch was deleted once the last page was converted, taking **L1** and **L2** with
it, and `§3.2-new` / `§3.2-shared` became `§3.2-story` / `§3.2-page` — there is no longer an
old form to contrast them with. Text elsewhere citing **a**–**d**, **L1**, **L2**,
`§3.2-new` or `§3.2-shared` predates this and means the steps above.)*

### §3.2-story (N1–N9)

Run **N1**–**N9** on every touched page, then continue into §3.2-page — these steps do not
replace S1 and S2. `site/topics/research-papers.html` is a worked example of the finished
shape, but everything you need is written out here — do not go looking in another task file
or another document for markup.

A topic page is built from four moving parts, and these steps touch all four:

1. `<nav class="section-index">` — one chip per section, each carrying a story count.
2. `<section class="topic-section" id="…">` — a heading, one `<p class="lead">`, its
   newest three stories, then an optional `<details>` fold holding the older ones.
3. `<article class="story" id="…">` — one story.
4. `<ul class="timeline index">` at the foot of the page — one line per story on the
   page, newest first, each linking that story's own `#id`.

The flat `<ul class="timeline">` with `.sources` inside each `<li>` **does not exist on a
topic page** and must not be recreated. Its history now lives in the stories, and the list
at the foot of the page is `<ul class="timeline index">`: a bare index of links, no
summaries, no sources. The flat form now exists **nowhere in `site/`** — not on the daily
pages, not on `index.html`, neither of which carries a timeline list at all. `ul.timeline`
survives in `styles.css` only as the base rule that `ul.timeline.index` inherits from, which
is why the class name is still there to be confused with. Do not be fooled by the substring
match: `<ul class="timeline index">` is not `<ul class="timeline">`, and the per-entry
summary-and-sources markup belongs to neither.

**Before N1 — is this an update rather than a new story?** STEP 2.3 says that when a later
message adds a material fact to an artifact already published, you update the existing
entry instead of creating a second one. On a topic page that entry is its
`<article class="story">`. Find it by artifact `id`, edit that story's `<p>` in place, and
add the new source to its `.sources`. Do not add a second story for the same artifact, do
not add a second `ul.timeline index` line, and do not change the story's `id`, its
`<span class="when">` or its position — the date is when the artifact landed, not when you
learned more about it, and `#id` is what the daily log links to. This is the one case where
a run edits existing story prose; everything below is about adding a new one.

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
  and never research the open web for one** — with the single named exception in
  STEP 1.6a, which lets you resolve an ingested issue's own canonical address from the
  publisher's public archive when the newsletter emitted only a tracking redirect, and
  requires you to verify the page before linking it. No URL in the source material and
  no archive to resolve to → use the unlinked form: `class="story unlinked"`, a plain-text `<h4>` with no `<a>`, and the
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
- **Pair every `.sources` anchor to its story by name, never by position.** When one
  newsletter issue yields several stories in a single run — the STEP 1.6a case, where you
  resolve the issue's per-item heading anchors from the publisher's archive — you end up
  holding a list of anchors and a list of stories. Match each anchor to its story by
  reading the anchor's own text and confirming it names that story's artifact. Do **not**
  walk the two lists in parallel and pair them off in order: the orders are not the same,
  and on 2026-09-21 three stories from one issue came out rotated by one, each carrying
  the next story's anchor. **If a story has no anchor of its own, cite the bare issue URL
  in `.sources` and never hand it a leftover anchor that belongs to a different story.**
  Note the scope: that fallback is about the `.sources` citation, not the headline. The
  headline follows STEP 1.6a, which permits the bare issue page as a *headline* link only
  where the issue page is itself the artifact — The Batch's opening letter — and otherwise
  says to use the unlinked form. A story headline-linked to a newsletter archive that is
  not about it is the "never link the newsletter" rule broken, and
  `check_story_link_state` cannot see it: any absolute URL counts as linked.
  This failure is invisible to `check-structure.py` and to every other automated check:
  a misassigned anchor is still a real, well-formed, resolving URL. Reading each anchor
  against its story before you write it is the only thing that catches it.
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

**But a number inside a lead is a claim about the section, and it is not covered by "the
through-line did not change."** Adding a story can leave the through-line exactly as it
was and still make the lead false. If the lead you are about to leave alone counts the
section's stories — "Two of the nine are contested attributions", "Four claims about what
an outsider can verify" — **recount it against the section's new total** and fix it, even
though you are not rewriting the lead. On 2026-09-21 a section grew from nine stories to
eleven; N6 correctly rebuilt its chip to `11` while the lead went on saying "Two of the
nine", so the page contradicted its own index inside one viewport.

Two things follow:

- **Recheck the numerator too, not just the denominator.** "Two of the nine" → "Two of the
  eleven" is only right if the two new stories are not themselves contested attributions.
  Read them before you pick the number.
- **A lead that enumerates gets extended, not renumbered.** "Four claims … how text is
  marked, where books end up, how a ranking works, what a vendor keeps" must gain a clause
  for the new story, not merely become "Five claims". And check the rest of the lead for a
  second number that depends on the same total — a following sentence reading "in three of
  the four" goes stale from the very same edit.

`check_lead_counts` catches the "N of the M" form automatically. It deliberately does
**not** flag a lead that opens with a bare count — "Two families", "Three instruments",
"Two constraints" — because those count kinds rather than stories and are a legitimate way
to frame a section. Nothing checks the enumerating form; that one is yours to get right.

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

**N8. Run the checker.** `python3 digest-routine/check-structure.py` — eleven checks,
including `check_lead_counts` from N5, `check_index_counts` from N6 and
`check_no_legacy_prose` from the rule at the top of §3.2. **The required result is every
check `PASS` and exit code 0.** There is no expected-failure state any more: the
`… not converted yet (no topic-section)` line existed for pages awaiting conversion, and
none remain. Seeing one now means a page has lost its structure — the stop rule at the top
of §3.2 applies. A failure naming a page you touched is yours to fix before finishing; a
failure on a page you did not touch is still a blocker, and still gets said out loud rather
than left for whoever caused it.

**N9. End of §3.2-story. Now go to §3.2-page** and run S1 and S2 on this page — rewrite
the `Current state` div and update the meta line. Every topic page has both and is not
finished without them.

### §3.2-page (S1, S2)

**These two steps run on every touched page, always.** The conversion did not change them:
`<div class="current-state">` and `<div class="meta">` sit where they always sat, with the
rules they always had. They are why a page is not finished when its last story is written.

**S1. Rewrite the `Current state` div.** This is the page's one piece of standing prose —
the only place a reader gets the argument rather than the items — and it is rewritten in
full every run, not appended to. It opens with the most recent cycle and narrates
backwards: lead with today's stories and their through-line, then compress what was
previously leading. Every run should leave it coherent rather than accreted.

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

This `<details>` is the one inside `<div class="current-state">`, and it is a different
thing from the per-section `Earlier in this section (N)` fold in N4.
Do not merge them and do not move stories into this one.

**S2. Update the meta line** to `<div class="meta">Last updated: YYYY-MM-DD</div>`.

That date is the **run date**, on every page this run touched. Pages no story routed to
keep their previous date.

**The page is now finished.** Move to the next touched page and start again at N1.

## 3.3 Constraints

- Never edit `styles.css`. Every class a topic page needs already exists: `topic-section`,
  `story`, `lead`, `when`, `via`, `sources`, `section-index`, `n`, `timeline index` with
  `date` and `label` inside it, `current-state` and `meta`. (`changed-today` is
  `index.html`'s, written by STEP 5, and `unlinked` has no rule of its own at all — it is a
  semantic marker `check_story_link_state` reads, not a style.) The stylesheet was last
  changed 2026-09-14, on user instruction, to add paragraph and `<details>` rules inside
  `.current-state`, and again 2026-09-20 for the story-item structure. Use what is there;
  do not add more, and never modify an existing rule — the daily pages and `index.html`
  depend on them.
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
