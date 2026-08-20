# Boreal DS — Code Review Report

**Generated:** 2026-08-20T15:53:06  
**Base ref:** `release/current`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🔴 **[class-jsdoc-stale-slot]** Class JSDoc documents @slot 'default' but no matching <slot> is rendered in this file. The CEM plugin cannot detect this — the stale tag ships as a phantom slot in custom-elements.json. Remove the tag or restore the slot. `packages/boreal-web-components/src/components/data-visualization/bds-collapse/bds-collapse-content/bds-collapse-content.tsx:7`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/data-visualization/bds-collapse/bds-collapse-group/bds-collapse-group.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/data-visualization/bds-collapse/bds-collapse-group/bds-collapse-group.tsx:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/data-visualization/bds-collapse/bds-collapse-header/bds-collapse-header.tsx:2`
- 🔴 **[class-jsdoc-stale-slot]** Class JSDoc documents @slot 'default' but no matching <slot> is rendered in this file. The CEM plugin cannot detect this — the stale tag ships as a phantom slot in custom-elements.json. Remove the tag or restore the slot. `packages/boreal-web-components/src/components/data-visualization/bds-collapse/bds-collapse/bds-collapse.tsx:10`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/data-visualization/bds-collapse/bds-collapse/bds-collapse.tsx:4`
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.
  - ⚠️ **False positive (validated by documentation-subagent):** ADR `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md` confirms this repo deliberately chose `release-it` over changesets tooling — there's no changesets mechanism in this repo to have an entry in.

### `class-jsdoc-stale-slot` — confirmed real (not a false positive)

Both flags are correct catches, though the auto-generated message is slightly imprecise ("no matching `<slot>` is rendered" — the slot *is* rendered, just unnamed). The actual bug: `@slot default - ...` should be `@slot - ...` (no name) per this codebase's convention for an unnamed/default slot — compare `bds-setting-steps.tsx:8`'s correct `@slot - Accepts one or more...`. As written, `custom-elements.json` will document a slot literally named `"default"`, which does not exist — `<slot name="default">` was never rendered; only an anonymous `<slot></slot>` / `<slot />` was. Affects `bds-collapse.tsx:10` and `bds-collapse-content.tsx:7`.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ⚠️ Storybook/MDX/README updated when behavior or APIs change — **false positive (validated by documentation-subagent)**: there is no separate `bds-collapse.stories.ts`, but `apps/boreal-docs/src/stories/data-visualization/bds-collapse-group/bds-collapse-group.stories.ts` + `.mdx` document all four subcomponents (`bds-collapse-group`, `bds-collapse`, `bds-collapse-header`, `bds-collapse-content`) together in one combined `argTypes` object grouped by `table.category`. Cross-checked accurate against current APIs (props, methods, slots, and the public `bdsOpen`/`bdsClose` events). The automated checker likely searched for a `bds-collapse`-named file and missed the combined `bds-collapse-group` one.
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ✅ Every @Prop() has `readonly` and an adjacent JSDoc block
- ✅ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ✅ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ✅ Only ElementInternals.setValidity() manages validity
- ✅ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
- ✅ JSDoc changes preserve custom-elements.json generation accuracy
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ✅ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Manual Findings — `bds-collapse.tsx` (subagent-validated)

1. 🔴 **Wrong slot name in class JSDoc — CONFIRMED** (`bds-collapse.tsx:10`, `bds-collapse-content.tsx:7`) — `@slot default` → should be `@slot`. Confirmed by both frontend-subagent and documentation-subagent. Real impact: Stencil's CEM/docs generator reads `@slot <name> - <description>` literally and will emit a slot table row named `"default"` in any CEM-derived output (e.g. auto-generated READMEs), even though no such named slot exists — only an unnamed one. Does not corrupt the hand-authored Storybook/MDX docs (see item 6), but is a real JSDoc/CEM bug.

2. 🟡 **No reactivity to dynamic slot content changes — CONFIRMED, real correctness gap** (`bds-collapse.tsx:96-99`, `104-146`) — `initSubcomponents()`/`validateStructure()` run once in `componentDidLoad()`; no `onSlotchange`/`MutationObserver`. Post-load slot swaps leave `this.header`/`this.content` stale and `syncChildren()` silently stops applying state to new children. **Testing-subagent confirmed this is currently untested** — no spec mutates `el.children` after mount; all specs mount final structure once. **Frontend-subagent's suggested fix**: `<slot onSlotchange={() => { this.initSubcomponents(); this.syncChildren(); }}></slot>` in `render()` — Stencil's non-shadow slot polyfill still dispatches `slotchange` on direct-child mutation. Same systemic pattern found in `bds-setting-steps.tsx` — worth a shared memory entry, not a one-off fix.

