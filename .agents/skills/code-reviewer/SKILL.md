---
name: code-reviewer
description: Boreal DS code review toolkit. Runs automated static analysis against Stencil/TypeScript components, maps findings to the project checklist, and saves a Markdown report to ai-work/reviews/. Use when reviewing pull requests or preparing changes for peer review.
---

# Code Reviewer

Automated review toolkit for the Boreal DS monorepo. Works by inspecting the git diff of the current worktree against `main`, scanning changed TypeScript/TSX files for Boreal DS rule violations, and writing a structured review report.

## Typical Workflow

### Phase 1 — Run the script

1. Create (or switch to) the worktree for the branch you want to review
2. Run from the worktree root:

   ```
   python3 .claude/skills/code-reviewer/scripts/review_report_generator.py .
   ```

3. Open the generated report in `ai-work/reviews/`

The script auto-derives the output filename from today's date, the current HEAD SHA, and the branch name — matching the `YYYY-MM-DD-commit-<sha>-<branch>-review.md` convention.

### Phase 2 — Reference enrichment

After the script generates the report, read and apply the reference files:

1. Read `ai-docs/guidelines/code-review-checklist.md` and `references/common_antipatterns.md`
2. For every ❌ (fail) item in the checklist, add sub-bullets directly under it in the saved report:
   - The relevant rule from `code-review-checklist.md`
   - The antipattern explanation from `common_antipatterns.md`
3. Edit the saved report file in `ai-work/reviews/` to include these annotations inline

### Phase 3 — Memory-guided review

After Phase 2, perform a semantic second pass using project memory:

1. Read `.claude/memory/MEMORY.md` and identify which topic files apply to the changed files
2. Load those topic files
3. Check for patterns the script cannot detect statically:
   - **`mouseleave` handlers** — check `e.relatedTarget` (destination) vs `e.target` (element being left). Source: `mouseleave-relatedtarget-vs-target.md`
   - **Enum-like props** — verify `validatePropValue + componentWillLoad() + stacked @Watch()` is present. Source: `feedback_prop_validation_pattern.md`
   - **FACE `disabled`** — verify `@State() private isDisabled` + `@Watch` + `formDisabledCallback` all write to the state mirror. Source: `stencil-prop-patterns.md`
   - **Form controls** — check `IFormControl<T>` composite interface in the `implements` clause. Source: `stencil-form-control-interfaces.md`
   - **Light DOM** — flag any `shadow: true` or `::part()` usage. Source: `project_no_shadow_dom.md`
   - **Event naming semantics** — flag names following `bds{Component}{Action}` (component noun embedded in the middle, e.g. `bdsBannerClose`). Source: `feedback_event_naming.md`
4. Replace `<!-- MEMORY_REVIEW_PLACEHOLDER -->` in the saved report with a populated `## Memory-Guided Review` section:
   - One sub-section per topic checked (findings or "No issues found")
   - A "Memory topic files consulted" list at the bottom

## Worktree Compatibility

All three scripts accept a `repo_path` argument and run `git` commands with `cwd=repo_path`. This means they read the git context (branch, SHA, diff) of the worktree they are pointed at, regardless of what is checked out elsewhere. No branch-switching is needed — just point at the worktree root.

## Scripts

### `review_report_generator.py` — Full pipeline (start here)

Orchestrates the two scripts below, renders a Markdown checklist report, and saves it to `ai-work/reviews/`.

```bash
# Standard run — auto-saves to ai-work/reviews/
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

| Rule                              | Severity | What it checks                                                                   |
| --------------------------------- | -------- | -------------------------------------------------------------------------------- |
| `prop-missing-jsdoc`              | error    | `@Prop()` without a JSDoc block directly above                                   |
| `prop-not-readonly`               | error    | `@Prop()` missing `readonly` (and not `mutable: true`)                           |
| `event-native-collision`          | error    | `@Event()` name that matches a native DOM event                                  |
| `fileoverview-tag`                | error    | `@fileoverview` used instead of `@file`                                          |
| `face-missing-attach-internals`   | error    | `formAssociated: true` without `@AttachInternals()` on the class                 |
| `face-native-constraint-on-input` | error    | Inner `<input>` carrying native constraint attributes                            |
| `class-jsdoc-internal`            | error    | `@internal` in a component class JSDoc                                           |
| `class-jsdoc-stale-slot`          | error    | `@slot` tag in class JSDoc with no matching `<slot>` rendered in the file        |
| `mutable-prop-any-cast`           | warning  | Mutable prop assigned with `as any`                                              |
| `nodetype-check`                  | warning  | `.nodeType` used instead of `instanceof Element`                                 |
| `unsafe-any`                      | warning  | Broad `any` usage in types or casts                                              |
| `class-jsdoc-invalid-tags`        | warning  | `@element` or `@method` in class-level JSDoc                                     |
| `face-reset-no-validity`          | warning  | `formResetCallback` without `updateValidity()`/`setValidity()`                   |
| `face-restore-no-validity`        | warning  | `formStateRestoreCallback` without validity re-sync                              |
| `spec-form-disabled-wrong`        | error    | Test uses `form.disabled` instead of `<fieldset disabled>`                       |
| `spec-missing-wait-for-changes`   | warning  | DOM assertion after prop set with no `waitForChanges()`                          |
| `import-order`                    | warning  | Import order violates: framework → `@/services` → `@/mixins` → `@/utils` → local |
| `barrel-wildcard-export`          | warning  | `export * from '...'` in a barrel file; use named re-exports instead             |
| `bool-prop-prefix`                | error    | `@Prop()` name starts with `is`, `has`, or `show`                                |
| `event-name-format`               | error    | `@Event()` name does not follow `bds{Action}` format                             |
| `prop-in-mixin`                   | error    | `@Prop()` declared inside a mixin factory function                               |
| `mixin-noop-constructor`          | warning  | No-op `constructor(...args)` in a `mixins/` file                                 |
| `aria-camel-set-attr`             | error    | `setAttribute` called with a camelCase ARIA attribute name                       |
| `declare-global-popover`          | warning  | Dead `declare global` Popover API augmentation block                             |
| `interface-bds-prefix`            | error    | Interface file named `IBds*.ts` instead of `I*.ts`                               |
| `getter-get-prefix`               | warning  | Getter accessor has a redundant `get` prefix in its name                         |

## Reference Documentation

- `ai-docs/guidelines/code-review-checklist.md` — full Boreal DS review checklist (sections 0–F)
