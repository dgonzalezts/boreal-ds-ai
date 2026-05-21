---
status: done
---

# bds-radio-button Implementation Plan

**Prerequisite:** `bds-radio-group` must already be implemented (see `EOA-12334-bds-radio-and-radio-group.md`). This plan adds `bds-radio-button` as a new leaf component and extends the group to handle it.

**Scope:** `bds-radio-button` (leaf component) + extension of `bds-radio-group` to support `type="radiobutton"`.

**Why a separate component (not a CSS-only variant of bds-radio):**

1. **DOM difference** — `bds-radio-button` has no circle indicator in the DOM; the absence is structural, not just CSS-hidden.
2. **Different API** — carries a `label` prop and an `icon` named slot that are meaningless on `bds-radio`.
3. **Segmented control CSS** — the adjacent-sibling layout requires a dedicated tag name; CSS combinators cannot target a subset of elements sharing the same tag name.

**Tech Stack:** Stencil, TypeScript, SCSS, `boreal-styleguidelines` design tokens, Storybook (Lit HTML stories + MDX docs), Jest / `@stencil/core/testing`.

---

## File tree created / modified

```
packages/boreal-web-components/src/components/forms/
  bds-radio-button/                         ← NEW
    bds-radio-button.tsx
    bds-radio-button.scss
    __test__/
      bds-radio-button.basics.spec.ts
      bds-radio-button.a11y.spec.ts
      bds-radio-button.events.spec.ts
    types/
      IRadioButton.ts
  bds-radio-group/
    bds-radio-group.tsx                     ← MODIFIED
    bds-radio-group.scss                    ← MODIFIED
    types/
      IRadioGroup.ts                        ← MODIFIED (type union extended)
    __test__/
      bds-radio-group.basics.spec.ts        ← MODIFIED (6 new type=radiobutton tests)
      bds-radio-group.events.spec.ts        ← MODIFIED (5 new bds-radio-button tests)
      bds-radio-group.keyboard.spec.ts      ← MODIFIED (5 new bds-radio-button tests)
  helpers/bds-divider/
    bds-divider.scss                        ← MODIFIED (--bds-divider-color custom property)
titles-text/bds-typography/utils/
  bds-typography-utils.ts                   ← MODIFIED (label variant: added COMPONENT_STATES.ERROR)

apps/boreal-docs/src/stories/forms/bds-radio-group/
  bds-radio-group.stories.ts               ← TODO (Task 6)
  bds-radio-group.mdx                      ← TODO (Task 7)
  _variants/
    RadioCircular.mdx                      ← TODO (Task 7)
    RadioButton.mdx                        ← TODO (Task 7)
```

**Note:** `bds-radio-button` has **no standalone Storybook entry** — it is a private building block. All documentation lives inside `bds-radio-group` stories and MDX.

---

## ✅ Task 1: IRadioButton.ts + IRadioGroup.ts

### `bds-radio-button/types/IRadioButton.ts` (created)

```typescript
export interface RadioButtonChangeDetail {
  checked: boolean;
  value: string;
}

export interface IRadioButton {
  checked: boolean;
  disabled: boolean;
  error: boolean;
  value: string;
  name: string;
  label: string;
  info: string;
  bdsChange: EventEmitter<RadioButtonChangeDetail>;
}
```

**Key decision:** `showDivider` and `isFirst` are NOT part of the interface. Dividers are injected at the parent level; the leaf has zero responsibility for them.

### `bds-radio-group/types/IRadioGroup.ts` (modified)

Extended `type` union: `'radio' | 'radiobutton'`.

---

## ✅ Tasks 2a–2d: bds-radio-button component

**Final component** (`bds-radio-button.tsx`):

