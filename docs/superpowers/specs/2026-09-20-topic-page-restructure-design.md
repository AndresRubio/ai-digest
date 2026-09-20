# Topic pages: one linked story item instead of four unlinked renderings

**Date:** 2026-09-20
**Status:** approved, pending implementation plan

## Problem

Topic pages are unreadable when you move through their subsections, and the summaries you
do read have nowhere to click.

The measured state of `site/topics/` on 2026-09-18:

| Page | Words | h3 sections | Timeline entries | Ext. links in prose |
|---|---|---|---|---|
| `tools-and-devex` | 23,643 | 11 | 98 | 1 |
| `model-releases` | 21,511 | 11 | 92 | 0 |
| `agents` | 19,857 | 12 | 84 | 0 |
| `safety-and-policy` | 19,625 | 12 | 66 | 0 |
| `infrastructure` | 17,183 | 11 | 65 | 0 |
| `evals-and-benchmarks` | 14,128 | 9 | 52 | 0 |
| `industry-and-business` | 13,282 | 6 | 50 | 0 |
| `applications` | 11,653 | 9 | 43 | 0 |
| `research-papers` | 8,888 | 10 | 30 | 0 |
| `embodied-and-robotics` | 8,824 | 7 | 32 | 0 |
| `training-and-rl` | 7,765 | 6 | 29 | 0 |

Three findings, in order of importance.

**1. Every story is rendered twice, and the copy you read has no link.** STEP 3.2a prepends a
timeline entry carrying label + summary + canonical URL — which is exactly the unit a reader
wants. STEP 3.2b then dissolves the same story a second time into `<h3>` living prose, which
carries the synthesis but drops the URL. Across all **104 sections site-wide** there is **one**
external link in prose. To get a summary and its source today you read a 1,500-word essay,
scroll past ~6,000 words, and hunt the timeline for the matching entry.

The worked example, `research-papers.html` → "Learning rules beyond backpropagation": Sakana's
PC-ALM appears **four times** — two unlinked prose paragraphs (483 words) and two timeline
entries (307 words). 790 words for one paper. The two timeline entries are the same artifact
reported by two newsletters, which STEP 2.3 already says should have been merged into one
story with two sources.

**2. There is no in-page navigation.** The sidebar lists the eleven topics and stops. Once you
are on a page there is no way to see what sections exist or jump to one. Sections run 101 to
1,560 words with no entry point.

**3. 186 entries link to the owner's mailbox, and real-source coverage is far worse than a
naive count suggests.** An earlier draft of this spec counted any `href="http…"` as a source
link and concluded coverage had *degraded* from 100% in May to 28% in August. That was wrong.
186 of those links are `outlook.office365.com/owa/?ItemID=…` permalinks — dead for every
reader, and a mailbox identifier on a public site. Excluding them:

| Month | Real public source | Entries linking to the mailbox |
|---|---|---|
| 2026-05 | 0/18 — **0%** | 18 |
| 2026-06 | 5/90 — **5%** | 88 |
| 2026-07 | 9/103 — 8% | 66 |
| 2026-08 | 38/181 — 20% | 14 |
| 2026-09 | 159/249 — **63%** | 0 |
| **All** | **211/641 — 32%** | **186** |

The real trend is the opposite of the earlier claim: source-link discipline has been steadily
*improving*, and reached 0 mailbox links in September. What the site carries is a pre-Gmail
Outlook legacy that the Gmail-era guard was never written to catch.

Two consequences. The 186 mailbox links are a **live violation of the project's second
unbendable rule** and must be removed regardless of this restructure. And only 32% of
historical entries can gain a real link without researching the open web, so 430 entries will
render as unlinked — honestly, rather than pointing at an inbox.

What is *not* broken: the `Current state` block. Its `<details>` fold works — visible portion
is 492–565 words across every page, inside STEP 3.2c's 500–900 budget. Leave it alone.

Also not broken: STEP 2.4. It already produces `label` (6–14 words), `summary` (2–4 sentences)
and the canonical URL per story. The data model is right; STEP 3 discards the link when it
renders.

