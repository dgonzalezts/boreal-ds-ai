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

- The primary intent (feature, bug fix, refactor, docs, chore, test, performance, hotfix, security, breaking change)
- The Jira ticket reference (e.g. `EOA-10099`)
- The affected package scope (`web-components`, `boreal-docs`, `boreal-styleguidelines`, `boreal-react`, `boreal-vue`)
- Whether any alternatives were considered that reviewers should know about
- Whether this is a breaking change (requires `!` in commit format)

## Step 2: Select the Appropriate Template

Based on the PR type identified in Step 1, select the matching template from `references/`:

| PR Type             | Template File                 | When to Use                                       |
| ------------------- | ----------------------------- | ------------------------------------------------- |
| **Feature**         | `feature-template.md`         | New functionality, components, or capabilities    |
| **Bug Fix**         | `bugfix-template.md`          | Fixes for defects, errors, or incorrect behavior  |
| **Hotfix**          | `hotfix-template.md`          | Urgent production fixes (security, critical bugs) |
| **Refactoring**     | `refactoring-template.md`     | Code improvements with no functional changes      |
| **Documentation**   | `documentation-template.md`   | README, JSDoc, Storybook, or guide updates        |
| **Security Patch**  | `security-patch-template.md`  | Security vulnerabilities (XSS, CSRF, CVE, etc.)   |
| **Test**            | `test-template.md`            | Adding/fixing tests only (no implementation)      |
| **Performance**     | `performance-template.md`     | Optimizations for speed, memory, or bundle size   |
| **Breaking Change** | `breaking-change-template.md` | API changes requiring consumer code updates       |

**Multi-type PRs:** If a PR spans multiple types (e.g., feature + docs), choose the primary type and mention secondary changes in the "Related Changes" section.

## Step 3: Write the Title

Follow the project's conventional commits format exactly:

```
<type>(<scope>): <TICKET> <imperative description>
```

For **breaking changes**, add `!` after the scope:

```
<type>(<scope>)!: <TICKET> <imperative description>
```

- **type:** `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `style`, `perf`
- **scope:** affected package short-name (e.g. `web-components`, `boreal-docs`, `boreal-react`)
- **TICKET:** always present, always before the description (e.g. `EOA-10099`)
- **`!`:** signals breaking change (breaking-change-template.md only)
- **Max length:** 100 characters total, matching `header-max-length` in `commitlint.config.js`

## Step 4: Fill in the Template

Open the selected template from `references/` and fill in all sections:

1. **Replace placeholder text** with actual PR content
2. **Fill required sections** (Description, Testing, etc.)
3. **Check applicable checkboxes** (mark with `[x]`)
4. **Remove non-applicable sections** (e.g., "Screenshots" if none)
5. **Add ticket reference** (`Refs` or `Closes` EOA-XXXXX)

**Template Sections:**

- **Description**: What changed and why (motivation, problem solved)
- **Implementation/Details**: How it was done (approach, patterns, decisions)
- **Impact**: Effects on existing code, performance, breaking changes
- **Testing**: Automated and manual verification steps
- **Related Changes**: Multi-scope impacts (other packages, docs, etc.)
- **Additional Remarks**: Context for reviewers, deferred work, non-obvious constraints
- **Checklist**: Project-specific quality gates (coverage, tokens, accessibility, etc.)

**Checklist Guidelines:**

- Check items you've completed: `- [x] Item completed`
- Leave unchecked if not applicable: `- [ ] Not applicable to this PR`
- Delete entire sections that don't apply (e.g., "Form Components" for non-form PRs)

See `references/pr-examples.md` for quick reference examples of well-formed Boreal DS PRs.

## Step 5: Output the Result

Write the completed PR title and body to `.claude/pr-description.md` at the workspace root:

```markdown
# PR Title

<title here>

---

# PR Body

<completed template content here>
```

**Important:**

- Remove all placeholder text from the template
- Keep the checklist with items marked appropriately
- Include the ticket reference (Refs/Closes EOA-XXXXX)
- Preserve section headings for readability

After writing the file, tell the user the path so they can open it directly. Do not print the full content inline in the terminal.

## Issue Reference Syntax

| Syntax              | Effect                      |
| ------------------- | --------------------------- |
| `Closes EOA-XXXXX`  | Closes the ticket on merge  |
| `Refs EOA-XXXXX`    | Links without closing       |
| `Refs #<PR-number>` | Cross-references another PR |

## Guidelines

- **One PR per feature or fix** — do not bundle unrelated changes
- **The description explains _why_**; the diff shows _what_
- **Use checklists** to verify quality gates before requesting review
- **Draft PRs preferred** for early, in-progress feedback
- **Templates are starting points** — adapt sections to fit your PR's specific needs
- **Delete non-applicable sections** rather than leaving placeholder text
