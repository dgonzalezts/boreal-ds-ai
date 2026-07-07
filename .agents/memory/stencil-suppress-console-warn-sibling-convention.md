---
name: stencil-suppress-console-warn-sibling-convention
description: suppressConsoleWarn() must be called in every spec file for a component, not just some — check sibling spec files before adding a new one
metadata:
  type: project
---

`suppressConsoleWarn()` (`src/utils/testing/mocks/console.ts`) is called by ~30 existing spec files to silence `console.warn` noise from Stencil's "Prop is immutable but was modified from within the component" dev-warning and this project's `Logger.warn` fallback paths. Unlike `suppressConsoleError()`, it was undocumented in both `ai-docs/guidelines/stencil-unit-testing-patterns.md` and `.agents/skills/testing-knowledge/SKILL.md` until this was found.

**Why:** `bds-pagination.basics.spec.ts` was missing this call while its siblings (`behavior.spec.ts`, `events.spec.ts`, `keyboard.spec.ts`) already had it — the component itself triggers the warning, so any spec file exercising it leaks console noise if it omits the call. No lint/CI check catches this.

**How to apply:** Before writing a new spec file in an existing component's `__test__/` directory, grep the directory for `suppressConsoleWarn`/`suppressConsoleError`. If sibling files call it, the new file must too. See [[testing-knowledge]] skill for the boilerplate pattern.
