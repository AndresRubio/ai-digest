# AI Digest Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the project root to `ai-digest`, remove the owner's mailbox identifiers from a public repo and its history, and leave GitHub Pages serving the same URL throughout.

**Architecture:** Three sequenced parts, each its own commit. Part 1 closes a live privacy leak and ships first so it is live regardless of what follows. Part 2 restructures folders and path references. Part 3 rewrites history, last, only after Parts 1–2 are pushed and verified green.

**Tech Stack:** git, GitHub Actions (Pages), `git-filter-repo`, Python 3 for scripted edits, `grep`/`curl` for verification. No application code.

## Global Constraints

- **Never write a mailbox identifier into a tracked file.** That includes this plan, the spec, the guard, and commit messages. Patterns are always *derived at runtime* from `digest-routine/sources.json`, which is gitignored.
- **The public URL must not change.** `https://andresrubio.github.io/ai-digest/` derives from the repo name. Every occurrence stays byte-identical.
- **`ai-digest` is replaced only where it is a filesystem path.** It must NOT be changed in: the nine site URLs, the git remote, prose like "the AI digest task", or the scheduled-task name `ai-digest` in `digest-routine/state/run-log.md`.
- **Never edit `ai-digest/styles.css`** (becomes `site/styles.css`).
- **Do not change `~/.gitconfig`.** Git identity changes are repo-local only.
- Repo root during Tasks 1–4: `/Users/autobot/Desktop/projects/mywiki 2`. From Task 5 onward: `/Users/autobot/Desktop/projects/ai-digest`.
- Commit message trailer on every commit: `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `/tmp/redact.py` (scratch, not committed) | Derives local-parts from `sources.json`, applies context-keyed replacements | 1 |
| `ai-digest/daily/2026-09-08.html`, `2026-09-09.html` | Published pages carrying a mailbox name | 1 |
| `digest-routine/sources.example.json` | Public allowlist; 14 identity refs in prose notes | 1 |
| `digest-routine/state/processed.json`, `run-log.md` | Ledger and log; 4 identity refs | 1 |
| `.github/workflows/pages.yml` | Deploy gate: widen scope, read patterns from secret, fail closed | 2 |
| `digest-routine/STEP5-index.md` | Adds the derived local identity check to §5.3 | 2 |
| `digest-routine/README.md` | Corrects the false redaction claim at line ~53 | 2 |
| `site/` (from `ai-digest/`) | The published site, renamed | 3 |
| `README.md` (new, repo root) | Explains the project to a stranger | 4 |
| `~/.claude/scheduled-tasks/ai-digest/SKILL.md` | Daily task's working directory | 5 |

---

### Task 1: Redact the 20 identity occurrences

**Files:**
- Create: `/tmp/redact.py` (scratch — never committed)
- Modify: `ai-digest/daily/2026-09-08.html`, `ai-digest/daily/2026-09-09.html`, `digest-routine/sources.example.json`, `digest-routine/state/processed.json`, `digest-routine/state/run-log.md`

**Interfaces:**
- Consumes: `digest-routine/sources.json` (gitignored) for the local-parts.
- Produces: a tracked tree with zero identity occurrences — Task 2's guard and Task 7's history scrub both assume this holds.

- [ ] **Step 1: Write the failing check**

Save as `/tmp/idcheck.sh`:

```bash
#!/bin/bash
# Fails if any mailbox local-part from sources.json appears in a tracked file.
cd "$(git rev-parse --show-toplevel)" || exit 2
PAT=$(python3 -c "
import re
s=open('digest-routine/sources.json').read()
lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)}
lp|={p.replace('.','') for p in lp}
print('|'.join(re.escape(p) for p in sorted(lp) if len(p)>4))
")
[ -z "$PAT" ] && { echo "FAIL: no patterns derived"; exit 2; }
if git grep -InEi "$PAT" -- . ; then
  echo "FAIL: identity found in tracked files"; exit 1
