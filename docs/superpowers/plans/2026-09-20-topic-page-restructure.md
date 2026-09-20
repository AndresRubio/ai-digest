# Topic Page Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every story on a topic page appear exactly once, under its heading, with its real public source as the headline link — and remove the 186 mailbox permalinks currently published.

**Architecture:** This repo has no build step, no tests, and no scripts — 90 HTML files, one CSS file, five Markdown instruction files. So "tests" here means a **structural checker**: `digest-routine/check-structure.py`, stdlib-only, asserting the spec's invariants across `site/`. It is written first, fails against today's pages, and each conversion task is done when the checker passes for that page. The checker then becomes a permanent STEP 5.3 gate, so the daily routine cannot regress the structure.

**Tech Stack:** Static HTML5, one hand-written `styles.css` (no framework, no JS), Python 3.9 stdlib only (`re`, `html.parser`, `glob`, `sys`, `json`), GitHub Actions, GitHub Pages.

## Global Constraints

- **Python 3.9.6 stdlib only.** No pip installs, no venv. `python3` on this machine is 3.9.6 — no `match`, no `str.removeprefix` in f-strings, no `list[str]` annotations at runtime.
- **No JavaScript is added to the site.** It has none today.
- **Call grep as `/usr/bin/grep`.** The shell shadows `grep` with ugrep run `--ignore-files`, which honours `.gitignore` and silently skips paths. A bare `grep -r` reports clean for the wrong reason.
- **No mailbox identifier may reach `site/`**: no `mail.google.com`, no `@gmail.com`, no `outlook.office365.com`, no `/owa/?ItemID`. Newsletter names are plain text, never links.
- **Never modify or remove an existing CSS rule.** `site/daily/` (78 files) and `site/index.html` depend on `.current-state`, `.changed-today`, `.meta`, `.sources`, `ul.timeline` and the sidebar rules. Only add.
- **Never rewrite a historical timeline entry's wording or date.** Moving an entry's summary into a story item is a move, not a rewrite.
- **Do not touch** `site/daily/*.html` or `site/index.html`.
- **`Current state` blocks are already correct** — visible portion 492–565 words behind a working `<details>`. Leave them alone.
- **`.lead` hard cap: 60 words.** Story summary: 2–4 sentences.
- **A section shows its newest 3 stories**; older ones go inside `<details>`.
- **Never fabricate a source URL.** No real URL → `class="unlinked"` on the `<article>` and an explicit note in `.sources`.
- Commit after every task. Do not push until the final verification task.

---

### Task 1: Strip the 192 mailbox permalinks from the published site

This is a live privacy fix and lands first, independent of everything else. All eleven topic pages carry `outlook.office365.com/owa/?ItemID=…` links — dead for readers, and a mailbox identifier on a public site.

**Files:**
- Modify: all 11 files in `site/topics/*.html`
- Create: `digest-routine/check-structure.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `check-structure.py` with `check_no_mailbox_links(paths) -> list[str]` returning a list of human-readable failure strings, empty when clean. Later tasks add more `check_*(paths) -> list` functions with the same signature and a `main()` that runs them all.

- [ ] **Step 1: Write the failing check**

Create `digest-routine/check-structure.py`:

```python
#!/usr/bin/env python3
"""Structural gate for site/topics/*.html. Stdlib only, Python 3.9 compatible.

Run:  python3 digest-routine/check-structure.py
Exit: 0 = all checks pass, 1 = at least one failure (failures printed).
"""
import glob
import re
import sys

TOPICS = "site/topics/*.html"

MAILBOX = re.compile(
    r"mail\.google\.com|outlook\.office365\.com|outlook\.live\.com|/owa/\?ItemID"
    r"|[A-Za-z0-9._%+-]+@gmail\.com"
)


