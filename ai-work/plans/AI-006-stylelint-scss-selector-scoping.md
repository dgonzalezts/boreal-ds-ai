---
ticket: —
status: pending
created: 2026-08-28
---

# Stylelint: Enforce SCSS Selector Scoping Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Add a mechanical, CI/pre-commit-enforced lint rule that forbids top-level (non-nested) selectors in Stencil component SCSS files outside the component's own `bds-*` root tag block — the exact defect class that caused the `bds-table`/`bds-calendar-grid` CSS leak (EOA-17494/EOA-17495, see `.agents/memory/stencil-light-dom-unscoped-selector-leak.md`).

**Architecture:** No built-in stylelint rule or published plugin checks "is this selector nested under a specific host selector" — it's a domain-specific structural constraint, not a generic CSS-quality rule. A small, local custom stylelint plugin (`stylelint.createPlugin`) is the right shape: same detection heuristic already validated in `code_quality_checker.py`'s `scss-unscoped-selector` rule (zero false positives across the whole package, catches all 18 real violations in the pre-fix commit), but running on a proper PostCSS AST via the `postcss-scss` syntax instead of line-based regex, and wired into the enforcement points that already exist (`lint-staged`, package `lint` script) rather than only firing when an agent happens to run the review skill.

**Tech Stack:** `stylelint` 17.14.1, `postcss-scss` 4.0.9 (SCSS-aware parser — required for `&`/interpolation to parse as valid nodes instead of syntax errors). No `stylelint-config-standard-scss` / `stylelint-scss` — deliberately excluded, see Task 1's acceptance criteria.

---

## Files to create / modify

| File                                                                          | Notes                                                                 |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `packages/boreal-web-components/stylelint-plugins/selector-scoped-to-host.cjs` | New — custom plugin implementing the `boreal/selector-scoped-to-host` rule |
| `packages/boreal-web-components/.stylelintrc.cjs`                              | New — stylelint config: `customSyntax: postcss-scss`, loads the plugin |
| `packages/boreal-web-components/package.json`                                  | Modify — add `stylelint`/`postcss-scss` devDependencies; extend `lint`/`lint:fix` scripts |
| `.lintstagedrc.js`                                                             | Modify — run the new lint step on staged `.scss` files (currently only `format` runs) |
| `.agents/memory/stencil-light-dom-unscoped-selector-leak.md`                   | Modify — note the rule is now mechanically enforced, not just documented |
| `.agents/memory/MEMORY.md`                                                     | Modify — changelog entry closing out the scaffold-review item |
| `ai-docs/guidelines/stencil-best-practices.md`                                 | Modify — cross-reference the enforced lint rule name in the existing §"Every selector must nest inside the root tag block" |

---

## Context the implementer needs before starting

- **No CI workflow runs lint today.** `.github/workflows/` has no job invoking `pnpm lint` / `turbo run lint` — the only enforcement point in this repo is the `pre-commit` Husky hook running `lint-staged` (`.lintstagedrc.js`). This plan's rule is therefore enforced **only at commit time**, same as the existing `eslint`/`prettier` checks on this package. Adding a CI lint job is a separate, larger decision (affects every package, not just this rule) — explicitly out of scope here.
- **`.lintstagedrc.js` currently runs only `format` (prettier) on staged `.scss`/`.css` files** — no lint step exists for stylesheets at all today. This plan closes that gap as a side effect.
- **Package-scoped install, not workspace-root.** `eslint`, `prettier`, `@stencil/sass` are all devDependencies of `packages/boreal-web-components/package.json` itself, not hoisted to the workspace root (`package.json` root only carries `turbo`). Follow that existing convention — install `stylelint`/`postcss-scss` scoped to the package via `pnpm --filter @telesign/boreal-web-components add -D <pkg>@<version>`, not `pnpm add -D -w`.
- **Reference implementation already exists and is validated.** `.agents/skills/code-reviewer/scripts/code_quality_checker.py`'s `check_scss_component`/`_is_unscoped_native_selector` functions implement the exact detection heuristic to port: a top-level (nesting depth 0) rule is a violation only if *every* comma-separated part of its selector list starts with a bare, non-hyphenated leading identifier (a native HTML element like `table`/`th`/`td` — Boreal custom elements are always hyphenated `bds-*`, so this cleanly distinguishes "leaked native-element rule" from the file's own legitimate host selector or a class/id/attribute-led selector). This was tested against the real pre-fix commit (`git show HEAD~1` on the CSS-leak bug) and matched all 18 known violations with zero false positives package-wide — port the same logic, don't redesign it.

---

### Task 1: Custom stylelint plugin + config

**Executor:** main thread (no executor — config/tooling task, no component code)
**Files:**

- `packages/boreal-web-components/stylelint-plugins/selector-scoped-to-host.cjs` (create)
- `packages/boreal-web-components/.stylelintrc.cjs` (create)
- `packages/boreal-web-components/package.json` (modify — add devDependencies only in this task; script wiring is Task 2)

