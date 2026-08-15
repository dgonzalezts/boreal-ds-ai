---
name: commitlint-scope-is-package-not-component
description: "commitlint scope-enum only accepts package/workspace names, never a component name — even if a plan's stated commit message uses one."
---

`commitlint.config.js`'s `scope-enum` rule restricts commit scopes to a fixed package/workspace
list: `[react, vue, web-components, styles, docs, examples, scripts, workspace, ci, deps, release,
multiple]`. It does **not** accept component names like `bds-calendar-grid`, `bds-button`, etc.

A commit message like `test(bds-calendar-grid): EOA-16692 add accessibility unit tests` fails the
`commit-msg` husky hook with:

```
✖   scope must be one of [react, vue, web-components, styles, docs, examples, scripts, workspace, ci, deps, release, multiple] [scope-enum]
```

This matters because implementation plans (`ai-work/plans/*.md`) sometimes write example commit
commands using the component name as the scope — copy-pasting that literally will fail commitlint.
Before committing, check `git log --oneline -10` for the actual convention already used earlier in
the same branch/feature (e.g. `feat(web-components): EOA-16692 ...`) and follow that scope, moving
the component name into the commit subject instead:

```bash
git commit -m "test(web-components): EOA-16692 add bds-calendar-grid accessibility unit tests"
```

Verified during `bds-calendar-grid` a11y test task (EOA-16692 Task 11) — all prior commits on that
branch used `web-components` as the scope, never the component name.