def check_no_mailbox_links(paths):
    """No mailbox URL or address may appear in a published page."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        for i, line in enumerate(text.splitlines(), 1):
            if MAILBOX.search(line):
                out.append("%s:%d mailbox identifier in published page" % (p, i))
    return out


CHECKS = [check_no_mailbox_links]


def main():
    paths = sorted(glob.glob(TOPICS))
    if not paths:
        print("no pages matched %s" % TOPICS)
        return 1
    failures = []
    for check in CHECKS:
        found = check(paths)
        print("%-34s %s" % (check.__name__, "PASS" if not found else "FAIL (%d)" % len(found)))
        failures.extend(found)
    for f in failures[:40]:
        print("  " + f)
    if len(failures) > 40:
        print("  ... and %d more" % (len(failures) - 40))
    print("\n%d page(s) checked, %d failure(s)" % (len(paths), len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it to verify it fails**

```bash
python3 digest-routine/check-structure.py
```

Expected: `check_no_mailbox_links  FAIL (186)`, exit 1, listing `site/topics/…:NNN mailbox identifier in published page`.

- [ ] **Step 3: Strip the links, keep the source names**

Each occurrence looks like:

```html
<div class="sources"><a href="https://outlook.office365.com/owa/?ItemID=…&amp;exvsurl=1&amp;viewmodel=ReadMessageItem">MarkTechPost newsletter</a></div>
```

Replace the whole `<a>` element with its own link text, leaving the surrounding `.sources` div and any non-mailbox links untouched:

```bash
python3 - <<'PY'
import glob, re
A = re.compile(
    r'<a\s+href="[^"]*(?:outlook\.office365\.com|outlook\.live\.com|/owa/\?ItemID)[^"]*"\s*>(.*?)</a>',
    re.S,
)
total = 0
for p in sorted(glob.glob("site/topics/*.html")):
    s = open(p, encoding="utf-8").read()
    s2, n = A.subn(lambda m: m.group(1).strip(), s)
    if n:
        open(p, "w", encoding="utf-8").write(s2)
    total += n
    print("%-46s %3d stripped" % (p, n))
print("total:", total)
PY
```

Expected total: 186.

- [ ] **Step 4: Run the checker to verify it passes**

```bash
python3 digest-routine/check-structure.py
```

Expected: `check_no_mailbox_links  PASS`, exit 0.

- [ ] **Step 5: Confirm no source name was lost and no other link was harmed**

```bash
/usr/bin/grep -c '<div class="sources">' site/topics/*.html
/usr/bin/grep -roE 'href="https?://[^"]+"' site/topics/ | wc -l
```

Expected: the `.sources` count is unchanged from before the edit (capture it first with the same command on `git stash`-ed state if unsure), and the remaining href count equals the pre-edit count minus 186.

- [ ] **Step 6: Commit**

```bash
git add digest-routine/check-structure.py site/topics/
git commit -m "Strip 186 Outlook mailbox permalinks from the published topic pages

They were dead links for every reader and put a mailbox item identifier on a
public site -- the exact failure the project's second rule forbids. The Gmail-era
guard never matched them because the project migrated from Outlook before it was
written. Source names are kept as plain text; no entry wording or date changed.

Adds check-structure.py, which fails on any mailbox identifier under site/.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Add the Outlook pattern to the CI deploy guard

The leak reached production because `pages.yml` only knows `mail.google.com`. Close that hole so it cannot recur.

**Files:**
- Modify: `.github/workflows/pages.yml:44-52` (the `site/` strictness block)

**Interfaces:**
- Consumes: nothing.
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Widen the site/ pattern**

In `.github/workflows/pages.yml`, in the *first* grep (the one scoped to `site/`), replace:

```bash
          grep -rInE 'mail\.google\.com|[A-Za-z0-9._%+-]+@gmail\.com' \
               --exclude-dir=.git --exclude=pages.yml site/
```

with:

```bash
          grep -rInE 'mail\.google\.com|outlook\.office365\.com|outlook\.live\.com|/owa/\?ItemID|[A-Za-z0-9._%+-]+@gmail\.com' \
               --exclude-dir=.git --exclude=pages.yml site/
```

Leave the second grep (whole-repo, `@gmail.com` only) exactly as it is. Its comment explains why it must stay narrow: this repo's own docs legitimately name `mail.google.com` as the pattern the guard catches, and widening it would fail the build on its documentation. The same now applies to the Outlook patterns, which this plan and spec both name.

- [ ] **Step 2: Update the comment above the checks**

Replace the comment line:

```
      # CI screens for two things: a real Gmail address anywhere in the repo, and
      # a mailbox URL (mail.google.com) anywhere in the published site. Both
```

with:

```
      # CI screens for two things: a real Gmail address anywhere in the repo, and
      # a mailbox URL anywhere in the published site -- Gmail (mail.google.com)
      # and Outlook Web (outlook.office365.com, /owa/?ItemID). The Outlook
      # patterns were added 2026-09-20 after 186 OWA permalinks, left over from
      # the pre-Gmail era, were found live on all eleven topic pages. Both
```

- [ ] **Step 3: Verify the widened pattern locally, exactly as the runner will**

```bash
set +e
/usr/bin/grep -rInE 'mail\.google\.com|outlook\.office365\.com|outlook\.live\.com|/owa/\?ItemID|[A-Za-z0-9._%+-]+@gmail\.com' --exclude-dir=.git --exclude=pages.yml site/
echo "exit=$?  (1 = clean)"
set -e
```

Expected: no output, `exit=1`.

- [ ] **Step 4: Verify the workflow is still valid YAML**

```bash
python3 -c "import json,sys;
import xml.etree.ElementTree  # noqa
print(open('.github/workflows/pages.yml').read().count('runs-on'), 'jobs have runs-on')"
/usr/bin/grep -n 'runs-on\|^jobs:\|^  [a-z]*:$' .github/workflows/pages.yml
```

Expected: 3 jobs (`guard`, `build`, `deploy`), each with `runs-on`. (PyYAML is not installed; this is a structural sanity check, and the real validation is GitHub accepting the workflow on push in Task 12.)

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/pages.yml
git commit -m "Teach the deploy guard the Outlook mailbox URL patterns

186 OWA permalinks reached the public site because the site/ gate matched only
mail.google.com. Scope stays on site/ for the same reason the Gmail URL check
does: the repo's own docs name these patterns, and a whole-tree match would fail
the build on its own documentation.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Add the new CSS, changing no existing rule

**Files:**
- Modify: `site/styles.css` (append only)

**Interfaces:**
- Consumes: nothing.
- Produces: the classes every later task's markup relies on — `.section-index` (with `.n`), `.topic-section` (with `.lead`), `.story` (with `.when`, `.unlinked`, `.via`), `ul.timeline.index`.

- [ ] **Step 1: Record the current rule set so the "append only" claim is checkable**

```bash
/usr/bin/grep -oE '^[^{]+\{' site/styles.css | sed 's/ *{$//' | sort > /tmp/css-selectors-before.txt
wc -l /tmp/css-selectors-before.txt
```

- [ ] **Step 2: Append the new rules**

Append to the end of `site/styles.css`:

```css

/* ---------------------------------------------------------------------------
   Topic-page story structure (added 2026-09-20, on user instruction).
   A story appears once, under its heading, with its source as the headline
   link. Nothing above this comment was modified: site/daily/ and index.html
   depend on those rules.
   --------------------------------------------------------------------------- */

/* In-page section index, sits under the Current state block */
.section-index { margin: 28px 0 8px; padding: 14px 18px; background: var(--sidebar-bg);
  border: 1px solid var(--border); border-radius: 6px; }
.section-index h2 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--muted); margin: 0 0 10px; border: 0; padding: 0; }
.section-index ul { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 6px 8px; }
.section-index a { font-size: 13px; text-decoration: none; background: var(--bg);
  border: 1px solid var(--border); border-radius: 20px; padding: 4px 11px; display: inline-block; }
.section-index a:hover { border-color: var(--accent); background: #ddf4ff; }
.section-index .n { color: var(--muted); font-variant-numeric: tabular-nums; }

/* A topic section: short synthesis lead, then linked stories */
.topic-section { margin-top: 34px; scroll-margin-top: 16px; }
.topic-section > h3 { margin-top: 0; }
.topic-section > .lead { max-width: 72ch; margin: 0.3em 0 1.2em; }

/* One story: date, linked headline, summary, sources */
.story { padding: 14px 0 14px 16px; border-left: 2px solid var(--border);
  margin-bottom: 4px; scroll-margin-top: 16px; }
.story:hover { border-left-color: var(--accent); }
.story h4 { font-size: 15.5px; margin: 0 0 5px; line-height: 1.4; font-weight: 600; }
.story h4 a { text-decoration: none; }
.story h4 a:hover { text-decoration: underline; }
.story h4 a[href]::after { content: " \2197"; font-size: 0.8em; color: var(--muted); font-weight: 400; }
.story .when { color: var(--muted); font-size: 12px; font-variant-numeric: tabular-nums;
  text-transform: uppercase; letter-spacing: 0.04em; display: block; margin-bottom: 3px; }
.story p { margin: 0 0 7px; max-width: 72ch; font-size: 14.5px; }
.story .sources { font-size: 12.5px; }
.story .sources a { margin-right: 0; }
.story .via { color: var(--muted); }

/* Older stories in a section fold away */
.topic-section details { margin-top: 10px; border-top: 1px solid var(--border); padding-top: 12px; }
.topic-section summary { cursor: pointer; font-size: 12px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }
.topic-section summary:hover { color: var(--accent); }

/* Timeline in index form: one line per story */
ul.timeline.index li { padding: 7px 0; display: grid; grid-template-columns: 92px 1fr;
  gap: 12px; align-items: baseline; }
ul.timeline.index .label { font-weight: 500; font-size: 14px; }
ul.timeline.index .label a { text-decoration: none; }
ul.timeline.index .label a:hover { text-decoration: underline; }

/* Narrow screens: the sidebar stacks and the timeline index drops to one column */
@media (max-width: 720px) {
  .layout { grid-template-columns: 1fr; }
  aside.sidebar { position: static; height: auto; }
  main { padding: 24px 16px; }
  ul.timeline.index li { grid-template-columns: 1fr; gap: 2px; }
}
```

- [ ] **Step 3: Verify no existing selector was changed or removed**

```bash
/usr/bin/grep -oE '^[^{]+\{' site/styles.css | sed 's/ *{$//' | sort > /tmp/css-selectors-after.txt
comm -23 /tmp/css-selectors-before.txt /tmp/css-selectors-after.txt
echo "^^ must be EMPTY (nothing removed)"
```

Expected: no output. Every pre-existing selector still present.

- [ ] **Step 4: Verify braces balance**

```bash
python3 -c "
s=open('site/styles.css').read()
print('open',s.count('{'),'close',s.count('}'),'balanced',s.count('{')==s.count('}'))"
```

Expected: `balanced True`.

- [ ] **Step 5: Commit**

```bash
git add site/styles.css
git commit -m "Add CSS for the story-item topic page structure

Append only: section index, topic-section with lead, story items, folded
older stories, timeline index form, and a narrow-screen block. Verified that
no pre-existing selector was modified or removed -- site/daily/ (78 files) and
index.html depend on them.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Extend the checker with every structural invariant

Write the full gate before converting any page, so conversion has a target that fails loudly.

**Files:**
- Modify: `digest-routine/check-structure.py`

**Interfaces:**
- Consumes: `check_no_mailbox_links(paths)` from Task 1.
- Produces: `check_anchors_resolve`, `check_index_counts`, `check_lead_length`, `check_story_link_state`, `check_timeline_order`, `check_no_wall_of_text`, `check_sidebar_consistency` — all `(paths) -> list[str]`, all registered in `CHECKS`. Plus module constants `SECTION_RE`, `STORY_RE`, `LEAD_RE` used by no one else.

- [ ] **Step 1: Write the checks**

Replace the `CHECKS = [check_no_mailbox_links]` line in `digest-routine/check-structure.py` with the following, inserted above it:

```python
SECTION_RE = re.compile(r'<section class="topic-section" id="([^"]+)">(.*?)</section>', re.S)
STORY_RE = re.compile(r'<article class="story([^"]*)" id="([^"]+)">(.*?)</article>', re.S)
LEAD_RE = re.compile(r'<p class="lead">(.*?)</p>', re.S)
INDEX_LINK_RE = re.compile(r'<a href="#([^"]+)">(.*?)</a>', re.S)
TIMELINE_INDEX_RE = re.compile(r'<ul class="timeline index">(.*?)</ul>', re.S)
SECTION_INDEX_RE = re.compile(r'<nav class="section-index">(.*?)</nav>', re.S)
COUNT_RE = re.compile(r'<span class="n">(\d+)</span>')


def _text(html_fragment):
    return re.sub(r"<[^>]+>", " ", html_fragment)


def _words(html_fragment):
    return len(_text(html_fragment).split())


def _converted(text):
    """A page is converted once it has at least one topic-section."""
    return '<section class="topic-section"' in text


def check_anchors_resolve(paths):
    """Every #fragment on a page points at an id on that same page, and ids are unique."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        if not _converted(text):
            out.append("%s not converted yet (no topic-section)" % p)
            continue
        ids = re.findall(r'<(?:section|article)[^>]*\sid="([^"]+)"', text)
        dupes = set(i for i in ids if ids.count(i) > 1)
        for d in sorted(dupes):
            out.append("%s duplicate id %r" % (p, d))
        known = set(ids)
        for frag, _label in INDEX_LINK_RE.findall(text):
            if frag not in known:
                out.append("%s dangling fragment #%s" % (p, frag))
    return out


