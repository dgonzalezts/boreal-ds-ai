# Boreal DS — Code Review Report

**Generated:** 2026-05-25T19:36:23
**Base ref:** `release/current`
**Repository:** `.`

---

## Scope Note

The diff against `release/current` includes files from previously merged PRs that are not part of `bds-select`. Findings are split into two groups:

- **In-scope (bds-select)** — new files introduced by this PR
- **Out-of-scope (bds-list-menu, bds-text-field)** — pre-existing or unrelated to this PR's intent; flagged for awareness but not blocking

---

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

---

## Automated Findings

### In-scope (bds-select)

- 🟡 **[prop-mutable-form-attr]** `@Prop({ mutable: true }) value` — flagged as a native form attr without `@State()` mirror. `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx:31`

  > **Context:** This is a **false positive** for this component. `bds-select` is not a FACE component (no `formAssociated: true`, no `ElementInternals`). The memory topic `stencil-prop-patterns.md` explicitly permits `mutable: true` for "non-FACE props that the component needs to write internally (e.g. `value` tracking internal selection state)." No action needed.

- 🔴 **[event-name-format]** `@Event() valueChange` does not follow `bds{Action}` format. `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx:49`

  > **Context:** This is an **intentional exception** — `valueChange` is the canonical Vue v-model event enforced by `IFormValueEmitter<T>` and registered in `vue-output-target.ts` `componentModels`. Every form component in the codebase uses this pattern. No action needed; this is a known tool false positive for Vue-compat events.

- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.
  > **Action required:** Add a changeset before merging. Run `pnpm changeset` at the workspace root and select the affected packages (`boreal-web-components`, `boreal-docs`).

### Out-of-scope (pre-existing or other PRs — not blocking this PR)

- 🔴 **[prop-missing-jsdoc]** `bds-list-menu-item.tsx:64` — `@Prop()` missing JSDoc block.
- 🔴 **[event-name-format]** `bds-list-menu-item.tsx:100` — Event name `'readonly'` flagged.
  > **Note:** Almost certainly a tool parser false positive. The checker is reading the TypeScript `readonly` modifier in `@Event() readonly bdsXxx!:` and misidentifying it as the event name. Verify by checking the actual declaration; if confirmed as a false positive, file a bug against the checker script.
- 🟡 **[import-order]** `bds-list-menu-item.tsx:3,4,9` — import order violations.
- 🔴 **[event-name-format]** `bds-list-menu.tsx:49,52` — same `'readonly'` false-positive as above.
- 🟡 **[class-jsdoc-invalid-tags]** `bds-list-menu.tsx` — `@element`/`@method` in class JSDoc.
- 🟡 **[import-order]** `bds-list-menu.tsx:4,5` — import order violations.
- 🟡 **[prop-mutable-form-attr]** `bds-text-field.tsx:98` — pre-existing, same pattern as bds-select value.
- 🔴 **[event-name-format]** `bds-text-field.tsx:194` — `valueChange`, same intentional Vue-compat exception.
- 🔴 **[face-native-constraint-on-input]** `bds-text-field.tsx` — `required` on inner `<input>`. Pre-existing FACE issue.

---

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
  > **Standard (coding_standards.md):** "Chromatic deploys and docs tooling depend on stories being up to date. Behavior changes without story updates produce stale visual tests." Every form component ships a `.stories.tsx` and `.mdx`. This component has neither. The documentation ticket `EOA-10544` is the stated intent of this branch — stories and MDX are **required before merge**. See test-spec-file-organisation.md for the expected file split.
  >
  > **Antipattern:** Shipping a component without Storybook stories means the component is invisible to the design team, inaccessible to visual regression, and undiscoverable in the docs site.
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every `@Prop()` has `readonly` and an adjacent JSDoc block

  > **Standard:** `stencil/required-jsdoc` and `stencil/props-must-be-readonly` are both ESLint errors (not warnings). Every `@Prop()` must have `readonly` and a `/** */` JSDoc block directly above it. Missing descriptions degrade `custom-elements.json` and Storybook argType auto-generation.
  >
  > **Antipattern (`common_antipatterns.md`):** "Missing JSDoc on @Prop(): Violates `stencil/required-jsdoc` and degrades `custom-elements.json`."
  >
  > **In bds-select specifically:** `searchable` and `name` have JSDoc and `readonly`. However the `value` prop (`bds-select.tsx:31`) is **missing `readonly`** — this is a build-breaking ESLint error. See M10. ❌

- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`

  > **Standard:** `mutable: true` on `disabled` causes two writers on the same reflected attribute — the component and the browser via `formDisabledCallback` — which can race. Use `@State() private isDisabled` + `@Watch('disabled')` + `formDisabledCallback` writing to the state mirror.
  >
  > **Exception (stencil-prop-patterns.md):** "For non-FACE props that the component needs to write internally (e.g. `value` tracking internal selection state), use `@Prop({ mutable: true })` without a cast." bds-select's `value` prop is non-FACE and uses this correctly. The automated finding is a **false positive** for this component.

- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)

  > **Standard:** "Use prefixed camelCase event names: `bds{Action}`."
  >
  > **Exception for `valueChange`:** `valueChange` is the canonical Vue v-model event enforced by `IFormValueEmitter<T>` (see `stencil-form-control-interfaces.md`). It is registered in `vue-output-target.ts` `componentModels` and cannot be renamed. This is an accepted deviation from the `bds{Action}` rule. `bdsChange` ✅ follows the convention correctly.

- ✅ Event names do not reuse native DOM events
- ✅ `@AttachInternals()` is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via `@Method()` — _N/A: bds-select is not a FACE component_
- ❌ Only `ElementInternals.setValidity()` manages validity — _N/A: bds-select uses a hidden `<input>` for form submission, not FACE_
  > The automated finding is on `bds-text-field` (out-of-scope, pre-existing). bds-select delegates form submission to a hidden `<input name={this.name} value={this.value}>`, which is a different (non-FACE) progressive enhancement pattern and does not require `ElementInternals`.
- ✅ `formResetCallback` and `formStateRestoreCallback` call `updateValidity()` — _N/A for this component_
- ❌ JSDoc changes preserve `custom-elements.json` generation accuracy

  > **Standard:** JSDoc descriptions on `@Prop()` feed `custom-elements.json`'s `description` field (stencil-prop-patterns.md). Missing or stale descriptions show up as empty argTypes in Storybook.
  >
  > **In bds-select:** Props have JSDoc. The failing item is on `bds-list-menu-item` (out of scope). bds-select passes. ✅

- ✅ Boolean `@Prop()` names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts` — `ISelect.ts` ✅
- ✅ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX — _pending; see missing-stories finding below_
- ✅ Storybook aliasing intact for `@telesign/boreal-web-components/css/*`
- ✅ Uses `dotenv --` and `--storybook-build-dir`

---

## Memory-Guided Review

> Topic files consulted: `stencil-form-control-interfaces.md`, `stencil-prop-patterns.md`, `feedback_custom_events_naming.md` (via MEMORY.md), `test-spec-file-organisation.md`, `stencil-light-dom-host-vs-class.md`, `dom-setattribute-aria-kebab-case.md`, `mouseleave-relatedtarget-vs-target.md`, `component-accessor-naming-conventions.md`

---

### 1. `valueChange` event — Intentional Vue v-model exception ✅

`bds-select` emits both `bdsChange` (standard) and `valueChange` (Vue v-model compat). `valueChange` is registered in `vue-output-target.ts` `componentModels`. Memory (`stencil-form-control-interfaces.md`) confirms this is the correct pattern — `componentModels` must land in the same PR as the component, and it does. No issues.

---

### 2. `mouseleave` handlers ✅

No `mouseleave` handlers are present in `bds-select`. Not applicable.

---

### 3. FACE / `formDisabledCallback` ✅

`bds-select` is not a FACE component. It uses a hidden `<input>` for form submission. No `@AttachInternals()`, no `ElementInternals`, no `formDisabledCallback` needed. The pattern is intentional and correct for a composite wrapper.

**One observation:** The hidden `<input>` has a `name` attribute (`<input type="hidden" value={this.value} name={this.name} />`). Memory (`stencil-form-control-interfaces.md`) warns that hidden inputs inside FACE components must NOT have `name`. However, since bds-select is NOT FACE, the `name` attribute is the **sole mechanism** for form submission and is required here. This is correct.

---

### 4. Light DOM / SCSS ✅

`bds-select.scss` uses `bds-select { ... }` as the root selector (not `:host`). Correct for light DOM. No `::slotted()` usage. Passes the pattern from `stencil-light-dom-host-vs-class.md`.

---

### 5. ARIA `setAttribute` — kebab-case ✅

All `setAttribute` calls use kebab-case ARIA names: `aria-expanded`, `aria-haspopup`, `aria-autocomplete`, `aria-controls`. Passes `dom-setattribute-aria-kebab-case.md`. No issues.

