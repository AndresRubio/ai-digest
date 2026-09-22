# STEP 2 — Extract discrete stories

Goal: turn the messages from STEP 1 into a list of distinct, substantive stories, each
with its sources attached.

## 2.1 Split

A single newsletter issue (The Batch, MarkTechPost, TLDR) usually carries several
unrelated items. Split each message into one story per distinct artifact or event. A
single-topic announcement (an Ollama model availability email) is one story.

## 2.1a Per-source edition rules

Some senders publish more than one newsletter from a single address. Where `sources.json`
carries a rules block for a sender, apply it **before** the quality bar below.

**TLDR** (`tldr_rules` in `sources.json`) is the current case. Two editions arrive daily
from `dan@tldrnewsletter.com`:

- Identify the edition by the header line in the body — `TLDR AI <date>` — never by size
  or arrival time. Those correlate today and will drift.
- Do **not** discard the general tech edition unseen. Scan it and lift only items that
  would have qualified in the AI edition and that the AI edition has not already covered —
  genuine releases do sometimes land only there (Claude Fable 5.1's GA on 2026-09-02 is the
  worked example). Everything else in it — consumer hardware, executive moves, regulatory
  filings, market news — is dropped.
- From the AI edition, take `HEADLINES & LAUNCHES`, `DEEP DIVES & ANALYSIS`, and
  `ENGINEERING & RESEARCH` in full.
- From `MISCELLANEOUS` and `QUICK LINKS`, keep an item only if it changes what an engineer
  can build, run, or rely on. A released artifact, benchmark result, method, capability
  claim, or infrastructure shift qualifies. IPO timing, bond-market analysis, share prices,
  and personnel news do not.
- Always drop anything marked `(SPONSOR)`, job postings including TLDR's own, the referral
  and swag block, and the advertise/work-for-us footers.

The distinction to hold onto: an acquisition that changes who controls infrastructure
engineers depend on (Nvidia buying Hugging Face) is developer news; an IPO date is not.

## 2.2 The quality bar

This is the step that keeps new entries reading like the ones already on the topic pages.
A story qualifies only if **both** hold:

1. It names a specific artifact — a model, paper, benchmark, tool, library, license,
   funding round, acquisition, or policy action.
2. It carries at least one concrete, checkable claim — a benchmark number, a price, a
   parameter or active-parameter count, a context length, a license, a date, a named
   architectural detail, or a stated capability with a scope.

Reject, regardless of sender:

- Event promotion: "join us on September 8", "book your GTC pass", livestream invites,
  demo days, webinars, conference session previews.
- Consumer product tips with no technical content ("turn feedback on a photo into an
  editing prompt").
- Pricing-page marketing with no substantive change. *A genuine pricing-model change is
  a story* — Ollama moving to transparent per-token pricing is an industry datapoint;
  "our plans are great" is not.
- Restatements of something already on the topic pages with nothing new added.

When a message is entirely rejected, it still counts toward "newsletters scanned" in the
daily log, and its id still goes into `processed.json` — it has been dealt with.

## 2.3 De-duplicate across messages

Two newsletters covering the same release is one story with two sources, not two stories.
Match on artifact name, not headline wording.

The same issue of the same newsletter arriving at two connected inboxes is *one* source,
not two. STEP 1 should have collapsed these already; if a pair reaches you here, keep a
single citation (prefer the account the user reads first, listed first under `accounts`
in `sources.json`) and do not cite the same issue twice.

Also check against what is already published: read the `<ul class="timeline index">`
lines from the last 14 days on the candidate topic pages. Those lines carry only a date
and a linked label — the summary lives in the `<article class="story">` the label points
at, so match on the label and follow the `#id` to read the story itself. If the artifact
is already there, do not create a second story. If the new message adds a material fact (a
benchmark that was missing, weights that have now shipped), **update that story's prose
and add your source to its `.sources`** rather than adding a duplicate, and say so in the
daily log. STEP 3 §3.2-story has a step for this, immediately before N1.

## 2.4 Write each story

For each surviving story, produce:

- `date` — the date of the underlying announcement where the newsletter states one,
  otherwise the message date.
- `label` — a headline of roughly 6–14 words, in the style already on the pages:
  artifact name first, then the claim. E.g. *"Inkling-Small (276B/12B active) beats its
  own 975B teacher"*.
- `summary` — two to four sentences. Lead with what shipped and the hard numbers. Name
  the honest trade-off where the source states one. Match the register of the existing
  pages: technical, specific, no hype adjectives.
- `url` — the canonical public URL of the artifact itself: the vendor post, the paper,
  the repository, the release notes. **Capturing it is required, not best-effort.** When
  the issue names one, this field gets it; STEP 3 renders it as the story's headline link,
  and a story whose headline is a dead end is the single failure this whole structure
  exists to prevent. Where every link in the issue is a tracking redirect, see STEP 1.6a —
  resolve the publisher's own archive if it has one. **Never invent a URL and never
  research the open web for one.** When the issue genuinely names none and none can be
  resolved, write the field as the explicit string `no public URL given` rather than
  leaving it empty or absent: an empty field reads as an oversight, and STEP 3 needs to
  tell "we looked and there is none" apart from "nobody looked". That string is what
  reaches the page, inside `.sources`, beside a story marked `class="story unlinked"`.
  **Never substitute a mailbox permalink for a missing source.** 192
  `outlook.office365.com` links reached the public site that way before 2026-09-20 — dead
  for every reader, and a mailbox identifier published on the open web. An honestly
  unlinked story beats a link only the owner can open.
- `sources` — one entry per contributing message, as a **display name only**: the
  newsletter name plus a short date, e.g. `Ollama (Aug 29)`, rendered as plain text.
  **Never emit a `mail.google.com` link** — see STEP 1.6; the site is public and a
  mailbox link exposes both the account address and a private message. The newsletter is
  never the link; `url` is.
- `topic` — the target topic page slug, decided in STEP 3.

**When one issue yields several stories, bind each URL to its story as you write it.**
A single newsletter commonly produces three or four stories, and the per-item anchors you
resolve under STEP 1.6a come back as a *list*. Match each one to its story by reading the
anchor's own text and confirming it names that story's artifact — never by walking the two
lists in parallel and pairing them off in order. The orders are not the same. On 2026-09-21
three stories from one issue were written out rotated by one, each carrying the next
story's anchor, and every one of those URLs was real, well-formed and resolving: no
downstream check caught it, and none can. If a story has no anchor of its own, give it the
bare issue URL **as its `.sources` citation**, never a leftover anchor belonging to a
different story. That fallback does not make it a headline link: STEP 1.6a allows the bare
issue page as a headline only where the issue page is itself the artifact, and otherwise
says to use the unlinked form. `url` stays `no public URL given`.

Escape `&` as `&amp;` and use `&mdash;` / `&rarr;` entities to match the existing markup.
