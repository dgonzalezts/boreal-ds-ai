# Boreal DS — Code Review Report

**Generated:** 2026-04-28T16:49:16
**Base ref:** `release/current`
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-tag/bds-tag.tsx:4`
  - **Standard:** Imports must follow framework → `@/services` → `@/mixins` → `@/utils` → local/relative order. The `./types` import at line 3 appears before the `@/utils` import at line 4 — they must be swapped.
  - **Antipattern:** Wrong import order — framework imports must come first, then internal aliases, then local/relative. Dependencies must flow downward.
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/feedback/bds-tag/types/index.ts:1`
  - **Standard:** Prefer named re-exports (`export { X } from './X'`) over wildcard re-exports (`export * from './X'`) in barrel files. Named exports give bundlers explicit edges to follow during tree-shaking.
  - **Antipattern:** Wildcard re-exports in barrels — `export * from './X'` hides module edges from the bundler and can prevent tree-shaking. Applies to all three lines in `types/index.ts`.
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/feedback/bds-tag/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/feedback/bds-tag/types/index.ts:3`
- 🟡 **[missing-tests]** ~~Component TSX files changed but no test files found in the diff.~~ _False positive — 5 spec files are present and all pass (551/551). Script did not detect them because they are in a sibling branch (`test/EOA-12332_tag`)._
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
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/\*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

### 1. Prop Validation — `@Watch` Decorator Missing on `checkPropValues` ❌

**Topic file:** `feedback_prop_validation_pattern.md`

The automated checklist passed this item as ✅ — **this is a false positive.** The `color` prop is an enum-typed `@Prop()` validated by `validatePropValue`, and `componentWillLoad()` correctly calls `checkPropValues()`. However, the required `@Watch('color')` decorator is absent from `checkPropValues`:

```tsx
// Current — missing @Watch
componentWillLoad() {
  this.checkPropValues();
}

private checkPropValues() {
  validatePropValue(Object.values(TAG_COLORS), TAG_COLORS.GRAY, this.el as HTMLElement, 'color');
}
```

Without `@Watch('color')`, invalid values set dynamically after mount (e.g. `tag.color = 'invalid'`) are silently accepted and rendered. **Required fix:**

```tsx
@Watch('color')
checkPropValues(): void {
  validatePropValue(Object.values(TAG_COLORS), TAG_COLORS.GRAY, this.el as HTMLElement, 'color');
}

componentWillLoad(): void {
  this.checkPropValues();
}
```

---

### 2. Hard-Coded Color Values in SCSS ❌

**Topic file:** `stencil-light-dom-host-vs-class.md` / token standards

The SCSS file uses `rgba(19, 19, 22, 0.15)` as a raw color value in multiple places:

```scss
&:hover:not(.bds-tag--selected):not(.bds-tag--disabled) {
  @include bds-hover-shadow(rgba(19, 19, 22, 0.15)); // hard-coded
}
&--selected {
  @include bds-focus-ring(
    $boreal-stroke-focus,
    $boreal-ui-inverse,
    rgba(19, 19, 22, 0.15)
  ); // hard-coded
}
// close button :hover, :focus, :active also use rgba(19, 19, 22, 0.15)
```

Components must reference only Usage/Semantic design tokens — never hard-coded `rgba()`/`hex` values. This value should be a `$boreal-*` SCSS variable. Check whether a shadow overlay token exists in `boreal-styleguidelines`; if not, one must be created before merging.

---

### 3. Named Slot Undocumented in Class JSDoc ⚠️

**Topic file:** JSDoc / CEM generation rules

The class-level JSDoc has two `@slot` entries but neither names the `icon` slot correctly:

```tsx
/**
 * @slot - Default slot for custom text content after the icon.
 * @slot - Icon slot for icon content before the text.   ← missing slot name
 */
```

The CEM analyzer reads the slot name from the `@slot` tag syntax: `@slot {name} - description`. The second entry should be:

```tsx
 * @slot icon - Icon slot for icon content before the text.