---

### 6. Getter accessor naming ✅

Private getters (`bdsList`, `bdsField`, `bdsInput`, `bdsPopover`) carry no `get` prefix. Passes `component-accessor-naming-conventions.md`.

---

### 7. Test spec file organisation — **Issues found**

Per `test-spec-file-organisation.md`, the project convention splits tests across typed spec files:

| Expected file               | Reason                                                                      |
| --------------------------- | --------------------------------------------------------------------------- |
| `bds-select.basics.spec.ts` | Props, render output — ✅ exists                                            |
| `bds-select.a11y.spec.ts`   | ARIA attributes (combobox role, aria-expanded, aria-controls) — **missing** |
| `bds-select.events.spec.ts` | `bdsChange` and `valueChange` emissions, `bdsClear` — **missing**           |
| `bds-select.slots.spec.ts`  | Named slots (`field`, `list`) change rendered state — **missing**           |

Additionally, `bds-select.spec.tsx` is a single trivial render test that duplicates `basics`. It should be merged into `basics` and removed.

Current `.basics.spec.ts` extension is `.ts`, not `.tsx`. Stencil spec files that use JSX (e.g. `<bds-select>`) should use `.spec.tsx`.

---

## Manual Review Findings

These issues are not detected by static analysis but were identified by reading the component implementation.

### Props and Interface Contract

**M8. `ISelect` interface declared but never used in `implements` clause** (`bds-select.tsx:25`, `types/ISelect.ts`)

```typescript
// Current — interface is unused; no compile-time enforcement
export class BdsSelect {

// Required
export class BdsSelect implements ISelect {
```

`ISelect` defines the public API contract (value, searchable, name). Without `implements ISelect`, TypeScript enforces nothing: a prop could be removed or its type changed and the build would succeed silently. The `implements` clause is the correct mechanism — the interface is the contract, the class body is the implementation.

---

**M9. Indexed access types on `@Prop()` declarations** (`bds-select.tsx:31, 34, 37`)

```typescript
// Current — violates stencil-prop-patterns.md
@Prop({ mutable: true, reflect: true }) value: ISelect['value'] = '';
@Prop() readonly searchable: ISelect['searchable'] = false;
@Prop() readonly name: ISelect['name'] = '';

// Required — concrete primitives; interface enforced via implements on the class
@Prop({ mutable: true }) readonly value: string = '';
@Prop() readonly searchable: boolean = false;
@Prop() readonly name: string = '';
```

Memory topic `stencil-prop-patterns.md` explicitly bans indexed access types (`IFoo['prop']`) on `@Prop()` declarations: _"TypeScript's indexed access types appear to work at editor time but produce an `error`-typed result in the Stencil compiler context. This causes `@typescript-eslint/no-unsafe-assignment` errors on every read of that prop (event emitter calls, JSX attributes, class map values, etc.)."_

The `implements ISelect` clause on the class body (M8) is the correct way to enforce the interface. The prop declaration itself must use the concrete primitive (`string`, `boolean`).

---

**M10. `value` prop missing `readonly` keyword** (`bds-select.tsx:31`)

```typescript
// Current — missing readonly; violates stencil/props-must-be-readonly (error)
@Prop({ mutable: true, reflect: true }) value: ISelect['value'] = '';

// Required
@Prop({ mutable: true }) readonly value: string = '';
```

`readonly` and `mutable: true` are orthogonal (from `stencil-prop-patterns.md`):

- `readonly` prevents **external consumers** from assigning to the prop after initialization.
- `mutable: true` allows the **component itself** to write `this.value` internally.

Omitting `readonly` violates `stencil/props-must-be-readonly`, which is configured as `'error'` — this will fail the ESLint step of the build. The other two props (`searchable`, `name`) correctly carry `readonly`, making this inconsistency more visible.

---

**M11. `reflect: true` on `value` is unjustified** (`bds-select.tsx:31`)

`bds-select.scss` contains no CSS attribute selector referencing `value` (e.g. `bds-select[value="..."]`). Per `stencil-prop-patterns.md`: _"Add `reflect: true` only when the prop value is directly referenced by a CSS attribute selector in the component SCSS."_ Reflecting the value adds DOM overhead with no benefit unless a consumer explicitly depends on reading `getAttribute('value')` — which, if intentional, should be documented.

```typescript
// Remove reflect: true unless a CSS attribute selector is added
@Prop({ mutable: true }) readonly value: string = '';
```

---

**Corrected declaration (M8–M11 combined):**

