---
name: stencil-auto-merged-spec-silent-regression
description: A spec file with no git conflict markers can still contain a real regression when both merge sides independently rewrote the same it() block under different titles
metadata:
  type: project
---

A `git merge` that reports a spec file as auto-merged (no `<<<<<<<` markers) is not proof the file is correct — it only proves no *line-range* overlapped. When both branches independently rewrite the same logical test (same intent, different `it(...)` title and different assertions), git's line-based 3-way merge treats them as unrelated hunks and can silently keep one side's version while dropping the other's, or keep stale selectors from a hunk that was a pure addition on only one side (no corresponding hunk on the other side to reconcile against).

Confirmed case: `bds-table.toolbar.spec.ts` auto-merged cleanly during the `release/current` → `EOA-15507` merge (commit `23c29d55`). The component's `.tsx` was hand-resolved to use `<bds-toolbar-start>`/`<bds-toolbar-end>` wrapper tags (from `release/current`) while keeping JSX-omission conditionals for the row-actions zone (from the feature branch). The auto-merged spec file silently:
1. Kept `release/current`'s rewritten `it('does not show the row actions zone...')` test (CSS `display:none` expectation) and *dropped* the feature branch's `it('does not render the row actions zone...')` test (JSX-omission / `toBeNull()` expectation) — both were valid `it()` blocks with different titles asserting mutually exclusive behaviors for the same scenario, so git kept only one.
2. Left an entire `describe('toolbar-right skeleton (loading)')` block (added only on the feature branch, no corresponding hunk on the other side) with stale `.bds-table__toolbar-right` selectors, even though sibling tests in the same file that *did* have overlapping hunks were correctly auto-updated to `bds-toolbar-end`.

Net effect: 3 test failures out of 30 in that file, all masked by "no conflict" merge output.

**How to apply:** after any merge that touches a component whose `.tsx` conflict was hand-resolved, do not trust "no conflict markers" for sibling spec files — run the spec suite, and for any spec file that auto-merged (check `git log --merges -p -- <file>` or diff against both `git show <parent1>:<file>` and `git show <parent2>:<file>`) treat passing tests as necessary but not sufficient: grep for it() titles that changed wording between the two parents on the same behavior, since a silently-dropped duplicate test is invisible to a green run.
