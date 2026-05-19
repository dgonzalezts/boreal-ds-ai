# Mutation Testing — Workflow Decisions

Decisions made during the `bds-grid` / `bds-grid-item` mutation testing session (2026-04-20).
These govern how Stryker is used across the project going forward.

---

## Stryker stays local — never pushed to remote

All Stryker artifacts (`stryker.*.config.mjs`, `jest.stryker.config.cjs`, installed packages,
`MUTATION_TESTING.md`) live on a local-only branch named `local/mutation-testing`, forked from
the feature branch being tested.

The feature branch and `main` are kept clean: no Stryker packages in any `package.json`,
no config files committed.

Rationale: mutation testing is compute-intensive and not suitable for CI. Committing Stryker
packages pollutes the dependency tree and lockfile for all contributors without providing
ongoing value in the merge pipeline.

---

## Stryker packages are scoped to the component package, never hoisted to workspace root

Install command:

```bash
pnpm add -D --filter boreal-web-components @stryker-mutator/core @stryker-mutator/jest-runner
```

No other package needs these dependencies. Installing at workspace root was tried and
identified as a mistake — it causes unnecessary hoisting and version conflicts with
unrelated packages.

---

## One Stryker config file per component

Naming convention: `stryker.<component>.config.mjs`

Examples:
- `stryker.grid.config.mjs`
- `stryker.button.config.mjs`

All component configs share a single `jest.stryker.config.cjs` but each carries its own
`mutate` glob and `testMatch` glob scoped to the component under test.

Rationale: running the full component package at once is impractical (too slow). Per-component
configs keep each run fast and make failure attribution unambiguous.

---

## Mutation score target: 100%

The required bar for this project is 100% killed mutants.

A score of 90–99% is acceptable only when surviving mutants are documented with an explanation
before a PR is merged. There is no blanket exemption.

Rationale: reaching 100% on `bds-grid` required adding boundary-condition tests that also
caught a real string-concatenation bug in offset arithmetic. The process proved that the
bar produces genuine quality improvements, not just coverage theatre.
