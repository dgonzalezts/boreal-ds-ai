---
name: writing-plans
description: >
  Use BEFORE writing any code when planning a new Stencil component, feature, or multi-step
  implementation task for Boreal DS. Invoke when the user says "write a plan", "create a plan",
  "plan this component", "plan the implementation", "I want to build X", "let's plan X", or
  provides a spec, ticket, or Figma design and asks what to do next. Produces a task-by-task
  implementation plan saved to ai-work/plans/ covering files to create or modify, acceptance criteria,
  unit test behaviors, manual test steps, and commit messages. Always use this skill before
  dispatching any implementation subagent or starting development work on a new component.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `ai-work/plans/<ticket-id>-<feature-name>.md`. Pull the ticket ID from the active branch, then confirm the filename with the user before saving.

## Task Granularity

**Each task maps to one logical development step** — the smallest unit a developer would naturally commit and manually test in sequence, as if coding without AI assistance.

Tasks follow the natural development order within each component. The reference below covers the **most complex case** — a form-associated leaf component paired with an orchestrator group. Simpler components are subsets: omit steps that do not apply (e.g. a display-only component skips form lifecycle and keyboard navigation; a standalone component with no group skips all group steps).

**Leaf component (e.g. `bds-radio`, `bds-checkbox-button`)**

1. Type interfaces — `IComponent.ts`, change detail types; no implementation yet
2. Scaffold — `@Prop` and `@Event` declarations only; `render()` returns a stub `<Host />`
3. Lifecycle + interaction — `componentDidLoad`, selection/toggle logic, click and keyboard handlers
4. `render()` — full DOM structure replacing the stub; class map; slots; hidden `<input>`
5. JSDoc audit — verify all `@Prop`, `@Event`, `@Method`, and the class-level block are complete
6. SCSS — all visual states using `$boreal-*` tokens; no hardcoded values
7. Unit tests — separate spec files per behavior area (basics, a11y, events, variants, keyboard)

**Group / orchestrator component (e.g. `bds-radio-group`, `bds-checkbox-group`) — append after the leaf is complete**

8. Scaffold — props, events, `@AttachInternals`, element getter; stub `render()`
9. Child listeners — `@Listen('bdsMount')` stamps name/state; `@Listen('bdsChange')` enforces selection contract
10. Keyboard navigation — roving tabindex, arrow key handling, wrap-around, skip-disabled _(omit if not applicable)_
11. `@Watch` + form lifecycle — `formResetCallback`, `formAssociatedCallback`, `formDisabledCallback`, validity
12. `componentDidLoad` + `render()` — slot wiring, layout count, full render tree
13. JSDoc audit
14. SCSS
15. Unit tests
16. Framework output targets — Vue `componentModels`, etc. _(omit if not applicable)_
17. Storybook story
18. MDX documentation

**Key invariant:** every task must be independently committable and have a manual test that can pass before the next task begins. Never merge two steps if the result of the first cannot be manually verified on its own.

## Existing Utility and Type Reuse Gate (Mandatory)

Before planning any new behavior or type, verify whether the codebase already provides a reusable utility, helper, mixin, type definition, hook, or service for that concern.

- Always perform a discovery step for each feature area (for example: navigation, focus, validation, formatting, selection state, event handling, or type definitions).
- For types, always check the shared type definitions directory (e.g. `src/types/`) before introducing new enums, unions, or interfaces.
- Prefer existing shared utilities and types over component-local implementations.
- Do not plan duplicate logic or types if an equivalent shared abstraction already exists.
- If an existing utility or type is found, the task acceptance criteria must explicitly require integration with that resource.
- If no utility or type is found, document the search result and justify the new implementation.
- If a utility or type exists but is insufficient, require:
  - a gap description
  - a plan to extend the shared resource first
  - a migration step so component-level temporary logic is removed

## Utility Discovery Checklist

Use this checklist during planning and include a short "utility discovery" note in each relevant task.

- Feature area identified: state the behavior being planned (for example keyboard navigation, focus management, validation, or selection).
- Search performed: list where the search happened (folders/modules) and the query terms used.
- Candidate utilities found: name the existing reusable abstractions that appear relevant.
- Fit assessment: decide whether each candidate fully fits, partially fits, or does not fit, with one-line rationale.
- Reuse decision: choose one candidate to integrate, or explicitly state that no suitable utility exists.
- Gap handling: when partially fitting, define what must be extended in the shared utility before component wiring.
- Anti-duplication check: confirm no parallel component-local implementation is planned for the same behavior.
- Test impact: specify which unit tests verify behavior through the shared utility integration path.
- Migration note (if temporary fallback is used): capture when and how temporary local logic will be removed.

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---

## Files to create / modify

| File                        | Notes                        |
| --------------------------- | ---------------------------- |
| `exact/path/to/file.ts`     | New — [brief description]    |
| `exact/path/to/existing.ts` | Modify — [brief description] |

---
```

The file table is a living checklist. It gives the implementer full orientation before reading any task.

## Task Structure

```markdown
### Task N: [Deliverable Layer Name]

**Files:**

- `exact/path/to/file.ts` (create)
- `exact/path/to/existing.ts` (modify)

**Acceptance criteria:**

- Bullet describing a prop, behavior, or constraint — not code
- Use tables for props (name / type / default / reflect / description)
- State which tokens, mixins, or patterns to use by name
- Call out edge cases and guards explicitly ("when disabled, X must not happen")
- Reference existing sibling components as the pattern to follow where applicable
- Existing shared utilities for this behavior were checked; implementation reuses them when available, otherwise includes a documented gap and extension plan

**Unit tests to cover** _(spec file: `__test__/component.behavior.spec.ts`)_:

- Behavior 1 — what the test must assert, not how to write it
- Behavior 2
- Tests confirm behavior through the shared utility integration path (or validate the documented fallback path when no reusable utility exists)
- ...

**Manual test _(waiveable)_:**

For logic or styling tasks, first list the playground scenarios to implement in `packages/boreal-web-components/src/index.html`. Each entry is a short description — no code, no markup:

- Scenario 1: [component/state to render and what to set up]
- Scenario 2: [interaction to test]
- ...

Then provide the validation checklist. Run: `pnpm dev:components` and validate each scenario:

- [ ] Given <initial state>, when <user action>, then <expected result>. Pass: <observable outcome>.

For non-visual tasks (types/utilities/docs-only), skip playground scenarios and validate with compiler/tests only.

Use `pnpm dev:docs` only for Storybook/MDX tasks (typically the final documentation tasks), not for component implementation tasks before docs exist.
```

**Commit:**

```bash
git commit -m "type(scope): TICKET-ID description"
```

## Remember

- Exact file paths always
- Acceptance criteria and behavior descriptions — not code blocks
- Token names, mixin names, and pattern references by name (not by example)
- Every implementation task has a manual test section
- For pre-documentation tasks, manual tests must use `pnpm dev:components` + `packages/boreal-web-components/src/index.html`; reserve `pnpm dev:docs` for Storybook/MDX validation tasks.
- Keep manual tests scoped to the current task only
- Prefer the smallest set of scenarios that proves behavior
- Do not include implementation details in the plan
- Unit test tasks describe behaviors to cover, not how to write the tests
- Never duplicate behavior already covered by shared utilities; utility discovery and reuse is required for every feature area
- DRY, YAGNI, TDD, frequent commits per task

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `ai-work/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**

- **REQUIRED SUB-SKILL:** Use subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

**If Parallel Session chosen:**

- Guide them to open new session in worktree
- **REQUIRED SUB-SKILL:** New session uses executing-plans

```

```
