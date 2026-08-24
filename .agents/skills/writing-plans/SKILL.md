---
name: writing-plans
description: >
  Use BEFORE writing any code when planning a new Stencil component, feature, or multi-step implementation task for Boreal DS. Invoke when the user says "write a plan", "create a plan", "plan this component", "plan the implementation", "I want to build X", "let's plan X", or provides a spec, ticket, or Figma design and asks what to do next. Produces a task-by-task implementation plan saved to ai-work/plans/ covering files to create or modify, acceptance criteria, unit test behaviors, manual test steps, and commit messages. Plans must include Executor fields on every task so executing-plans can dispatch to the correct specialist subagent. Always use this skill before dispatching any implementation subagent or starting development work on a new component.
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `ai-work/plans/<ticket-id>-<feature-name>.md`. Pull the ticket ID from the active branch, then confirm the filename with the user before saving.

## Pre-Plan: Ticket Brief

When the user provides a Jira ticket ID (e.g. `EOA-12345`), write a ticket brief **before** producing the plan file. The brief captures the work scope at a level that survives handoffs — what is in, what is explicitly out, and what is still unknown.

**Output path:** `ai-work/tickets/<TICKET-ID>-{slug}.md`

**Structure:**

```markdown
# <TICKET-ID> — {slug}

**Ticket:** [link or ID]
**Goal:** One sentence describing what this work produces and why.

## Scope

**In:** bullet list of what will be built or changed
**Out:** bullet list of what is explicitly excluded from this ticket

## Acceptance Criteria

- [ ] Measurable, testable criteria the implementer can verify
- [ ] ...

## Dependencies

- Other tickets, packages, or external decisions this work depends on

## Open Questions

- Unresolved decisions or unknowns that may affect scope or approach
```

After writing the ticket brief, proceed to the plan. The plan file's preamble must include a reference to the ticket brief:

```markdown
**Ticket brief:** [`ai-work/tickets/<TICKET-ID>-{slug}.md`](../tickets/<TICKET-ID>-{slug}.md)
```

If no ticket ID is provided, skip the ticket brief step entirely and proceed directly to the plan.

---

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

## Figma Research Gate for Styling Tasks (Mandatory)

Any task whose acceptance criteria produce SCSS/CSS or otherwise change rendered appearance is a **styling task**, and must carry a Figma research gate *authored into the plan*, before implementation starts. This is a plan-authoring obligation, not implementer guidance: a styling task without a research gate section is an incomplete task.

The gate exists because reactive Figma research fails predictably. Styling gaps do not announce themselves — the implementer sees a plausible-looking rendered component, ships it, and the user finds the gap by eye. Each round-trip costs a full review cycle, and the gaps arrive one at a time rather than all at once, so the cost compounds.

### Authoring the gate

While planning a styling task, enumerate — do not defer to the implementer — the full research surface:

1. **Visual regions** the task renders (e.g. trigger field, popover chrome, header row, weekday header, day cell, footer). Each region is a separate Figma pull.
2. **Interaction states** the component supports: default, hover, focus, active, pressed, disabled.
3. **Modifier states** the component supports: selected, today, out-of-range, invalid, readonly, required.
4. **The cross product** of 2 × 3 that the design realistically supports — Selected+Disabled, Today+Hover, Selected+Hover, and so on. Combination states are where source-order and specificity bugs hide, and they are the states least likely to be pulled unless named explicitly.
5. **Structural dimensions**: fixed widths/heights, and how sibling regions align to each other. Two regions that must share a width will drift apart unless the shared dimension is stated.

Write that enumeration into the task as a **Figma research pass** block placed *above* the acceptance criteria, phrased as work to complete before any SCSS is written.

### Task shape for a styling task

```markdown
**Figma research pass (complete before writing any SCSS):**

Pull `get_design_context` / `get_metadata` for each row below. A row is done only when it was actually pulled — never when it was inferred from a sibling variant.

- [ ] Region: <region> — default state
- [ ] Region: <region> — hover / focus / active
- [ ] Modifier: <modifier> — default, and its hover / focus / active variants pulled *separately*
- [ ] Combination: <modifierA> + <modifierB>
- [ ] Dimensions: <region A> and <region B> width/height alignment, pulled from Figma's layout data

**Acceptance criteria:**

- Every row of the Figma research pass above is checked off, with the pulled value recorded, before the first SCSS line is written.
- Uses `$boreal-*` tokens exclusively; no hardcoded colours, spacing, or radii.
- Every interaction state × modifier state combination enumerated above has an explicit rule, or an explicit note that Figma shows no difference for it.
- Non-interactive states (e.g. disabled) suppress the native focus outline — verify `outline` handling is not scoped only to the interactive-state block.
- Verified against the **compiled** CSS output, not just the SCSS source: confirm each top-level selector matches DOM the component actually renders.
```