## The change

A story appears **once** on its topic page, under the heading it belongs to, with its link
attached. The timeline stops being a second copy and becomes a chronological index.

### Section shape

```html
<section class="topic-section" id="learning-rules">
  <h3>Learning rules beyond backpropagation</h3>
  <p class="lead">One or two sentences: the through-line that makes these items a group.</p>

  <article class="story">
    <span class="when">2026-09-15</span>
    <h4><a href="https://pub.sakana.ai/pc-alm/">Headline, 6&ndash;14 words, artifact first</a></h4>
    <p>Two to four sentences. Hard numbers first, then the honest trade-off.</p>
    <div class="sources"><a href="URL">Vendor</a> &middot; <a href="URL">arXiv</a>
      &middot; <span class="via">via TLDR AI (Sep 15), MarkTechPost (Sep 17)</span></div>
  </article>

  <details>
    <summary>Earlier in this section (N)</summary>
    <!-- older <article class="story"> items, newest first -->
  </details>
</section>
```

Rules:

- The **headline is the link**, to the canonical public URL. No URL available → render the
  `<h4>` as plain text, add `class="unlinked"` to the `article`, and state
  `no public URL given` in `.sources`. Never fabricate a URL and never link the newsletter.
- Newsletter names stay **plain text** inside `.via`. The STEP 1.6 prohibition on
  `mail.google.com` and on any mailbox identifier is unchanged and absolute.
- `.lead` is **one or two sentences, hard cap 60 words.** It carries the through-line only.
  It is not a place for the essays to survive.
- A section shows its **newest 3 stories**; everything older goes inside `<details>`.
- `id` on each `<section>` is the kebab-case slug of the heading, stable across runs. Each
  `<article class="story">` also carries a stable `id`, slugged from its artifact name, so the
  timeline can link straight to it.

### Section index

Directly below the `Current state` block, above the first section:

```html
<nav class="section-index">
  <h2>On this page</h2>
  <ul>
    <li><a href="#learning-rules">Learning rules beyond backprop <span class="n">4</span></a></li>
    ...
  </ul>
</nav>
```

One chip per `<section>`, in page order, with the story count (visible + folded). Rebuilt
every run so counts stay true.

### Timeline

Keeps one line per **story** — so entries merged in backfill collapse to a single line — with
its date. Drops the summary, which now lives once, in the section.

```html
<ul class="timeline index">
  <li><span class="date">2026-09-15</span>
      <span class="label"><a href="#pc-alm">Headline</a></span></li>
</ul>
```

The label links to **that story's own anchor on the same page**, not out to the source and not
merely to its section. The timeline is a finding aid: "when did this land, and where on this
page does it live." Strictly newest-first, as now.

Because a story older than the newest three sits inside a closed `<details>`, each
`<article class="story">` carries a stable `id` and the fold must open when the fragment
points inside it. Browsers do this natively for fragment navigation into a closed `<details>`;
where they do not, the reader lands on the section heading, which is acceptable degradation.
**No JavaScript is added** — the site has none today and this change does not introduce any.

### CSS

`styles.css` gains `.section-index`, `.topic-section`, `.story` (with `.when`, `.unlinked`,
`.via`) and `ul.timeline.index`. **No existing rule is modified or removed** — `.current-state`,
`.changed-today`, `.meta`, `.sources`, the sidebar and the base `ul.timeline` all stay as they
are, because daily pages and the index depend on them.

## Backfill

All eleven pages convert. Reconciliation is roughly 640 timeline entries against ~104 prose
sections, and it is judgement rather than a script: some prose has no matching timeline entry,
some entries were never written into prose, and duplicates like the two PC-ALM entries must
merge into one story with both sources.

Per page:

1. Parse existing timeline entries → candidate story items (they already hold label, summary,
   sources, and a URL where one was captured).
