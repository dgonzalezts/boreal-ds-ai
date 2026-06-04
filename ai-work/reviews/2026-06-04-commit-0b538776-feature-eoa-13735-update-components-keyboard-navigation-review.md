# Boreal DS — Code Review Report

**Generated:** 2026-06-04
**Branch:** `feature/select-integration-text-and-tag-fields`
**Epics:** EOA-13735 (keyboard migration) · EOA-10544 (bds-dialog)
**Base ref:** `release/current`
**Commit:** `0b538776`

---

## Summary

|                     |                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------- |
| **Overall quality** | Good — the `KeyboardController` abstraction is well-designed and the migration is consistent |
| **Recommendation**  | **Hold for fixes** — 5 real issues must be addressed before merging                          |
| **Critical**        | 0                                                                                            |
| **Major**           | 3                                                                                            |
| **Minor**           | 4                                                                                            |
| **Nit**             | 3                                                                                            |
| **Static analysis** | 9 checklist failures (of which 7 are false positives — see annotations)                      |

---

## Automated Findings — Annotated

> Items marked ⚠️ **FALSE POSITIVE** are confirmed incorrect after reading the source. Items marked 🔴 **REAL** require action.

### Event naming — `readonly` parsed as event name (false positive × 3)

Lines `bds-list-menu-item.tsx:100`, `bds-list-menu.tsx:53`, `bds-list-menu.tsx:56` are all reported as `event-name-format` violations with event name `'readonly'`. This is a **parser bug in the static analyser**: it is reading the TypeScript `readonly` property modifier on the `@Event()` field declaration, not the event name. The actual event names are `bdsSelectItem`, `bdsChange`, and `bdsSelect` — all compliant.

**No action required.**

### Event naming — `valueChange` (false positive × 5)

`bds-toggle.tsx:104`, `bds-checkbox-button.tsx:75`, `bds-checkbox-card.tsx:86`, `bds-checkbox-group.tsx:123`, `bds-radio-group.tsx:124` are flagged for the event name `valueChange` not following `bds{Action}` format.

`valueChange` is the **intentional exception** to the naming convention. It is the reserved name for Vue `v-model` integration — the output target's `componentModels` config reads it as the `event` trigger for two-way binding. Renaming it would silently break Vue v-model on all form components. See project memory: _"Exception: `valueChange` is reserved for Vue v-model integration."_

**No action required.**

### `prop-missing-jsdoc` — bds-breadcrumb-item (false positive × 9) and bds-list-menu-item (false positive × 1)

The script reports 9 missing JSDoc blocks on `bds-breadcrumb-item.tsx` (lines 28, 35, 43, 51, 58, 65, 72, 79, 86) and 1 on `bds-list-menu-item.tsx:64`. Reading both files confirms JSDoc blocks are present immediately above every flagged `@Prop()`. This is a script parsing issue, not a real violation.

**No action required.**

---

### 🔴 REAL: `bool-prop-prefix` — `showCollapse` on `bds-breadcrumb-item`

**File:** `bds-breadcrumb-item.tsx:51`
**Rule:** `bool-prop-prefix` / `coding_standards.md` — Boolean props must use a plain adjective, no `is`/`has`/`show` prefix.

```ts
// ❌ Current
@Prop() readonly showCollapse: boolean = false;

// ✅ Fix — options:
@Prop() readonly collapse: boolean = false;      // renders the collapse indicator
@Prop() readonly collapsible: boolean = false;   // if semantics need to convey "can collapse"
```

The prop is marked `Internal prop controlled by the parent breadcrumb` in its JSDoc — it is not part of the public API. Regardless, the naming convention applies uniformly to all `@Prop()` declarations.

**Standard:** _"Props must match native HTML attribute style — single adjectives without a verb prefix."_ (common_antipatterns.md § FACE)

---

### 🔴 REAL: `face-native-constraint-on-input` — `required` on inner `<input>` in `bds-toggle`

**File:** `bds-toggle.tsx`
**Rule:** `face-native-constraint-on-input`

The inner `<input>` carries a native `required` attribute. Validity ownership must stay with `ElementInternals.setValidity()`. Native constraint attributes on inner inputs produce **double validation events**: one from the inner input's native validation and one from the component's `ElementInternals`. This can cause unexpected focus behaviour when a form calls `reportValidity()`.

**Fix:** Remove `required` from the inner `<input>`. Use `this.internals.setValidity({ valueMissing: true }, 'Required', ...)` in `updateValidity()` instead.

