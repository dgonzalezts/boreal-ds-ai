# EOA-17662 (Task 53d) — `bds-date-picker` consolidated mutation pass (deferred)

**Parent:** [EOA-17662](https://telesign.atlassian.net/browse/EOA-17662) (Tasks 53/53a consolidated mutation testing)
**Status:** Open / deferred (2026-09-25)

## Goal

Run the consolidated Stryker pass for `bds-date-picker` (Phase 5-9 scope) and triage its survivors, closing the last gap in the EOA-17662 mutation gate.

## Why it was deferred

The full run is **897 mutants** and projects **~7 hours** on the 11-core/18GB dev machine, and it exhausted memory (102 MB free, 8 GB compressed). Two retunes did not fix the per-mutant cost:

- `mutator.excludedMutations: [StringLiteral, ObjectLiteral, ArrowFunction, BlockStatement]` cut mutants 1300 → 897.
- `jest.enableFindRelatedTests: false` let `coverageAnalysis: 'perTest'` select per-mutant covering tests, but did not reduce the rate meaningfully — each mutant still runs a large share of the component's 523 tests (all 16 spec files import `bds-date-picker.tsx`).

## Config (local-only — recreate in an isolated worktree; never commit)

`packages/boreal-web-components/stryker.bds-date-picker.config.mjs`:

```js
/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  packageManager: 'pnpm',
  reporters: ['html', 'clear-text', 'progress'],
  htmlReporter: { fileName: 'reports/mutation/mutation-bds-date-picker.html' },
  testRunner: 'jest',
  plugins: ['@stryker-mutator/jest-runner'],
  jest: {
    projectType: 'custom',
    configFile: 'jest.stryker.bds-date-picker.cjs',
    enableFindRelatedTests: false,
  },
  mutate: [
    'src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx',
    'src/components/forms/bds-date-picker/bds-date-picker/helpers/renderBanner.tsx',
    'src/components/forms/bds-date-picker/bds-date-picker/helpers/renderCalendarPanel.tsx',
    'src/components/forms/bds-date-picker/bds-date-picker/helpers/renderFooter.tsx',
    'src/components/forms/bds-date-picker/bds-date-picker/helpers/renderPresets.tsx',
    'src/components/forms/bds-date-picker/bds-date-picker/helpers/renderRangeHeader.tsx',
    'src/components/forms/bds-date-picker/bds-date-picker/helpers/renderTimeSelector.tsx',
    'src/components/forms/bds-date-picker/bds-date-picker/utils/constants.ts',
    'src/components/forms/bds-date-picker/bds-date-picker/utils/draft-state.ts',
    'src/components/forms/bds-date-picker/bds-date-picker/utils/presets.ts',
    'src/components/forms/bds-date-picker/bds-date-picker/utils/value-mapping.ts',
  ],
  coverageAnalysis: 'perTest',
  mutator: {
    excludedMutations: ['StringLiteral', 'ObjectLiteral', 'ArrowFunction', 'BlockStatement'],
  },
  timeoutMS: 10000,
  concurrency: 2,
  incremental: true,
  incrementalFile: 'reports/stryker-incremental.bds-date-picker.json',
};
```

`packages/boreal-web-components/jest.stryker.bds-date-picker.cjs`:

```js
const { getJestPreset } = require('@stencil/core/testing');
const { testRegex: _dropped, ...preset } = getJestPreset();

module.exports = {
  ...preset,
  moduleNameMapper: { ...preset.moduleNameMapper, '^@/(.*)$': '<rootDir>/src/$1', '@utils/test': '<rootDir>/src/utils/__test__' },
  testMatch: [
    '<rootDir>/src/components/forms/bds-date-picker/bds-date-picker/__test__/**/*.spec.ts',
    '<rootDir>/src/components/forms/bds-date-picker/bds-date-picker/utils/__test__/**/*.spec.ts',
  ],
  maxWorkers: 1,
};
```

## Instructions

- Run in an isolated worktree branched off the feature branch, `pnpm install`, add `@stryker-mutator/core` + `@stryker-mutator/jest-runner` scoped to `@telesign/boreal-web-components`, add `*.config.mjs`/`*.config.cjs`/`.stryker-tmp/` to ESLint ignores.
- Run when the machine is otherwise free; keep `concurrency: 2` / `maxWorkers: 1`.
- Triage survivors with the same `git blame` phase-bucketing method as Tasks 53/53a.
- Expect a sizable Phase 5-9 test gap; if so, it should become its own remediation ticket rather than being absorbed here.

## Acceptance criteria

- `bds-date-picker` ≥90% per target area, or survivors documented as equivalents with reasoning.
- Real gaps closed in the phase-owning spec files; full Jest suite green.
- Result written to `ai-work/qa/mutation-reports/mutation-bds-date-picker.md`.
