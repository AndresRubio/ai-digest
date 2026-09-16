# Restructure to `ai-digest/`, close the identity leak, scrub history

**Date:** 2026-09-16
**Status:** approved, pending implementation plan

## Problem

Three things, discovered together.

1. **The project is badly named on disk.** The repo is `ai-digest`, the folder is `mywiki 2`,
   and the published site lives in a nested `ai-digest/` inside it. Nothing about the layout
   tells you what the project is.
2. **The repo is public and leaks the owner's mailbox names.** 20 occurrences of two Gmail
   local-parts across 5 tracked files. Two of them are on the live website.
3. **The deploy gate does not catch it.** `pages.yml` greps for `mail.google.com` and
   `…@gmail.com`. A bare local-part has neither, so the guard passes. It was written against
   "a mailbox link or full address", not "the mailbox name".

`digest-routine/README.md:53` compounds this by claiming `sources.example.json` is published
"with only the account identity redacted". The `accounts[].email` field was redacted. The
fourteen prose `note` fields were not.

Nothing else leaked: non-newsletter correspondence appears in no tracked file, and
`sources.json` is correctly untracked and gitignored.

## Goals

- Root folder named `ai-digest`, no `mywiki` anywhere.
- No mailbox identifier in any tracked file, in the working tree **or** in git history.
- A deploy gate that actually catches this class, without itself publishing the strings.
- GitHub Pages keeps working at the same URL throughout.

## Non-goals

- Changing the public URL. `andresrubio.github.io/ai-digest/` derives its path from the
  **repo name**, not from any folder. It does not change and must not.
- Restructuring `digest-routine/`. It is well-named and well-documented; leave it.
- Changing the global git identity in `~/.gitconfig`. That would silently affect every other
  project on the machine. Repo-local only.

---

## Final layout

```
~/Desktop/projects/ai-digest/           # repo root, renamed from "mywiki 2"
├── README.md                           # NEW
├── LICENSE
├── .gitignore
├── .github/workflows/pages.yml
├── .claude/{launch.json,settings.local.json}
├── site/                               # renamed from ai-digest/  (89 files)
│   ├── index.html
│   ├── styles.css
│   ├── topics/                         # 11 pages
│   └── daily/                          # 76 pages
├── digest-routine/
│   ├── README.md, STEP1–STEP5
│   ├── sources.json (gitignored), sources.example.json
│   ├── archive/, state/
└── docs/superpowers/specs/
```

`ai-digest/` → `site/` is done with `git mv`, so all 89 files keep their history.
`mywiki 2` → `ai-digest` is a plain `mv`; git does not track the root folder's name.

---

## Part 1 — Close the leak

Runs first and ships as its own commit, so the privacy fix is live regardless of what
happens to the restructure.

### 1.1 Redact 20 occurrences in 5 files

| File | Hits | Replacement |
|---|---|---|
| `ai-digest/daily/2026-09-08.html` | 1 | "the previously configured secondary inbox" |
| `ai-digest/daily/2026-09-09.html` | 1 | "the retired account" |
| `digest-routine/sources.example.json` | 14 | "the primary inbox" / "the retired inbox" |
| `digest-routine/state/processed.json` | 3 | "the retired account" |
| `digest-routine/state/run-log.md` | 1 | "the retired account" |

Rewriting the two published daily pages is a deliberate exception to the project's
no-rewriting-history rule. It follows the precedent `digest-routine/README.md` already
records for 2026-09-14, when every Gmail link was stripped site-wide on user instruction.
Entry *facts* are unchanged; only the mailbox name is removed.

Redactions use plain prose ("the primary inbox"), not the `<primary-inbox>` angle-bracket
style used in some existing `run-log.md` lines — angle brackets need escaping in HTML, and
plain prose reads correctly in all five files. Existing angle-bracket placeholders are
already safe and are left alone.

### 1.2 Widen the deploy gate — without publishing the patterns

The guard cannot hold the literal strings: `pages.yml` is public, so a regex naming the
mailboxes would publish them in the file meant to prevent exactly that.

**`pages.yml` reads the patterns from a repository secret** at runtime:

- Secret name: `IDENTITY_PATTERNS`, an extended-regex alternation of the forbidden
  local-parts. The exact value is given to the user separately, never committed.
- The guard **fails closed**: if the secret is unset or empty, the job fails with an
  explanatory error rather than silently passing. A guard that no-ops when misconfigured is
  worse than no guard, because it looks green.
- Scope widens from `ai-digest/` to the **whole repository**, excluding `.git/`. The repo is
  public, so the site was never the only exposed surface — `state/`, `docs/` and
  `sources.example.json` are equally readable.
- The existing `mail.google.com` / `@gmail.com` patterns stay, hardcoded — they are generic
  and identify nobody.

### 1.3 Add the same check to STEP 5.3

The local check derives its patterns from `digest-routine/sources.json`, which holds the real
addresses and is gitignored. It reads `accounts[].email` plus `aliases[]`, takes the
local-parts, and greps the tracked tree for them. No literal enters any tracked file, and the
check automatically covers any inbox added later.

If `sources.json` is missing, STEP 5.3 reports the check as skipped rather than passed.

### 1.4 Make README:53 true

Reword to state what is actually published, and note that the identity is redacted from the
prose notes as well as the `email` field.

---

## Part 2 — Restructure

Ships as a second commit.

### 2.1 Moves