**Standard:** _"The custom element owns validity; inner inputs do not carry native constraint attrs."_ (coding_standards.md § FACE)
**Antipattern:** _"Causes double validation events and focus errors."_ (common_antipatterns.md § FACE)

---

### 🟡 REAL: `face-reset-no-validity` — `bds-checkbox-button` and `bds-checkbox-card`

**Files:** `bds-checkbox-button.tsx`, `bds-checkbox-card.tsx`
**Rule:** `face-reset-no-validity`

Both components define `formResetCallback` but do not call `updateValidity()` or `setValidity()` after restoring the default state. After a form reset the `valid` / `invalid` CSS pseudo-classes will be stale — they will reflect the pre-reset value instead of the reset value.

**Fix:** Call `this.updateValidity()` (or equivalent) at the end of `formResetCallback`.

**Standard:** _"`formResetCallback` and `formStateRestoreCallback` must call `updateValidity()` after restoring state."_ (coding_standards.md § FACE)

---

### 🟡 REAL: `prop-mutable-form-attr` — six components

**Files:** `bds-checkbox-button.tsx:58`, `bds-checkbox-card.tsx:71`, `bds-checkbox-group.tsx:80`, `bds-radio-button.tsx:24`, `bds-radio-card.tsx:51`, `bds-radio-group.tsx:83`, `bds-radio.tsx:24`

Multiple FACE components use `mutable: true` on the `disabled` prop instead of a `@State()` mirror. `mutable: true` on `disabled` creates two writers on the same reflected attribute — the component code and the browser's FACE lifecycle — which produces a Stencil compiler warning and can race with `formDisabledCallback`.

**Fix pattern:**

```ts
// ❌ Current
@Prop({ mutable: true }) disabled: boolean = false;

// ✅ Fix
@Prop({ reflect: true }) readonly disabled: boolean = false;
@State() private isDisabled: boolean = false;

@Watch('disabled')
handleDisabledChange(val: boolean) { this.isDisabled = val; }

formDisabledCallback(disabled: boolean) { this.isDisabled = disabled; }

componentWillLoad() { this.isDisabled = this.disabled; }
```

Then reference `this.isDisabled` everywhere in the render and event handlers.

**Note:** These are pre-existing violations not introduced by this PR, but they are present in touched files so they must be fixed before merge.

**Standard:** _"Do not use `mutable: true` on native form attributes. Use a `@State()` mirror."_ (coding_standards.md § TypeScript)

---

### 🟡 REAL: `getter-get-prefix` — `bds-button` and `bds-tooltip`

**Files:** `bds-button.tsx:218`, `bds-tooltip.tsx:104`

Both files have getter accessors with redundant `get` prefix:

- `bds-button.tsx:218` — `get getSomeValue()` → rename to `get someValue()`
- `bds-tooltip.tsx:104` — `get getPlacement()` → rename to `get placement()`

**Standard:** _"Getter accessors must not carry a `get` prefix."_ (coding_standards.md § Naming)

---

### ℹ️ Import order warnings (pre-existing)

The `import-order` warnings across many files (`bds-button`, `bds-button-group`, `bds-banner`, `bds-tag`, `bds-radio`, `bds-radio-card`, `bds-radio-button`, `bds-dialog`, `bds-tooltip`, `bds-list-menu`, `bds-list-menu-item`) appear to be pre-existing violations that are not introduced by this PR. They are captured here for tracking but should be addressed in a dedicated clean-up pass rather than blocking this feature.

---

### ℹ️ Barrel wildcard exports and `class-jsdoc-invalid-tags` (pre-existing)

`mixins/index.ts` and `utils/index.ts` use `export * from`. `bds-banner` and `bds-list-menu` use `@method` in class-level JSDoc. Pre-existing — track separately.

---

### ℹ️ Missing changeset

No changeset file exists for this PR. A changeset is required for version bumping before release.

---

## Manual Review — KeyboardController & Keyboard Navigation

### MAJOR-1: `initialActiveSelector` can resolve to a disabled item

**File:** `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/linear-navigation.ts:170`
**Severity:** major

```ts
// current
const initialIndex =
  initial !== -1
    ? initial
    : strategyType === FOCUS_STRATEGY.ROVING_TABINDEX
      ? 0
      : -1;
```

When `initial === -1` (no pre-selected item and `initialActiveSelector` matched nothing), the roving-tabindex strategy always falls back to index 0. If the first item in the list is disabled — which is valid in, e.g., `bds-radio-group` when the user disables the first option — `tabindex="0"` is assigned to a disabled element. Tab-cycling will land on a disabled, non-interactive element.

