# Boreal DS — Code Review Report

**Generated:** 2026-08-20T14:36:07  
**Base ref:** `release/current`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/navigation/bds-setting-steps/bds-setting-step-item-header/bds-setting-step-item-header.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/navigation/bds-setting-steps/bds-setting-step-item-header/bds-setting-step-item-header.tsx:4`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/navigation/bds-step/bds-step-item/bds-step-item.tsx:41`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/navigation/bds-step/bds-step-item/bds-step-item.tsx:59`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/navigation/bds-step/bds-step-item/bds-step-item.tsx:70`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/navigation/bds-step/bds-stepper/bds-stepper.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/navigation/bds-step/bds-stepper/bds-stepper.tsx:5`
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.
  - ⚠️ **False positive (validated by documentation-subagent):** this repo removed changesets tooling entirely (commit `16c93201`, "chore(release): EOA-9606 remove changesets in favor of release-it") in favor of `release-it` + conventional commits (`pnpm commit`). This checklist item is stale for the current release workflow and does not indicate a real gap in this PR.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ⚠️ Storybook/MDX/README updated when behavior or APIs change — **false positive (validated by documentation-subagent)**: `apps/boreal-docs/src/stories/navigation/bds-setting-steps/bds-setting-steps.stories.ts` and its companion `.mdx` already exist and are comprehensive (8 stories including `WithoutStepper` and `MultipleSteps`, which specifically demonstrate `stepperVisible` and position-assignment behavior; full MDX sections for usage, slots, accessibility, and properties). The class/prop JSDoc on `bds-setting-steps.tsx` was also confirmed accurate against actual `componentDidLoad()` behavior.
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
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

## Manual Findings — `bds-setting-steps.tsx` (subagent-validated)

The static checker does not detect cross-file architectural coupling or missing-reactivity bugs. A manual pass on the new file `packages/boreal-web-components/src/components/navigation/bds-setting-steps/bds-setting-steps/bds-setting-steps.tsx` was independently validated by the `frontend-subagent` and `testing-subagent`.

1. 🔴 **Cross-boundary imperative mutation** (`bds-setting-steps.tsx:20-29`) — `componentDidLoad()` reaches through two component boundaries: `querySelectorAll('bds-setting-step-item')` into slotted children, then `step.querySelector('bds-step-item')` into *their* internal light DOM, then a raw `setAttribute('position', ...)`. The sibling `bds-stepper.tsx:496` sets the same `position` prop declaratively via JSX (`position={...}`) because it renders `bds-step-item` directly.
   - **Fix available and precedented**: `bds-setting-step-item.tsx:34-38` already binds `status={this.stateStepper}` declaratively onto its internal `<bds-step-item>` — the same pattern could carry a new `position` prop on `bds-setting-step-item`, set from `bds-setting-steps` as a JS property instead of reaching two levels deep via `setAttribute`.
   - **Risk**: silently breaks if `bds-setting-step-item`'s internal markup/selector (`bds-setting-step-item__step-item`) changes — no compile-time signal, only a visual regression.

2. 🔴 **No reactivity to dynamic slot changes** (`bds-setting-steps.tsx:20`, `<slot>` at line 34) — `componentDidLoad()` runs exactly once; no `onSlotchange` handler, no `MutationObserver`. If `bds-setting-step-item` children are added, removed, or reordered after initial load (common in React/Vue consumers with conditional rendering), `position` attributes go stale silently with no error or visual re-sync.
   - Confirmed by both frontend-subagent and testing-subagent as a real correctness gap, not an edge case to waive.

3. 🟡 **Duplicated position-assignment logic** — the first/middle/last index calculation is duplicated between `bds-stepper.tsx:496` and `bds-setting-steps.tsx:22-27` with no shared helper. The two callsites already differ slightly in arity (`this.internalSteps.length - 1` vs. a precomputed `last` local) and could drift further.

4. 🟢 **Test coverage gap** — existing specs (`bds-setting-steps.basics.spec.ts`, `bds-setting-steps.variants.spec.ts`) only cover fixed-child-count markup present at initial `newSpecPage` mount. Missing:
   - A test for the single-child tie-break: `index === 0 ? 'initial' : index === last ? 'last' : 'middle'` resolves to `'initial'` (not `'last'`) when there is exactly one child, since `index === 0` is checked first. Deterministic and likely intentional, but currently unverified by any spec.
   - A test documenting the current static-only behavior (position not recomputed after a child is added/removed post-load), so the no-reactivity gap above is a visible, intentional contract rather than an undocumented landmine.

5. 🔴 **`stepperVisible` boolean prop defaults to `true`** (`bds-setting-steps.tsx:18`) — fires `stencil/ban-default-true` (official `@stencil/eslint-plugin` rule, active via `stencil.configs.flat.recommended` in `eslint.config.ts:11`), reproduced directly: `npx eslint bds-setting-steps.tsx` → `warning stencil/ban-default-true`. This is the **only** boolean `@Prop()` in the entire `boreal-web-components` package that defaults to `true` — every other boolean prop in the codebase defaults to `false`, consistent with HTML boolean-attribute convention (absent = off). Recommend either suppressing the rule with a justification comment or inverting the prop's polarity/name to default-false.

## Live QA Findings — `bds-setting-step-item-header` (via qa-subagent, Storybook `localhost:6006`)

6. 🔴 **Caret-selection bug on back-button click — CONFIRMED, cross-browser (Chromium + WebKit).** `bds-setting-step-item-header.tsx:64-76` renders the back button as `<i tabindex="0" role="button" class="...__back-btn">` — a focusable, empty, non-text element with no `user-select: none` in `bds-setting-step-item-header.scss:29-49` (unlike `bds-avatar.scss:35` and `bds-table.scss:181`, which do set it on their non-text interactive elements). A real click leaves `window.getSelection()` as `{ type: "Caret", anchorNode: "I" }` — a blinking caret with nothing to select. Verified fix: setting `user-select: none` on the element flips `Selection.type` to `"None"`.
   - **Fix**: add `user-select: none;` to `.bds-setting-step-item-header__back-btn` in `bds-setting-step-item-header.scss`.
7. 🟢 **Text highlighting on header title click — NOT a bug, expected behavior.** The title/description contain real text content; native browser text selection there is correct and desirable (e.g. copying a step title). No `user-select: none` should be added to `.__title`.
8. 🟡 **Side finding (MultipleSteps story): duplicate step-number badges.** `bds-setting-steps.tsx:20-29` auto-assigns `position` (initial/middle/last) but never `stepNumber`, which defaults to `1` on every `bds-step-item` (`bds-step-item.tsx:41`). In the `MultipleSteps` story, both the current and pending steps visually show badge `"1"`. Needs a product/design decision on whether `bds-setting-steps` should also auto-assign `stepNumber = index + 1`, or whether numbering is intentionally left to consumers.
9. General e2e sweep: all 8 stories in `bds-setting-steps.stories.ts` render with zero component-level console errors; `MultipleSteps` position-attribute logic (`initial`/`middle`/`last`) verified correct via DOM query and screenshot. Two unrelated, pre-existing environmental/adjacent issues surfaced (not blocking, not part of this PR's scope): external icon-font stylesheet blocked by CORS in the sandboxed QA environment, and stories passing an unsupported `type="email"` to `bds-text-field`.

## Memory-Guided Review

- **`dom-setattribute-aria-kebab-case.md`** — not applicable; `setAttribute('position', ...)` is not an ARIA attribute, no casing violation.
- **`component-accessor-naming-conventions.md`** — no getters in this file; no issue.
- **`feedback_boolean_prop_naming.md`** — `stepperVisible` correctly avoids `is`/`has`/`show` prefixes; no issue.
- **`.claude/agents/qa-subagent.md` / stencil-child-component-props-in-tests pattern** — the variants spec registers all three components (`BdsSettingSteps`, `BdsSettingStepItem`, `BdsStepItem`) in `newSpecPage`, so child DOM assertions (`getAttribute('position')`) are valid and not subject to the "unregistered child returns null" pitfall documented in project memory.
- No memory topic directly covers the cross-boundary `setAttribute` pattern in Finding 1 or the missing-`slotchange` gap in Finding 2 — worth capturing as new memory entries given this session's findings.

Memory topic files consulted: `dom-setattribute-aria-kebab-case.md`, `component-accessor-naming-conventions.md`, `feedback_boolean_prop_naming.md`, `.agents/memory/stencil-child-component-props-in-tests.md`.

---

**Result: 25 passed · 2 failed** (2 of the 2 failed items are false positives for this repo's release workflow and existing docs — see annotations above; 5 additional real issues found via manual review + live QA, not captured by automated checks: cross-boundary `setAttribute` coupling, missing slot reactivity, duplicated position logic, `ban-default-true` boolean-prop violation, and a caret-selection UI bug on the back button)

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_