def check_index_counts(paths):
    """Each section-index chip's count equals that section's real story count."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        if not _converted(text):
            continue
        real = {}
        for sid, body in SECTION_RE.findall(text):
            real[sid] = len(STORY_RE.findall(body))
        nav = SECTION_INDEX_RE.search(text)
        if not nav:
            out.append("%s has sections but no section-index nav" % p)
            continue
        listed = set()
        for li in re.findall(r"<li>(.*?)</li>", nav.group(1), re.S):
            m = INDEX_LINK_RE.search(li)
            c = COUNT_RE.search(li)
            if not m or not c:
                out.append("%s section-index entry missing link or count" % p)
                continue
            sid, claimed = m.group(1), int(c.group(1))
            listed.add(sid)
            if sid not in real:
                out.append("%s index points at unknown section #%s" % (p, sid))
            elif real[sid] != claimed:
                out.append("%s #%s index says %d stories, page has %d"
                           % (p, sid, claimed, real[sid]))
        for sid in real:
            if sid not in listed:
                out.append("%s section #%s missing from the index" % (p, sid))
    return out


def check_lead_length(paths):
    """Every section lead is 60 words or fewer, and every section has exactly one."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        if not _converted(text):
            continue
        for sid, body in SECTION_RE.findall(text):
            leads = LEAD_RE.findall(body)
            if len(leads) != 1:
                out.append("%s #%s has %d leads, expected 1" % (p, sid, len(leads)))
                continue
            n = _words(leads[0])
            if n > 60:
                out.append("%s #%s lead is %d words (cap 60)" % (p, sid, n))
    return out


