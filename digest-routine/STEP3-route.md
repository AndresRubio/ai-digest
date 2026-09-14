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
"Security benchmarks" and "Product search & e-commerce" were added. A new page also needs
adding to the sidebar `<ul>` of **every** page in the site and to the index topic list.

## 3.2 Per touched page, in order

**a. Prepend the timeline entry.** Insert at the top of `<ul class="timeline">`:

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

**b. Rewrite the relevant `<h3>` section.** These are living prose, not logs. Work the
new story into the existing argument — extend the thread, note where it confirms or
contradicts what the section already claims, and keep the section readable end to end.
Do not append a stranded sentence at the end.

**c. Rewrite the `Current state` div.** Same discipline, one level up: it opens with the
most recent cycle and narrates backwards. Lead it with today's stories and their
through-line, then compress what was previously leading. This div is allowed to be long
— the existing ones are — but every run should leave it coherent rather than accreted.

**d. Update the meta line** to `<div class="meta">Last updated: YYYY-MM-DD</div>`.

## 3.3 Constraints

- Never edit `styles.css`. Every class you need already exists: `timeline`, `date`,
  `label`, `sources`, `current-state`, `changed-today`, `meta`.
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
