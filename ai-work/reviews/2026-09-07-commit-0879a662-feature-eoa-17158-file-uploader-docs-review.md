# Boreal DS — Code Review Report

**Generated:** 2026-09-07T12:29:13  
**Base ref:** `release/current`  
**Repository:** `.`  
**Validated by:** frontend-subagent, testing-subagent, documentation-subagent (2026-09-07)

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:30`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:45`
- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:2`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:3`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:98`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/forms/bds-file-uploader/bds-file-list/bds-file-list.tsx:2`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-file-uploader/bds-file-picker/bds-file-picker.tsx:123`
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
  - Checklist (`code-review-checklist.md:35`): "**Docs updated**: Storybook/MDX/README updates exist when behavior or APIs change."
  - This PR *is* the docs update, so the automated scan's generic doc-staleness heuristic is not the relevant risk here — the actual failure mode is the reverse: the new docs themselves are stale/wrong relative to the already-shipped component API. See the consolidated findings below.
- ✅ Public APIs, events, and props follow naming conventions
- ✅ Self-referencing `{ ...x, ... }` spreads guard against no-op reassignment (reference stability)
- ✅ Event handlers guard against redundant re-invocation of the same imperative action

### A — Stencil (boreal-web-components)

- ✅ Every @Prop() has `readonly` and an adjacent JSDoc block
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
  - Checklist (`code-review-checklist.md:64`): "**Mutable props**: `mutable: true` is not used on native form attributes (`disabled`, `checked`, `value`) — use a `@State()` mirror instead."
  - Antipattern (`common_antipatterns.md:46`): "`mutable: true` on `disabled`: Stencil warns and creates two writers on the same reflected attribute (the component and the browser via `formDisabledCallback`). Use `@State() private isDisabled` as the internal working copy instead."
  - Finding is on `bds-progress-bar.tsx:30` — `@Prop({ mutable: true, reflect: true }) value: number = 0;`. `bds-progress-bar` is not itself FACE (no `formAssociated`), so this isn't the `disabled`-writer-collision scenario the rule targets; it's a pre-existing pattern on an unrelated, already-shipped component swept in only because this branch's diff base is `release/current`, not a regression introduced by the docs commit under review.
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
  - Checklist (`code-review-checklist.md:83`): "**Event naming**: Custom events use the `bds{Action}` prefixed camelCase pattern."
  - Memory (`.agents/memory/MEMORY.md:35`): "**Custom event naming** — `@Event()` names follow `bds{Action}` camelCase... Exception: `valueChange` is reserved for Vue `v-model` integration."
  - Both automated hits (`bds-progress-bar.tsx:45`, `bds-file-picker.tsx:123`) are `valueChange` — an intentional, documented exception (also confirmed by checklist §B: `eventAttr` used when `valueChange` emits a primitive), not a real violation. **False positive** — the static checker doesn't know about this exception.
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
- ❌ Getter accessors carry no redundant `get` prefix
  - Checklist (`code-review-checklist.md:67`): "**Getter accessor naming**: Getter methods do not carry a `get` prefix — `get placement()` not `get getPlacement()`."
  - Antipattern (`common_antipatterns.md:89`): "Writing `get getPlacement()` is redundant — the `get` keyword already marks it as an accessor. Use `get placement()` instead."
  - Finding is `bds-progress-bar.tsx:98` — `private get getClassMap(): StyleModifiers`. Same as above: pre-existing on an already-shipped component, swept in by the `release/current` diff base rather than introduced by this docs PR. Real violation, out of scope for this review's actual change set.
- ✅ No unused `@State()`/non-`reflect` `@Prop()` fields

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

### Custom event naming exception (`valueChange`)

`.agents/memory/MEMORY.md:35` documents `valueChange` as a reserved exception to the `bds{Action}` event-naming rule (Vue `v-model` integration). Both automated `event-name-format` hits (`bds-progress-bar.tsx:45`, `bds-file-picker.tsx:123`) are this exact event — **false positives**, already annotated inline above. No action needed.

### Storybook argTypes patterns (`storybook-argtypes-name-collision.md`)

This memory file documents that `<ArgTypes>` filters resolve against the whole shared `meta.argTypes` object, not per sub-component — which prompted a manual audit of `bds-file-uploader.stories.ts`'s `argTypes`/`args` wiring beyond what the static checker covers. Two issues found:

- **`disabled` argType is fully inert.** Declared in `meta.argTypes` (line 50) with `table.category: 'BDS File Uploader'` and a default (`args.disabled = false`, line 135), but `bds-file-uploader` has no `disabled` prop at all (only `multiple` — see `bds-file-uploader.tsx:21`) and no story ever binds `args.disabled` to `bds-file-picker`'s actual `disabled` prop. The control renders in Storybook and does nothing.
- **`name` argType is mis-categorized.** Declared under `table.category: 'BDS File Uploader'` (line 36), but `name` is a `bds-file-picker` prop (`bds-file-picker.tsx:70`) — `bds-file-uploader` itself has no `name` prop. Should be categorized `'BDS File Picker'` alongside `required`/`maxSize`/`maxFiles`/`accept`/`error`/`errorMessage`, which are correctly categorized there.

Both compound the `?name=`/`?error-message=` Lit boolean-directive bug already reported (see the consolidated findings below): the `name` control is miscategorized *and* non-functional even when moved to the right story.

### FACE / component-API conventions (`stencil-best-practices.md` §"Component API Conventions")

`bds-file-picker.tsx` was cross-checked against the FACE checklist in `.agents/memory/MEMORY.md:9-23` — `@AttachInternals()` on the class body (not a mixin), `@Method()` wrappers for `checkValidity()`/`reportValidity()`, `IFormControl<File[]>` in the `implements` clause, and `formResetCallback`/`formStateRestoreCallback` both calling `updateValidity()` are all present and correct. No issues found. (The gap here isn't in the component — it's that the *docs* omit `checkValidity()`/`reportValidity()` from the MDX Methods table; see consolidated findings.)

### Storybook/MDX-specific memory (`storybook-vite-quirks.md`, `storybook-action-wiring-web-components.md`, `storybook-source-snippet-non-primitive-props.md`)

None of these apply here: the story file uses direct event listeners in inline `<script>` blocks rather than Storybook's `action()` wiring, and no non-primitive prop (array/object) is bound via Lit property binding, so the source-snippet-override pattern isn't triggered.

### Event naming semantics — `bds{Component}{Action}` pattern check

Memory (`.agents/memory/MEMORY.md:35`) states: "Custom events use the `bds{Action}` prefixed camelCase pattern. No component noun in the middle (`bdsClose`, not `bdsBannerClose`)."

**Finding:** `bds-file-list.tsx:40` declares `@Event() bdsClickAdd!: EventEmitter<void>;`. This event name embeds two action verbs ("Click" and "Add") rather than following the simpler `bds{Action}` pattern. While not a direct violation of the "component noun in the middle" rule (there's no "List" or "File" in the name), it deviates from the established pattern of single-action events like `bdsClose`, `bdsChange`, `bdsOpen`.

**Recommendation:** Consider renaming to `bdsAdd` or `bdsRequestAdd` for consistency with other components. However, this is a **minor style issue** rather than a blocking violation, as the event does not embed a component noun.

### Light DOM — unscoped selector check

Memory (`.agents/memory/stencil-light-dom-unscoped-selector-leak.md`) documents that top-level selectors outside the root tag block leak as global CSS.

**Finding:** `bds-file-uploader.scss` correctly nests all selectors under `.bds-file-uploader { ... }` (lines 1-6). No unscoped selectors found. ✓

### FACE architecture — composite wrapper pattern

`bds-file-uploader.tsx` itself is **not** a form control — it's a composite wrapper that delegates to `bds-file-picker`. This is architecturally correct: only the leaf component (`bds-file-picker`) needs FACE, not the container. The wrapper correctly uses `@Listen('bdsClickAdd')` to coordinate between child components without duplicating form-control logic.

### Memory topic files consulted

- `.agents/memory/MEMORY.md` (index)
- Inline: "Component API Conventions" section (FACE, event naming, `IComponent.ts`, getter naming)
- Inline: "Storybook + Vite" section (`storybook-argtypes-name-collision.md`, `storybook-action-wiring-web-components.md`, `storybook-source-snippet-non-primitive-props.md`, `storybook-vite-quirks.md`)
- `stencil-light-dom-unscoped-selector-leak.md`
- `ai-docs/guidelines/code-review-checklist.md`
- `.agents/skills/code-reviewer/references/common_antipatterns.md`

---

## Consolidated Findings

All findings from the automated scan, memory-guided review, and three specialist subagent validations (frontend, testing, documentation) consolidated into a single actionable list.

### 🔴 Blocking — Frontend Architecture

| # | File | Line(s) | Issue | Fix |
|---|------|---------|-------|-----|
| F1 | `bds-file-uploader.tsx` | 36-55 | **Missing `@Watch('multiple')`** — Prop delegation to children only happens in `componentWillLoad()`. Runtime changes to `multiple` have no effect on `<bds-file-picker>` or `<bds-file-list>`. Silent correctness bug. | Add `@Watch('multiple')` handler that calls `preloadAttrs()` |
| F2 | `bds-file-picker.scss` | 27-30 | **`:focus` instead of `:focus-visible`** — Violates Safari cross-browser commitment. Missing `outline: none` + `@include bds-focus-ring` pattern used across 17+ other components. Drop zone is keyboard-focusable (`tabIndex={0}`) and handles Enter/Space. | Replace `:focus` with `:focus-visible`, add `outline: none` and `@include bds-focus-ring` |

### 🔴 Blocking — Documentation (copy-paste-breaking errors)

| # | File | Line(s) | Issue | Fix |
|---|------|---------|-------|-----|
| D1 | `stories.ts` | 160, 239, 388 | `?name=${args.name}` on string prop — Lit's boolean `?attr=` directive only toggles attribute presence, never writes the value. `bds-file-picker.syncFormValue()` treats `name=""` as "no name" and skips appending files to FormData, silently breaking form submission. | Change to `name=${args.name}` |
| D2 | `stories.ts` | 166, 245, 394 | `?error-message=${args.errorMessage}` on string prop — same issue as D1. Typed validation message is discarded. | Change to `error-message=${args.errorMessage}` |
| D3 | `bds-file-uploader.mdx` | 219 | Documents `removeFiles(files: File[])` — real method is `removeFile(target: File \| number)`. Wrong name, arity, and parameter type. Consumer gets `TypeError`. | Change to `removeFile(target: File \| number)` |
| D4 | `bds-file-uploader.mdx` | 227 | Documents `bdsFileSelected` — real event is `bdsFilesSelected` (plural, emits `File[]`). `addEventListener('bdsFileSelected', ...)` never fires. | Change to `bdsFilesSelected` with payload type `CustomEvent<File[]>` |
| D5 | `bds-file-uploader.mdx` | 114 | `slot="helperText"` (camelCase) in main usage example — component only defines kebab-case `helper-text` slot. Content silently falls into default slot. | Change to `slot="helper-text"` |
| D6 | `bds-file-uploader.mdx` | ~213 | Methods table missing `checkValidity()` and `reportValidity()` — both public `@Method()`s critical for form integration. | Add both rows |
| D7 | `stories.ts` | 274 | `event.target.files[0].name` in EventsAndMethodsFilePicker — `files` is property-only (`attribute: null`), so `event.target.files` is `undefined`. Crashes with `TypeError`. | Change to `event.detail[0].name` with empty guard |

### 🟡 Should Fix — Documentation

| # | File | Line(s) | Issue | Fix |
|---|------|---------|-------|-----|
| D8 | `stories.ts` | 154 | Default story doesn't bind `args.multiple` — control renders but does nothing. | Add `?multiple=${args.multiple}` to `<bds-file-uploader>` |
| D9 | `stories.ts` | 50-57, 135 | `disabled` argType is fully inert — no story binds it to `<bds-file-picker>`. | Remove or bind to `<bds-file-picker disabled=${args.disabled}>` |
| D10 | `stories.ts` | 45 | `name` argType categorized as `'BDS File Uploader'` — should be `'BDS File Picker'`. | Change category |
| D11 | `stories.ts` | 321-322 | `FileList` story binds `multiple` to `<bds-file-list>` instead of `<bds-file-uploader>` — inconsistent with other stories. | Move `?multiple` to `<bds-file-uploader>` |
| D12 | `bds-file-uploader.mdx` | 269-304 | No Events section for `<bds-file-list>` — it emits `bdsClickAdd`, which `bds-file-uploader` listens for internally. | Add Events subsection |
| D13 | `bds-file-uploader.mdx` | 277-280 | File List properties table missing `multiple` prop — it's a public `@Prop()` on `bds-file-list`. | Add `multiple` row |
| D14 | `bds-file-uploader.mdx` | 225-232 | Events table omits all `CustomEvent` payload types — developers can't write typed handlers. | Add payload type to each row |

### 🟡 Should Fix — Testing

| # | File | Line(s) | Issue | Fix |
|---|------|---------|-------|-----|
| T1 | `bds-file-picker.methods.spec.ts` | 143-170 | `checkValidity()`/`reportValidity()` assertions too weak — assert `typeof === 'boolean'` but never the actual value. Would not catch mutants. | Assert actual boolean values (`toBe(true)` / `toBe(false)`) |
| T2 | `bds-file-picker.methods.spec.ts` | — | `removeFile()` with non-member File reference untested — guard path (`indexOf` → `-1`) not covered. | Add test with File not in array |
| T3 | `bds-file-picker.forms.spec.ts` | — | `formStateRestoreCallback` `else` branch untested — unknown state → `files = []` path not verified. | Add test that populates files, restores unknown state, asserts reset |
| T4 | `bds-file-picker/__test__/bds-file-picker.spec.tsx` | — | Empty spec file (0 bytes) — dead weight, could confuse CI/coverage. | Delete file |

### 🟢 Nice to Have

| # | File | Line(s) | Issue | Fix |
|---|------|---------|-------|-----|
| F3 | `bds-file-picker.tsx` | 524-537 | Drop zone missing `aria-label`/`aria-labelledby` — relies on slotted text content for accessible name. | Add explicit `aria-label` or `aria-labelledby` |
| F4 | `bds-file-list.tsx` | 55 | Hardcoded English "Add file" button label — no i18n mechanism. | Add prop/slot for localization |
| F5 | `bds-file-picker.scss` | 3, 88 | `$boreal-spatial-spacing-3xs` used as border width — semantic conflation of spacing and border tokens. | Use dedicated border-width token |

### ℹ️ Out of Scope (pre-existing on unrelated components)

| # | File | Issue |
|---|------|-------|
| — | `bds-progress-bar.tsx:30` | `mutable: true` on `value` prop — pre-existing, not introduced by this PR |
| — | `bds-progress-bar.tsx:45` | `valueChange` event naming — false positive (documented Vue exception) |
| — | `bds-progress-bar.tsx:98` | `get getClassMap()` getter naming — pre-existing, not introduced by this PR |

### ✅ Confirmed Correct

| Aspect | Assessment |
|--------|-----------|
| Wrapper/leaf FACE split | ✅ Only `bds-file-picker` is `formAssociated: true` — correct |
| `@AttachInternals()` placement | ✅ On class body, not in mixin — follows ADR-0001 |
| `IFormControl<File[]>` implementation | ✅ `value` getter/setter delegates to `files` |
| FACE lifecycle callbacks | ✅ All 4 present and correct |
| Constraint validation | ✅ `checkValidity()`/`reportValidity()` exposed as `@Method()`s |
| `@State()` mirror for `disabled` | ✅ No `mutable: true` on prop |
| Event coordination | ✅ `@Listen('bdsClickAdd')` catches bubbling event correctly |
| Slot architecture | ✅ Well-structured across all 3 components |
| CSS nesting | ✅ All selectors nested under root tag block — no unscoped leaks |
| Reference-stable state | ✅ `commitFiles()` creates new arrays; `clear()` guards no-op |
| Event naming (picker) | ✅ All follow `bds{Action}` pattern; `valueChange` is documented exception |
| Boolean prop naming | ✅ No `is`/`has`/`show` prefixes |
| Getter naming | ✅ No redundant `get` prefix |
| `files` as property-only | ✅ `@Prop({ mutable: true, attribute: null })` — correct for `File[]` |
| Light DOM selectors | ✅ No unscoped selectors in any SCSS file |

---

## Core Utility Regression Analysis: `internals.ts`

The PR modifies `packages/boreal-web-components/src/utils/form/internals.ts`, a core utility used by all FACE components.

### Changes Made

| Change | Used by File Uploader? | Used by Any Component? |
|--------|------------------------|------------------------|
| `FormControlValue` type (adds `FormData` to union) | ✅ Yes — `bds-file-picker.syncFormValue()` passes `FormData` | ✅ Yes — `bds-checkbox-group` already passes `FormData` |
| `state` parameter on `setFormValue` | ❌ No | ❌ No — **dead code** |
| Conditional arity logic (`if (state !== undefined)`) | ❌ No (only `else` branch runs) | ❌ No |
| JSDoc updates | ✅ Yes — documents `FormData` naming behavior | ✅ Yes |
| `runValidators` `anchor` parameter | ✅ Yes — `bds-file-picker.updateValidity()` passes anchor | ✅ Yes — already existed |

### Regression Risk: ✅ Safe

- **Backward compatible** — all existing callers pass 1-2 args; the conditional arity preserves exact behavior
- **Type expansion** — `FormData` added to `FormControlValue` union; old callers passing `string | File | null` still work
- **No test breakage** — tests use `toHaveBeenCalledWith(value)` which still matches 1-arg calls

### Recommendation

**Remove the unused `state` parameter.** No caller in the codebase passes a 3rd argument. The conditional arity logic (lines 51-55) adds complexity without benefit. If needed later, it can be added when a component actually requires it.

**Add unit tests for `internals.ts`.** This is a core utility with no dedicated test file. Coverage should include:
- `setFormValue` with `string`, `File`, `FormData`, `null`
- `setFormValue` with and without `state` (if kept)
- `runValidators` with passing/failing validators
- `runValidators` with and without `anchor`

---

## Test Suite Assessment

**Branch:** `feature/EOA-17158_file-uploader-test` (commit `475efc1`)

### Coverage Summary

| Component | Spec Files | Lines | Assessment |
|-----------|-----------|-------|------------|
| `bds-file-picker` | 10 | ~2,200 | ✅ Comprehensive — all 7 methods, 6 events, 4 FACE callbacks, 4 slots, 5 watchers |
| `bds-file-list` | 3 | ~500 | ✅ Complete — props, events, slots |
| `bds-file-uploader` | 3 | ~400 | ✅ Complete — props, event coordination, slots, null guards |
| **Total** | **16** | **~3,100** | **Structurally excellent** |

### What Tests Would Catch

- ✅ `removeFiles()` vs `removeFile()` mismatch (D3) — tests exercise real method signature
- ✅ `bdsFileSelected` vs `bdsFilesSelected` mismatch (D4) — tests listen for plural event name
- ✅ Missing `bds-file-list` events section (D12) — 5 dedicated tests cover `bdsClickAdd`
- ⚠️ Missing `checkValidity()`/`reportValidity()` from MDX (D6) — tests exist but assertions too weak

### Testing Gaps (see T1-T4 above)

The test suite is structurally excellent but needs stronger assertions on validity methods and a few more edge-case tests to reach ≥ 90% mutation score.

---

## Overall Assessment

**Not ready to merge.** 21 actionable findings across frontend architecture, documentation, and testing.

### Blocking (must fix before merge)

- **F1:** Missing `@Watch('multiple')` on `bds-file-uploader` — silent correctness bug
- **F2:** `:focus` → `:focus-visible` fix on drop zone — Safari cross-browser commitment
- **D1-D7:** Documentation copy-paste-breaking errors (wrong method names, wrong event names, broken code examples)

### Should Fix (quality)

- **D8-D14:** Inert controls, miscategorization, missing documentation sections
- **T1-T4:** Testing gaps (weak assertions, untested guard paths, empty spec file)

### Nice to Have

- **F3-F5:** Accessibility, i18n, token semantics

### Refuted Findings

**None.** All findings were confirmed by at least one subagent. The `bdsClickAdd` event naming observation was confirmed as a minor style deviation but not a blocking issue.

---

**Result: 26 passed · 4 failed**

_Generated by [review_report_generator.py](.agents/skills/code-reviewer/scripts/review_report_generator.py)_
_Validated by frontend-subagent, testing-subagent, and documentation-subagent (2026-09-07)_