- `componentDidLoad` stamps `role="radio"`, `aria-checked`, `tabindex="-1"` on the host
- `select()` guards disabled/already-checked; sets `checked`, updates `aria-checked`, emits `bdsChange`
- `handleClick` / `handleKeyDown` (Space key) delegate to `select()`
- `render()` includes: host CSS classes (`--checked`, `--error`, `--disabled`), hidden native `<input type="radio" aria-hidden="true">`, icon slot container, `<bds-typography>` for label
- **`state` prop forwarded to `bds-typography`**: `state={this.error ? 'error' : this.disabled ? 'disabled' : 'default'}` — required because typography's own scoped CSS overrides CSS `color` inheritance; the `state` prop is the only reliable way to control text color
- **No `showDivider` / `isFirst` props** — removed entirely; dividers are parent-injected

### Additional change: `bds-typography-utils.ts`

Added `COMPONENT_STATES.ERROR` to the `label` variant's allowed states:

```typescript
label: {
  states: [COMPONENT_STATES.DISABLED, COMPONENT_STATES.ERROR],
  required: true,
  canUseTooltip: true,
},
```

This was required to allow `state="error"` on `<bds-typography variant="label">` inside `bds-radio-button`.

---

## ✅ Task 3: Unit tests

### `bds-radio-button.basics.spec.ts`

Covers: host rendering, CSS classes (`--checked`, `--disabled`, `--error`), hidden native input, icon slot container, label rendering via `bds-typography`, info tooltip, `state` prop forwarded to `bds-typography` (error / disabled / default).

**Tests removed** (props were removed from component): `showDivider=true/false`, `isFirst`.

**Tests added**: `state="error"`, `state="disabled"`, `state="default"` forwarding to `bds-typography`.

### `bds-radio-button.a11y.spec.ts`

Covers: `role="radio"`, `aria-checked="false"` default, `aria-checked="true"` after click, `tabindex="-1"`, `aria-hidden="true"` on internal input.

### `bds-radio-button.events.spec.ts`

Covers: `bdsChange` emission on click with correct payload, no emission when already checked, no emission when disabled, emission on Space key, no emission on other keys, `checked` property set to `true` after click.

### `bds-radio-group.basics.spec.ts` additions

6 new tests:
- `should reflect type="radiobutton" as an attribute`
- `should not inject bds-divider elements when type is radio`
- `should inject bds-divider elements between bds-radio-button children when type is radiobutton` (expects 2 dividers for 3 buttons)
- `should inject vertical dividers for horizontal radiobutton groups`
- `should inject horizontal dividers for vertical radiobutton groups`
- `should propagate error prop to bds-radio-button children on load`

### `bds-radio-group.events.spec.ts` additions

5 new tests:
- `should emit bdsChange from the group when a bds-radio-button child fires bdsChange`
- `should emit valueChange when a bds-radio-button child fires bdsChange`
- `should uncheck other bds-radio-buttons when one fires bdsChange`
- `should propagate error state to bds-radio-button children when error prop changes`
- `should propagate disabled state to bds-radio-button children when disabled prop changes`

### `bds-radio-group.keyboard.spec.ts` additions

5 new tests with `bds-radio-button` children (ArrowRight, ArrowLeft, wrap, skip-disabled, tabindex update).

---

## ✅ Task 4: Extend bds-radio-group to handle bds-radio-button

### Changes applied to `bds-radio-group.tsx`

**Type alias:**
```typescript
type LeafElement = HTMLBdsRadioElement | HTMLBdsRadioButtonElement;
```

**LEAF_TAGS constant:**
```typescript
const LEAF_TAGS = ['BDS-RADIO', 'BDS-RADIO-BUTTON'];
```

**radioElements getter:**
```typescript
return Array.from(this.el.querySelectorAll<LeafElement>('bds-radio, bds-radio-button'));
```

**type prop:**
```typescript
@Prop({ reflect: true }) readonly type: 'radio' | 'radiobutton' = 'radio';
```

**componentWillLoad** — queries both `bds-radio[checked]` and `bds-radio-button[checked]` to resolve initial value.

**Divider injection (parent-level, orientation-aware):**

