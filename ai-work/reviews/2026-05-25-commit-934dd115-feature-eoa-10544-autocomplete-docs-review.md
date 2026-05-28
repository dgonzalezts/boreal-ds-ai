# Boreal DS — Code Review Report

**Generated:** 2026-05-25T19:36:23 (updated 2026-05-26)
**Base ref:** `release/current`
**Repository:** `.`

---

## Scope Note

The diff against `release/current` includes files from previously merged PRs that are not part of `bds-select`. Findings are split into two groups:

- **In-scope (bds-select + KeyboardController tests)** — new test files introduced by this PR
- **Out-of-scope (bds-list-menu, bds-text-field)** — pre-existing or unrelated to this PR's intent; flagged for awareness but not blocking

The primary focus of this branch (`feature/EOA-10544-autocomplete-testing`) is adding unit tests for:

1. `bds-select` — four typed spec files (basics, a11y, events, slots)
2. `KeyboardController` utility — three spec files (controller, focus strategies, navigation)
3. `bds-list-menu` / `bds-list-menu-item` — basics and events specs

---

## Affected Packages

- **boreal-web-components (Stencil)** — checklist section(s): A, tests

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
- ✅ **New logic is covered by tests** — all four typed spec files now present _(was ❌ in prior revision)_
- ✅ Tests use `waitForChanges()` before DOM assertions _(with one exception — see T3)_
- ❌ Storybook/MDX/README updated when behavior or APIs change
  > Stories and MDX files are now present (`bds-select.stories.ts`, `bds-select.mdx`). However both files have blocking correctness errors (wrong element names in MDX, missing `menu-role` in stories). See S1, D1, D2.
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every `@Prop()` has `readonly` and an adjacent JSDoc block

  > **In bds-select specifically:** `value` prop (`bds-select.tsx:31`) is **missing `readonly`** — build-breaking ESLint error. See M10.

- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`

  > **Exception (stencil-prop-patterns.md):** bds-select's `value` prop is non-FACE and uses this correctly. Automated finding is a **false positive** for this component.

- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)

  > **Exception for `valueChange`:** canonical Vue v-model event, cannot be renamed.

- ✅ Event names do not reuse native DOM events
- ✅ `@AttachInternals()` is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via `@Method()` — _N/A: bds-select is not a FACE component_
- ❌ Only `ElementInternals.setValidity()` manages validity — _N/A: bds-select uses a hidden `<input>` for form submission, not FACE_
  > The automated finding is on `bds-text-field` (out-of-scope, pre-existing).
- ✅ `formResetCallback` and `formStateRestoreCallback` call `updateValidity()` — _N/A for this component_
- ❌ JSDoc changes preserve `custom-elements.json` generation accuracy

  > **In bds-select:** Props have JSDoc. The failing item is on `bds-list-menu-item` (out of scope). bds-select passes. ✅

- ✅ Boolean `@Prop()` names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts` — `ISelect.ts` ✅
- ✅ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX — _pending; see missing-stories finding_
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

### 7. Test spec file organisation ✅ _(was ❌ in prior revision)_

All four required spec file types are now present:

| Expected file               | Status                        |
| --------------------------- | ----------------------------- |
| `bds-select.basics.spec.ts` | ✅ Exists — 3 tests           |
| `bds-select.a11y.spec.ts`   | ✅ Exists — 1 test (see T1)   |
| `bds-select.events.spec.ts` | ✅ Exists — 2 tests (see T4)  |
| `bds-select.slots.spec.ts`  | ✅ Exists — 1 test (see T5)   |

`bds-select.spec.tsx` still exists as a duplicate of the basics render test. See T2 for the merge recommendation.

---

## Unit Testing Review

This section covers all new test files introduced in this branch.

### T1. `bds-select.a11y.spec.ts` — Good foundation, missing dynamic state

The single test verifies the initial ARIA state (`aria-expanded="false"`, role, `aria-haspopup`, `aria-controls`, `aria-autocomplete`). The `aria-controls` ↔ `id` link assertion is particularly valuable.

**Missing coverage:**

- `aria-expanded="true"` when the popover is open (the test only covers the closed state)
- `aria-autocomplete="list"` when `searchable=true` — the component sets a different value for searchable mode; this state is untested
- When `searchable=true`, the input `role` may differ from the non-searchable case — not covered

