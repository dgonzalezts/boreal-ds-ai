---
name: stencil-scoped-test-invocation
description: "How to correctly scope a Jest/Stencil test run to one component, and why with-node.sh requires --filter instead of cd."
---

Two verified, non-obvious constraints when running the spec suite scoped to a single component (discovered during `bds-tooltip` Stryker mutation testing, 2026-07-01, Stencil 4.42.1).

**1. Do not use `--testPathPattern` to scope a run.**

`stencil test --spec -- --testPathPattern=bds-tooltip` gets mangled by Stencil's CLI wrapper into a character-class regex (`/b|d|s|-|t|o|o|l|t|i|p/i`) before it reaches Jest. This matches almost any file in the repo containing any single one of those characters, silently running (or "covering") far more than intended. Reproduces even with clean, unquoted args — not a shell-quoting artifact, but a quirk in how Stencil forwards this specific flag.

Correct alternative: pass a bare positional path or glob, which Stencil forwards to Jest correctly:

```bash
pnpm --filter boreal-web-components run test -- src/components/overlays/bds-tooltip
```

To scope coverage stats to the same component (otherwise `test:coverage` computes the percentage against the project-wide `collectCoverageFrom` default even when only one component's specs ran, producing a misleadingly low number), pass `--collectCoverageFrom` explicitly:

```bash
.agents/scripts/with-node.sh pnpm --filter boreal-web-components run test:coverage -- \
  src/components/overlays/bds-tooltip \
  --collectCoverageFrom="src/components/overlays/bds-tooltip/**/*.tsx"
```

`--collectCoverageFrom` glob must match **all** component source files (main component + sub-components + utils). Use `**/*.tsx` pattern.

**2. `--coverageReporters` must be passed twice (or more).**

Stencil's CLI parses a single `--coverageReporters=text` as a string and forwards it to Jest, which expects an array. This causes `TypeError: coverageReporters.forEach is not a function` in Jest's CoverageReporter. Multiple flags create the required array:

```bash
.agents/scripts/with-node.sh pnpm --filter boreal-web-components run test:coverage -- \
  src/components/overlays/bds-tooltip \
  --collectCoverageFrom="src/components/overlays/bds-tooltip/**/*.tsx" \
  --coverageReporters=text --coverageReporters=text-summary
```

**2. `with-node.sh` resets the working directory to repo root internally.**

`.agents/scripts/with-node.sh` runs `cd "$(git rev-parse --show-toplevel)"` before exec'ing its argument. A prior `cd packages/boreal-web-components && .agents/scripts/with-node.sh pnpm run test` silently loses the `cd` — the wrapper resolves `pnpm run test` against the workspace root, not the package, and fails with `Missing script`.

Use `pnpm --filter <package>` from the repo root instead of `cd`-ing into the package directory when invoking commands through `with-node.sh`. `--filter` is unaffected by cwd.

Full command examples and context: `.claude/skills/testing-knowledge/SKILL.md` §"Running the Spec Suite Scoped to One Component".