**Fix:** Resolve the initial index to the first _enabled_ item when the fallback is needed:

```ts
const initialIndex =
  initial !== -1
    ? initial
    : strategyType === FOCUS_STRATEGY.ROVING_TABINDEX
      ? items.findIndex((el) => !el.hasAttribute("disabled")) // first enabled
      : -1;
```

---

### MAJOR-2: `bds-dialog` JSDoc — `closable` description is inverted

**File:** `packages/boreal-web-components/src/components/overlays/bds-dialog/bds-dialog.tsx:105`
**Severity:** major (documentation accuracy, feeds `custom-elements.json`)

```ts
/** Hide the close button in the header. */  // ❌ wrong — closable=false means hidden
@Prop() readonly closable: IDialog['closable'] = false;

/** Show the close button in the header. */  // ✅ correct
```

The prop default is `false` (no close button). Setting `closable=true` shows the button. The current JSDoc says "Hide" which is the opposite. This ships to `custom-elements.json` and the framework wrappers.

---

### MAJOR-3: Missing unit tests for `bds-dialog` Tab-trap and `bds-list-menu` arrow navigation

**Severity:** major (test coverage gap)

#### bds-dialog Tab-trap — no unit tests

`bds-dialog.__test__/bds-dialog.behavior.spec.ts` tests Escape-key handling and backdrop click, but contains **zero Tab-trap tests**. The following scenarios are unverified by automated tests:

| Scenario                                     | What to assert                                               |
| -------------------------------------------- | ------------------------------------------------------------ |
| Tab at last focusable element wraps to first | Focus moves to `items[0]`                                    |
| Shift+Tab at first element wraps to last     | Focus moves to `items[last]`                                 |
| Hidden element excluded from trap cycle      | A `[hidden]` button inside the dialog is not in `getItems()` |
| `display: none` element excluded             | Same as above for `display: none`                            |

#### bds-list-menu keyboard navigation — no spec file

There is no keyboard spec file for `bds-list-menu`. The `:not([hidden])` hidden-item-skip logic and ArrowDown/ArrowUp navigation are only verified by a manual `index.html` example (added in commit `b0bcfb31`). A dedicated `bds-list-menu.keyboard.spec.ts` is needed, mirroring the structure of `bds-radio-group.keyboard.spec.ts`.

Minimum coverage required:

- ArrowDown moves focus to the next enabled item
- ArrowUp moves focus to the previous enabled item
- Hidden items (`:not([hidden])`) are skipped during navigation
- `Home` moves to the first item, `End` to the last
- `Enter`/`Space` triggers item activation (click)

---

### MINOR-1: `setFocusTrap` focusable selector is incomplete

**File:** `packages/boreal-web-components/src/utils/a11y/keyboard/KeyboardController.ts:664-671`
**Severity:** minor (a11y gap — affects future components, not current usage)

```ts
const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(", ");
```

Missing from the ARIA APG focusable-elements list:

- `[contenteditable]:not([contenteditable="false"])` — rich-text editors
- `details > summary:first-of-type` — native disclosure widget
- `audio[controls]`, `video[controls]`

For the current dialog usage (action buttons and form inputs) this is not a blocking issue. Add these for completeness — or document the intentional exclusions.

---

### MINOR-2: `aria-activedescendant` auto-generated IDs are unstable

**File:** `packages/boreal-web-components/src/utils/a11y/keyboard/focus/aria-activedescendant.ts`
**Severity:** minor

When items lack explicit `id` attributes, the function generates IDs with `Math.random()`. Each call to `applyAriaActiveDescendant()` regenerates IDs for items that still lack them. If the items array is recreated (e.g., after a filter/sort), old IDs become stale — `aria-activedescendant` may point to a non-existent element, causing screen readers to announce nothing.

**Fix:** Cache the generated ID on the element permanently so that subsequent calls for the same element reuse the same ID:

```ts
if (!item.id)
  item.id = `${prefix}-${i}-${Math.random().toString(36).slice(2, 7)}`;
```

The fix is simply moving from `item.id = ...` (always overwrite) to `if (!item.id) item.id = ...` (assign once). This is a one-character change and is the correct pattern.

---

### MINOR-3: `bds-dialog` missing `aria-describedby` for body slot

**File:** `packages/boreal-web-components/src/components/overlays/bds-dialog/bds-dialog.tsx`
**Severity:** minor (a11y)

`aria-labelledby="bds-dialog-title"` is correctly set on the `<dialog>` element when `titleDialog` is provided. However, there is no `aria-describedby` linking the dialog body slot to the `<dialog>` element. Screen readers announce the label immediately on focus but do not automatically read the description without `aria-describedby`.