**Action:** Add a second test that opens the popover (via click or `bdsOpen` event) and asserts `aria-expanded="true"`, and a third test for `searchable=true` asserting `aria-autocomplete="list"`.

---

### T2. `bds-select.spec.tsx` — Incomplete duplicate, should be removed

```typescript
// bds-select.spec.tsx — missing BdsListMenuItem in components array
components: [BdsSelect, BdsListMenu, BdsTextField],
html: `...
  <bds-list-menu-item variant="label">Group 1</bds-list-menu-item>
  ...`
```

`BdsListMenuItem` is used in the HTML template but not registered in `components`. In Stencil's test environment, unregistered child custom elements are not upgraded — the test currently passes only because the single assertion is `assertExists(page.root, ...)`, which succeeds regardless of child rendering. The test adds no value over `bds-select.basics.spec.ts` and masks the missing registration.

**Action:** Delete `bds-select.spec.tsx`. The render coverage is already provided by `bds-select.basics.spec.ts`.

---

### T3. `bds-select.basics.spec.ts` — Missing `waitForChanges()` before hidden input assertion

```typescript
// bds-select.basics.spec.ts:40–65 — "Should have input hidden with value"
const { root } = await newSpecPage({ ... });
const input = root.querySelector('input[type="hidden"]');
expect(input.getAttribute('name')).toBe('autocomplete-selector'); // ← no waitForChanges() before this
expect(input.getAttribute('value')).toBe('2');
```

`componentDidLoad` and `@Watch` effects run asynchronously after `newSpecPage` resolves. Assertions on rendered DOM state that depends on lifecycle effects must follow `await waitForChanges()`. The third test ("Should have selected value and option text in text field") correctly calls `waitForChanges()` before asserting on `bds-text-field` value — the second test should follow the same pattern.

**Action:** Add `await waitForChanges()` after `newSpecPage` in the second test before the hidden input assertions.

---

### T4. `bds-select.events.spec.ts` — Import path inconsistency, missing `bdsClear` test

**Import inconsistency:**

```typescript
// bds-select.events.spec.ts:7-8 — two separate import paths for the same test utilities
import { assertExists } from '@/utils/testing/helpers';
import { attachInternals } from '@/utils/testing/mocks/elementInternals';

// bds-select.basics.spec.ts:2 — consistent barrel import
import { assertExists, attachInternals, suppressConsoleWarn } from '@/utils';
```

`assertExists` and `attachInternals` are both re-exported from `@/utils`. Using the internal sub-paths couples the test to the internal directory layout and diverges from the pattern established in `basics.spec.ts`. Align to the barrel import `@/utils`.

**Missing `bdsClear` coverage:**

The original review flagged `bdsClear` as required. The event is referenced in the component but has no test. A test clicking the clear button (when the field has a value) and asserting the `bdsClear` event fires and `value` resets to `''` is needed.

**Action:** Consolidate imports to `@/utils`. Add a `bdsClear` emission test.

---

### T5. `bds-select.slots.spec.ts` — Structural check only, not a slot behavior test

```typescript
// bds-select.slots.spec.ts — asserting that what was put into HTML exists in HTML
const bdsSlotField = root.querySelector('bds-text-field[slot="field"]');
assertExists(bdsSlotField, 'Slot with name "field" should be rendered');

const bdsSlotList = root.querySelector('bds-list-menu[slot="list"]');
assertExists(bdsSlotList, 'Slot with name "list" should be rendered');
```

These assertions verify that elements placed into slots via the HTML fixture are present in the DOM — which is always true because the test itself put them there. A slot spec should verify that the component **uses** the slot content correctly: that `slot="field"` content renders in the trigger area and `slot="list"` content is moved into the popover.

The test does correctly check that `bds-list-menu` appears inside `bds-popover` after `waitForChanges()`, which is the valuable assertion here.

**Action:** Remove the trivially-true `assertExists` checks for `bds-text-field[slot="field"]` and `bds-list-menu[slot="list"]`. Keep the popover structure assertion. Add a test verifying that the `field` slot content is rendered in the expected position relative to the popover trigger.

---

### T6. `KeyboardController.spec.ts` — High quality, one pattern note

