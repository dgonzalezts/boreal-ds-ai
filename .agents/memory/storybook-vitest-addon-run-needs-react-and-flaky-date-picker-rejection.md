# Storybook vitest addon run: needs `react`/`react-dom` in the docs app, and about half of the runs exit 1

Verified on Storybook 10.6.7 and Vitest 5.1.0 (EOA-20193, 2026-11-13).

## The Problem

`pnpm exec vitest run --project storybook` in `apps/boreal-docs` takes about 11 s (48 files, 606 tests) but:

- needs `react` and `react-dom` declared in the docs app: pnpm's strict layout leaves `react` unresolvable under Vitest, while the dev server and the build resolve it through Storybook's own tooling;
- about half of the runs still exit 1 because of an unhandled rejection `[AnchoredMixin.show]: triggerSlot is required`, coming from `src/stories/forms/bds-date-picker/bds-date-picker.stories.ts`.

## The Fix

`react` and `react-dom` are declared in the docs app (EOA-20193). The rejection is NOT fixed. Unverified hypotheses: `openPopover` is called before the trigger slot renders, or a teardown race. For that reason the run is not part of any gate.

## How to verify

Run the command several times from `apps/boreal-docs`; compare the exit code against the test summary (all tests green with exit 1 means the rejection, not a failing story).

Related: [[storybook-vite-quirks]], [[bds-popover-escape-ordering-and-focus-neutral-dismissals]].
