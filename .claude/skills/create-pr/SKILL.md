---
name: create-pr
description: Create pull request descriptions following Boreal DS conventions. This skill should be used when opening PRs, writing PR descriptions, or preparing changes for review. Works cross-tool — produces a title and body to copy into any platform (GitHub, Bitbucket, CLI, web UI). Does not automate submission.
---

# Create Pull Request

Produce a PR title and description following Boreal DS engineering conventions.

## Step 1: Analyse the Changes

Before writing, resolve the base branch, then inspect what will be in the PR:

```bash
# Resolve the default remote branch (works regardless of main/master/develop)
BASE=$(git rev-parse --abbrev-ref origin/HEAD | sed 's|origin/||')

git log $BASE..HEAD --oneline        # all commits going in
git diff $BASE...HEAD --stat         # files changed (three-dot: from common ancestor)
```

If `origin/HEAD` is not set, fall back to reading the repo's default branch name
from the platform (e.g. GitHub UI) or asking the user which branch to target.

Determine:
- The primary intent (feature, bug fix, refactor, docs, chore)
- The Jira ticket reference (e.g. `EOA-10099`)
- The affected package scope (`web-components`, `boreal-docs`, `boreal-styleguidelines`)
- Whether any alternatives were considered that reviewers should know about

## Step 2: Write the Title

Follow the project's conventional commits format exactly:

```
<type>(<scope>): <TICKET> <imperative description>
```

- **type:** `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `style`
- **scope:** affected package short-name (e.g. `web-components`, `boreal-docs`)
- **TICKET:** always present, always before the description

## Step 3: Write the Description

Use this four-section structure. Omit any section with nothing genuine to say:

```
<One sentence — what this PR does at the highest level.>

<Why — the motivation. What problem does this solve or what decision does it establish?>

<Alternatives considered, if any — what was tried or rejected and why.>

<Notes for reviewers — non-obvious constraints, intentionally deferred items, or areas needing careful attention.>

Refs EOA-XXXXX
```

**Include:** ticket reference (`Refs` or `Closes`), links to related PRs or plan documents.
**Do not include:** test plan sections, bullet-point diff summaries, or padding.

See `references/pr-examples.md` for concrete Boreal DS PR examples.

## Step 4: Output the Result

Write the PR title and body to `.claude/pr-description.md` at the workspace root so the user can open it in their editor and copy freely:

```markdown
# PR Title

<title here>

---

# PR Body

<body here>
```

After writing the file, tell the user the path so they can open it directly. Do not print the full content inline in the terminal.

## Issue Reference Syntax

| Syntax | Effect |
|---|---|
| `Closes EOA-XXXXX` | Closes the ticket on merge |
| `Refs EOA-XXXXX` | Links without closing |
| `Refs #<PR-number>` | Cross-references another PR |

## Guidelines

- One PR per feature or fix — do not bundle unrelated changes
- The description explains *why*; the diff shows *what*
- Draft PRs are preferred for early, in-progress feedback
