---
name: code-reviewer
description: Boreal DS code review toolkit. Runs automated static analysis against Stencil/TypeScript components, maps findings to the project checklist, and saves a Markdown report to ai-work/reviews/. Use when reviewing pull requests or preparing changes for peer review.
---

# Code Reviewer

Automated review toolkit for the Boreal DS monorepo. Works by inspecting the git diff of the current worktree against `main`, scanning changed TypeScript/TSX/SCSS files for Boreal DS rule violations, and writing a structured review report.

## Scope

This skill is designed for reviewing changes to the Boreal DS monorepo. Findings are categorized by **severity** (Blocking/Should Fix/Nice to Have) and **scope** (Frontend/Documentation/Testing), aligned with the three specialist subagents:

- **Frontend** — Component structure, events, props, accessibility, cross-browser safety, SCSS patterns
- **Documentation** — MDX accuracy, stories, argTypes wiring, code examples, API completeness
- **Testing** — Coverage, assertion strength, edge cases, FACE lifecycle testing

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

### Phase 4 — Consolidated Findings

After Phase 3 (or Phase 5 if subagents are dispatched), consolidate ALL findings into a single actionable list.

#### Categorization Rules

Every finding must be classified by **severity** and **scope**:

**Severity levels** (fixed):

- 🔴 **Blocking** — Must fix before merge (correctness bugs, regressions, broken examples)
- 🟡 **Should Fix** — Quality improvements (inert controls, missing docs, weak tests)
- 🟢 **Nice to Have** — Minor enhancements (style deviations, token semantics)

**Scope** (aligned with subagents):

- **Frontend** — Component structure, events, props, accessibility, cross-browser, SCSS
- **Documentation** — MDX accuracy, stories, argTypes, code examples, API completeness
- **Testing** — Coverage, assertions, edge cases, FACE lifecycle

**Combined format**: `<severity> - <scope>`

#### Table Format

Each category uses this exact table structure:

```markdown
### 🔴 Blocking - Frontend

| #   | File                    | Line(s) | Issue                                                                                                                     | Fix                                                          | PR comment                                                                |
| --- | ----------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| 1   | `bds-file-uploader.tsx` | 36-55   | **Missing `@Watch('multiple')`** — Prop delegation only happens in `componentWillLoad()`. Runtime changes have no effect. | Add `@Watch('multiple')` handler that calls `preloadAttrs()` | Runtime `multiple` changes may not apply to the children — can you check? |
```

**`PR comment` column**: One plain-language sentence the reviewer can paste onto the PR. State the concern only — no root-cause detail and no suggested fix. Do not use `|` inside the cell (reword or escape it) so the table keeps its columns. Applies to the severity × scope findings tables only, not to Out of Scope or Confirmed Correct.

**Numbering**: Sequential within each category (1, 2, 3...)

**Ordering within categories**:

1. By file path (alphabetical)
2. By line number (ascending)
3. By severity within same file

**Source attribution**: Add source in parentheses at the end of the **Issue** column (the `PR comment` column carries no source tag):

- `(automated)` — from `code_quality_checker.py`
- `(memory)` — from Phase 3 memory-guided review
- `(frontend-subagent)` — from frontend validation
- `(testing-subagent)` — from testing validation
- `(documentation-subagent)` — from documentation validation
- `(manual)` — from agent's own analysis

#### Sections to Include

Only include sections that have findings. Order by severity (Blocking → Should Fix → Nice to Have), then by scope (Frontend → Documentation → Testing).

The severity × scope findings tables include the `PR comment` column; Out of Scope and Confirmed Correct do not.

**Always include** (even if empty):

- **Out of Scope** — Pre-existing issues on unrelated components
- **Confirmed Correct** — Aspects verified as working (two-column table: Aspect | Assessment — no `PR comment` column)

**Omit if empty**:

- All severity × scope combinations (e.g., "Blocking - Frontend", "Should Fix - Documentation", etc.)

### Phase 5 — Subagent Validation (Optional)

For PRs touching multiple packages or with significant changes, dispatch specialist subagents in parallel.

