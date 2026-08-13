---
name: stencil-testpathpattern-vs-passthrough-arg
description: stencil test --spec --testPathPattern "X" silently matches an alternation-of-characters regex instead of scoping to a path; use a bare passthrough path after -- instead
metadata:
  type: project
---

`node_modules/.bin/stencil test --spec --coverage --testPathPattern "date-engine"` does not scope
to the intended path the way it would with raw `jest`. Stencil's CLI wraps the jest args, and the
value comes through mangled into a per-character alternation regex (`/d|a|t|e|-|e|n|g|i|n|e/i`),
which matches nearly every spec file in the repo and runs the entire suite instead of the target
files.

**Fix**: pass the target path as a bare positional arg after `--` instead of via `--testPathPattern`:

```bash
node_modules/.bin/stencil test --spec --coverage -- src/services/date-engine
```

This also confirms and extends the existing memory note
`.agents/memory/bds-search-bar` area's observation that `--testPathPattern` "doesn't scope
correctly in this repo's test runner" — the concrete failure mode is this character-alternation
mangling, and the working alternative is the bare-path passthrough form above.

**To check per-file coverage** (not just whether tests pass) when running a scoped subset, the
global coverage threshold in `jest.config` will fail spuriously (it's computed against files
actually touched by the run, not the whole repo, but the threshold config still applies per-run).
Override it and scope coverage collection to just the target file:

```bash
node_modules/.bin/stencil test --spec --coverage --coverageThreshold='{}' \
  -- --collectCoverageFrom='src/services/date-engine/grid.ts' src/services/date-engine
```