```

Without the name, the `icon` slot will not appear in the generated `custom-elements.json` manifest, which breaks Storybook ArgTypes and React/Vue wrapper docs.

---

### 4. ARIA Role Gap When `multiselect=false` and `readonly=false` ⚠️

**Topic file:** Accessibility standards

The `role` attribute logic leaves the host element without a semantic role in the default interactive state (`multiselect=false, readonly=false`):

```tsx
role={this.multiselect ? 'option' : this.readonly ? 'button' : undefined}
```

When both props are at their defaults, the host element is:

- Focusable (`tabIndex=0`)
- Clickable (fires `bdsSelect` via `onClick`)
- Has a keyboard event handler
- But has **no ARIA role**

A focusable, interactive element without a role is an accessibility violation. Consider `role="group"` (containing both the label and the dismiss button) or align with the WAI-ARIA chips pattern used by your multiselect parent.

---

### 5. MDX Documents `aria-readonly` But Component Does Not Implement It ⚠️

**Topic file:** Accessibility / documentation accuracy

The MDX accessibility section states:

> _"Disabled and Read Only states are communicated using `aria-disabled` and `aria-readonly`."_

The component sets `aria-disabled` correctly but never sets `aria-readonly`. The `readonly` prop only removes the close button from the DOM — no ARIA attribute is applied. Either implement `aria-readonly="true"` on the host when `readonly=true`, or correct the MDX to accurately describe what is actually implemented.

---

### Memory Topic Files Consulted

- `feedback_prop_validation_pattern.md` — prop validation pattern with `@Watch` + `componentWillLoad()`
- `feedback_event_naming.md` — `bds{Action}` event naming convention (no issues found)
- `stencil-prop-patterns.md` — `mutable: true` and `readonly` rules (no issues found for `selected`)
- `component-accessor-naming-conventions.md` — getter naming and boolean expressions (no issues found)
- `project_no_shadow_dom.md` — light DOM assumptions (no issues found)
- `stencil-light-dom-host-vs-class.md` — SCSS token and selector patterns (hard-coded color found)

---

**Result: 26 passed · 1 failed (automated) + 5 findings from memory-guided review (1 critical, 4 advisory) + 3 test quality findings (1 critical gap, 2 advisory)**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_

---

## Unit Test Review

**Test run:** 551/551 passed across all 5 spec files.

**Files reviewed:**

- `bds-tag.basics.spec.tsx` — 6 tests
- `bds-tag-events.spec.tsx` — 11 tests
- `bds-tag.a11y.spec.tsx` — 14 tests
- `bds-tag.variants.spec.tsx` — 8 tests (table-driven)
- `bds-tag.slots.spec.tsx` — 2 tests

### What passes well

- `waitForChanges()` is called correctly after every interaction before assertions.
- `assertExists()` is used consistently instead of bare `toBeTruthy()`, providing descriptive failure messages.
- Event payload shape is verified (id, el, selected) — not just that the event fires.
- All 8 color variants are covered by a table-driven test in `variants.spec.tsx`.
- The guard logic for `disabled` and `readonly` is tested for both click and keyboard paths.
- ARIA attribute presence and absence is explicitly verified for all relevant states.

---

### T1. No test for `multiselect` selected-state toggling ❌

**File:** `bds-tag-events.spec.tsx`

`handleSelection` toggles `this.selected = !this.selected` when `multiselect=true` and emits the new value in the payload. No test verifies that:

1. `selected` flips from `false` → `true` after a click when `multiselect=true`.
2. The emitted `bdsSelect` payload carries the updated `selected` value.

This is the only behaviorally non-trivial branch left untested. Required:

```tsx
it("should toggle selected state on click when multiselect", async () => {
  const page = await newSpecPage({
    components: [BdsTag],
    html: `<bds-tag multiselect="true">Option</bds-tag>`,
  });

  const root = page.root;
  assertExists(root, "Tag container should exist");

  const spy = jest.fn();
  root.addEventListener("bdsSelect", spy);

  root.click();
  await page.waitForChanges();

  expect(root.getAttribute("aria-selected")).toBe("true");
  expect(spy).toHaveBeenCalledWith(
    expect.objectContaining({
      detail: expect.objectContaining({ selected: true }),
    }),
  );
});
```

---

### T2. No test for invalid `color` fallback via `validatePropValue` ❌

**File:** `bds-tag.variants.spec.tsx`

`componentWillLoad()` calls `validatePropValue` to reset invalid `color` values to `gray`. No test verifies this guard fires. This gap compounds with the missing `@Watch('color')` finding (Memory §1): even the initial-load path is never regression-tested.

Required:

```tsx
it("should fallback to gray color when an invalid color is provided", async () => {
  const page = await newSpecPage({
    components: [BdsTag],
    html: `<bds-tag color="invalid"></bds-tag>`,
  });

  const root = page.root as HTMLElement;
  expect(root.classList.contains("bds-tag--gray")).toBe(true);
  expect(root.classList.contains("bds-tag--invalid")).toBe(false);
});
```

---

### T3. "should have unique custom id" may be a false-positive ⚠️

**File:** `bds-tag.basics.spec.tsx`

The test passes `id="id-test"` in HTML and then asserts `getAttribute('id') === 'id-test'`. However, the component always generates its own internal `_id` via `createId('bds-tag')` and renders `<Host id={this._id}>` — it makes no provision for an externally supplied id.

If Stencil's test environment applies Host props before the HTML attribute is overwritten, the test would fail. If the test environment does not replay Host prop overrides onto pre-set HTML attributes, it passes vacuously — asserting browser behavior rather than component behavior.

Verify the intended behavior and either:

- Remove the test (component always owns its own id), or
- Add an `id` prop to the component that consumers can use to override the generated id, and test that path explicitly.