**Suggested fix:** Add a wrapping `id` to the body div and reference it:

```tsx
<div id="bds-dialog-body" class={`bds-dialog__body ...`}>
  <slot></slot>
</div>
```

```tsx
<dialog aria-modal="true" aria-describedby="bds-dialog-body" ...>
```

---

### NIT-1: `bds-tooltip` — `mouseleave` still uses `e.target` instead of `e.relatedTarget`

**File:** `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:184`
**Severity:** nit (pre-existing bug, not introduced by this PR)

```ts
// ❌ current — e.target is the trigger, never the floating element
trigger.addEventListener("mouseleave", (e: MouseEvent) =>
  this.hide(e.target as HTMLElement),
);

// ✅ fix
trigger.addEventListener("mouseleave", (e: MouseEvent) =>
  this.hide(e.relatedTarget as HTMLElement),
);
```

This file was touched in this PR (import-order changes). `stayOnHover` is silently non-functional because `validateHide()` tests whether the pointer is _moving into_ the floating content — but `e.target` is always the trigger itself, so the check always fails. Documented in project memory as unfixed since 2026-04-13. Opportunistic fix recommended.

---

### NIT-2: `bds-tooltip` — `!x || false` antipattern in `canShowArrow`

**File:** `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx:102`
**Severity:** nit

```ts
// ❌ current — || false is an unreachable branch
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow || false;
}

// ✅ fix
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow;
}
```

---

### NIT-3: `bds-dialog` — Escape binding always registered regardless of `escapeClose`

**File:** `packages/boreal-web-components/src/components/overlays/bds-dialog/bds-dialog.tsx:130-139`
**Severity:** nit

The Escape key binding is unconditionally registered in `componentDidLoad()`. The early-return guard `if (!this.escapeClose) return;` is inside the handler, so the listener always fires and immediately returns. Functionally correct, but if `escapeClose` is reactive (changed at runtime), the handler will always check the current prop value — which is actually the right behaviour for a reactive prop. The nit is just the slight overhead of a no-op handler invocation on every Escape key press.

---

## Memory-Guided Review

### `mouseleave` / `e.relatedTarget` vs `e.target`

**Topic:** `mouseleave-relatedtarget-vs-target.md`

`bds-tooltip.tsx` is in this PR's diff (import-order fixes). The `mouseleave` bug documented in memory is **still present** at line 184. See NIT-1 above for details and the one-line fix.

**Status:** Bug confirmed unfixed, opportunistic fix recommended.

---

### Disabled prop — `mutable: true` on FACE form attrs

**Topic:** `stencil-prop-patterns.md`

Multiple form components (`bds-checkbox-button`, `bds-checkbox-card`, `bds-checkbox-group`, `bds-radio-button`, `bds-radio-card`, `bds-radio-group`, `bds-radio`) in this PR's diff use `mutable: true` on `disabled`. The standard pattern requires a `@State() private isDisabled` mirror to avoid compiler warnings and FACE lifecycle races. See Static Analysis → REAL findings above.

**Status:** Confirmed pre-existing, must be fixed before merge per project standards.

---

### Event naming — `valueChange` exception

**Topic:** `MEMORY.md` — Component API Conventions

All `valueChange` events flagged by the static analyser are intentional. `valueChange` is the reserved Vue v-model integration event. The project memory explicitly documents this exception. The static analyser has no awareness of it — this is a known limitation.

**Status:** No action required. Consider adding an analyser suppress-comment or updating the analyser's exception list.

---

### Custom event naming — `bdsSelectItem` and `bdsSelect`

**Topic:** `MEMORY.md` — Custom event naming rule

`bdsSelectItem` (bds-list-menu-item) and `bdsSelect` (bds-list-menu) both follow the `bds{Action}` format correctly. The static analyser's `readonly` false positive does not reflect a real naming issue here.

**Status:** No action required.

---

### FACE — `formResetCallback` without validity

**Topic:** `stencil-face-constraint-validation-pattern.md`

Confirmed: `bds-checkbox-button` and `bds-checkbox-card` both have `formResetCallback` implementations that restore the checked state but do not re-sync validity. After a form reset the `:valid`/`:invalid` pseudo-classes will be wrong until the user interacts with the component. See REAL finding above.

**Status:** Must fix before merge.

---

### Composite component event boundary

**Topic:** `stencil-composite-light-dom-event-boundary.md`

