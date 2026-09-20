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