### Rules that make the gate actually bite

- **No variant generalization.** A pulled state for one variant says nothing about the same state on a sibling variant. If the plan needs Hover on both `Actual: True` and `Actual: False`, both are separate checklist rows.
- **No stale pixel values.** Any dimension, padding, or colour already written into the plan's prose from earlier research is *unconfirmed* until re-pulled at implementation time. Mark such values explicitly: `(unconfirmed — re-pull before use)`. Plans outlive the Figma state they were written against.
- **Host-level styles are not class selectors.** On a Stencil component, styling the host through a class the `<Host>` never carries compiles to dead CSS with zero build errors. Any styling task touching host-level properties must state the host-selector mechanism by name in its acceptance criteria.
- **Chain `@qa-subagent`.** Every styling task takes `**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)` — styling tasks are the canonical case for the chain described under Executor Mapping.

## Integration & Edge-Case Gate (Mandatory)

Any task that **modifies existing behavior** — not a brand-new file with no prior callers — is an **integration task**, and must carry an integration research pass *authored into the plan*, before the task is dispatched. This is a plan-authoring obligation, not implementer guidance: an integration task without this pass is an incomplete task.

The gate exists because integration gaps fail the same way styling gaps do: reactively. A task's acceptance criteria can look complete while silently missing a function with multiple callers, a public-API boundary case, or a default/empty state that was never made explicit — and the implementer, working from the plan's prose rather than the live source, has no way to know what wasn't written down. Each gap surfaces one at a time, after code exists, rather than all at once during planning.