`bds-list-menu` uses `@Listen('bdsSelectItem')` to intercept child item clicks. The child item's `bdsSelectItem` event has `bubbles: true, composed: true`. The parent re-emits `bdsChange` and `bdsSelect`. This is the correct pattern for composite components — the parent listens and re-emits. No `stopPropagation()` gap detected.

**Status:** No issues found.

---

## Memory topic files consulted

- `mouseleave-relatedtarget-vs-target.md`
- `stencil-prop-patterns.md`
- `stencil-face-constraint-validation-pattern.md`
- `stencil-form-control-interfaces.md`
- `stencil-composite-light-dom-event-boundary.md`
- `component-accessor-naming-conventions.md`
- `MEMORY.md` — Custom event naming rule (valueChange exception)

---

## Positive Observations

1. **`KeyboardController` lifecycle management is exemplary.** A single `AbortController` cleans up every event listener. No component needs `removeEventListener`. The `detach()` call in `disconnectedCallback()` is consistently applied across all 9+ migrated components — no missing pairs found.

2. **Deterministic chord normalisation.** `createCombinationKey` sorts modifiers in declaration order and regular keys alphabetically. `'ctrl+shift+s'` and `'shift+ctrl+s'` produce the same lookup key. This is a subtle but important correctness property that prevents duplicate-binding bugs.

3. **`initRovingTabindex` vs `applyRovingTabindex` distinction is correct.** The initialisation path sets `tabindex` attributes without calling `.focus()`, preventing focus theft on page load. This is the exact ARIA APG recommendation for composite widget initialisation.

4. **Auto-repeat throttling is well-calibrated.** Arrow key repeat is throttled to ~10 ops/second (100 ms), Tab-trap repeat to ~6.7 ops/second (150 ms). Both prevent the visual "blur" of focus cycling too fast while remaining responsive.

5. **`bds-radio-group.setLinearNavigation` correctly implements the ARIA radiogroup pattern.** Selection follows focus (`onNavigate` updates `this.value` immediately) — matching the APG recommendation that in a radiogroup, arrow keys both move focus _and_ select the item simultaneously.

6. **815 lines of unit tests for the keyboard utility.** The `KeyboardController`, navigation, and focus spec files collectively cover the utility's core contract. Component tests can rely on the utility being correct and focus on integration concerns.

7. **`bds-list-menu` hidden-item skip logic is clean.** The `:not([hidden])` selector in the `querySelectorAll` query of `_setupKeyboard()` correctly excludes hidden items at query time — no manual visibility checks needed in the handler.

8. **`bds-dialog` focus save/restore pattern is correct.** `saveFocus()` in `onBeforeShow` and `restoreFocus()` in `onAfterHide` follow the ARIA modal dialog pattern. The `<dialog>` native element is used (not a `<div role="dialog">`), which provides correct platform semantics.

---

## Action Items Summary

| #   | Severity | File                                               | Action                                                  |
| --- | -------- | -------------------------------------------------- | ------------------------------------------------------- | --- | ------------------------ |
| 1   | major    | `linear-navigation.ts:170`                         | Fix initialActive fallback to skip disabled items       |
| 2   | major    | `bds-dialog.tsx:105`                               | Fix `closable` JSDoc from "Hide" to "Show"              |
| 3   | major    | `bds-dialog.behavior.spec.ts`                      | Add Tab-trap boundary tests                             |
| 3b  | major    | `bds-list-menu/`                                   | Add `bds-list-menu.keyboard.spec.ts`                    |
| 4   | minor    | `bds-breadcrumb-item.tsx:51`                       | Rename `showCollapse` → `collapse`                      |
| 5   | minor    | `bds-toggle.tsx`                                   | Remove `required` from inner `<input>`                  |
| 6   | minor    | `bds-checkbox-button.tsx`, `bds-checkbox-card.tsx` | Add `updateValidity()` to `formResetCallback`           |
| 7   | minor    | `bds-checkbox-*`, `bds-radio-*` (7 files)          | Replace `mutable: true` disabled with `@State()` mirror |
| 8   | nit      | `bds-tooltip.tsx:184`                              | Fix `e.target` → `e.relatedTarget` (opportunistic)      |
| 9   | nit      | `bds-tooltip.tsx:102`                              | Remove `                                                |     | false`from`canShowArrow` |
| 10  | nit      | `bds-button.tsx:218`, `bds-tooltip.tsx:104`        | Remove `get` prefix from getter names                   |

---

**Result: 15 passed · 9 failed (7 false positives, 2 real static findings) · 10 manual findings**

_Automated analysis by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
_Reference enrichment and memory-guided review by Claude Code_