fi
echo "PASS: no identity in tracked files"
```

- [ ] **Step 2: Run it to verify it fails**

```bash
chmod +x /tmp/idcheck.sh && /tmp/idcheck.sh
```

Expected: prints the 20 matching lines, then `FAIL: identity found in tracked files`, exit 1.

- [ ] **Step 3: Write the redaction script**

Save as `/tmp/redact.py`:

```python
import re, pathlib, json
root = pathlib.Path(".")
src = (root / "digest-routine/sources.json").read_text()
addrs = sorted(set(re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com', src)))
primary = json.loads(src)["accounts"][0]["email"].split("@")[0]
parts = {a.split("@")[0] for a in addrs}
retired = sorted(p for p in parts if p != primary and p != primary.replace(".", ""))
assert retired, "expected a retired local-part in sources.json"
R, P = retired[0], primary
variants = lambda p: [p, p.replace(".", "")]

RULES = []
for r in variants(R):
    RULES += [
        (rf"the previously configured {re.escape(r)} inbox", "the previously configured secondary inbox"),
        (rf"the retired {re.escape(r)} inbox",   "the retired inbox"),
        (rf"the retired {re.escape(r)} account", "the retired account"),
        (rf"\({re.escape(r)} removed from config", "(the retired account removed from config"),
    ]
for p in variants(P):
    RULES += [
        (rf"arriving at {re.escape(p)}:",      "arriving at the primary inbox:"),
        (rf"not present in {re.escape(p)}",    "not present in the primary inbox"),
        (rf"Not seen at {re.escape(p)}",       "Not seen at the primary inbox"),
        (rf"verified against {re.escape(p)}",  "verified against the primary inbox"),
    ]
# Fallbacks catch anything the context rules missed.
for r in variants(R): RULES.append((re.escape(r), "the retired account"))
for p in variants(P): RULES.append((re.escape(p), "the primary inbox"))

FILES = [
    "ai-digest/daily/2026-09-08.html",
    "ai-digest/daily/2026-09-09.html",
    "digest-routine/sources.example.json",
    "digest-routine/state/processed.json",
    "digest-routine/state/run-log.md",
]
total = 0
for f in FILES:
    path = root / f
    t = orig = path.read_text()
    for pat, rep in RULES:
        t = re.sub(pat, rep, t)
    n = sum(1 for _ in re.finditer("|".join(re.escape(v) for p in (R, P) for v in variants(p)), orig))
    if t != orig:
        path.write_text(t); total += n
    print(f"{f}: {n} occurrences")
print("total:", total)

# sources.example.json and processed.json must still be valid JSON.
for f in ("digest-routine/sources.example.json", "digest-routine/state/processed.json"):
    json.loads((root / f).read_text())
    print("valid JSON:", f)
```

- [ ] **Step 4: Run it**

```bash
cd "/Users/autobot/Desktop/projects/mywiki 2" && python3 /tmp/redact.py
```

Expected: `1, 1, 14, 3, 1` per file, `total: 20`, and both `valid JSON:` lines.

- [ ] **Step 5: Run the check to verify it now passes**

```bash
/tmp/idcheck.sh
```

Expected: `PASS: no identity in tracked files`, exit 0.

- [ ] **Step 6: Confirm only identity strings changed**

```bash
git diff --stat
git diff | grep -E '^[+-]' | grep -viE 'primary inbox|retired account|retired inbox|secondary inbox' | grep -vE '^(\+\+\+|---)'
```

Expected: 5 files changed; the second command prints nothing — every changed line is a redaction.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -F - <<'EOF'
Redact mailbox identifiers from tracked files

The repo is public and 20 occurrences of the owner's Gmail local-parts
were tracked across five files, two of them on the published site.

Replaced with the role names already used elsewhere in the log
("the primary inbox", "the retired account"). Entry facts are unchanged;
only the mailbox name is removed. Rewriting the two published daily pages
follows the precedent set on 2026-09-14, when Gmail links were stripped
site-wide.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 2: Widen the deploy gate and document it honestly

**Files:**
- Modify: `.github/workflows/pages.yml` (guard job), `digest-routine/STEP5-index.md` (§5.3), `digest-routine/README.md` (~line 53)

**Interfaces:**
- Consumes: the clean tree from Task 1.
- Produces: a guard that fails closed on a missing `IDENTITY_PATTERNS` secret. Task 6 depends on the secret existing before its push.

- [ ] **Step 1: Replace the guard job in `.github/workflows/pages.yml`**

Replace the whole `guard:` job with:

```yaml
  guard:
    name: Check for leaked identity
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # The digest is built from a private Gmail inbox and this repo is public,
      # so the whole tree is screened -- not just the site. The mailbox patterns
      # live in a repository secret, never in this file: a regex naming the
      # mailboxes would publish them in the file meant to prevent exactly that.
      - name: No mailbox identifiers anywhere in the repo
        env:
          IDENTITY_PATTERNS: ${{ secrets.IDENTITY_PATTERNS }}
        run: |
          # Fail closed. A guard that no-ops when misconfigured is worse than no
          # guard, because it reports green.
          if [ -z "$IDENTITY_PATTERNS" ]; then
            echo "::error::IDENTITY_PATTERNS secret is unset. Refusing to publish unscreened."
            exit 1
          fi
          if grep -rInEi "$IDENTITY_PATTERNS" --exclude-dir=.git . ; then
            echo "::error::Found a mailbox identifier -- refusing to publish."
            exit 1
          fi
          if grep -rInE 'mail\.google\.com|[A-Za-z0-9._%+-]+@gmail\.com' \
               --exclude-dir=.git --exclude=pages.yml . ; then
            echo "::error::Found a Gmail address or mailbox URL -- refusing to publish."
            exit 1
          fi
          echo "Clean: no mailbox identifiers, Gmail addresses or mailbox URLs."
```

- [ ] **Step 2: Verify the YAML parses**

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/pages.yml')); print('valid YAML')"
```

Expected: `valid YAML`.

- [ ] **Step 3: Verify the guard's own logic locally, both branches**

```bash
IDENTITY_PATTERNS="" bash -c 'if [ -z "$IDENTITY_PATTERNS" ]; then echo "fail-closed OK"; exit 0; fi; echo "BUG: did not fail closed"'
IDENTITY_PATTERNS="$(python3 -c "
import re
s=open('digest-routine/sources.json').read()
lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)}
lp|={p.replace('.','') for p in lp}
print('|'.join(sorted(p for p in lp if len(p)>4)))
")" bash -c 'grep -rInEi "$IDENTITY_PATTERNS" --exclude-dir=.git . && echo "BUG: leak found" || echo "clean-branch OK"'
```

Expected: `fail-closed OK` then `clean-branch OK`.

- [ ] **Step 4: Add the identity check to `digest-routine/STEP5-index.md` §5.3**

Insert immediately after the existing `no mail.google.com URL` bullet:

```markdown
- **no mailbox identifier appears in any tracked file.** Derive the local-parts from
  `digest-routine/sources.json` (gitignored, so the literals never enter the repo) and grep
  the tracked tree for them:
  `python3 -c "import re;s=open('digest-routine/sources.json').read();lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)};lp|={p.replace('.','') for p in lp};print('|'.join(sorted(p for p in lp if len(p)>4)))"`
  then `git grep -InEi "<that pattern>"` must come back empty. This catches what the
  `@gmail.com` gate above cannot: a bare mailbox name with no domain attached, which is how
  20 identifiers reached the public repo before 2026-09-16. If `sources.json` is absent,
  report the check as **skipped**, never as passed.
```

- [ ] **Step 5: Correct the false claim in `digest-routine/README.md`**

Replace:

```
published as `sources.example.json` with only the account identity redacted, so the
routine stays reviewable.
```

with:

```
published as `sources.example.json` with the account identity redacted from both the
`accounts[].email` field and the prose `note` fields, so the routine stays reviewable.
Until 2026-09-16 the notes still named the mailboxes; that is what the identity gate in
STEP 5.3 and the `pages.yml` guard now exist to prevent recurring.
```

- [ ] **Step 6: Re-run the identity check**

```bash
/tmp/idcheck.sh
```

Expected: `PASS`.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -F - <<'EOF'
Widen the deploy gate to catch bare mailbox names

The old guard grepped for mail.google.com and @gmail.com, so a bare
local-part passed straight through -- which is how 20 identifiers reached
a public repo. The guard now reads its patterns from an IDENTITY_PATTERNS
repository secret rather than holding them in this file, fails closed when
the secret is unset, and screens the whole repo instead of only the site.

STEP 5.3 gains the same check, deriving patterns from the gitignored
sources.json. README no longer claims a redaction that had not been applied.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 3: Rename `ai-digest/` to `site/` and update path references

**Files:**
- Rename: `ai-digest/` → `site/` (89 tracked files)
- Modify: `.github/workflows/pages.yml` (6), `digest-routine/README.md` (6), `digest-routine/STEP5-index.md` (4), `digest-routine/STEP1-ingest.md` (1), `digest-routine/STEP4-log.md` (1), `docs/superpowers/specs/2026-09-03-gmail-ai-digest-routine-design.md` (6), `.claude/settings.local.json` (16), `.claude/launch.json` (1)

**Interfaces:**
- Consumes: clean tree from Task 2.
- Produces: site at `site/`. Task 4's README and Task 6's deploy both assume this path.

- [ ] **Step 1: Record the URL baseline (must not change)**

```bash
git grep -c 'andresrubio\.github\.io/ai-digest/' -- . | tee /tmp/urls-before.txt
```

Expected: a per-file count list. Keep it; Step 6 compares against it.

- [ ] **Step 2: Rename with git so history follows**

```bash
git mv ai-digest site && git status --short | head -3
```

Expected: entries shown as `R  ai-digest/... -> site/...`.

- [ ] **Step 3: Rewrite path references only**

```bash
python3 - <<'PY'
import pathlib, re
targets = [
 ".github/workflows/pages.yml",
 "digest-routine/README.md",
 "digest-routine/STEP5-index.md",
 "digest-routine/STEP1-ingest.md",
 "digest-routine/STEP4-log.md",
 "docs/superpowers/specs/2026-09-03-gmail-ai-digest-routine-design.md",
 ".claude/settings.local.json",
]
URL = "andresrubio.github.io/ai-digest/"
SENTINEL = "\x00URL\x00"
for f in targets:
    p = pathlib.Path(f); t = p.read_text()
    t = t.replace(URL, SENTINEL)          # protect the public URL
    t = t.replace("ai-digest/", "site/")  # path-scoped only: requires the slash
    t = t.replace("../ai-digest", "../site")
    t = t.replace(SENTINEL, URL)
    p.write_text(t); print("rewrote", f)

# launch.json uses a bare directory argument, no trailing slash.
p = pathlib.Path(".claude/launch.json"); t = p.read_text()
t = t.replace('"--directory", "ai-digest"', '"--directory", "site"')
p.write_text(t); print("rewrote .claude/launch.json")
PY
```

- [ ] **Step 4: Also fix the stale root path in the 2026-09-03 spec**

```bash
python3 - <<'PY'
import pathlib
p = pathlib.Path("docs/superpowers/specs/2026-09-03-gmail-ai-digest-routine-design.md")
t = p.read_text().replace("/Users/autobot/Downloads/mywiki 2",
                          "/Users/autobot/Desktop/projects/ai-digest")
p.write_text(t); print("rewrote root path in 2026-09-03 spec")
PY
```

- [ ] **Step 5: Verify JSON and YAML still parse**

```bash
python3 -c "
import json,yaml
json.load(open('.claude/launch.json')); json.load(open('.claude/settings.local.json'))
yaml.safe_load(open('.github/workflows/pages.yml')); print('launch.json, settings.local.json, pages.yml all parse')
"
```

Expected: the confirmation line.

- [ ] **Step 6: Verify the URL survived and no path ref remains**

```bash
git grep -c 'andresrubio\.github\.io/ai-digest/' -- . > /tmp/urls-after.txt
diff /tmp/urls-before.txt /tmp/urls-after.txt && echo "URLs unchanged"
git grep -nE 'ai-digest/' -- . ':!docs/superpowers/specs/2026-09-16*' ':!docs/superpowers/plans' \
  | grep -v 'andresrubio\.github\.io' || echo "no stale path refs"
grep -n '"ai-digest"' .claude/launch.json || echo "launch.json clean"
git grep -n 'ai-digest' -- digest-routine/state/run-log.md
```

Expected: `URLs unchanged`; `no stale path refs`; `launch.json clean`; and the run-log line still showing `scheduled task 'ai-digest' created` — the task **name**, correctly untouched.

- [ ] **Step 7: Verify the site still renders**

```bash
(cd site && python3 -m http.server 8731 >/dev/null 2>&1 &) ; sleep 2
curl -s -o /dev/null -w "index:%{http_code} " http://localhost:8731/index.html
curl -s -o /dev/null -w "topic:%{http_code} " http://localhost:8731/topics/agents.html
curl -s -o /dev/null -w "daily:%{http_code}\n" http://localhost:8731/daily/2026-09-16.html
pkill -f "http.server 8731"
ls site/topics/*.html | wc -l; ls site/daily/*.html | wc -l
```

Expected: `index:200 topic:200 daily:200`, then `11` and `76`.

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -F - <<'EOF'
Rename the site directory to site/ and update path references

The repo is ai-digest and the published site lived in a nested ai-digest/,
which read as a stutter once the root folder was renamed. The site is now
site/, renamed with git mv so all 89 files keep their history.

Path references updated across pages.yml, the STEP files, both READMEs,
launch.json and settings.local.json. The public URL is untouched: its
/ai-digest/ path comes from the repo name, not from any folder. The
scheduled-task name in run-log.md is likewise left alone.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 4: Add the root README

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: the `site/` layout from Task 3.
- Produces: nothing other tasks depend on.

- [ ] **Step 1: Write `README.md`**

```markdown
# ai-digest

A self-updating AI-news knowledge base, built each weekday morning from newsletter email
and published as a static site.

**Live:** <https://andresrubio.github.io/ai-digest/>

## Layout

| Path | What it is |
|---|---|
| `site/` | The published site — `index.html`, eleven topic pages, one page per run. Deployed from here by `.github/workflows/pages.yml` on every push to `main`. |
| `digest-routine/` | How a run works: `STEP1`–`STEP5`, the source allowlist, and run state. Start at [`digest-routine/README.md`](digest-routine/README.md). |
| `docs/` | Design specs and implementation plans. |

## How a run works

A scheduled task reads `digest-routine/STEP1-ingest.md` through `STEP5-index.md` in order and
follows them exactly. All the logic lives in those five files, so changing what the routine
does never means changing the task. Briefly: scan the connected Gmail account, split
newsletters into discrete stories, apply a quality bar, route each story to one of eleven
topic pages and rewrite that page's prose, then write a daily log and update the index.

## Two rules the project does not bend

**It never writes to Gmail.** No labels, no read-state changes, no archiving, no sending.
De-duplication is local, via `digest-routine/state/processed.json`. This is enforced at the
point of tool loading, not just by instruction — the routine loads only the two read tools by
name, so the destructive ones never enter its context.

**No mailbox identifier reaches the site.** This repo and the site are both public. Sources
are cited by newsletter name and date, never as a link into a mailbox. `pages.yml` screens
every push and fails the deploy rather than publish a violation; STEP 5.3 runs the same check
locally. The patterns live in a repository secret, never in a tracked file.
```

- [ ] **Step 2: Verify every relative link resolves**

```bash
for f in digest-routine/README.md .github/workflows/pages.yml digest-routine/state/processed.json; do
  [ -e "$f" ] && echo "ok: $f" || echo "BROKEN: $f"
done
curl -s -o /dev/null -w "live site: %{http_code}\n" https://andresrubio.github.io/ai-digest/
```

Expected: three `ok:` lines and `live site: 200`.

- [ ] **Step 3: Commit**

```bash
git add README.md && git commit -F - <<'EOF'
Add a root README

The repo had only LICENSE and .gitignore at top level, so a visitor to a
public repo saw three folders and no explanation. Covers what the project
is, the live URL, the three folders, how a run works, and the two hard
rules. Points at digest-routine/README.md rather than restating it.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 5: Rename the root folder and re-point external dependencies

**Files:**
- Rename: `/Users/autobot/Desktop/projects/mywiki 2` → `/Users/autobot/Desktop/projects/ai-digest`
- Modify: `~/.claude/scheduled-tasks/ai-digest/SKILL.md`, `.claude/settings.local.json`
- Rename: `~/.claude/projects/-Users-autobot-Desktop-projects-mywiki-2` → `…-ai-digest`

**Interfaces:**
- Consumes: committed tree from Task 4.
- Produces: the final on-disk path. Tasks 6–7 run from there.

- [ ] **Step 1: Confirm the tree is committed before moving**

```bash
cd "/Users/autobot/Desktop/projects/mywiki 2" && git status --porcelain
```

Expected: empty. If not, commit before continuing — moving a dirty tree invites confusion.

- [ ] **Step 2: Move the folder**

```bash
cd /Users/autobot && mv "/Users/autobot/Desktop/projects/mywiki 2" "/Users/autobot/Desktop/projects/ai-digest" && ls -d "/Users/autobot/Desktop/projects/ai-digest"
```

- [ ] **Step 3: Re-point the scheduled task — the one that breaks silently**

```bash
python3 - <<'PY'
import pathlib
p = pathlib.Path("/Users/autobot/.claude/scheduled-tasks/ai-digest/SKILL.md")
t = p.read_text()
new = t.replace("/Users/autobot/Desktop/projects/mywiki 2", "/Users/autobot/Desktop/projects/ai-digest")
assert new != t, "expected the old path in SKILL.md"
p.write_text(new)
print([l for l in new.splitlines() if "Work in" in l])
PY
```

Expected: the `Work in …/ai-digest` line.

- [ ] **Step 4: Re-point settings and the Claude state directory**

```bash
python3 - <<'PY'
import pathlib, json
p = pathlib.Path("/Users/autobot/Desktop/projects/ai-digest/.claude/settings.local.json")
t = p.read_text().replace("/Users/autobot/Desktop/projects/mywiki 2",
                          "/Users/autobot/Desktop/projects/ai-digest")
p.write_text(t); json.loads(t); print("settings.local.json rewritten and valid")
PY
mv "/Users/autobot/.claude/projects/-Users-autobot-Desktop-projects-mywiki-2" \
   "/Users/autobot/.claude/projects/-Users-autobot-Desktop-projects-ai-digest"
ls "/Users/autobot/.claude/projects/-Users-autobot-Desktop-projects-ai-digest/memory/"
```

Expected: the confirmation line, then `MEMORY.md` and three memory files — proof the memories followed.

- [ ] **Step 5: Verify git and the absence of the old name**

```bash
cd "/Users/autobot/Desktop/projects/ai-digest"
git rev-parse --show-toplevel
git remote -v | head -1
grep -ril mywiki . --exclude-dir=.git || echo "no 'mywiki' anywhere in the tree"
grep -rl mywiki /Users/autobot/.claude/scheduled-tasks/ || echo "no 'mywiki' in scheduled tasks"
```

Expected: new toplevel; `AndresRubio/ai-digest` remote; both "no 'mywiki'" lines.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -F - <<'EOF'
Repoint local paths after the root folder rename

The repo root is now ~/Desktop/projects/ai-digest, matching the repo name.
Scheduled task and Claude state directory moved alongside it.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 6: Create the secret, push Parts 1–2, verify Pages

**Files:** none modified. This task is a gate.

**Interfaces:**
- Consumes: all commits from Tasks 1–5.
- Produces: a verified-green deploy. **Task 7 must not start until this passes** — never rewrite history on top of an unverified tree.

- [ ] **Step 1: Print the secret value for the user**

```bash
cd "/Users/autobot/Desktop/projects/ai-digest" && python3 -c "
import re
s=open('digest-routine/sources.json').read()
lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)}
lp|={p.replace('.','') for p in lp}
print('|'.join(sorted(p for p in lp if len(p)>4)))
"
```

- [ ] **Step 2: STOP — the user creates the secret**

The value from Step 1 goes to **Settings → Secrets and variables → Actions → New repository secret**, named `IDENTITY_PATTERNS`. Only the user can do this; it needs their GitHub credentials.

**Do not push until they confirm it exists.** The guard fails closed, so pushing first turns the deploy red.

- [ ] **Step 3: Push**

```bash
git push && git log --oneline -5
```

- [ ] **Step 4: Watch the deploy**

```bash
sleep 45
curl -s "https://api.github.com/repos/AndresRubio/ai-digest/actions/runs?per_page=1" \
 | python3 -c "import json,sys; r=json.load(sys.stdin)['workflow_runs'][0]; print(r['status'], r['conclusion'], r['html_url'])"
