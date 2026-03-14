---
name: code-reviewer
description: Boreal DS code review toolkit. Runs automated static analysis against Stencil/TypeScript components, maps findings to the project checklist, and saves a Markdown report to .ai/reviews/. Use when reviewing pull requests or preparing changes for peer review.
---

# Code Reviewer

Automated review toolkit for the Boreal DS monorepo. Works by inspecting the git diff of the current worktree against `main`, scanning changed TypeScript/TSX files for Boreal DS rule violations, and writing a structured review report.

## Typical Workflow

```
1. Create (or switch to) the worktree for the branch you want to review
2. Run one command from the worktree root:

   python3 .claude/skills/code-reviewer/scripts/review_report_generator.py .

3. Open the generated report in .ai/reviews/
```

The script auto-derives the output filename from today's date, the current HEAD SHA, and the branch name — matching the `YYYY-MM-DD-commit-<sha>-<branch>-review.md` convention.

## Worktree Compatibility

All three scripts accept a `repo_path` argument and run `git` commands with `cwd=repo_path`. This means they read the git context (branch, SHA, diff) of the worktree they are pointed at, regardless of what is checked out elsewhere. No branch-switching is needed — just point at the worktree root.

## Scripts

### `review_report_generator.py` — Full pipeline (start here)

Orchestrates the two scripts below, renders a Markdown checklist report, and saves it to `.ai/reviews/`.

```bash
# Standard run — auto-saves to .ai/reviews/
python3 .claude/skills/code-reviewer/scripts/review_report_generator.py .

# Diff against a branch other than main
python3 .claude/skills/code-reviewer/scripts/review_report_generator.py . --base release/current

# Save to a custom path instead
python3 .claude/skills/code-reviewer/scripts/review_report_generator.py . --output path/to/report.md

# Print report only, do not write to disk
python3 .claude/skills/code-reviewer/scripts/review_report_generator.py . --no-save
```

### `pr_analyzer.py` — PR scope and hygiene

Inspects `git diff <base>...HEAD` to detect which packages are touched, which checklist sections (A–E) apply, and whether tests, stories, or a changeset are missing.

```bash
python3 .claude/skills/code-reviewer/scripts/pr_analyzer.py .
python3 .claude/skills/code-reviewer/scripts/pr_analyzer.py . --base release/current --verbose
```

### `code_quality_checker.py` — Static analysis

Scans `.tsx`/`.ts` files for violations of Boreal DS coding standards. When run via `review_report_generator.py` it scans only the changed files; when run directly it scans any path.

```bash
# Scan a single component
python3 .claude/skills/code-reviewer/scripts/code_quality_checker.py packages/boreal-web-components/src/components/forms/bds-checkbox/

# Scan the whole web-components package
python3 .claude/skills/code-reviewer/scripts/code_quality_checker.py packages/boreal-web-components/
```

## Rules Enforced

| Rule | Severity | What it checks |
|---|---|---|
| `prop-missing-jsdoc` | error | `@Prop()` without a JSDoc block directly above |
| `prop-not-readonly` | error | `@Prop()` missing `readonly` (and not `mutable: true`) |
| `event-native-collision` | error | `@Event()` name that matches a native DOM event |
| `fileoverview-tag` | error | `@fileoverview` used instead of `@file` |
| `face-missing-attach-internals` | error | `formAssociated: true` without `@AttachInternals()` on the class |
| `face-native-constraint-on-input` | error | Inner `<input>` carrying native constraint attributes |
| `class-jsdoc-internal` | error | `@internal` in a component class JSDoc |
| `mutable-prop-any-cast` | warning | Mutable prop assigned with `as any` |
| `nodetype-check` | warning | `.nodeType` used instead of `instanceof Element` |
| `unsafe-any` | warning | Broad `any` usage in types or casts |
| `class-jsdoc-invalid-tags` | warning | `@element` or `@method` in class-level JSDoc |
| `face-reset-no-validity` | warning | `formResetCallback` without `updateValidity()`/`setValidity()` |
| `face-restore-no-validity` | warning | `formStateRestoreCallback` without validity re-sync |
| `spec-form-disabled-wrong` | error | Test uses `form.disabled` instead of `<fieldset disabled>` |
| `spec-missing-wait-for-changes` | warning | DOM assertion after prop set with no `waitForChanges()` |
| `import-order` | warning | Import order violates: framework → `@/services` → `@/mixins` → `@/utils` → local |
| `barrel-wildcard-export` | warning | `export * from '...'` in a barrel file; use named re-exports instead |

## Reference Documentation

- `references/code_review_checklist.md` — full Boreal DS review checklist (sections 0–E)
- `references/coding_standards.md` — coding standards summary
- `references/common_antipatterns.md` — recurring failure patterns with explanations