The three describe blocks cover key binding lifecycle, linear navigation, and grid navigation with good isolation. The `beforeAll` focus/scrollIntoView mock pattern is correct for JSDOM environments. The `dispatchKeyboard` helper is well-designed.

One observation: the `'warns when navigation is configured before attach'` test uses `jest.spyOn(console, 'warn')` without `suppressConsoleWarn()` at the file level. The spy implementation correctly silences the output (`mockImplementation(() => undefined)`), so no output leaks, but the pattern is inconsistent with the component spec files which use the `suppressConsoleWarn()` utility. Minor style inconsistency, not blocking.

The `grid navigation` tests cover edge cases well (null cells, irregular rows, closest-column vertical navigation). No findings.

---

### T7. `focus.spec.ts` — Correct isolation, one assertion gap

Unit tests for the focus strategy primitives (`initRovingTabindex`, `applyRovingTabindex`, `applyAriaActiveDescendant`, grid variants, `resolveCurrentIndex`). The `afterEach(() => { document.body.innerHTML = ''; })` cleanup prevents DOM bleed between tests.

**One gap:** the `applyRovingTabindex` test:

```typescript
// focus.spec.ts:62–70
items[0].setAttribute('tabindex', '0');
applyRovingTabindex(items, 2);
expect(items.map(item => item.getAttribute('tabindex'))).toEqual(['-1', null, '0']);
```

`items[1].getAttribute('tabindex')` is expected to be `null`. This is correct only if `applyRovingTabindex` does not touch items that were never `tabindex="0"`. The test passes today, but if the implementation ever initializes all items to `-1` before applying the active index (a common refactor), this assertion would break. Consider whether the intent is "items[1] is untouched" (assert `null`) or "items[1] is not the active item" (assert `!= '0'`). If the former, add a comment to make the intent clear; if the latter, use `.not.toBe('0')`.

---

### T8. `navigation.spec.ts` — Good isolation, key-name coupling is unavoidable

The file tests `setupLinearNavigation` and `setupGridNavigation` directly via mock `LinearNavigationAccess` / `GridNavigationAccess` objects. This is the right approach — it avoids spinning up a full `KeyboardController` for pure navigation logic.

The `registerHandler` / `isModifier` / `keyName` helper functions in this file replicate a subset of the key-name logic from inside `KeyboardController`. This is an acceptable duplication because the access interface's `register` callback is opaque to the navigation setup functions, and the test needs to inspect what keys were registered. No action required.