1. `git mv ai-digest site`
2. `mv "/Users/autobot/Desktop/projects/mywiki 2" "/Users/autobot/Desktop/projects/ai-digest"`

### 2.2 Path references — 37, all path-scoped

| File | Refs |
|---|---|
| `.github/workflows/pages.yml` | 6 — `paths:` filter, guard scope, `cp -R` source, comment |
| `digest-routine/README.md` | 7 |
| `digest-routine/STEP5-index.md` | 4 — including the §5.3 verification one-liner |
| `digest-routine/STEP1-ingest.md` | 1 |
| `digest-routine/STEP4-log.md` | 1 |
| `digest-routine/state/run-log.md` | 1 |
| `docs/superpowers/specs/2026-09-03-*.md` | 6, plus one stale `Downloads/mywiki 2` path |
| `.claude/launch.json` | 1 — `--directory` |
| `.claude/settings.local.json` | 2 — absolute paths |

**The correctness risk.** `ai-digest` also appears in strings that must not change: the
`andresrubio.github.io/ai-digest/` URLs, the git remote, the scheduled-task name, and prose
such as "the AI digest task". This is a **path-scoped** replacement of `ai-digest/` used as a
filesystem path — never a blind string substitution. Verified by confirming every
`andresrubio.github.io/ai-digest/` URL is byte-identical before and after.

This spec is exempt: its `ai-digest/…` references describe the **pre-move** state and the
move itself, so rewriting them to `site/` would make it describe something that never
happened. It is dated 2026-09-16 and reads correctly as written.

Per the user's decision, the dated files (`2026-09-03` spec, `run-log.md`) **are** updated.
This departs from the project's usual convention of leaving dated records alone; it was
chosen deliberately so no file anywhere names a stale path.

### 2.3 New root README

~30 lines: what the project is, the live URL, the three top-level folders and what each
holds, how a run happens, and the two hard rules — never writes to Gmail, no mailbox
identifiers on the public site. Links to `digest-routine/README.md` rather than restating it.

---

## Part 3 — Scrub history

Runs last, after both commits, so a single pass covers old and new commits alike.

**Scope:** every commit on `main` — one branch, one author, no tags. (11 today, plus this
spec and the two commits from Parts 1–2.)

1. **Back up first.** `git bundle create ~/Desktop/ai-digest-pre-rewrite-2026-09-16.bundle --all`,
   written outside the repo. Nothing destructive runs before this exists and is verified
   with `git bundle verify`.
2. **Rewrite** with `git-filter-repo` (`brew install git-filter-repo`), replacing the
   mailbox local-parts in historical blobs and rewriting the author on every commit to
   `2109109+AndresRubio@users.noreply.github.com`. The numeric-ID form keeps every commit
   linked to the GitHub profile, so the contribution graph survives.
   Display name `Andrés Rubio del Saz` is **unchanged** — the user asked for the address.
3. **Re-add the remote.** `git-filter-repo` removes `origin` by design; it must be restored.
4. **Force-push** `main`.
5. **Set `git config --local user.email`** to the noreply address, so future commits do not
   re-leak. Repo-local: `~/.gitconfig` sets this globally and is out of scope.

### Known limitation, accepted

A force-push is not erasure. GitHub keeps unreachable commits addressable by direct SHA until
it garbage-collects, and any existing clone or fork retains the old history. What leaks is a
mailbox *name*, not a credential, so this is acceptable — but the outcome is "no longer in
the visible history", not "gone".

---

## Verification

Ordered, and the last item is the one that actually matters.

1. `git log --follow site/index.html` — history survived the rename.
2. `grep -ri mywiki` over the tracked tree — empty.
3. Path refs to the old `ai-digest/` directory — gone. Every `andresrubio.github.io/ai-digest/`
   URL — byte-identical to before (9 in tracked files predating this spec, which adds 3 more).
4. Identity patterns — absent from the working tree **and** from `git log --all -p`.
5. Leak guard — run its logic locally against the whole repo; passes.
6. Guard fails closed — run it with the secret unset; the job must fail.
7. Site renders — preview on :8731; 11 topic pages and 76 daily pages present, 89 files total.
8. **Pages deploys green and the live URL still serves.** The restructure commit touches
   `site/**`, so it triggers a real deploy; the force-push triggers another. Both must go
   green, and `andresrubio.github.io/ai-digest/` must return 200 with the current content.

## Rollback

- Parts 1–2: ordinary commits; `git revert`.
- Part 3: restore from the bundle and force-push back. This is why step 3.1 is not optional.
- Folder rename: `mv` back, and re-point the scheduled task and Claude state directory.

## External dependencies re-pointed

Outside the repo, and easy to forget — the daily task breaks silently if missed.

| Thing | Change |
|---|---|
| `~/.claude/scheduled-tasks/ai-digest/SKILL.md` | working directory → `~/Desktop/projects/ai-digest` |
| Claude project state dir | → `-Users-autobot-Desktop-projects-ai-digest`, carrying memories and session history |
| This session's working directory | re-pointed after the move |
| GitHub repo secret | `IDENTITY_PATTERNS` must be created by the user before the guard can pass |

## Open item for the user

The GitHub Actions secret is the one step that cannot be automated — repository secrets
require the user's own credentials. The guard fails closed until it exists, which means
**the first push after Part 1 will fail its deploy** unless the secret is created first.
Sequence the secret creation before pushing Part 1.
