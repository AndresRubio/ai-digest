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


SECTION_RE = re.compile(r'<section class="topic-section" id="([^"]+)">(.*?)</section>', re.S)
STORY_RE = re.compile(r'<article class="story([^"]*)" id="([^"]+)">(.*?)</article>', re.S)
LEAD_RE = re.compile(r'<p class="lead">(.*?)</p>', re.S)
INDEX_LINK_RE = re.compile(r'<a href="#([^"]+)">(.*?)</a>', re.S)
TIMELINE_INDEX_RE = re.compile(r'<ul class="timeline index">(.*?)</ul>', re.S)
SECTION_INDEX_RE = re.compile(r'<nav class="section-index">(.*?)</nav>', re.S)
COUNT_RE = re.compile(r'<span class="n">(\d+)</span>')
ABS_URL_HREF_RE = re.compile(r'href="https?://[^"/]+')


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


def check_flat_structure(paths):
    """Reject nested <section>/<article> tags before any other check trusts them.

    SECTION_RE and STORY_RE are non-greedy regexes that assume a flat,
    non-nested structure: a topic-section body contains only articles, and a
    story body contains no article of its own. If a topic-section body
    nests another <section>, the non-greedy match stops at that inner
    </section> and silently truncates the captured body, hiding every
    <article class="story"> that follows it from check_index_counts and
    check_lead_length. This check enforces the flat-structure assumption
    directly (by scanning for a nested opening tag) so that assumption is
    safe for the rest of the checks to rely on; it fails loudly instead of
    letting a truncated parse pass quietly.
    """
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        if not _converted(text):
            continue
        for sid, body in SECTION_RE.findall(text):
            if "<section" in body:
                out.append(
                    "%s section #%s contains a nested <section>; nesting is "
                    "not supported, structure checks cannot be trusted" % (p, sid)
                )
        for _classes, sid, body in STORY_RE.findall(text):
            if "<article" in body:
                out.append(
                    "%s story #%s contains a nested <article>; nesting is "
                    "not supported, structure checks cannot be trusted" % (p, sid)
                )
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


NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
# "Two of the nine are contested attributions" -- a lead that says "N of the M"
# is asserting M is the section's story count. Deliberately narrow: it does NOT
# match a lead that opens with a bare count ("Two families", "Three
# instruments"), because those count kinds rather than stories and are a
# legitimate way to frame a section.
LEAD_COUNT_RE = re.compile(
    r"\b(%s)\s+of\s+the\s+(%s)\b" % ("|".join(NUMBER_WORDS), "|".join(NUMBER_WORDS)),
    re.I,
)


def check_lead_counts(paths):
    """A lead saying "N of the M" must have M equal to the section's story count.

    Added 2026-09-22 after a digest run grew a section from 9 to 11 stories:
    STEP 3.2e rebuilt the section-index chip to 11, but the lead kept reading
    "Two of the nine", so the page asserted a number its own index contradicted
    in the same viewport. The routine treats a lead as prose to leave alone
    unless the through-line changed -- but a number inside a lead is a claim
    about the section, and the story count can change without the through-line
    changing at all.
    """
    out = []
    for p in paths:
        text = open(p, encoding="utf-8").read()
        if not _converted(text):
            continue
        for sid, body in SECTION_RE.findall(text):
            n = len(STORY_RE.findall(body))
            leads = LEAD_RE.findall(body)
            if len(leads) != 1:
                continue  # check_lead_length reports this
            lead = _text(leads[0])
            for num, den in LEAD_COUNT_RE.findall(lead):
                claimed = NUMBER_WORDS[den.lower()]
                if claimed != n:
                    out.append(
                        "%s #%s lead says %r of the %r, section has %d stories"
                        % (p, sid, num.lower(), den.lower(), n)
                    )
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
            linked = bool(ABS_URL_HREF_RE.search(head.group(1)))
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
    check_flat_structure,
    check_index_counts,
    check_lead_length,
    check_lead_counts,
    check_story_link_state,
    check_timeline_order,
    check_no_wall_of_text,
    check_sidebar_consistency,
]


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