**Acceptance criteria:**

- Add devDependencies `stylelint@17.14.1` and `postcss-scss@4.0.9` to `packages/boreal-web-components/package.json`, installed via `pnpm --filter @telesign/boreal-web-components add -D stylelint@17.14.1 postcss-scss@4.0.9` (run `fnm use` first per repo convention). Do **not** add `stylelint-config-standard-scss` or `stylelint-scss` — this plan's scope is the one structural rule that prevents the CSS-leak bug class, not a general lint-rule rollout across ~40 existing component SCSS files (YAGNI; broader adoption is a separate future decision with its own noise/triage cost).
- `selector-scoped-to-host.cjs` exports a plugin built with `stylelint.createPlugin('boreal/selector-scoped-to-host', ...)`. Rule logic, ported from `code_quality_checker.py`:
  - Walk only top-level (root-nesting) `Rule` nodes in the PostCSS AST (i.e. `rule.parent.type === 'root'`) — nested rules are exactly what the fix pattern produces and must never be flagged.
  - Skip non-rule root nodes: `@use`, `@import`, `@mixin`, `@function`, `@keyframes`, `@media`, `@supports`, `@if`/`@else`/`@each`/`@for`/`@while`, SCSS variable declarations (`$foo: ...;` — these parse as `Declaration` nodes at root, not `Rule`, so no special-casing needed beyond checking `node.type === 'rule'`).
  - For a top-level `Rule` node, split `rule.selector` on `,`; for each comma-separated part, take the first whitespace/combinator-separated compound, extract its leading identifier (`^[a-zA-Z][a-zA-Z0-9-]*`). If every part's leading identifier contains no hyphen (i.e. every part is a bare native-HTML-element selector — `table`, `thead th`, `th[data-sortable]`, etc.), report a violation on that rule. A selector where **any** part starts with `.`/`#`/`&`/`[`/`:`/`*`, or with a hyphenated custom-element tag (`bds-*`), is not flagged — this correctly leaves the file's own host selector and any top-level class-based utility (e.g. `.bds-skeleton`) alone, matching current accepted patterns.
  - Message text should name the offending selector and explain the mechanism (unscoped, page-wide CSS via Stencil's global-stylesheet compilation) — mirror the message already used in `code_quality_checker.py`'s `scss-unscoped-selector` finding for consistency between the two tools.
- `.stylelintrc.cjs`: sets `customSyntax: 'postcss-scss'`, loads the plugin via a relative `plugins: ['./stylelint-plugins/selector-scoped-to-host.cjs']`, sets `rules: { 'boreal/selector-scoped-to-host': true }`. No `extends` — this repo has no stylelint config to extend from, and none is being added per the YAGNI decision above.
- Existing shared utilities checked: no existing SCSS-linting infrastructure exists anywhere in the repo (confirmed via repo-wide search for `stylelint` — zero references before this task) — this is genuinely new tooling, not a duplicate of anything.

**Manual test** _(non-visual config task — validate via CLI, not `pnpm dev:components`)_:

- [ ] Given the plugin and config as written, when run via `pnpm --filter @telesign/boreal-web-components exec stylelint 'src/components/data-visualization/bds-table/bds-table/bds-table.scss'` against the **current** (already-fixed) file, then it reports zero violations. Pass: clean exit, no `boreal/selector-scoped-to-host` findings.
- [ ] Given the same command run against a scratch copy of the **pre-fix** file (`git show HEAD~1:packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.scss > /tmp/bds-table-prefix.scss`, then `pnpm --filter @telesign/boreal-web-components exec stylelint --custom-syntax postcss-scss --config .stylelintrc.cjs /tmp/bds-table-prefix.scss`), then it reports a violation for each of the known top-level leaks (`table`, `thead`, `th[data-sortable]`, `th[data-reorderable]`, `th`, `td`, `thead th`, `tbody tr td`, etc. — 16 total per the earlier Python-tool validation). Pass: violation count and flagged selectors match the earlier `code_quality_checker.py` run against the same commit.

**Commit:**

```bash
git commit -m "chore(web-components): AI-006 add custom stylelint rule for SCSS selector scoping"
```

---

### Task 2: Wire into the lint pipeline

**Executor:** main thread (no executor)
**Files:**

- `packages/boreal-web-components/package.json` (modify)
- `.lintstagedrc.js` (modify)

**Acceptance criteria:**

- `packages/boreal-web-components/package.json` scripts:
  - `"lint"` becomes `"eslint && stylelint 'src/**/*.scss'"` (appends to the existing ESLint step rather than replacing it).
  - `"lint:fix"` becomes `"eslint --fix && stylelint 'src/**/*.scss' --fix"` — note in a code comment—free way (no inline comments per project rule; state this only in the plan, not in the file) that `--fix` will not auto-fix `boreal/selector-scoped-to-host` violations (moving a selector into a nested block is a structural change, not something stylelint's autofixer performs) — it's included only for parity with any future auto-fixable rule and for the built-in stylelint formatting fixes it already performs.
  - No new script name needed — folding into the existing `lint`/`lint:fix` means `turbo.json`'s existing `lint`/`lint:fix` task entries (which already just delegate to each package's own script) require **no changes**.
- `.lintstagedrc.js`: the `'packages/boreal-web-components/src/**/*.{css,scss}'` entry currently runs only `format`. Add a preceding step running the new stylelint check, e.g. `() => 'pnpm --filter @telesign/boreal-web-components run lint'` (matching the existing `() => 'command'` function form used elsewhere in this file to avoid lint-staged appending file paths to a `--filter` command — see the file's own header comment for why). Confirm this doesn't redundantly re-run ESLint against `.scss` files (it does — `pnpm run lint` also runs `eslint`, which no-ops harmlessly against non-`.ts`/`.tsx` glob matches per `eslint.config.ts`'s `files: ['src/**/*.{ts,tsx}']`); if that's judged wasteful, use a scoped invocation instead — but prefer the simple form unless it measurably slows the hook.

**Manual test** _(non-visual config task)_:

- [ ] Given a staged change to any `.scss` file under `packages/boreal-web-components/src/`, when `git commit` runs, then the pre-commit hook invokes the new lint step (visible in the hook's console output) before the commit completes. Pass: hook output shows stylelint running, commit succeeds when clean.
- [ ] Given a staged `.scss` file deliberately containing a top-level `table { }` rule outside its host block (scratch-test only — revert before finishing this task), when `git commit` runs, then the hook fails and blocks the commit with the `boreal/selector-scoped-to-host` message. Pass: commit is blocked; revert the scratch violation afterward and confirm a clean commit proceeds normally.

**Commit:**

```bash
git commit -m "chore(web-components): AI-006 wire scss selector-scoping lint into pre-commit and package scripts"
```

---

### Task 3: Full-package validation pass

**Executor:** main thread (no executor — verification-only task; no new source files)
**Files:** none

**Acceptance criteria:**

- Running `pnpm --filter @telesign/boreal-web-components run lint` (or `stylelint 'src/**/*.scss'` directly) against the full, current package tree reports **zero** `boreal/selector-scoped-to-host` violations — cross-checked against the `code_quality_checker.py` full-package sweep already run during the earlier scaffold-review session (which found zero `scss-unscoped-selector` findings across the same tree). Any discrepancy between the two tools' results on the same files is a bug in the new plugin (most likely a PostCSS-AST edge case the regex-based Python tool didn't hit, e.g. SCSS interpolation `#{...}` in a selector) and must be fixed in Task 1's plugin before this task can pass — do not suppress or ignore a real finding to make this task green.
- Document the validation run (command + zero-violation output) in this task's PR/commit description or a short note in `ai-work/qa/` if a discrepancy required a fix, for traceability.

**Manual test:** N/A — this task's acceptance criteria *are* the manual test; no further scenario needed.

**Commit:** N/A — verification-only task; no code changes expected unless the acceptance criteria above force a Task 1 fix (in which case that fix is committed as part of Task 1's commit, amended or as a new commit per normal workflow, not folded in here).

---

### Task 4: Close the loop in docs and memory

**Executor:** main thread (no executor)
**Files:**

- `.agents/memory/stencil-light-dom-unscoped-selector-leak.md` (modify)
- `.agents/memory/MEMORY.md` (modify)
- `ai-docs/guidelines/stencil-best-practices.md` (modify)

**Acceptance criteria:**

- `stencil-light-dom-unscoped-selector-leak.md`'s "Why this class of bug is hard to catch" section gets a short addition noting that, as of this plan, `packages/boreal-web-components` now has a mechanical `stylelint` rule (`boreal/selector-scoped-to-host`) enforced at commit time via `lint-staged` — closing the "static review of `.tsx`/`.ts` misses it" gap for the SCSS side specifically. Keep the existing "Prevention checklist" as-is; add the tooling fact as a new short paragraph, don't rewrite the existing content.
- `MEMORY.md` changelog gets one new entry (dated the day this task lands) referencing this plan (`ai-work/plans/AI-006-stylelint-scss-selector-scoping.md`) and summarizing that the previously-manual/agent-only check is now a real, commit-blocking lint rule.
- `ai-docs/guidelines/stencil-best-practices.md`'s existing §"Every selector must nest inside the root tag block — no top-level siblings" (added during the earlier scaffold review) gets one sentence added noting the rule is enforced by `stylelint`'s `boreal/selector-scoped-to-host` rule, not just documented convention — so a reader knows a violation will be caught mechanically, not just by review discipline.

**Manual test:** N/A — docs-only task, validated by reading the diff for accuracy against Tasks 1–3's actual final state.

**Commit:**

```bash
git commit -m "docs: AI-006 document stylelint enforcement of scss selector scoping"
```
