---
name: repo-root-diff-stat-unrelated-changes
description: git diff --stat at repo root shows large pre-existing unrelated working-tree changes; scope diffs to the component path
metadata:
  type: project
---

As of 2026-09-24, `git diff --stat` at the repo root reports ~9k lines across files unrelated to any current frontend task: `examples/react-testapp/package.json` + `src/App.tsx`, `examples/vue-testapp/src/App.vue`, `packages/boreal-react/package.json`, `packages/boreal-web-components/src/index.html`, and `pnpm-lock.yaml`. These are pre-existing working-tree modifications, not produced by the task at hand.

Consequence: when a task's acceptance criterion is "the diff is import-only / scope-only", a bare `git diff` / `git diff --stat` looks catastrophically large and can be mistaken for an accidental mass edit. Always scope the verification to the changed paths:

```
git diff -- <path1> <path2>
git diff --stat -- packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/
```

Only the scoped diff is meaningful for the change under review. Do not stage or commit the unrelated files.
