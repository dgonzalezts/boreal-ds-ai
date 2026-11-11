# Boreal DS — Code Review Report

**Generated:** 2026-11-11T12:58:18  
**Base ref:** `origin/release/current`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.tsx:88`
- 🔴 **[face-native-constraint-on-input]** Inner <input> carries native constraint attribute `required`. Ownership of validity must stay with `ElementInternals.setValidity()`. `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.tsx`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox-group/bds-checkbox-group.tsx:81`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox-group/bds-checkbox-group.tsx:124`
- 🟡 **[unstable-state-reference]** 'value' is reassigned via `{ ...this.value, ... }` with no preceding guard checking whether the new value actually differs — this creates a new reference (and a re-render) even when nothing logically changed. `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox-group/bds-checkbox-group.tsx:241`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-color-picker/bds-color-picker/bds-color-picker.tsx:106`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-color-picker/bds-color-picker/bds-color-picker.tsx:146`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-number-field/bds-number-field.tsx:90`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-number-field/bds-number-field.tsx:162`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx:84`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx:128`
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx:134`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx:99`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx:155`
- 🔴 **[face-native-constraint-on-input]** Inner <input> carries native constraint attribute `required`. Ownership of validity must stay with `ElementInternals.setValidity()`. `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx:67`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx:166`
- 🔴 **[face-native-constraint-on-input]** Inner <input> carries native constraint attribute `required`. Ownership of validity must stay with `ElementInternals.setValidity()`. `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`
- 🟡 **[unused-prop]** @Prop() 'rel' is declared but never referenced anywhere else in this file — likely dead code. Remove it, or add a comment explaining a genuine deferred/external use (e.g. an ADR-governed future-phase prop). `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:39`
- 🟡 **[unused-prop]** @Prop() 'htmlFor' is declared but never referenced anywhere else in this file — likely dead code. Remove it, or add a comment explaining a genuine deferred/external use (e.g. an ADR-governed future-phase prop). `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:66`
- 🟡 **[unused-prop]** @Prop() 'target' is declared but never referenced anywhere else in this file — likely dead code. Remove it, or add a comment explaining a genuine deferred/external use (e.g. an ADR-governed future-phase prop). `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:72`
- 🟡 **[unused-prop]** @Prop() 'downloadable' is declared but never referenced anywhere else in this file — likely dead code. Remove it, or add a comment explaining a genuine deferred/external use (e.g. an ADR-governed future-phase prop). `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:75`
- 🟡 **[unused-prop]** @Prop() 'filename' is declared but never referenced anywhere else in this file — likely dead code. Remove it, or add a comment explaining a genuine deferred/external use (e.g. an ADR-governed future-phase prop). `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:78`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:6`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:10`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx:99`
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
- ✅ Public APIs, events, and props follow naming conventions
- ❌ Self-referencing `{ ...x, ... }` spreads guard against no-op reassignment (reference stability)
- ✅ Event handlers guard against redundant re-invocation of the same imperative action

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ❌ Only ElementInternals.setValidity() manages validity
- ✅ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
- ✅ JSDoc changes preserve custom-elements.json generation accuracy
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ❌ Getter accessors carry no redundant `get` prefix
- ❌ No unused `@State()`/non-`reflect` `@Prop()` fields

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

Checked light DOM, prop validation, FACE disabled mirror and event naming against touched files. Automated `valueChange` / `required` hits are pre-existing and out of scope. No new `shadow: true` usage. Validated by frontend-, testing- and documentation-subagent.


---

## Consolidated Findings

### 🔴 Blocking - Frontend

| # | File | Line(s) | Issue | Fix | PR comment |
|---|------|---------|-------|-----|-----------|
| 1 | `bds-dropdown.scss` | 3 | `--popover-content-padding: $boreal-spatial-padding-2xs 0;` is not interpolated, so the CSS is invalid and the padding change has no effect. (frontend-subagent) | Use `#{$boreal-spatial-padding-2xs} 0` | The padding custom property does not seem to compile to a valid value. |

### 🔴 Blocking - Documentation

| # | File | Line(s) | Issue | Fix | PR comment |
|---|------|---------|-------|-----|-----------|
| 1 | `bds-typography.mdx` | 165, 177, 197 | Still documents removed `state="disabled"` / `state="error"`. (documentation-subagent) | Use `disabled` / `error` | The docs still mention the removed `state` prop. |