def check_story_link_state(paths):
    """A story is either linked or explicitly marked unlinked. No silent third state."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        if not _converted(text):
            continue
        for classes, sid, body in STORY_RE.findall(text):
            head = re.search(r"<h4>(.*?)</h4>", body, re.S)
            if not head:
                out.append("%s story #%s has no <h4>" % (p, sid))
                continue
            linked = 'href="http' in head.group(1)
            marked = "unlinked" in classes
            if linked and marked:
                out.append("%s story #%s is linked but marked unlinked" % (p, sid))
            elif not linked and not marked:
                out.append("%s story #%s has no link and no unlinked marker" % (p, sid))
            elif not linked and "no public URL" not in body:
                out.append("%s story #%s unlinked without a stated reason" % (p, sid))
            if not re.search(r'<span class="when">\d{4}-\d{2}-\d{2}</span>', body):
                out.append("%s story #%s missing a well-formed date" % (p, sid))
    return out


def check_timeline_order(paths):
    """The timeline index is present, newest-first, and links only to real stories."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        if not _converted(text):
            continue
        m = TIMELINE_INDEX_RE.search(text)
        if not m:
            out.append("%s has no <ul class=\"timeline index\">" % p)
            continue
        story_ids = set(sid for _c, sid, _b in STORY_RE.findall(text))
        dates = re.findall(r'<span class="date">(\d{4}-\d{2}-\d{2})</span>', m.group(1))
        if dates != sorted(dates, reverse=True):
            for i in range(1, len(dates)):
                if dates[i] > dates[i - 1]:
                    out.append("%s timeline out of order at %s after %s"
                               % (p, dates[i], dates[i - 1]))
                    break
        for frag, _label in INDEX_LINK_RE.findall(m.group(1)):
            if frag not in story_ids:
                out.append("%s timeline links #%s, which is not a story" % (p, frag))
    return out