```typescript
export class BdsSelect implements ISelect {
  @Prop({ mutable: true }) readonly value: string = '';
  @Prop() readonly searchable: boolean = false;
  @Prop() readonly name: string = '';
```

---

### Correctness

**M1. Memory leak — missing `disconnectedCallback`** (`bds-select.tsx:111–115`)

`addElementListener` registers DOM event listeners on `this.bdsList`, `this.bdsField`, `this.bdsInput`, and `this.bdsPopover` in `componentDidLoad`. There is no `disconnectedCallback` to remove them. If the component is conditionally rendered and destroyed, listeners accumulate on the next mount's children.

Fix: add `disconnectedCallback` calling `removeEventListener` on each registered handler. Requires storing handler references (currently anonymous arrow functions).

**M2. Dead code: `visibleOptions === undefined` guard** (`bds-select.tsx:225`)

```typescript
updateElementProp(
  this.bdsList,
  "empty",
  visibleOptions === undefined || visibleOptions.length === 0,
);
```

`querySelectorAll` always returns a `NodeList`, never `undefined`. The first operand is unreachable. Remove the `=== undefined` check.

**M3. Silent error discard in `loadValue`** (`bds-select.tsx:270`)

```typescript
.catch(() => {});
```

All `setSelectedValues()` failures are silently discarded. At minimum, add `console.warn` in development so failures surface during testing.

---

### Code Quality

**M4. Verbose boolean negation** (`bds-select.tsx:126`)

```typescript
updateElementProp(this.bdsField, "selectable", this.searchable ? false : true);
// → should be:
updateElementProp(this.bdsField, "selectable", !this.searchable);
```

**M5. Method name typo** (`bds-select.tsx:242`)

`resetChilds` → `resetChildren`. Update JSDoc and all three call sites (`listenField`, `listenPopOver`, `listenListMenu`).

**M6. Comment typos** (`bds-select.tsx:54, 142`)

- Line 54: `"Watch popver visible"` → `"Watch popover visible"`
- Line 142: `"sett value emitting event"` → `"set value emitting event"`

---

### Architecture / Fragility

**M7. Cross-component DOM piercing** (`bds-select.tsx:99–103`)

```typescript
return this.bdsField.querySelector("input");
```

This reaches into `bds-text-field`'s rendered output to find its `<input>`. It works because Stencil defaults to light DOM. If `bds-text-field` ever opts into shadow DOM (`shadow: true`), `querySelector` will return `null` and all ARIA attributes set on the input will silently be dropped.

This is the correct workaround given the current architecture — there is no other mechanism. This fragility should be acknowledged as a known dependency on `bds-text-field` remaining light DOM.

---

## Summary

| Category                       | Status                                        | Count                             |
| ------------------------------ | --------------------------------------------- | --------------------------------- |
| Automated: errors (in-scope)   | ⚠️ False positives — see notes                | 1 real (missing-changeset)        |
| Automated: warnings (in-scope) | ✅ False positive (mutable value on non-FACE) | —                                 |
| Missing documentation          | ❌ Blocking                                   | Stories + MDX required            |
| Props / interface contract     | ❌ Blocking (build error)                     | 4 (M8, M9, M10, M11)              |
| Manual: correctness            | ❌ Should fix                                 | 3 (M1, M2, M3)                    |
| Manual: code quality           | ⚠️ Non-blocking                               | 3 (M4, M5, M6)                    |
| Manual: fragility              | ℹ️ Informational                              | 1 (M7)                            |
| Test coverage                  | ❌ Should fix before merge                    | a11y, events, slots specs missing |

**Result: 21 passed · 6 checklist failures (4 out-of-scope pre-existing)**

---

**Blocking before merge:**

1. Fix `@Prop()` declarations: add `implements ISelect`, use concrete primitives, add `readonly` to `value`, remove `reflect: true` (M8–M11) — M10 is a build-breaking ESLint error
2. Add Storybook stories and MDX (ticket EOA-10544)
3. Add changeset (`pnpm changeset`)
4. Fix memory leak (M1) — `disconnectedCallback`
5. Add `bds-select.a11y.spec.ts`, `bds-select.events.spec.ts`

**Recommended (non-blocking):** 6. Remove dead `=== undefined` check (M2) 7. Add console.warn to `.catch` (M3) 8. Fix boolean negation, typos, method name (M4–M6) 9. Merge trivial `bds-select.spec.tsx` into `bds-select.basics.spec.ts`

---

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py) + manual enrichment_