### 🟡 Should Fix - Frontend

| # | File | Line(s) | Issue | Fix | PR comment |
|---|------|---------|-------|-----|-----------|
| 1 | `bds-typography.tsx` | 35-36 | Commented-out `state` prop and orphaned JSDoc left behind. (frontend-subagent) | Delete both lines | Is the commented-out `state` prop meant to stay? |
| 2 | `renderFieldParts.tsx`, `bds-toggle.tsx:274`, checkbox/radio group, color-picker | - | Helper is red when disabled and error, where before disabled took precedence. (frontend-subagent) | `error={effectiveError && !isDisabled}` | A disabled field with an error now shows a red helper. |
| 3 | `bds-radio.scss` | 7-9 | `inline-flex` became `grid`, so the standalone radio is now block-level and fills the row. (frontend-subagent) | Use `inline-grid` | The radio now seems to stretch to full width. |
| 4 | `bds-typography.tsx` | prop removal | Removing public `state` is breaking, with no BREAKING CHANGE footer or migration note. (frontend-subagent) | Add footer or changelog entry | Should this carry a breaking-change note? |

### 🟡 Should Fix - Documentation

| # | File | Line(s) | Issue | Fix | PR comment |
|---|------|---------|-------|-----|-----------|
| 1 | `bds-dialog.stories.ts` | 318-325 | Added `<script>` is inert in Lit and would redeclare top-level `const` on re-render. `handleButtonClick` is unused by it. (documentation-subagent) | Move to `parameters.docs.source.code` or remove | Does this script run? It looks unused. |

### 🟡 Should Fix - Testing

| # | File | Line(s) | Issue | Fix | PR comment |
|---|------|---------|-------|-----|-----------|
| 1 | `bds-radio-group.basics.spec.ts` | 265, 337, 348 | `getAttribute(...).toBeDefined()` always passes since null is defined. (testing-subagent) | Use `hasAttribute(...)` toBe(true) | Some assertions here can never fail. |
| 2 | `bds-typography` specs | - | No tests for helper `error`, disabled link href/aria-disabled, label aria-disabled, props ignored on unsupported variants. (testing-subagent) | Add them | Can we cover the new props? |
| 3 | color-picker, toggle specs | - | No tests for readOnly divider removal or toggle label `disabled`. (testing-subagent) | Add them | The new behaviour has no tests. |

### 🟢 Nice to Have

| # | File | Line(s) | Issue | Fix | PR comment |
|---|------|---------|-------|-----|-----------|
| 1 | `_radio-input-button.scss` | 24-26 | `transition: 120ms transform` is overridden by `bds-transition-surface`. Dot is 9px not 10px. (frontend-subagent) | Remove or merge transitions | The transform transition has no effect. |
| 2 | `bds-radio-card.scss` | - | Shared hover now adds button shadow to radio-card. (frontend-subagent) | Confirm with design | Is the new card hover intended? |
| 3 | `bds-radio-button.basics.spec.ts` | 28 | Asserts null `__dot`, now meaningless. (testing-subagent) | Remove | This assertion is now trivial. |
| 4 | `bds-typography.stories.tsx` | 150-168 | `disabled` argType has no `if`, `error` does. (documentation-subagent) | Align | The controls look inconsistent. |
| 5 | Specs | - | Titles still say "state". (testing-subagent) | Rename | Test names are outdated. |

### ℹ️ Out of Scope

| Aspect | Assessment |
|--------|-----------|
| `bds-banner.tsx` open() JSDoc says "close" | Pre-existing |
| `valueChange` event names, mutable form props | Pre-existing |

### ✅ Confirmed Correct

| Aspect | Assessment |
|--------|-----------|
| Banner TOC anchors | Match headings |
| CompactVariant rename | No leftovers |
| Typography `?disabled`/`?error` wiring | Valid |
| Color-picker readOnly dividers | Safe, compact unaffected |
| Specs (27 suites, 321 tests) | Pass |

## Overall Assessment

**Not ready to merge.** 2 blocking, remaining should-fix listed above.


---

**Result: 22 passed · 8 failed**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_