**Coverage gap:** The `setupLinearNavigation` test for `onNavigate` asserts that `onNavigate` is called with the next index and that `document.activeElement` is **not changed** (focus delegation is the caller's responsibility). This is the correct contract. However, the test does not cover what happens when `onNavigate` does call `applyFocus` via the controller — that path is covered in `KeyboardController.spec.ts` instead, which is the right separation.

---

### T9. `bds-list-menu-item.events.spec.ts` — JSDOM navigation test is fragile

```typescript
// bds-list-menu-item.events.spec.ts:101–110
it('Should redirect when href is clicked', async () => {
  ...
  root.click();
  await page.waitForChanges();
  expect(window.location.href).toBe('https://example.com/');
});
```

JSDOM normalizes URLs (appending `/`), which is why the assertion uses `'https://example.com/'`. However, JSDOM does not fully support navigation — `window.location.href` assignment may or may not fire page load events depending on the JSDOM version. This test is currently green but is tightly coupled to JSDOM behavior rather than the component's logic (which likely calls `window.location.href = this.href`).

The `new-tab` test correctly spies on `window.open` and is the preferable pattern. For the `href` test, spying on `window.location` assignment (or extracting the navigation call into a mockable method) would make this test more reliable.

**Action (non-blocking):** Refactor the `href` test to spy on `window.location` or extract the navigation to a mockable helper, matching the `new-tab` test pattern.

---

### T10. `bds-list-menu.basics.spec.ts` — Good coverage

Nine tests cover: default props, first-item activation, selected-item activation, option role propagation for listbox mode, disabled-item edge case, checkable propagation, select-controls rendering, empty-state rendering, and `waitForChanges()` after checkable propagation.

The test for `aria-multiselectable="false"` as a default is a good catch of the default ARIA state. No findings.

---

## Storybook Documentation Review

### `bds-select.stories.ts`

#### S1. `renderSelect` is missing `menu-role="listbox"` on `bds-list-menu` ❌

```typescript
// Current — Default and Searchable stories render without menu-role
<bds-list-menu slot="list">

// Required — combobox ARIA pattern requires the popup to have role="listbox"
<bds-list-menu slot="list" menu-role="listbox">
```

The `Default` and `Searchable` stories both use the shared `renderSelect` render function. Without `menu-role="listbox"`, the list menu does not get `role="listbox"`, which breaks the combobox ARIA contract established by `aria-haspopup="listbox"` on the input. The a11y spec (`bds-select.a11y.spec.ts:49`) explicitly asserts `listMenu.getAttribute('menu-role') === 'listbox'`. The stories should match what the a11y test verifies.

**Action:** Add `menu-role="listbox"` to `bds-list-menu` in `renderSelect`.

---

#### S2. Five stories hardcode `value="option2"` in the template, breaking the `value` Control ❌

```typescript
// Disabled story — args.value is ignored
render: args => html`
  <bds-select value="option2" name="combining-field-attrs">  // ← hardcoded
```

The same pattern appears in `Error`, `CombiningTextfieldAttributes`, `CombiningListMenuElements`, and `FormIntegration`. In each case the Storybook Controls panel shows a `value` input but changing it has no effect because the template uses a string literal instead of `${args.value}`. The contrast with the `Default` and `Searchable` stories (which correctly use `value=${args.value}`) makes this inconsistency visible to users.

**Action:** Replace all hardcoded `value="option2"` in custom render templates with `value=${args.value}`.

---

#### S3. `Error` story defaults `disabled: true` — misleading showcase ⚠️

```typescript
export const Error: Story = {
  args: {
    disabled: true,  // ← disabled + error is an edge case, not the canonical error story
    error: true,
  },
```

The `Error` story should demonstrate the error validation state on an interactive (enabled) field. Disabled + error is an unusual combination that should be a separate story if needed. The current default makes the primary error visual hard to understand.

**Action:** Set `disabled: false` in `Error` story args.

---

#### S4. `CombiningListMenuElements` uses `checkable` on a single item without `selection-mode="multiple"` ⚠️

```typescript
<bds-list-menu slot="list">   // ← no selection-mode="multiple"
  ...
  <bds-list-menu-item value="option6" checkable>  // ← isolated checkable
```

`bds-list-menu.basics.spec.ts` (T10) confirms that checkable rendering requires both `checkable="true"` and `selection-mode="multiple"` on the parent `bds-list-menu`. A single item with `checkable` but no parent coordination is undefined behavior and produces inconsistent rendering.

**Action:** Either add `selection-mode="multiple" checkable` to the parent `bds-list-menu`, or remove `checkable` from the single item.

---

#### S5. `meta.args` missing defaults for `disabled` and `error` ⚠️

```typescript
args: {
  name: '',
  value: '',
  searchable: false,
  // disabled and error are absent
},
```

Both props are declared in `argTypes` but have no default in `meta.args`. The Controls panel will show these as uncontrolled (no initial value) until a story sets them. Add `disabled: false, error: false` to `meta.args` for consistent baseline behavior.

---

#### S6. Story export name typo: `CombiningTexfieldAttributes` ⚠️

`CombiningTexfieldAttributes` is missing the `t` in `Textfield`. This becomes the Storybook navigation label and the URL slug.

**Action:** Rename to `CombiningTextfieldAttributes`.

---

#### S7. `FormIntegration` inline `<script>` is invisible in the Source panel ℹ️

Per project memory (`storybook-js-property-bindings-invisible-in-source-panel.md`), `<script>` tags inside Lit templates are not shown in Storybook's Source panel. Users viewing "Show code" for the FormIntegration story will see the HTML template but not the form submit handler. The MDX should include the handler in a `<script>` code block so it is visible in the docs.

---

### `bds-select.mdx`

#### D1. Code snippet uses `<bds-list-item>` — wrong element name ❌

```html
<!-- Current — bds-list-item does not exist in this design system -->
<bds-list-menu slot="list" menu-role="listbox">
    <bds-list-item value="1">Option 1</bds-list-item>
    <bds-list-item value="2">Option 2</bds-list-item>
    <bds-list-item value="3">Option 3</bds-list-item>
</bds-list-menu>

<!-- Required -->
<bds-list-menu slot="list" menu-role="listbox">
    <bds-list-menu-item value="1">Option 1</bds-list-menu-item>
    <bds-list-menu-item value="2">Option 2</bds-list-menu-item>
    <bds-list-menu-item value="3">Option 3</bds-list-menu-item>
</bds-list-menu>
```

`bds-list-item` is not a registered component in Boreal DS. Any developer who copies this snippet will get a non-functional component with no console error (custom elements silently degrade to `HTMLElement`). This is the most critical correctness issue in the docs.

---

#### D2. "When to use it" references non-existent component names ❌

```mdx
<!-- Line 54 — wrong component name -->
Use the `<bds-list-select>` always accompanied by the input component...

<!-- Line 57 — wrong component name -->
The col-select component is the standard choice for single-option dropdown selection.
```

Neither `bds-list-select` nor `col-select` exist in Boreal DS. These appear to be copy-paste artefacts from a different design system. Both should read `<bds-select>`.

---

#### D3. Accessibility section is an unfulfilled placeholder ⚠️

```mdx
{/* TODO: Add accessibility information */}
The Select component is designed with accessibility in mind...
```

The TODO comment is present in the published docs. The placeholder text does not mention any specific ARIA roles, keyboard interactions, or screen reader behavior. Given that `bds-select` implements the full ARIA combobox pattern (role=`combobox`, `aria-expanded`, `aria-controls`, `aria-haspopup="listbox"`, `aria-autocomplete`), this section should document:

- **Keyboard navigation:** Arrow keys open/navigate, Enter selects, Escape closes, Home/End jump
- **ARIA roles in use:** `combobox` on the input, `listbox` on the list, `option` on each item
- **Screen reader announcement:** what is read on open, on navigate, on select

---

#### D4. `FormIntegration` script handler not shown in the docs ⚠️

The `FormIntegration` story's `<script>` tag (form submit handler, `FormData` extraction) is invisible in the Source panel (per memory constraint S7). The MDX "How to use it" section should include a code block showing the JavaScript needed to wire up form submission:

```js
const form = document.querySelector('#example-form');
form.addEventListener('submit', e => {
  e.preventDefault();
  const formData = new FormData(form);
  console.log(Object.fromEntries(formData.entries()));
});
```

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

**M10. `value` prop missing `readonly` keyword** (`bds-select.tsx:31`)

`readonly` and `mutable: true` are orthogonal. Omitting `readonly` violates `stencil/props-must-be-readonly` (configured as `'error'`) — build-breaking.

**M11. `reflect: true` on `value` is unjustified** (`bds-select.tsx:31`)

No CSS attribute selector in `bds-select.scss` references `[value="..."]`. Per `stencil-prop-patterns.md`: add `reflect: true` only when referenced by a CSS attribute selector.

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

`addElementListener` registers DOM event listeners in `componentDidLoad`. No `disconnectedCallback` removes them. Fix: add `disconnectedCallback` calling `removeEventListener` on each registered handler (requires storing handler references).

**M2. Dead code: `visibleOptions === undefined` guard** (`bds-select.tsx:225`)

`querySelectorAll` always returns a `NodeList`, never `undefined`. Remove the `=== undefined` check.

**M3. Silent error discard in `loadValue`** (`bds-select.tsx:270`)

```typescript
.catch(() => {});
```

Add at minimum `console.warn` in development.

---

### Code Quality

**M4. Verbose boolean negation** (`bds-select.tsx:126`)

```typescript
updateElementProp(this.bdsField, "selectable", this.searchable ? false : true);
// → should be:
updateElementProp(this.bdsField, "selectable", !this.searchable);
```

**M5. Method name typo** (`bds-select.tsx:242`)

`resetChilds` → `resetChildren`. Update JSDoc and all three call sites.

**M6. Comment typos** (`bds-select.tsx:54, 142`)

- Line 54: `"Watch popver visible"` → `"Watch popover visible"`
- Line 142: `"sett value emitting event"` → `"set value emitting event"`

---

### Architecture / Fragility

**M7. Cross-component DOM piercing** (`bds-select.tsx:99–103`)

```typescript
return this.bdsField.querySelector("input");
```

Works because Stencil defaults to light DOM. If `bds-text-field` ever opts into shadow DOM, `querySelector` returns `null` and ARIA attributes are silently dropped. Known dependency — should be documented.

---

## Summary

| Category                                | Status                                           | Count                                               |
| --------------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| Automated: errors (in-scope)            | ⚠️ False positives — see notes                   | 1 real (missing-changeset)                          |
| Automated: warnings (in-scope)          | ✅ False positive (mutable value on non-FACE)    | —                                                   |
| Props / interface contract              | ❌ Blocking (build error)                        | 4 (M8, M9, M10, M11)                               |
| Manual: correctness                     | ❌ Should fix                                    | 3 (M1, M2, M3)                                     |
| Manual: code quality                    | ⚠️ Non-blocking                                  | 3 (M4, M5, M6)                                     |
| Manual: fragility                       | ℹ️ Informational                                 | 1 (M7)                                              |
| Test coverage — spec files present      | ✅ All four types present _(was ❌)_             | basics, a11y, events, slots                         |
| Test quality — bds-select               | ⚠️ Should fix before merge                       | 5 (T1, T2, T3, T4, T5)                             |
| Test quality — KeyboardController       | ✅ High quality                                  | 1 note (T6, non-blocking)                           |
| Test quality — focus/navigation utils   | ✅ Good isolation                                | 1 minor note (T7)                                   |
| Test quality — bds-list-menu*           | ⚠️ One fragile test (T9)                         | 1 (T9, non-blocking)                               |
| Stories (`bds-select.stories.ts`)       | ❌ Blocking correctness errors                   | 2 blocking (S1, S2) · 4 non-blocking (S3–S6) · 1 info (S7) |
| MDX (`bds-select.mdx`)                  | ❌ Blocking correctness errors                   | 2 blocking (D1, D2) · 2 should fix (D3, D4)        |

**Result: 21 component checks passed · 6 checklist failures (4 out-of-scope pre-existing) · 10 test files reviewed · 11 docs findings**

---

**Blocking before merge:**

1. Fix `@Prop()` declarations: add `implements ISelect`, use concrete primitives, add `readonly` to `value`, remove `reflect: true` (M8–M11) — M10 is a build-breaking ESLint error
2. Fix MDX code snippet: replace `<bds-list-item>` with `<bds-list-menu-item>` (D1)
3. Fix MDX prose: replace `<bds-list-select>` and `col-select` with `<bds-select>` (D2)
4. Add `menu-role="listbox"` to `bds-list-menu` in stories `renderSelect` function (S1)
5. Replace hardcoded `value="option2"` with `${args.value}` in all custom render templates (S2)
6. Add changeset (`pnpm changeset`)
7. Fix memory leak (M1) — `disconnectedCallback`

**Should fix (docs quality — before merge):**

8. Fill in Accessibility section — ARIA roles, keyboard navigation, screen reader behavior (D3)
9. Add `FormIntegration` script handler as a code block in MDX (D4)
10. Set `disabled: false` in `Error` story args (S3)
11. Fix `CombiningListMenuElements` isolated `checkable` item — add `selection-mode="multiple"` to parent (S4)

**Should fix (test quality — before merge):**

12. Delete `bds-select.spec.tsx` — duplicate render test with missing `BdsListMenuItem` registration (T2)
13. Add `await waitForChanges()` in basics "Should have input hidden with value" test (T3)
14. Consolidate event spec imports to `@/utils` barrel (T4)
15. Add `bdsClear` emission test to events spec (T4)
16. Remove trivially-true slot assertions; add structural slot behavior test (T5)
17. Add `aria-expanded="true"` (open state) and `searchable=true` ARIA tests (T1)

**Recommended (non-blocking):**

18. Add `disabled: false, error: false` to `meta.args` (S5)
19. Rename `CombiningTexfieldAttributes` → `CombiningTextfieldAttributes` (S6)
20. Remove dead `=== undefined` check (M2)
21. Add console.warn to `.catch` (M3)
22. Fix boolean negation, typos, method name (M4–M6)
23. Refactor `href` navigation test in `bds-list-menu-item.events.spec.ts` to spy on `window.location` (T9)
24. Clarify `applyRovingTabindex` test intent for `null` vs `!= '0'` tabindex assertion (T7)

---

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py) + manual enrichment — updated 2026-05-26 with unit testing review and Storybook documentation review_
