---
name: stencil-new-optin-prop-breaks-sibling-tests-same-file
description: A new opt-in boolean prop (default false) gating previously-unconditional markup silently breaks pre-existing tests in the same spec file that never set the new attribute
metadata:
  type: project
---

When a plan task adds a new opt-in `@Prop()` (default `false`) that gates markup which used to render unconditionally (e.g. `bds-table`'s `filterable`/`columnLayoutToggle` gating the Filter/Column-visibility buttons and the `hasToolbarRight`/`hasToolbar` getters), pre-existing tests in the *same* spec file that asserted on that markup without ever setting the new attribute will start failing — not because of a test bug, but because the implementation subagent's task scope was narrower than the file's existing coverage.

**Why:** implementation and test-writing are dispatched as separate subagent tasks in this project's plan-execution flow (`.agents/rules/plan-execution.md`). The frontend-subagent's task was scoped to the new props only; it has no mandate to touch the test file. The testing-subagent's task description names only the new scenarios, so it's easy to run just the new tests and miss that 10 older tests in `bds-table.toolbar.spec.ts` regressed (verified during EOA-16000 Task 13: `emits bdsFilter...`, `renders the real Table actions button-group...`, three `searchable` describe tests, and four `toolbar-right skeleton (loading)` tests — all needed `filterable="true"`/`column-layout-toggle="true"` added to their fixture HTML).

**How to apply:** before declaring a testing task complete, run the *entire* target spec file (not just newly-added `it` blocks) and treat any failure as in-scope to fix, even if the task description didn't mention it — the file must be green as a whole. Grep the touched component's render code for new prop-gated conditionals and check every existing spec file in `__test__/` that asserts on the now-gated markup.