```

Expected: eventually `completed success`. Re-run until `completed`. If `failure`, open the URL — the likeliest cause is a missing or mistyped secret.

- [ ] **Step 5: Verify the live site**

```bash
curl -s -o /dev/null -w "root:%{http_code} " https://andresrubio.github.io/ai-digest/
curl -s -o /dev/null -w "topic:%{http_code} " https://andresrubio.github.io/ai-digest/topics/agents.html
curl -s -o /dev/null -w "daily:%{http_code}\n" https://andresrubio.github.io/ai-digest/daily/2026-09-16.html
PAT=$(python3 -c "
import re
s=open('digest-routine/sources.json').read()
lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)}
lp|={p.replace('.','') for p in lp}
print('|'.join(sorted(p for p in lp if len(p)>4)))
")
curl -s https://andresrubio.github.io/ai-digest/daily/2026-09-08.html | grep -ciE "$PAT" || echo "published page is clean"
```

Expected: three `200`s and `published page is clean`.

---

### Task 7: Scrub git history

**Files:** all commits on `main`. Nothing in the working tree changes.

**Interfaces:**
- Consumes: the verified-green state from Task 6.
- Produces: rewritten history. Terminal task.

- [ ] **Step 1: Back up first — nothing destructive runs before this**

```bash
cd "/Users/autobot/Desktop/projects/ai-digest"
git bundle create ~/Desktop/ai-digest-pre-rewrite-2026-09-16.bundle --all
git bundle verify ~/Desktop/ai-digest-pre-rewrite-2026-09-16.bundle
git rev-parse HEAD > ~/Desktop/ai-digest-pre-rewrite-HEAD.txt
ls -lh ~/Desktop/ai-digest-pre-rewrite-2026-09-16.bundle
```

Expected: `The bundle is okay`, a non-zero file size, and the saved SHA. **If the bundle does not verify, stop.**

- [ ] **Step 2: Install `git-filter-repo`**

```bash
brew install git-filter-repo && git filter-repo --version
```

- [ ] **Step 3: Confirm the history still contains the strings**

```bash
PAT=$(python3 -c "
import re
s=open('digest-routine/sources.json').read()
lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)}
lp|={p.replace('.','') for p in lp}
print('|'.join(sorted(p for p in lp if len(p)>4)))
")
git log --all -p | grep -ciE "$PAT"
```

Expected: a non-zero count — this is what Step 5 must drive to zero.

- [ ] **Step 4: Build the replacements file outside the repo**

```bash
python3 - <<'PY'
import re, json, pathlib
s = open("digest-routine/sources.json").read()
primary = json.loads(s)["accounts"][0]["email"].split("@")[0]
parts = {a.split("@")[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com', s)}
parts |= {p.replace(".", "") for p in parts}
primary_variants = {primary, primary.replace(".", "")}
lines = []
for p in sorted(parts, key=len, reverse=True):
    if len(p) <= 4: continue
    repl = "the-primary-inbox" if p in primary_variants else "the-retired-account"
    lines.append(f"{p}@gmail.com==>redacted@example.invalid")
    lines.append(f"{p}==>{repl}")
pathlib.Path("/tmp/replacements.txt").write_text("\n".join(lines) + "\n")
print(len(lines), "replacement rules written to /tmp/replacements.txt")
PY
```

Expected: a rule count of at least 6. The file lives in `/tmp`, never in the repo.

- [ ] **Step 5: Rewrite content and author across all commits**

```bash
git filter-repo --force \
  --replace-text /tmp/replacements.txt \
  --email-callback 'return b"2109109+AndresRubio@users.noreply.github.com" if b"@gmail.com" in email else email'
```

The callback rewrites any Gmail author/committer address and leaves everything else alone, so
the `Co-Authored-By: … <noreply@anthropic.com>` trailers are preserved. `--replace-text`
operates on blob contents; commit messages were verified clean beforehand, so no
`--replace-message` pass is needed.

- [ ] **Step 6: Verify the rewrite**

```bash
PAT=$(python3 -c "
import re
s=open('digest-routine/sources.json').read()
lp={a.split('@')[0] for a in re.findall(r'[A-Za-z0-9._%+-]+@gmail\.com',s)}
lp|={p.replace('.','') for p in lp}
print('|'.join(sorted(p for p in lp if len(p)>4)))
")
git log --all -p | grep -ciE "$PAT" || echo "0 occurrences in history"
git log --all --format='%an <%ae>' | sort -u
git log --oneline | wc -l
```

Expected: `0 occurrences in history`; exactly one author line showing the `users.noreply.github.com` address; the same commit count as before the rewrite.

- [ ] **Step 7: Restore the remote — `git-filter-repo` removes it by design**

```bash
git remote add origin git@github.com:AndresRubio/ai-digest.git
git remote -v
```

- [ ] **Step 8: Set the repo-local identity so future commits do not re-leak**

```bash
git config --local user.email "2109109+AndresRubio@users.noreply.github.com"
git config --local user.name "Andrés Rubio del Saz"
git config --local --list | grep user
```

Expected: the noreply address. `~/.gitconfig` is deliberately untouched.

- [ ] **Step 9: Force-push**

```bash
git push --force-with-lease origin main || git push --force origin main
git log --oneline -3
```

`--force-with-lease` is tried first; it refuses if the remote moved unexpectedly. Falling back to `--force` is correct here only because the rewrite intentionally discards the remote's history.

- [ ] **Step 10: Final verification**

```bash
sleep 45
curl -s "https://api.github.com/repos/AndresRubio/ai-digest/actions/runs?per_page=1" \
 | python3 -c "import json,sys; r=json.load(sys.stdin)['workflow_runs'][0]; print(r['status'], r['conclusion'])"
curl -s -o /dev/null -w "live: %{http_code}\n" https://andresrubio.github.io/ai-digest/
curl -s https://api.github.com/repos/AndresRubio/ai-digest/commits?per_page=100 \
 | python3 -c "
import json,sys
c=json.load(sys.stdin)
print('commits:',len(c))
print('author emails:',sorted({x['commit']['author']['email'] for x in c}))
"
```

Expected: `completed success`; `live: 200`; and author emails showing only the noreply address and `noreply@anthropic.com`.

- [ ] **Step 11: Tell the user what the rewrite did and did not achieve**

State plainly: the strings are out of the visible history and the working tree, the author email is scrubbed, Pages is green, and the backup bundle is at `~/Desktop/ai-digest-pre-rewrite-2026-09-16.bundle`. Also state that GitHub may keep the old commits reachable by direct SHA until it garbage-collects, and that any existing clone or fork retains them — so this is "out of the visible history", not erasure. Offer to keep or delete the bundle.

---

## Notes for the executor

- **Task 6 Step 2 is a hard stop.** Pushing before the secret exists turns the deploy red. That is the guard working, but fix it by creating the secret, not by weakening the guard.
- **Never start Task 7 on a red Task 6.** Rewriting history over an unverified tree makes diagnosis far harder.
- **If anything goes wrong in Task 7:** `git fetch ~/Desktop/ai-digest-pre-rewrite-2026-09-16.bundle 'refs/*:refs/*'`, reset to the SHA in `~/Desktop/ai-digest-pre-rewrite-HEAD.txt`, and force-push back.
- The literal mailbox strings must never appear in a commit message, this plan, or the spec. Every pattern is derived at runtime from the gitignored `sources.json`.
- **Never hand-type even a fragment of a mailbox name.** The derived pattern matches whole
  local-parts, so a fragment typed into a file passes the check while still identifying the
  account. The first draft of this plan did exactly that in three places and the check
  reported clean — the same too-narrow-pattern failure that put 20 identifiers in a public
  repo. When a command needs the pattern, derive it at runtime; never paste it.