def check_no_wall_of_text(paths):
    """No paragraph anywhere on a topic page runs past 350 words."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        for para in re.findall(r"<p[^>]*>(.*?)</p>", text, re.S):
            n = _words(para)
            if n > 350:
                out.append("%s paragraph of %d words (cap 350)" % (p, n))
    return out


def check_sidebar_consistency(paths):
    """Topic pages link siblings bare and mark exactly their own entry active."""
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        own = p.split("/")[-1]
        aside = re.search(r"<aside class=\"sidebar\">(.*?)</aside>", text, re.S)
        if not aside:
            out.append("%s has no sidebar" % p)
            continue
        block = aside.group(1)
        if 'href="topics/' in block or 'href="../topics/' in block:
            out.append("%s sidebar uses a non-sibling path for topic links" % p)
        active = re.findall(r'<a href="([^"]+)" class="active">', block)
        if active != [own]:
            out.append("%s marks %r active, expected [%r]" % (p, active, own))
    return out


CHECKS = [
    check_no_mailbox_links,
    check_anchors_resolve,
    check_index_counts,
    check_lead_length,
    check_story_link_state,
    check_timeline_order,
    check_no_wall_of_text,
    check_sidebar_consistency,
]
```

- [ ] **Step 2: Run it to verify it fails for the right reasons**

```bash
python3 digest-routine/check-structure.py
```

Expected: `check_no_mailbox_links PASS` (Task 1 fixed that), `check_sidebar_consistency PASS` (sidebars are already correct), and `check_anchors_resolve FAIL (11)` — every page reporting `not converted yet (no topic-section)`. The count-, lead-, story- and timeline- checks report PASS only because they skip unconverted pages; that is intended and Task 5 turns them live.

- [ ] **Step 3: Verify the checker itself is sound, against a known-good fixture**

```bash
mkdir -p /tmp/fixture/site/topics && cat > /tmp/fixture/site/topics/x.html <<'HTML'
<aside class="sidebar"><ul><li><a href="x.html" class="active">X</a></li></ul></aside>
<nav class="section-index"><ul><li><a href="#alpha">Alpha <span class="n">1</span></a></li></ul></nav>
<section class="topic-section" id="alpha">
<p class="lead">Short lead.</p>
<article class="story" id="thing">
<span class="when">2026-09-15</span>
<h4><a href="https://example.com/">Thing ships</a></h4>
<p>It shipped.</p>
<div class="sources"><a href="https://example.com/">Vendor</a></div>
</article>
</section>
<ul class="timeline index"><li><span class="date">2026-09-15</span><span class="label"><a href="#thing">Thing ships</a></span></li></ul>
HTML
cd /tmp/fixture && python3 /Users/autobot/Desktop/projects/ai-digest/digest-routine/check-structure.py; echo "exit=$?"
```

Expected: every check PASS, `exit=0`. If any check fails here, the check is wrong, not the fixture — fix the checker before converting real pages.

- [ ] **Step 4: Verify the checker actually catches breakage**

```bash
cd /tmp/fixture && sed -i '' 's/<span class="n">1<\/span>/<span class="n">7<\/span>/' site/topics/x.html
python3 /Users/autobot/Desktop/projects/ai-digest/digest-routine/check-structure.py; echo "exit=$?"
```

Expected: `check_index_counts FAIL (1)` reporting `#alpha index says 7 stories, page has 1`, `exit=1`. Then `rm -rf /tmp/fixture`.

- [ ] **Step 5: Commit**

```bash
cd /Users/autobot/Desktop/projects/ai-digest
git add digest-routine/check-structure.py
git commit -m "Add the full structural gate for converted topic pages

Anchors resolve and are unique, index counts match reality, leads stay under
60 words, every story is either linked or explicitly marked unlinked, the
timeline index is newest-first and points only at real stories, no paragraph
exceeds 350 words, sidebars keep their depth rules. Verified against a
known-good fixture and a deliberately broken one.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Convert the pilot page — `research-papers.html`

Smallest page (30 entries, 10 sections, 8,888 words). It establishes the shape every later page copies, so it gets its own review gate.

**Files:**
- Modify: `site/topics/research-papers.html`

**Interfaces:**
- Consumes: CSS classes from Task 3, checker from Task 4.
- Produces: the canonical converted-page shape that Tasks 6–15 replicate verbatim in structure.

- [ ] **Step 1: Inventory the page before touching it**

```bash
cd /Users/autobot/Desktop/projects/ai-digest
python3 - <<'PY'
import re
p = "site/topics/research-papers.html"
s = open(p, encoding="utf-8").read()
tl = re.search(r'<ul class="timeline">(.*?)</ul>', s, re.S).group(1)
lis = re.findall(r"<li>(.*?)</li>", tl, re.S)
print("timeline entries:", len(lis))
print("h3 sections:", len(re.findall(r"<h3>", s)))
for li in lis:
    d = re.search(r'<span class="date">([\d-]+)</span>', li).group(1)
    lab = re.sub(r"<[^>]+>", "", re.search(r'<span class="label">(.*?)</span>', li, re.S).group(1))
    url = re.search(r'href="(https?://[^"]+)"', li)
    print("%s  %-72s %s" % (d, lab[:72], "LINK" if url else "-- no url --"))
PY
```

Record this output. It is the source of truth for Step 5's no-loss check.

- [ ] **Step 2: Build the converted page**

Working through the inventory, by hand (this is judgement, not a script):

1. Keep `<head>`, the sidebar, `<h1>`, `.meta`, and the whole `.current-state` div **byte-identical**.
2. Insert the `<nav class="section-index">` immediately after `</div>` of `.current-state`.
3. For each existing `<h3>`, emit a `<section class="topic-section" id="SLUG">` where `SLUG` is the kebab-case heading (`Learning rules beyond backpropagation` → `learning-rules-beyond-backpropagation`).
4. Reduce that section's existing prose to one `<p class="lead">` of **60 words or fewer**. Before cutting, move any fact the prose carries that the matching timeline summary lacks into that story's summary.
5. Emit each story as an `<article>`, newest first, the first three visible and the rest inside `<details>`.
6. Merge duplicate entries for one artifact into a single story carrying every source — the two PC-ALM entries (2026-09-15 and 2026-09-14) are the known case on this page.
7. Rewrite the timeline as `<ul class="timeline index">`, one line per story, newest-first, each linking `#story-id`.

The exact target markup:

```html
      <nav class="section-index">
        <h2>On this page</h2>
        <ul>
          <li><a href="#learning-rules-beyond-backpropagation">Learning rules beyond backpropagation <span class="n">1</span></a></li>
        </ul>
      </nav>

      <section class="topic-section" id="learning-rules-beyond-backpropagation">
        <h3>Learning rules beyond backpropagation</h3>
        <p class="lead">Local learning rules have always worked at toy depth and collapsed as networks grow &mdash; which is exactly where backprop&rsquo;s global backward pass earns its cost. Judge entries here on depth first.</p>

        <article class="story" id="pc-alm">
          <span class="when">2026-09-15</span>
          <h4><a href="https://pub.sakana.ai/pc-alm/">Sakana&rsquo;s PC-ALM trains 1,000-layer networks with a layer-local rule and no backward pass</a></h4>
          <p>Reaches <strong>77.75%</strong> on the repository&rsquo;s reference cell against 78.66% for backpropagation and 68.13% for standard predictive coding &mdash; nine tenths of the gap closed while removing the global backward pass entirely. Each layer gets a feedback control dynamical system that distributes supervision credit locally, and that holds to 1,000 layers, well past where earlier local rules stopped competing.</p>
          <p>Two limits travel with it: residual MLPs rather than transformers, and no wall-clock or energy comparison &mdash; which is the whole reason to want a local rule. MIT-licensed JAX, runs on CPU.</p>
          <div class="sources"><a href="https://pub.sakana.ai/pc-alm/">Sakana AI</a> &middot; <a href="https://arxiv.org/abs/2605.31022">arXiv</a> &middot; <a href="https://github.com/SakanaAI/pc-alm">GitHub</a> &middot; <span class="via">via TLDR AI (Sep 15), MarkTechPost (Sep 17)</span></div>
        </article>

        <details>
          <summary>Earlier in this section (2)</summary>
          <!-- older <article class="story" id="…"> items, newest first, same shape -->
        </details>
      </section>
```

An entry with no real public URL takes this shape instead:

```html
        <article class="story unlinked" id="static-retrieval-8mb">
          <span class="when">2026-08-13</span>
          <h4>An 8MB retrieval model embeds all of English Wikipedia on a laptop in under eight minutes</h4>
          <p>Training on 660 million pairs then quantizing aggressively yields a static retrieval model of 8MB. Static embeddings give up the contextual sensitivity of a transformer for size.</p>
          <div class="sources"><span class="via">via MLOps Community (Aug 13) &mdash; no public URL given</span></div>
        </article>
```

And the timeline:

```html
      <h2>Timeline</h2>
      <ul class="timeline index">
        <li><span class="date">2026-09-15</span><span class="label"><a href="#pc-alm">Sakana&rsquo;s PC-ALM trains 1,000-layer networks with no backward pass</a></span></li>
      </ul>
```

- [ ] **Step 3: Run the checker**

```bash
python3 digest-routine/check-structure.py
```

Expected: `research-papers.html` produces no failures. The other ten still report `not converted yet`.

- [ ] **Step 4: Verify no story and no source was lost**

```bash
python3 - <<'PY'
import re, subprocess
p = "site/topics/research-papers.html"
old = subprocess.run(["git", "show", "HEAD:" + p], capture_output=True, text=True).stdout
new = open(p, encoding="utf-8").read()

def urls(s):
    return set(re.findall(r'href="(https?://[^"]+)"', s))

old_tl = re.search(r'<ul class="timeline">(.*?)</ul>', old, re.S).group(1)
print("old timeline entries:", len(re.findall(r"<li>", old_tl)))
print("new stories:         ", len(re.findall(r'<article class="story', new)))
print("new timeline lines:  ", len(re.findall(r"<li>", re.search(r'<ul class="timeline index">(.*?)</ul>', new, re.S).group(1))))
lost = urls(old) - urls(new)
print("source URLs lost:", len(lost))
for u in sorted(lost):
    print("  LOST", u)
PY
```

Expected: `source URLs lost: 0`. New story count equals old entry count minus merges, and new timeline lines equals new story count. Any lost URL is a defect — restore it before continuing.

- [ ] **Step 5: Verify it renders, in both themes and at phone width**

```bash
python3 -m http.server 8731 --directory site
```

If the sandbox refuses the server (it has before, with `PermissionError` on `os.getcwd()`), run it with the sandbox disabled for that one call. Then open `http://localhost:8731/topics/research-papers.html` in the browser pane and confirm: the section index chips jump to their sections; a timeline line jumps to its story and expands the `<details>` if it is folded; the layout has no horizontal scroll at 375px; every headline link opens a real vendor or arXiv page, never an inbox.

- [ ] **Step 6: Commit**

```bash
git add site/topics/research-papers.html
git commit -m "Convert research-papers to linked story items

Ten sections reduced to <=60-word leads with their stories beneath them,
newest three visible and the rest folded. The two PC-ALM entries merge into
one story carrying both sources. Timeline becomes a one-line index into the
page. No source URL lost; Current state untouched.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Tasks 6–15: Convert the remaining ten pages (one page per task)

Each page is its own task, its own checker run, and its own commit, in ascending size so the shape is well-practised before the hardest pages. **Follow Task 5's Steps 1–6 exactly**, substituting the page and its known merge cases. Do not batch pages into one commit: a reviewer must be able to reject one page while approving its neighbour.

| Task | Page | Entries | Sections | Words |
|---|---|---|---|---|
| 6 | `training-and-rl.html` | 29 | 6 | 7,765 |
| 7 | `embodied-and-robotics.html` | 32 | 7 | 8,824 |
| 8 | `applications.html` | 43 | 9 | 11,653 |
| 9 | `industry-and-business.html` | 50 | 6 | 13,282 |
| 10 | `evals-and-benchmarks.html` | 52 | 9 | 14,128 |
| 11 | `infrastructure.html` | 65 | 11 | 17,183 |
| 12 | `safety-and-policy.html` | 66 | 12 | 19,625 |
| 13 | `agents.html` | 84 | 12 | 19,857 |
| 14 | `model-releases.html` | 92 | 11 | 21,511 |
| 15 | `tools-and-devex.html` | 98 | 11 | 23,643 |

Two page-specific notes:

- **`agents.html` and `tools-and-devex.html` overlap heavily** — "The agentic harness" exists on both (1,560 and 659 words). Keep both sections; each keeps the stories routed to its own page, and the leads cross-link with a relative `<a href="tools-and-devex.html">` as the pages already do. Do not move stories between pages: STEP 3.1 assigns one story to one page, and re-routing history is out of scope.
- **`tools-and-devex.html` holds the site's only prose external link.** Preserve it — Step 4's "source URLs lost: 0" check will catch it if dropped.

Each of Tasks 6–15 ends with:

```bash
python3 digest-routine/check-structure.py
```

Expected: no failures for any page converted so far.

---

### Task 16: Rewrite the routine so runs produce the new structure

Without this, the next digest run writes prose paragraphs back onto the converted pages.

**Files:**
- Modify: `digest-routine/STEP2-extract.md` (§2.4)
- Modify: `digest-routine/STEP3-route.md` (§3.2, §3.3)
- Modify: `digest-routine/STEP5-index.md` (§5.3)
- Modify: `README.md`

**Interfaces:**
- Consumes: the page shape from Task 5, the checker from Task 4.
- Produces: instructions the scheduled task follows; nothing consumes them in code.

- [ ] **Step 1: Strengthen URL capture in STEP 2.4**

In `digest-routine/STEP2-extract.md`, replace the `sources` bullet's final sentence:

```
  newsletter names a canonical public URL for the artifact, link that: it is the only
  linked source an entry should carry, and the only one a reader can actually open.
```

with:

```
  newsletter names a canonical public URL for the artifact, capturing it is **required**,
  not best-effort: it becomes the story's headline link and is the only thing a reader can
  actually open. Where the newsletter names none, record the story as having no public URL
  so it renders as explicitly unlinked. Never substitute a mailbox permalink for a missing
  source -- 186 `outlook.office365.com` links reached the public site that way before
  2026-09-20, and they were dead for every reader.
```

- [ ] **Step 2: Replace STEP 3.2a and 3.2b**

In `digest-routine/STEP3-route.md`, replace the whole of **a.** and **b.** under §3.2 with:

````markdown
**a. Add the story to its section.** Insert at the top of the matching
`<section class="topic-section">`, directly after its `<p class="lead">`:

```html
        <article class="story" id="ARTIFACT-SLUG">
          <span class="when">YYYY-MM-DD</span>
          <h4><a href="PUBLIC_URL">Headline, 6&ndash;14 words, artifact first</a></h4>
          <p>Two to four sentences. Hard numbers first, then the honest trade-off.</p>
          <div class="sources"><a href="PUBLIC_URL">Vendor</a> &middot; <span class="via">via Newsletter (Mon D)</span></div>
        </article>
```

`id` is the kebab-case artifact name and must be unique on the page. The headline **is**
the link. With no public URL, drop the `<a>`, add `class="story unlinked"`, and write
`&mdash; no public URL given` inside `.via`. Never link a newsletter name, and never emit a
`mail.google.com` or `outlook.office365.com` URL (STEP 1.6).

Then move any story now beyond the newest three into that section's `<details>`, and update
its `<summary>` count.

**b. Update the section lead only if the through-line changed.** The `<p class="lead">` is
one or two sentences, **60 words maximum**, naming what makes these stories a group. It is
not a summary of the new story -- that is what the story's own `<p>` is for. Most runs
leave the lead untouched. A lead over 60 words fails `check-structure.py`.
````

- [ ] **Step 3: Add the new 3.2e and fix 3.2d's neighbours**

After the existing **d.** in §3.2, add:

````markdown
**e. Rebuild the section index and the timeline index.** The `<nav class="section-index">`
carries one chip per section in page order with its true story count (visible + folded):

```html
          <li><a href="#SECTION-ID">Section heading <span class="n">N</span></a></li>
```

The timeline gains one line per story, newest-first, linking that story's own anchor:

```html
        <li><span class="date">YYYY-MM-DD</span><span class="label"><a href="#ARTIFACT-SLUG">Headline</a></span></li>
```

It carries no summary -- the summary lives once, in the story.
````

- [ ] **Step 4: Amend the styles.css prohibition in §3.3**

Replace the first bullet of §3.3:

```
- Never edit `styles.css`. Every class you need already exists: `timeline`, `date`,
  `label`, `sources`, `current-state`, `changed-today`, `meta`. (It was last changed on
  2026-09-14, on user instruction, to add paragraph and `<details>` rules inside
  `.current-state`. Use those elements; do not add more.)
```

with:

```
- Never edit `styles.css`. Every class you need already exists: `section-index`,
  `topic-section`, `lead`, `story`, `when`, `unlinked`, `via`, `timeline index`, `timeline`,
  `date`, `label`, `sources`, `current-state`, `changed-today`, `meta`. (Last changed on
  2026-09-20, on user instruction, to add the story-item structure; before that on
  2026-09-14 for the `.current-state` paragraph rules. Use these classes; do not invent
  more, and do not modify an existing rule -- `site/daily/` and `index.html` depend on them.)
```

- [ ] **Step 5: Make the checker a required STEP 5.3 gate**

In `digest-routine/STEP5-index.md` §5.3, replace the `no paragraph is a wall of text` bullet with:

````markdown
- **the structural gate passes.** Run it and paste the result; do not assume:

  ```bash
  python3 digest-routine/check-structure.py
  ```

  Exit 0 is required. It asserts: no mailbox identifier anywhere in `site/`; every
  `#fragment` resolves to an id on the same page and no id is duplicated; each section-index
  count equals the real story count; every lead is <=60 words; every story is either linked
  or explicitly marked `unlinked` with a stated reason; the timeline index is newest-first
  and points only at real stories; no paragraph exceeds 350 words; every sidebar links
  siblings bare and marks exactly its own entry active. A failure is a blocker, not a note.
````

- [ ] **Step 6: Update the README's description of a run**

In `README.md`, replace:

```
newsletters into discrete stories, apply a quality bar, route each story to one of eleven
topic pages and rewrite that page's prose, then write a daily log and update the index.
```

with:

```
newsletters into discrete stories, apply a quality bar, route each story to one of eleven
topic pages and add it there as a linked story item under the right heading, then write a
daily log and update the index. A structural gate (`digest-routine/check-structure.py`)
runs before every push and fails the run on a broken anchor, a miscounted index, an
over-long lead, an unmarked missing source, or any mailbox identifier under `site/`.
```

- [ ] **Step 7: Verify the routine files still describe what the site actually is**

```bash
cd /Users/autobot/Desktop/projects/ai-digest
/usr/bin/grep -n 'living prose\|multiple `<p>` paragraphs\|120.250 words' digest-routine/STEP3-route.md
echo "^^ must be EMPTY: the prose-paragraph discipline is gone"
/usr/bin/grep -c 'topic-section\|class="story"' digest-routine/STEP3-route.md
echo "^^ must be > 0"
python3 digest-routine/check-structure.py
```

Expected: the first grep returns nothing, the second returns a non-zero count, the checker exits 0.

- [ ] **Step 8: Commit**

```bash
git add digest-routine/ README.md
git commit -m "Teach the routine to write linked story items, and gate it

STEP 2.4 makes capturing a canonical public URL required and forbids ever
substituting a mailbox permalink. STEP 3.2 replaces 'rewrite the section as
living prose' with 'add a story item and keep the lead true', adds the index
rebuild, and widens the styles.css class list. STEP 5.3 now runs
check-structure.py as a hard gate before every push.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 17: Full-site verification and push

**Files:** none modified — this task only verifies and pushes.

**Interfaces:**
- Consumes: everything above.
- Produces: the deployed site.

- [ ] **Step 1: Run the structural gate over all eleven pages**

```bash
cd /Users/autobot/Desktop/projects/ai-digest
python3 digest-routine/check-structure.py; echo "exit=$?"
```

Expected: every check PASS, `exit=0`, `11 page(s) checked, 0 failure(s)`.

- [ ] **Step 2: Run the three leak gates exactly as CI and STEP 5.3 do**

```bash
set +e
/usr/bin/grep -rInE 'mail\.google\.com|outlook\.office365\.com|outlook\.live\.com|/owa/\?ItemID|@gmail\.com' site/; echo "site/ exit=$? (1=clean)"
git grep -InE '[A-Za-z0-9._%+-]+@gmail\.com' -- . ':!.github/workflows/pages.yml'; echo "tracked exit=$? (1=clean)"
PAT=$(python3 -c "import re;s=open('digest-routine/sources.json').read();lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)};lp|={p.replace('.','') for p in lp};print('|'.join(sorted(p for p in lp if len(p)>4)))")
git grep --untracked -InEi "$PAT" -- . ':!digest-routine/sources.json'; echo "local-parts exit=$? (1=clean)"
set -e
```

All three must report `exit=1`. If `sources.json` is absent, report the third check **skipped**, never passed — there is no CI backstop for it.

- [ ] **Step 3: Confirm nothing was lost site-wide**

```bash
python3 - <<'PY'
import re, glob, subprocess
base = "71701a3"  # last commit before this work
tot_old_urls = tot_new_urls = 0
for p in sorted(glob.glob("site/topics/*.html")):
    old = subprocess.run(["git", "show", "%s:%s" % (base, p)], capture_output=True, text=True).stdout
    new = open(p, encoding="utf-8").read()
    ok = set(re.findall(r'href="(https?://[^"]+)"', old))
    nk = set(re.findall(r'href="(https?://[^"]+)"', new))
    mailbox = set(u for u in ok if "outlook" in u or "owa/?ItemID" in u)
    lost = ok - nk - mailbox
    tot_old_urls += len(ok - mailbox); tot_new_urls += len(nk)
    print("%-46s real urls %3d -> %3d   mailbox removed %3d   LOST %d"
          % (p, len(ok - mailbox), len(nk), len(mailbox), len(lost)))
    for u in sorted(lost):
        print("     LOST", u)
print("totals: real %d -> %d" % (tot_old_urls, tot_new_urls))
PY
```

Expected: `LOST 0` on every page, and mailbox-removed summing to 186.

- [ ] **Step 4: Render-check three pages in the browser**

Serve `site/` and open `research-papers.html` (pilot), `tools-and-devex.html` (largest) and `agents.html` (most cross-links). On each: section-index chips jump correctly, a folded story opens when reached from the timeline, no horizontal scroll at 375px, and no headline link points anywhere but a real public page.

- [ ] **Step 5: Confirm the word-count goal was actually met**

```bash
python3 - <<'PY'
import re, glob, subprocess
base = "71701a3"
for p in sorted(glob.glob("site/topics/*.html")):
    def w(s):
        m = re.search(r"<main>(.*)</main>", s, re.S)
        return len(re.sub(r"<[^>]+>", " ", m.group(1)).split()) if m else 0
    old = subprocess.run(["git", "show", "%s:%s" % (base, p)], capture_output=True, text=True).stdout
    a, b = w(old), w(open(p, encoding="utf-8").read())
    print("%-46s %6d -> %6d  (%+d%%)" % (p, a, b, round(100 * (b - a) / a)))
PY
```

Expected: every page substantially smaller; the spec's target is roughly 6,000–8,000 words per page. A page that barely moved means leads were left too long — go back and cut before pushing.

- [ ] **Step 6: Push**

```bash
git push origin main
```

- [ ] **Step 7: Confirm the deploy actually ran and succeeded**

```bash
sleep 45
curl -s "https://api.github.com/repos/AndresRubio/ai-digest/actions/runs?per_page=3" \
 | python3 -c "
import json,sys
for r in json.load(sys.stdin)['workflow_runs']:
    print(r['head_sha'][:7], r['status'], r.get('conclusion'), r['display_title'][:60])"
```

Expected: a run for the new head SHA. Unlike the spec commit, this one touches `site/**`, so the workflow **will** fire. Wait for `completed success`. If `guard` fails, the leak gate caught something — fix it and push again rather than re-running the job.

- [ ] **Step 8: Confirm the live site serves the new structure**

```bash
curl -s "https://andresrubio.github.io/ai-digest/topics/research-papers.html" -o /tmp/live.html -w "http %{http_code}\n"
for m in 'section-index' 'topic-section' 'class="story"' 'timeline index' 'outlook.office365.com'; do
  printf '%-24s %s\n' "$m" "$(/usr/bin/grep -c "$m" /tmp/live.html)"
done
```

Expected: the first four are non-zero, `outlook.office365.com` is **0**.

---

## Self-Review

**Spec coverage.** Section shape → Task 5 Step 2 (and 6–11). Section index → Tasks 3, 4, 5, 16 Step 3. Timeline index → Tasks 3, 4, 5, 16 Step 3. Story id + fold-opening anchors → Tasks 4 (`check_anchors_resolve`), 5 Step 5. CSS additions with no existing rule modified → Task 3, verified by `comm`. Backfill all eleven → Tasks 5–15. Mailbox-link removal first → Task 1. Bounded link repair → Task 5 Step 2 item 6 and the `unlinked` markup; no task researches the open web. STEP 2.4 / 3.2 / 3.3 / 5.3 → Task 16. Verification list → Task 4's checks plus Task 17. Outlook pattern added to the CI gate → Task 2.

**Gap found and closed:** the spec's verification list requires "each `.lead` is ≤60 words" and "no duplicate id", neither of which the original Task 4 draft asserted. Both are now in `check_lead_length` and `check_anchors_resolve`.

**Placeholder scan:** no TBD/TODO. The one `<!-- older <article …> -->` comment in Task 5 Step 2 is inside illustrative target markup whose full shape is given immediately above and below it, and Task 5's Step 1 inventory enumerates every entry that fills it.

**Type consistency:** every checker is `check_*(paths) -> list[str]`; all eight are registered in `CHECKS`; `main()` calls each with `sorted(glob.glob(TOPICS))`. `_text`, `_words`, `_converted` are defined once in Task 4 and used only there. Class names match across Task 3 (CSS), Task 4 (regexes), Task 5 (markup) and Task 16 (routine docs): `section-index`, `topic-section`, `lead`, `story`, `when`, `unlinked`, `via`, `timeline index`.

**The checker in Tasks 1 and 4 was executed before this plan shipped.** The two Python blocks
were extracted, assembled exactly as the two tasks instruct, and compiled clean on Python
3.9.6. Against the known-good fixture: all eight checks PASS, exit 0. Against nine deliberate
mutations — wrong index count, dangling fragment, duplicate id, 61-word lead, unlinked story
with no marker, mailbox link, wrong sidebar active marker, out-of-order timeline, 400-word
paragraph — each was caught by its own check, exit 1 every time. Against the real `site/` as
it stands today it reports `check_no_mailbox_links FAIL (186)` and `check_anchors_resolve
FAIL (11)`, totalling 197 — which is exactly what Task 4 Step 2 tells the implementer to
expect. The code in this plan runs as written; it is not pseudocode.

**Known risk:** Tasks 5–15 are the bulk of the effort and are genuinely manual — 641 entries reconciled against 104 sections, with merge decisions the checker cannot make. The checker catches structural breakage, not a bad lead or a wrong merge. Tasks 6–15 therefore each need a human or reviewing-agent read of the prose, not just a green checker.