```typescript
private _buttonCount: number = 0;

private insertDividers(): void {
  this.el.querySelectorAll('bds-divider[data-injected]').forEach(d => d.remove());
  if (this.type !== 'radiobutton') return;

  const dividerOrientation = this.orientation === 'horizontal' ? 'vertical' : 'horizontal';
  const buttons = this.radioElements.filter(
    (el): el is HTMLBdsRadioButtonElement => el.tagName === 'BDS-RADIO-BUTTON',
  );
  buttons.forEach((btn, i) => {
    if (i === 0) return;
    const divider = document.createElement('bds-divider');
    divider.setAttribute('orientation', dividerOrientation);
    divider.setAttribute('data-injected', '');
    btn.parentNode?.insertBefore(divider, btn);
  });
}

private updateLayoutCount() {
  const count = this.radioElements.length;
  this.el.style.setProperty('--layout-count', `${count}`);
  if (count !== this._buttonCount) {
    this._buttonCount = count;
    this.insertDividers();
  }
}
```

**Key implementation decisions:**

- **`insertBefore` not `before()`** — JSDOM (Stencil's test runner) does not support `ChildNode.before()`; `parentNode.insertBefore(node, ref)` is universally supported and identical in behaviour.
- **`this.radioElements.filter()` not `:scope > bds-radio-button`** — Stencil scoped mode physically moves slot content inside `.bds-radio-group__options`, so `:scope >` returns 0 results on the host element. The proven `querySelectorAll` subtree approach works correctly.
- **`_buttonCount` loop guard** — `radioElements` only counts `bds-radio`/`bds-radio-button`, not injected `bds-divider` elements, so injecting dividers never changes the count and the `slotchange` loop is broken.

---

## ✅ Task 5: SCSS

### `bds-radio-button.scss` (actual implementation)

```scss
bds-radio-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: $boreal-spacing-2xs $boreal-spacing-s;
  border: 1px solid $boreal-stroke-default-light;
  border-radius: $boreal-radius-s;
  cursor: pointer;
  outline: none;
  background-color: transparent;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    color 0.2s ease;

  input[type='radio'] {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
    margin: 0;
    pointer-events: none;
  }

  &:hover:not(.--disabled) { border-color: $boreal-ui-success-dark; }
  &:focus-visible, &:focus { box-shadow: 0 0 0 2px $boreal-stroke-focus; outline: none; }

  &.--checked {
    border-color: $boreal-ui-success-base;
    background-color: $boreal-bg-primary-lighter;
    color: $boreal-ui-success-base;
    &:hover:not(.--disabled) { border-color: $boreal-ui-success-dark; color: $boreal-ui-success-dark; }
  }

  &.--error { border-color: $boreal-stroke-danger-base; }
  &.--disabled { cursor: not-allowed; pointer-events: none; color: $boreal-text-disabled; background-color: $boreal-bg-neutral; }

  .bds-radio-button__label {
    font-size: $boreal-typography-font-size-sm;
    font-weight: $boreal-typography-font-weight-regular;
    line-height: $boreal-typography-line-height-sm;
  }

  .bds-radio-button__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    &:empty { display: none; }
  }
}

bds-radio-group[type='radiobutton'] {
  bds-radio-button { border: none; border-radius: 0; }
}
```

### `bds-radio-group.scss` additions (actual implementation)

```scss
bds-radio-group[type='radiobutton'] {
  .bds-radio-group__options {
    display: inline-flex;
    gap: 0;
    padding: $boreal-spacing-3xs;
    border: 1px solid $boreal-stroke-default-light;
    background-color: $boreal-ui-inverse;
    border-radius: $boreal-radius-xs;
    overflow: hidden;
  }

  &[orientation='vertical'] .bds-radio-group__options { flex-direction: column; }

  &.--error .bds-radio-group__options { border-color: $boreal-stroke-danger-base; }

  &.--error bds-radio-button.--error { color: $boreal-stroke-danger-base; }

  &.--error bds-divider[data-injected] {
    --bds-divider-color: #{$boreal-stroke-danger-base};
  }
}
```

### `bds-divider.scss` modification

Changed `background-color` to use a CSS custom property so parent context can override divider color without coupling components:

```scss
.bds-divider {
  background-color: var(--bds-divider-color, #{$boreal-ui-default-lighter});
  ...
}
```

---

## ⬜ Task 6: Storybook stories

**File to modify:** `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts`

**No standalone `bds-radio-button` stories** — it is a private building block. All stories showing `bds-radio-button` must be inside the `bds-radio-group` story file, using `type="radiobutton"`.

Stories to add:

1. **RadioButton** — `type="radiobutton"`, horizontal segmented control with 3 `<bds-radio-button>` children, one pre-selected
2. **RadioButtonWithIcons** — same as above with icon slot filled on each button
3. **RadioButtonWithTooltips** — `type="radiobutton"` with `info` prop on individual buttons
4. **RadioButtonDisabled** — `type="radiobutton"` with `disabled` prop on the group
5. **RadioButtonError** — `type="radiobutton"` with `error` prop and `errorMessage`

Follow the existing Lit HTML story convention in the file.

---

## ⬜ Task 7: MDX documentation refactoring

**Files to create/modify:**

- `apps/boreal-docs/src/stories/forms/bds-radio-group/_variants/RadioCircular.mdx` ← NEW (extract existing)
- `apps/boreal-docs/src/stories/forms/bds-radio-group/_variants/RadioButton.mdx` ← NEW
- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.mdx` ← MODIFY

**Goal:** Organize variant-specific content into separate MDX files. Both Radio (Circular) and Radio Button variants get equal treatment as importable sections.

### `RadioCircular.mdx`

Extract all existing circular examples from the main MDX:
- Basic Usage Canvas (`Default` story)
- Horizontal Orientation Canvas (`Horizontal` story)
- Pre-selected Value Canvas (`WithValue` story)
- With Info Tooltip Canvas (`WithInfoTooltip` story)
- With Icons Canvas (`WithIcons` story)

### `RadioButton.mdx`

New section covering the radiobutton variant:
- Description and when-to-use guidance
- Visual differences from circle variant
- Usage code example
- `bds-radio-button` props table (value, label, info, checked, disabled, error, name; slots: icon, default)
- Canvas previews for all 5 stories from Task 6
- Accessibility note (identical keyboard/ARIA behavior to circle variant)

### Main `bds-radio-group.mdx`

Refactor to import both variant files:

```mdx
import RadioCircularDocs from './_variants/RadioCircular.mdx';
import RadioButtonDocs from './_variants/RadioButton.mdx';

...

<RadioCircularDocs />
<RadioButtonDocs />
```

Remove extracted circular examples. Keep all shared sections (States, Form Integration, Accessibility, Props/ArgTypes).

---

## Verification

```bash
# Full radio suite
eval "$(fnm env --shell bash)" && fnm use && \
  pnpm --filter boreal-web-components test -- --testPathPattern="bds-radio"

# TypeScript clean check
eval "$(fnm env --shell bash)" && fnm use && \
  pnpm --filter boreal-web-components exec tsc --noEmit

# Storybook visual check (after Task 6+7)
pnpm dev:docs
# Forms/Radio Group → navigate to "Radio Button Variant" section
# → Canvas shows: RadioButton, RadioButtonWithIcons, RadioButtonWithTooltips, RadioButtonDisabled, RadioButtonError
# → Verify: pill shape, NO circle indicator, segmented control layout, icon slot, all states
# → Keyboard: same Arrow/Tab/Space behavior as Radio (Circular) variant
```

---

## Critical Constraints

- **No `@use` in SCSS files** — `$boreal-*` tokens are globally injected via `injectGlobalPaths`; adding `@use` causes a Sass double-import error
- **Hidden native input required** — visually suppressed via `input[type='radio'] { position: absolute; opacity: 0; ... }`
- **No `:host` selectors** — all selectors target element tag names directly
- **`insertBefore` not `before()`** — JSDOM compatibility constraint discovered during testing
- **`radioElements.filter()` not `:scope >`** — Stencil scoped mode constraint; slot content is physically moved by the compiler
- Do NOT remove or alter the existing `bds-radio` implementation — this plan only adds and extends
- No inline code comments; no `Co-Authored-By` commit trailers
- Interface file: `IRadioButton.ts` (no `Bds` prefix — project convention)
