---
name: coverage-verify-touched-lines-not-whole-file
description: For a regression-check task on a small diff, verify coverage on the specific touched lines via lcov.info hit-counts, not the whole-file percentage — pre-existing gaps are common and out of scope.
metadata:
  type: feedback
---

`bds-search-bar.tsx` and `bds-select.tsx` sit at ~70%/72% statement/branch coverage overall (below the project's 80% Jest threshold in `testing.config.ts`), driven by long-standing untested debounce/keyboard/pointerdown logic unrelated to any given small diff.

**Why:** When asked to verify a small, targeted change (e.g. one new classMap key + a couple of SCSS `flex-shrink` additions) didn't break anything, running whole-file `test:coverage` reports a scary sub-90% (even sub-80%) number that has nothing to do with the change under review. Backfilling the whole component to 90% is a large, separate undertaking and is out of scope for a regression-check task — per `plan-execution.md` "keep scope tight."

**How to apply:** After running scoped `test:coverage`, don't stop at the summary percentage. Cross-check the specific line ranges the diff touched against `coverage/lcov.info`:

```bash
awk '/SF:.*<path-to-file>$/{flag=1} flag{print} /end_of_record/{if(flag){exit}}' \
  packages/boreal-web-components/coverage/lcov.info | grep '^DA:' | awk -F',' '$2==0'
```

If the touched lines all show a non-zero hit-count, the diff itself is fully exercised even though the file-wide score is low — report both facts distinctly (file-wide score vs. touched-lines coverage) rather than blocking on the aggregate number. Only treat the aggregate gate as blocking when the task is "write/complete tests for this component" rather than "confirm this specific change didn't regress anything."

**Scoped-command gotcha (2026-09-28, `bds-calendar-grid`):** with a *narrow* positional path
(`.../bds-calendar-grid`) and a *broad* `--collectCoverageFrom` glob (`.../bds-date-picker/**/*.tsx`),
`test:coverage` exits non-zero (`ERR_PNPM_RECURSIVE_RUN_FIRST_FAIL`) because the **global 80%
threshold** in `testing.config.ts` is evaluated against the aggregate, which now includes untested
sibling component files (`bds-date-picker.tsx` + its `helpers/render*.tsx` at 0%). The component
under test can be at 98.37% stmts / 94.98% branches and the command still fails. Fix: point
`--collectCoverageFrom` at the component's own directory
(`.../bds-calendar-grid/**/*.tsx`) so the aggregate == the component — then the command is green
(`EXIT=0`). Report both runs when the task prescribes the broad glob.