#### When to Dispatch

- PR touches 3+ files across frontend + docs + tests
- PR adds a new component or major feature
- PR modifies core utilities (e.g., `src/utils/form/internals.ts`)

#### Subagent Dispatch

Dispatch these three subagents in parallel:

1. **frontend-subagent**: Validate component structure, event naming, prop delegation, slot architecture, SCSS, accessibility, cross-browser safety
2. **testing-subagent**: Validate test coverage, assertion strength, edge-case testing, FACE lifecycle coverage
3. **documentation-subagent**: Validate MDX accuracy, stories correctness, argTypes wiring, code-example validity, API completeness

#### Merging Subagent Outputs

Each subagent returns:

- Confirmed findings (with line numbers)
- Refuted findings (with reasoning)
- Additional findings (with severity classification)

Merge into the consolidated findings table using the categorization rules above. Attribute each finding to its source subagent.

### Phase 6 — Core Utility Regression Analysis

If the PR modifies files in `src/utils/` or other shared utilities:

1. **Identify callers**: Grep across `src/` for all usages of the changed utility
2. **Assess each change**:
   - Is it used by the component under review?
   - Is it used by any other component?
   - Is it backward-compatible?
3. **Create usage table**:

```markdown
| Change         | Used by Component? | Used by Others? | Regression Risk |
| -------------- | ------------------ | --------------- | --------------- |
| Type expansion | ✅ Yes             | ✅ Yes          | ✅ Safe         |
| New parameter  | ❌ No              | ❌ No           | ⚠️ Dead code    |
```

4. **Recommendations**:
   - If dead code is found, recommend removal
   - If no unit tests exist for the utility, recommend adding them
   - If backward compatibility is broken, flag as 🔴 Blocking

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