2. Merge duplicate entries for one artifact into a single story carrying every source.
3. Assign each story to a section, starting from the existing `<h3>` set. Keep every
   existing heading, its wording and its order. **New sections are allowed where a story
   genuinely fits none of them** (user ruling, 2026-09-20, after the pilot found 7 of 30
   such stories). Add one only when no existing heading honestly describes the story --
   misfiling is the worse outcome. Prefer a grouping the page's `Current state` already makes.
4. Reduce each existing prose section to its `.lead` — ≤60 words. Where the prose carries a
   fact absent from the matching story summary, move the fact into the summary before cutting.
5. Where prose describes a story with no timeline entry, create the story item from the prose
   and mark it unlinked.
6. Rebuild the section index and rewrite the timeline as an index.
7. Leave `Current state` untouched.

**Mailbox-link removal is mandatory and comes first.** All 186 `outlook.office365.com`
permalinks are stripped across all eleven pages before any restructuring, as its own commit.
The link is removed; the plain-text newsletter name stays. This is a leak fix, not a style
change, and it is not contingent on the rest of this work landing.

**Link repair beyond that is bounded.** Where an entry carries no real URL, do not go hunting
the open web. Fill one only where another entry on the site already cites the same artifact.
The remaining ~430 entries render as unlinked with an explicit note. A gap stated plainly is
better than a guessed URL, and far better than a link into the owner's inbox.

Not in scope: `site/daily/*.html` (78 files) and `site/index.html` keep their current
structure. Historical timeline entry wording and dates are not rewritten — the STEP 3.3 rule
holds, and moving an entry's summary into a story item is a move, not a rewrite.

## Routine changes

**STEP 3.2a** — timeline entry becomes the one-line index form.

**STEP 3.2b** — replaces "rewrite the relevant `<h3>` section as living prose". New instruction:
add the story as an `<article class="story">` at the top of its section, move any story pushed
past the third into `<details>`, and update `.lead` only if the new story changes the
through-line. The 120–350-word-paragraph discipline is deleted; the `.lead` cap replaces it.

**STEP 3.2c** — unchanged. `Current state` keeps working as it does.

**STEP 3.2e (new)** — rebuild `<nav class="section-index">` with current counts.

**STEP 3.3** — the "Never edit `styles.css`" prohibition is amended, not dropped: it lists the
classes a run may use and continues to forbid a run inventing new ones. The stylesheet changes
once, in this work, on user instruction — as it last did on 2026-09-14.

**STEP 2.4** — strengthened on URL capture, since 28% coverage is the failure this whole change
exposes: when a newsletter names a canonical public URL, capturing it is required, not
best-effort. When it names none, the story records that explicitly.

## Verification

- No page contains a `mail.google.com` URL, an `outlook.office365.com` / `/owa/?ItemID`
  permalink, or a Gmail address. `pages.yml` gates the first and third today; this work adds
  the Outlook pattern to that gate, since its absence is why 186 of them reached production.
  The STEP 5.3 local check for bare mailbox local-parts runs before push as always.
- Every `<article class="story">` has either a linked `<h4>` or `class="unlinked"` plus an
  explicit no-URL note. No silent third state.
- Every `.section-index` anchor resolves to a `<section id>` on the same page, and every
  timeline `.label` anchor resolves to an `<article class="story" id>`. No dangling fragments,
  and no duplicate `id` on a page.
- Section index counts equal the actual story count in each section.
- Each `.lead` is ≤60 words.
- Timelines stay newest-first and nothing is lost: post-conversion line count equals
  pre-conversion entry count minus merged duplicates, with every merge listed explicitly.
- Sidebar blocks still follow the depth rules in STEP 3.3 — topic pages link siblings bare,
  each marks its own entry `active`.
- Pages render correctly at desktop and mobile width, light and dark.

## Expected result

`research-papers.html` "Learning rules beyond backpropagation" goes from 790 words across four
renderings to ~150 words in one, with the link as the headline. Page totals should land around
6,000–8,000 words from 8,000–23,600, with every story reachable from the section index and
every available source one click from its summary.