3. 🟡 **Standalone (no `bds-collapse-group`) usage silently drops events — PARTIALLY CONFIRMED** (`bds-collapse.tsx:79`, `87`, `100-103`) — Frontend-subagent confirms the missing-ancestor-warning DX gap is real and fits `validateStructure()`'s existing warning pattern naturally. However, the "should be `@internal`" framing is weaker than originally stated: a repo-wide grep found **zero existing uses of `@internal` JSDoc anywhere** in `boreal-web-components/src/components` — there's no established convention to point to, so this is a suggestion to establish one, not a deviation from precedent. **Testing-subagent confirms the standalone-no-emit behavior itself is already tested** (`bds-collapse.events.spec.tsx:64`, open path only; close path shares the identical guard so is a low-value gap, not a real one).

4. 🟢 **Opacity has no CSS transition, only height does — CONFIRMED** (`bds-collapse-content.scss:8-13`) — `.bds-collapse-content__body` transitions `height` but not `opacity`, so the fade snaps instantly while height eases over 200ms. Frontend-subagent's suggested fix: add `opacity 200ms ease-out` to the same `transition` declaration.

5. 🟢 **Test coverage — mostly solid, one real gap (testing-subagent).** `validateStructure()`'s 5 warning paths (missing/duplicate header, missing/duplicate content, unsupported children) are fully covered in `bds-collapse.slot.spec.tsx` via `jest.spyOn(console, 'warn')`, including a negative case and an aggregate case. Standalone no-emit is covered for the open path. **Real gap**: no spec constructs the dynamic-swap scenario in finding 2 — recommend a test that mounts, replaces `bds-collapse-header`/`content` post-load, calls `expand()`, and asserts on whether the new elements get synced (documenting current behavior either way).

6. 🟢 **Docs coverage — accurate, false positive on the automated flag (documentation-subagent).** No dedicated `bds-collapse.stories.ts` exists, but `bds-collapse-group.stories.ts`/`.mdx` document all four subcomponents together via a combined `argTypes` object — cross-checked accurate against current props/methods/slots/events. See annotation on the automated `Storybook/MDX/README` checklist item above.

## Memory-Guided Review

- **`feedback_custom_events_naming.md`** — `bdsCollapseOpen`/`bdsCollapseClose`/`bdsCollapseHeaderClick` embed the component noun in the event name (`bds{Component}{Action}` shape), which the memory topic flags as an anti-pattern (`bdsClose` not `bdsBannerClose`). However, `bds-collapse-group.tsx`'s own public-facing events (`bdsOpen`, `bdsClose`) correctly follow the `bds{Action}` convention — the flagged names are internal group-communication events only (see Manual Finding 3), not the public API surface, which softens this from a real violation to a naming choice on an internal channel. Worth a second look if `@internal` tagging is ever formalized project-wide.
- **`dom-setattribute-aria-kebab-case.md`** — not applicable; no `setAttribute` calls with ARIA attributes in this file.
- **`component-accessor-naming-conventions.md`** — `initSubcomponents`, `initCollapseGroup`, `validateStructure`, `syncChildren` are private methods, not getters; no issue.
- **`feedback_boolean_prop_naming.md`** — `expanded` correctly avoids `is`/`has`/`show` prefixes; no issue.
- **`stencil-child-component-props-in-tests.md`** — relevant to Manual Finding 5's recommended new test: any spec asserting on `bds-collapse-header`/`bds-collapse-content` DOM state after a dynamic swap must register both child components in `newSpecPage`'s `components` array, or `getAttribute`/property reads will silently return `null` per this memory topic's documented pitfall.
- No memory topic directly covers the `componentDidLoad()`-only child-caching pattern in Manual Finding 2 — this is the second time it's surfaced (also found in `bds-setting-steps.tsx` in the prior review session) and is now a recurring, verified pattern across two independent components. Recommend promoting it to a new memory entry via `knowledge-keeper` rather than re-discovering it a third time.

Memory topic files consulted: `feedback_custom_events_naming.md`, `dom-setattribute-aria-kebab-case.md`, `component-accessor-naming-conventions.md`, `feedback_boolean_prop_naming.md`, `.agents/memory/stencil-child-component-props-in-tests.md`.

---

**Result: 26 passed · 1 failed** (2 of the automated flags — Storybook/MDX and missing-changeset — are false positives for this repo; the `class-jsdoc-stale-slot` flag is confirmed real; 5 additional issues found via manual review, all validated by frontend/testing/documentation subagents: dynamic-slot-change reactivity gap, standalone-event DX gap, CSS transition mismatch, a real test-coverage gap, and a recurring `componentDidLoad()`-only-caching pattern worth a shared memory entry)

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_