| Rule                              | Severity | What it checks                                                                                                                                                                                                                                                                                                                         |
| --------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prop-missing-jsdoc`              | error    | `@Prop()` without a JSDoc block directly above                                                                                                                                                                                                                                                                                         |
| `prop-not-readonly`               | error    | `@Prop()` missing `readonly` (and not `mutable: true`)                                                                                                                                                                                                                                                                                 |
| `event-native-collision`          | error    | `@Event()` name that matches a native DOM event                                                                                                                                                                                                                                                                                        |
| `fileoverview-tag`                | error    | `@fileoverview` used instead of `@file`                                                                                                                                                                                                                                                                                                |
| `face-missing-attach-internals`   | error    | `formAssociated: true` without `@AttachInternals()` on the class                                                                                                                                                                                                                                                                       |
| `face-native-constraint-on-input` | error    | Inner `<input>` carrying native constraint attributes                                                                                                                                                                                                                                                                                  |
| `class-jsdoc-internal`            | error    | `@internal` in a component class JSDoc                                                                                                                                                                                                                                                                                                 |
| `class-jsdoc-stale-slot`          | error    | `@slot` tag in class JSDoc with no matching `<slot>` rendered in the file                                                                                                                                                                                                                                                              |
| `mutable-prop-any-cast`           | warning  | Mutable prop assigned with `as any`                                                                                                                                                                                                                                                                                                    |
| `nodetype-check`                  | warning  | `.nodeType` used instead of `instanceof Element`                                                                                                                                                                                                                                                                                       |
| `unsafe-any`                      | warning  | Broad `any` usage in types or casts                                                                                                                                                                                                                                                                                                    |
| `class-jsdoc-invalid-tags`        | warning  | `@element` or `@method` in class-level JSDoc                                                                                                                                                                                                                                                                                           |
| `face-reset-no-validity`          | warning  | `formResetCallback` without `updateValidity()`/`setValidity()`                                                                                                                                                                                                                                                                         |
| `face-restore-no-validity`        | warning  | `formStateRestoreCallback` without validity re-sync                                                                                                                                                                                                                                                                                    |
| `spec-form-disabled-wrong`        | error    | Test uses `form.disabled` instead of `<fieldset disabled>`                                                                                                                                                                                                                                                                             |
| `spec-missing-wait-for-changes`   | warning  | DOM assertion after prop set with no `waitForChanges()`                                                                                                                                                                                                                                                                                |
| `import-order`                    | warning  | Import order violates: framework → `@/services` → `@/mixins` → `@/utils` → local                                                                                                                                                                                                                                                       |
| `barrel-wildcard-export`          | warning  | `export * from '...'` in a barrel file; use named re-exports instead                                                                                                                                                                                                                                                                   |
| `bool-prop-prefix`                | error    | `@Prop()` name starts with `is`, `has`, or `show`                                                                                                                                                                                                                                                                                      |
| `event-name-format`               | error    | `@Event()` name does not follow `bds{Action}` format                                                                                                                                                                                                                                                                                   |
| `prop-in-mixin`                   | error    | `@Prop()` declared inside a mixin factory function                                                                                                                                                                                                                                                                                     |
| `mixin-noop-constructor`          | warning  | No-op `constructor(...args)` in a `mixins/` file                                                                                                                                                                                                                                                                                       |
| `aria-camel-set-attr`             | error    | `setAttribute` called with a camelCase ARIA attribute name                                                                                                                                                                                                                                                                             |
| `declare-global-popover`          | warning  | Dead `declare global` Popover API augmentation block                                                                                                                                                                                                                                                                                   |
| `interface-bds-prefix`            | error    | Interface file named `IBds*.ts` instead of `I*.ts`                                                                                                                                                                                                                                                                                     |
| `getter-get-prefix`               | warning  | Getter accessor has a redundant `get` prefix in its name                                                                                                                                                                                                                                                                               |
| `unused-state`                    | warning  | `@State()` field whose name appears nowhere else in the file                                                                                                                                                                                                                                                                           |
| `unused-prop`                     | warning  | `@Prop()` field (without `reflect: true`) whose name appears nowhere else in the file                                                                                                                                                                                                                                                  |
| `unstable-state-reference`        | warning  | Self-referencing `{ ...x, ... }` spread reassigned/returned with no preceding guard checking whether the value actually changed — always creates a new reference, causing redundant re-renders                                                                                                                                         |
| `scss-unscoped-selector`          | error    | A component `.scss` file's own top-level selector (`table`, `thead th`, `td[data-pinned]`, etc.) sits outside the `bds-*` root tag block — Stencil compiles it as unscoped, global CSS that leaks onto any matching element on the page, including other components. See `.agents/memory/stencil-light-dom-unscoped-selector-leak.md`. |

## Reference Documentation

- `ai-docs/guidelines/code-review-checklist.md` — full Boreal DS review checklist (sections 0–F)

## Report Template

The final report must follow this structure:

```markdown
# Boreal DS — Code Review Report

**Generated:** <timestamp>
**Base ref:** `<branch>`
**Repository:** `<path>`
**Validated by:** <subagent list if dispatched, else omit>

## Affected Packages

<from pr_analyzer.py>

## Automated Findings

<from code_quality_checker.py + pr_analyzer.py>

## Review Checklist

<from review_report_generator.py with Phase 2 enrichment>

## Memory-Guided Review

<from Phase 3>

---

## Consolidated Findings

<Only include severity × scope sections that have findings. Order: Blocking → Should Fix → Nice to Have, then Frontend → Documentation → Testing>

### 🔴 Blocking - Frontend

<table — findings table, includes the PR comment column>

### 🔴 Blocking - Documentation

<table — findings table, includes the PR comment column>

... (other severity × scope sections as needed)

### ℹ️ Out of Scope

<table — no PR comment column>

### ✅ Confirmed Correct

<table — no PR comment column>

---

## Core Utility Regression Analysis

<from Phase 6, if applicable>

## Test Suite Assessment

<if testing-subagent dispatched, include coverage summary>

---

## Overall Assessment

**<Ready to merge | Not ready to merge>.** <N> actionable findings.

### Blocking (must fix before merge)

<list of blocking findings>

### Should Fix (quality)

<list of should-fix findings>

### Nice to Have

<list of nice-to-have findings>

### Refuted Findings

<list or "None">

---

**Result: <X> passed · <Y> failed**
```