**This gate runs in addition to, not instead of, the live grounding check `executing-plans` performs before dispatching each task** (see that skill's Step 2) — this gate catches what planning-time research finds; the execution-time check is a safety net for anything that changed or was missed between planning and dispatch (plans go stale as earlier tasks land and shift the actual code).

### When this gate applies

A task triggers this gate when it does **any** of the following:

- Modifies a function, method, or file that already has more than one call site
- Changes what a public `@Prop`, `@Event`, or exported function accepts or returns
- Introduces a new prop/state that interacts with an existing default, empty, or reset state
- Extends a draft-state / controlled-value pattern that other code paths (Cancel, Clean, form reset, re-open) already depend on

It does **not** apply to: brand-new files with no existing callers, pure type-only additions with no existing consumers yet, scaffold-only tasks (stub `render()`, prop declarations with no wired behavior), or docs/story-only tasks.

### Authoring the gate

While planning an integration task, read the **actual current source** of every file it will touch — not just describe the file path — and enumerate:

1. **Call sites**: every existing caller of a function/method this task changes, and whether each one needs to change too or is correctly covered by changing the shared function once.
2. **Public-API boundary cases**: what happens when a consumer passes a value that doesn't match the new expected shape (stale/mismatched prop combinations, malformed input) — crossing the boundary means "trust internal guarantees" no longer applies.
3. **Default/empty-state decisions**: any state that's newly ambiguous (a fresh value, a cleared value, a toggled-off feature) gets an explicit, stated default — not left for the implementer to invent.
4. **Reactive-prop assumptions**: whether a new prop is expected to be reactive after mount (`@Watch`-driven) or is a set-once config value — state this explicitly if it isn't obvious.

Write that enumeration into the task as an **Integration research pass** block placed *above* the acceptance criteria.

### Task shape

```markdown
**Integration research pass (complete before writing acceptance criteria):**

Read the actual current source of each file below — not just its file path — before finalizing this task's scope.

- [ ] Call sites: `<function/method>` is called from `<site A>`, `<site B>`, ... — confirm the shared fix covers all of them.
- [ ] Boundary case: `<prop/value>` — what happens when a consumer passes `<malformed/mismatched input>`?
- [ ] Default/empty state: `<new ambiguous state>` defaults to `<explicit value>`.
- [ ] Reactivity: `<new prop>` is/is not expected to be reactive after mount.

**Acceptance criteria:**

- Every row of the Integration research pass above is reflected in a concrete acceptance-criteria bullet or an explicit "no gap found" note.
- ...
```

### Rules that make the gate actually bite

- **No deferring to the implementer.** "Handle edge cases appropriately" is not a substitute for naming the specific case and its resolution.
- **Findings propagate.** If a later task in the plan shares the same root cause (e.g. the same default-state decision applies to a dual/range variant of the same feature), cross-reference it there too rather than re-deriving it.
- **Chain `@qa-subagent`** only if the task also has real visual/behavioral output — this gate is about correctness coverage, not a trigger for manual QA on its own.

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
---
ticket: EOA-XXXXX # Jira ticket ID; use — for non-ticket work (AI-XXX, etc.)
component: bds-component # bds-* tag name; omit this line for non-component plans
status: pending # always pending for new plans; sync-plans updates this
created: YYYY-MM-DD # date this plan was written
---

# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Ticket brief:** [`ai-work/tickets/<TICKET-ID>-{slug}.md`](../tickets/<TICKET-ID>-{slug}.md) _(omit if no ticket ID was provided)_

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

## Executor Mapping

Every task in a plan must declare an `**Executor:**` field. Use this table to assign the correct executor:

| Task type                                                        | Executor                  |
| ---------------------------------------------------------------- | ------------------------- |
| Type interfaces, scaffold, lifecycle, render(), JSDoc, SCSS      | `@frontend-subagent`      |
| Unit tests (all spec files)                                      | `@testing-subagent`       |
| Storybook story, MDX documentation                               | `@documentation-subagent` |
| Framework output targets, build scripts, CI fixes, release steps | `@release-subagent`       |
| Manual QA, React/Vue wrapper parity, live-browser verification (Safari included) | `@qa-subagent`            |
| Utility/config tasks with no component code                      | main thread (no executor) |

### Chaining Executors for Visual/Behavioral Tasks

A task's `**Executor:**` line may chain a second subagent when the task produces output a human needs to actually look at or interact with:

```
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
```

Apply the chain only to tasks whose manual test is a real interaction or visual scenario — a rendered component, a styling change, a wired-up event flow. Do not chain it onto tasks whose "manual test" is just a compiler check or a Jest run (type interfaces, config/dependency tasks, barrel files, non-visual utility logic) — those are already fully verified by their primary executor, and dispatching `@qa-subagent` there means reviewing nothing. As a rule of thumb: if the task's Manual Test section under Task Structure below has playground scenarios and a Given/When/Then checklist, chain `@qa-subagent`; if it says "validate with compiler/tests only," don't.

## Task Structure

Implementation and its unit tests are always **separate tasks** — matching `Task Granularity`'s numbered steps (e.g. leaf step 6 SCSS / step 7 Unit tests) and the `Executor Mapping` table, which routes them to different subagents (`@frontend-subagent` vs `@testing-subagent`). Never fold a `**Unit tests to cover**` section into an implementation task's block.

**Implementation task:**

```markdown
### Task N: [Deliverable Layer Name]

**Executor:** @frontend-subagent
**Files:**

- `exact/path/to/file.ts` (create)
- `exact/path/to/existing.ts` (modify)

_(If this task produces SCSS/CSS or otherwise changes rendered appearance, insert the Figma research pass block here — see Figma Research Gate for Styling Tasks.)_

**Acceptance criteria:**

- Bullet describing a prop, behavior, or constraint — not code
- Use tables for props (name / type / default / reflect / description)
- State which tokens, mixins, or patterns to use by name
- Call out edge cases and guards explicitly ("when disabled, X must not happen")
- Reference existing sibling components as the pattern to follow where applicable
- Existing shared utilities for this behavior were checked; implementation reuses them when available, otherwise includes a documented gap and extension plan
- If the task produces SCSS/CSS or changes rendered appearance, it carries a completed Figma research pass block per the Figma Research Gate for Styling Tasks section above

**Manual test _(required — not waiveable)_:**

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
git commit -m "feat(scope): TICKET-ID description"
```

**Unit test task** — one consolidated task at the end of the current component (or version/phase, in multi-version plans) block, covering every behavior area that block's implementation tasks introduced, in separate spec files — the same pattern already used for Storybook/MDX documentation and for the mutation-testing consolidation described under Testing Phases below. Do not add a unit-test task after each individual implementation task.

```markdown
### Task N: [Component] unit tests

**Executor:** @testing-subagent
**Files:**

- `__test__/component.basics.spec.ts` (create)
- `__test__/component.events.spec.ts` (create)
- `__test__/component.variants.spec.ts` (create)
- _(one file per behavior area introduced by this block's implementation tasks — a11y and keyboard get their own spec files where applicable)_

**Unit tests to cover** _(grouped by spec file)_:

- `basics` — Behavior 1, Behavior 2 — what each test must assert, not how to write it
- `events` — Behavior 3
- `variants` — Behavior 4
- Tests confirm behavior through the shared utility integration path (or validate the documented fallback path when no reusable utility exists)
- Coverage-phase only (≥90%); mutation testing deferred to the consolidated mutation task (per Testing Phases below)
- ...

**Manual test:** N/A — non-visual task, validated via `pnpm test` and the coverage report only.
```

**Commit:**

```bash
git commit -m "test(scope): TICKET-ID description"
```

## Framework Wrapper Parity (React/Vue)

Any component shipping through the React and Vue output-target wrappers needs its behavior verified through both wrappers, not just the raw web component — but *when* that verification happens depends on the component's maturity, and the two cases call for opposite defaults.

**Brand-new component, or a version introducing its first meaningful interactive behavior:** default to **consolidated** parity-check tasks, not one per implementation task. Early tasks in a new component (type interfaces, scaffolding, a stub `render()`) produce nothing a framework wrapper could diverge on — there's no behavior yet to compare. Checking parity on those tasks anyway just repeats the wrapper-verification pipeline for no signal. Instead, add one parity-check task at each meaningful checkpoint — typically once per version, right after that version's documentation task — that re-runs the version's key manual-test scenarios through both wrappers in one pass.

**Established component receiving incremental enhancements**, where the component already ships production behavior through both wrappers and each task in the plan adds one complete, independently-usable feature on top of that stable base: parity-per-task is the better default instead. Each such task genuinely *could* introduce a framework-specific regression (event handling, prop/attribute forwarding, two-way-binding behavior) the moment it lands, and catching it immediately — scoped to the one feature that just shipped — is cheaper than debugging it later in one large combined pass.

The dividing line is whether the task under consideration has real behavior to diverge on yet, not the size of the plan. A large plan for a still-new component stays consolidated until the component is actually composable and interactive; a small plan adding one feature to a mature, already-shipping component can reasonably check parity every task.

**Task shape for a parity-check task:**

```markdown
**Executor:** @qa-subagent
**Files:** none (verification-only task; no new source files)

**Acceptance criteria:**
- States which prior task(s)' scenarios are being re-verified through both wrappers
- Uses a pack-based verification pipeline (not a live dev server against wrapper packages) — a live dev server can serve a stale wrapper bundle after a rebuild, producing false framework-specific bug reports
- Any regression found is logged as a new task, not fixed inline in the verification task itself

**Manual test (required):**
Repeat the referenced scenario(s) through both the React and Vue wrapper playgrounds using the pack-based pipeline, then validate:
- [ ] Given <scenario>, when repeated through the React wrapper, then behavior matches the raw web component exactly. Pass: no divergence.
- [ ] Given <scenario>, when repeated through the Vue wrapper (including two-way binding where applicable), then behavior matches exactly. Pass: no divergence.

**Commit:** N/A — verification-only task; no code changes expected unless a regression is found.
```

## Testing Phases: Coverage vs. Mutation Testing

Two distinct test-quality gates apply to every component, and they belong at different points in a plan:

- **Coverage-phase** (standard Jest test execution, ≥90% coverage) is cheap and fast. Write and gate it within the consolidated unit-test task described in Task Structure above — one such task per component (or version/phase) block, not per implementation task. That task is the single point where coverage is verified for everything its block introduced.
- **Mutation-phase** (Stryker, ≥90% mutation score) is comparatively expensive in both time and hardware. Never run it per block. Consolidate it into a single dedicated task, placed at (or near) the end of the whole plan, that runs mutation testing once across every testable unit the plan created or modified — each unit keeping its own config file, per the one-config-per-component convention. Every unit-test task earlier in the plan should explicitly note "coverage-phase only; mutation testing deferred to the consolidated task" so it's clear the gate isn't being skipped, just deferred.

If a mutant survivor reveals a genuine gap in an earlier task's test coverage, close it by extending that task's existing spec file — the consolidated task's job is closing test gaps the coverage phase missed, not introducing new behavior.

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
- Every styling task carries a Figma research pass enumerating region × interaction state × modifier state, authored at plan time — never left for the implementer to discover reactively
- Every integration task (one that modifies existing behavior with real callers) carries an integration research pass covering call sites, API-boundary cases, and default/empty-state decisions, authored at plan time — `executing-plans`' live grounding check is a safety net for drift, not a substitute for this
- Pixel values written into plan prose are unconfirmed by default; mark them so and require a re-pull
- DRY, YAGNI, TDD, frequent commits per task

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `ai-work/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**

- Stay in this session
- Read the `**Executor:**` field on each task and dispatch: `@<subagent>: <task title, files, acceptance criteria, unit tests, manual test checklist, commit message>`
- Review subagent output against acceptance criteria before proceeding to the next task

**If Parallel Session chosen:**

- Guide them to open new session in worktree
- **REQUIRED SUB-SKILL:** New session uses `executing-plans`
