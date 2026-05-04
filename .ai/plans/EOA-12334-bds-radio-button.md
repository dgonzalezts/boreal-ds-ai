---
status: pending
---

# bds-radio-button Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Prerequisite:** `bds-radio-group` must already be implemented (see `EOA-12334-bds-radio-and-radio-group.md`). This plan adds `bds-radio-button` as a new leaf component and extends the group to handle it.

**Scope:** `bds-radio-button` (leaf component) + extension of `bds-radio-group` to support `type="radiobutton"`.

**Why a separate component (not a CSS-only variant of bds-radio):**

1. **DOM difference** — `bds-radio-button` has no circle indicator (`.bds-radio__button`, `.bds-radio__dot`) in the DOM at all; the absence is structural, not just CSS-hidden.
2. **Different API** — carries a `label` string prop and an `icon` named slot that are meaningless on `bds-radio`.
3. **Segmented control CSS** — the adjacent-sibling border-collapsing layout requires a dedicated tag name; CSS `+` combinators cannot target a subset of elements sharing the same tag name.

Evidence: Colibri's `col-radio-button` (`.ai/lib/colibri-components.txt`) has the same structural separation from `col-radio`.

**Tech Stack:** Stencil, TypeScript, SCSS, `boreal-styleguidelines` design tokens, Storybook (Lit HTML stories + MDX docs), Jest / `@stencil/core/testing`.

---

## File tree to create / modify

```
packages/boreal-web-components/src/components/forms/bds-radio/
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
    bds-radio-group.tsx                     ← MODIFY (add 'radiobutton' type, extend LEAF_TAGS)
    types/
      IRadioGroup.ts                        ← MODIFY (extend type union)

apps/boreal-docs/src/stories/forms/bds-radio-group/
  bds-radio-group.stories.ts               ← MODIFY (add type=radiobutton stories)
  bds-radio-group.mdx                      ← MODIFY (refactor to import both variants)
  _variants/
    RadioCircular.mdx                      ← NEW (extract existing circular examples)
    RadioButton.mdx                        ← NEW (radiobutton variant documentation)
```

**Note:** `bds-radio-button` has **no standalone Storybook entry** — it is a private building block like `bds-radio`. All documentation lives inside `bds-radio-group` stories and MDX.

---

## Task 1: IRadioButton.ts + update IRadioGroup.ts

### Create: `bds-radio-button/types/IRadioButton.ts`

```typescript
import type { EventEmitter } from "@stencil/core/internal";

export interface RadioButtonChangeDetail {
  checked: boolean;
  value: string;
}

export interface RadioButtonMountDetail {
  element: HTMLElement;
}

export interface IRadioButton {
  checked: boolean;
  disabled: boolean;
  error: boolean;
  value: string;
  name: string;
  label: string;
  bdsChange: EventEmitter<RadioButtonChangeDetail>;
  bdsMount: EventEmitter<RadioButtonMountDetail>;
}
```

### Modify: `bds-radio-group/types/IRadioGroup.ts`

Extend the `type` union:

```typescript
// Before
type: "radio";

// After
type: "radio" | "radiobutton";
```

---

## Task 2: bds-radio-button TSX

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-button/bds-radio-button.tsx`

`bds-radio-button` is NOT form-associated. It uses the same event contract as `bds-radio` (`bdsMount` + `bdsChange`) so the group handles both uniformly.

Key differences from `bds-radio`:

- No circle indicator — neither `.bds-radio__button` nor `.bds-radio__dot` appear in the DOM
- `icon` named slot rendered conditionally before the label
- The hidden native `<input type="radio">` is still included (same as `bds-radio`) for form submission fallback and focus forwarding

```typescript
import { Component, Element, Event, EventEmitter, Host, Prop, h } from '@stencil/core';
import type { IRadioButton, RadioButtonChangeDetail, RadioButtonMountDetail } from './types/IRadioButton';

@Component({
  tag: 'bds-radio-button',
  styleUrl: 'bds-radio-button.scss',
  scoped: false,
})
export class BdsRadioButton implements IRadioButton {
  @Element() el!: HTMLBdsRadioButtonElement;

  @Prop({ mutable: true, reflect: true }) checked: boolean = false;
  @Prop({ reflect: true }) readonly disabled: boolean = false;
  @Prop() readonly value: string = 'on';
  @Prop({ mutable: true }) name: string = '';
  @Prop() readonly label: string = '';
  @Prop({ reflect: true }) readonly error: boolean = false;

  @Event() bdsChange!: EventEmitter<RadioButtonChangeDetail>;
  @Event({ bubbles: true, composed: true }) bdsMount!: EventEmitter<RadioButtonMountDetail>;

  componentDidLoad() {
    this.el.setAttribute('role', 'radio');
    this.el.setAttribute('aria-checked', String(this.checked));
    this.el.setAttribute('tabindex', '-1');
    this.bdsMount.emit({ element: this.el });
  }

  private select() {
    if (this.disabled || this.checked) return;
    this.checked = true;
    this.el.setAttribute('aria-checked', 'true');
    this.bdsChange.emit({ checked: true, value: this.value });
  }

  private handleClick = () => this.select();

  private handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === ' ') {
      event.preventDefault();
      this.select();
    }
  };

  render() {
    return (
      <Host
        class={{
          'bds-radio-button': true,
          '--checked': this.checked,
          '--error': this.error,
          '--disabled': this.disabled,
        }}
        onClick={this.handleClick}
        onKeyDown={this.handleKeyDown}
      >
        <input
          type="radio"
          name={this.name}
          value={this.value}
          checked={this.checked}
          disabled={this.disabled}
          aria-hidden="true"
          tabIndex={-1}
          onFocus={() => (this.el as HTMLElement).focus()}
        />
        <span class="bds-radio-button__icon">
          <slot name="icon" />
        </span>
        <span class="bds-radio-button__label">{this.label || <slot />}</span>
      </Host>
    );
  }
}
```

**Manual test (waiveable):**

- Render `<bds-radio-button label="Option A" value="a"></bds-radio-button>` in isolation
- Verify **no** `.bds-radio__button` or `.bds-radio__dot` element exists in the DOM
- Verify the hidden `<input type="radio">` IS present with `aria-hidden="true"` and `tabindex="-1"`
- Verify label renders; click emits `bdsChange`; Space also triggers selection
- Render with `<svg slot="icon">…</svg>` and verify the icon appears before the label
- Render inside `<bds-radio-group type="radiobutton">` with siblings — verify segmented border-collapsing CSS takes effect

---

## Task 3: bds-radio-button tests

**Files:** `__test__/bds-radio-button.basics.spec.ts`, `bds-radio-button.a11y.spec.ts`, `bds-radio-button.events.spec.ts`

### bds-radio-button.basics.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadioButton } from "../bds-radio-button";

describe("bds-radio-button basics", () => {
  it("renders without circle indicator", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="Option"></bds-radio-button>',
    });
    expect(root.querySelector(".bds-radio__button")).toBeNull();
    expect(root.querySelector(".bds-radio__dot")).toBeNull();
  });

  it("renders hidden native input for form fallback", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="Option" value="x"></bds-radio-button>',
    });
    const input = root.querySelector('input[type="radio"]') as HTMLInputElement;
    expect(input).toBeTruthy();
    expect(input.getAttribute("aria-hidden")).toBe("true");
    expect(input.tabIndex).toBe(-1);
    expect(input.value).toBe("x");
  });

  it("renders label text", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="My Option"></bds-radio-button>',
    });
    expect(root.querySelector(".bds-radio-button__label").textContent).toBe(
      "My Option",
    );
  });

  it("renders icon slot container", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="Option"></bds-radio-button>',
    });
    expect(root.querySelector(".bds-radio-button__icon")).toBeTruthy();
  });

  it("reflects checked", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button checked label="Option"></bds-radio-button>',
    });
    expect(root.classList.contains("--checked")).toBe(true);
  });

  it("reflects disabled", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button disabled label="Option"></bds-radio-button>',
    });
    expect(root.classList.contains("--disabled")).toBe(true);
  });

  it("reflects error", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button error label="Option"></bds-radio-button>',
    });
    expect(root.classList.contains("--error")).toBe(true);
  });
});
```

### bds-radio-button.a11y.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadioButton } from "../bds-radio-button";

describe("bds-radio-button a11y", () => {
  it("has role=radio on host", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A"></bds-radio-button>',
    });
    expect(root.getAttribute("role")).toBe("radio");
  });

  it("aria-checked is false by default", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A"></bds-radio-button>',
    });
    expect(root.getAttribute("aria-checked")).toBe("false");
  });

  it("aria-checked updates to true on click", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A"></bds-radio-button>',
    });
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(root.getAttribute("aria-checked")).toBe("true");
  });

  it("native input has aria-hidden=true so AT ignores it", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A"></bds-radio-button>',
    });
    const input = root.querySelector('input[type="radio"]');
    expect(input.getAttribute("aria-hidden")).toBe("true");
  });

  it("has tabindex attribute on host after mount", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A"></bds-radio-button>',
    });
    expect(root.hasAttribute("tabindex")).toBe(true);
  });
});
```

### bds-radio-button.events.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadioButton } from "../bds-radio-button";

describe("bds-radio-button events", () => {
  it("emits bdsChange with correct payload on click", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A" value="a"></bds-radio-button>',
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy.mock.calls[0][0].detail).toEqual({ checked: true, value: "a" });
  });

  it("does not emit bdsChange when already checked", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button checked label="A" value="a"></bds-radio-button>',
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy).not.toHaveBeenCalled();
  });

  it("does not emit bdsChange when disabled", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button disabled label="A"></bds-radio-button>',
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy).not.toHaveBeenCalled();
  });

  it("emits bdsChange on Space key", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A" value="a"></bds-radio-button>',
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.dispatchEvent(new KeyboardEvent("keydown", { key: " " }));
    await waitForChanges();
    expect(spy).toHaveBeenCalledTimes(1);
  });

  it("emits bdsMount on componentDidLoad", async () => {
    const spy = jest.fn();
    document.addEventListener("bdsMount", spy);
    await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="A"></bds-radio-button>',
    });
    expect(spy).toHaveBeenCalledTimes(1);
    document.removeEventListener("bdsMount", spy);
  });
});
```

---

## Task 4: bds-radio-button SCSS

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-button/bds-radio-button.scss`

No `@use` import — `$boreal-*` tokens are globally injected by `injectGlobalPaths` in `stencil.config.ts`. Start directly with the selector.

The hidden native input must be visually suppressed — in light DOM it would otherwise render as a visible native radio circle alongside the custom button. The adjacent-sibling border-collapsing CSS for segmented control layout is scoped to `bds-radio-group[type='radiobutton']` context.

```scss
bds-radio-button {
  display: inline-flex;
  align-items: center;
  gap: $boreal-spacing-2xs;
  padding: $boreal-spacing-2xs $boreal-spacing-s;
  border: 1px solid $boreal-stroke-default-light;
  border-radius: $boreal-border-radius-s;
  cursor: pointer;
  outline: none;
  background-color: transparent;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease;

  input[type="radio"] {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
    margin: 0;
    pointer-events: none;
  }

  &:hover:not(.--disabled) {
    border-color: $boreal-ui-success-dark;
  }

  &:focus-visible,
  &:focus {
    box-shadow: 0 0 0 2px $boreal-stroke-focus;
    outline: none;
  }

  &.--checked {
    border-color: $boreal-ui-success-base;
    background-color: $boreal-bg-primary-lighter;
    color: $boreal-ui-success-base;

    &:hover:not(.--disabled) {
      border-color: $boreal-ui-success-dark;
      color: $boreal-ui-success-dark;
    }
  }

  &.--error {
    border-color: $boreal-stroke-danger-base;
  }

  &.--disabled {
    cursor: not-allowed;
    pointer-events: none;
    color: $boreal-text-disabled;
    background-color: $boreal-bg-neutral;
  }

  .bds-radio-button__label {
    font-size: $boreal-typography-font-size-sm;
    font-weight: $boreal-typography-font-weight-regular;
    line-height: $boreal-typography-line-height-sm;
  }

  .bds-radio-button__icon {
    display: flex;
    align-items: center;
    justify-content: center;

    &:empty {
      display: none;
    }
  }
}

bds-radio-group[type="radiobutton"] {
  bds-radio-button + bds-radio-button {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    margin-left: -1px;
  }

  bds-radio-button:not(:last-of-type) {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }
}
```

---

## Task 5: Extend bds-radio-group to handle bds-radio-button

**Files to modify:**

- `bds-radio-group/bds-radio-group.tsx` — read the current file first; then apply the following targeted changes:

### Change 1 — Type alias

```typescript
// Before
type LeafElement = HTMLBdsRadioElement;

// After
type LeafElement = HTMLBdsRadioElement | HTMLBdsRadioButtonElement;
```

### Change 2 — LEAF_TAGS constant

```typescript
// Before
const LEAF_TAGS = ["BDS-RADIO"];

// After
const LEAF_TAGS = ["BDS-RADIO", "BDS-RADIO-BUTTON"];
```

### Change 3 — radioElements getter

```typescript
// Before
return Array.from(this.el.querySelectorAll<LeafElement>("bds-radio"));

// After
return Array.from(
  this.el.querySelectorAll<LeafElement>("bds-radio, bds-radio-button"),
);
```

### Change 4 — type prop

```typescript
// Before
@Prop({ reflect: true }) readonly type: 'radio' = 'radio';

// After
@Prop({ reflect: true }) readonly type: 'radio' | 'radiobutton' = 'radio';
```

No other logic changes needed — all group methods (`navigateTo`, `updateTabIndexes`, `handleRadioMount`, `handleRadioChange`, `handleKeyDown`) already include the `LEAF_TAGS` guard and operate on `LeafElement[]`. Both leaf types will be handled correctly once the constant, getter, and type prop are updated.

**Manual test (waiveable):**

- Render `<bds-radio-group type="radiobutton" name="g">` with multiple `<bds-radio-button>` children
- Verify segmented control visual (border-collapsing between adjacent buttons)
- Verify single selection (clicking one deselects others)
- Verify Arrow keys navigate and select
- Verify Tab enters the group at the checked (or first non-disabled) button

---

## Task 6: Storybook stories

**File to modify:**

- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts`

**No standalone `bds-radio-button` stories** — it is a private building block. All stories showing `bds-radio-button` must be inside the `bds-radio-group` story file, using `type="radiobutton"`.

Add the following stories to `bds-radio-group.stories.ts`:

1. **RadioButton** — `type="radiobutton"`, horizontal segmented control appearance with 3 `<bds-radio-button>` children, one pre-selected
2. **RadioButtonWithIcons** — same as above but with icon slot filled on each button
3. **RadioButtonDisabled** — `type="radiobutton"` with `disabled` prop on the group
4. **RadioButtonError** — `type="radiobutton"` with `error` prop and `errorMessage`

These stories demonstrate the button variant's visual states within the group context. Follow the existing Lit HTML story convention and use the `showIcons` Storybook-only control pattern if needed.

---

## Task 7: MDX documentation refactoring

**Files to create/modify:**

- `apps/boreal-docs/src/stories/forms/bds-radio-group/_variants/RadioCircular.mdx` ← NEW (extract existing)
- `apps/boreal-docs/src/stories/forms/bds-radio-group/_variants/RadioButton.mdx` ← NEW
- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.mdx` ← MODIFY (refactor to import both)

**Goal:** Organize variant-specific content into separate MDX files for better maintainability and readability. Both Radio (Circular) and Radio Button variants get equal treatment as importable sections.

**No standalone Storybook entry** — `bds-radio-button` is a private building block. All documentation lives inside the Radio Group docs via MDX imports.

---

### Step 1: Extract existing circular examples to `_variants/RadioCircular.mdx`

Read the current `bds-radio-group.mdx` and extract all content from the "Component preview" section that relates to the Radio (Circular) variant into a new file.

**Content to extract:**

- Callout about "Show code" tip
- "Basic Usage" section + Canvas
- "Horizontal Orientation" section + Canvas
- "Pre-selected Value" section + Canvas
- "With Info Tooltip" section + Canvas
- "With Icons" section + Canvas

**Full RadioCircular.mdx structure:**

```mdx
import { Canvas } from "@storybook/addon-docs/blocks";
import { Callout } from "@/components/docs";
import * as BdsRadioGroupStories from "../bds-radio-group.stories";

## Radio (Circular) Variant

Traditional radio buttons with circular indicators. This is the default variant using `<bds-radio>` child elements.

<Callout variant="tip" icon="💡">
  You can click on the **Show code** button in the bottom-right section of the
  following code snippets to see how to use the component.
</Callout>

### Basic Usage

The default configuration uses vertical orientation with no pre-selected value. Provide a `label` and optionally `helper-text` to guide the user.

<Canvas of={BdsRadioGroupStories.Default} />

### Horizontal Orientation

Use `orientation="horizontal"` to display options side by side. Best suited for short labels where screen width allows.

<Canvas of={BdsRadioGroupStories.Horizontal} />

### Pre-selected Value

Set the `value` attribute to pre-select one of the radio options. This is useful for controlled state scenarios and default form values.

<Canvas of={BdsRadioGroupStories.WithValue} />

### With Info Tooltip

The `info` attribute adds a tooltip icon next to the group label, useful for providing additional context without cluttering the UI.

<Canvas of={BdsRadioGroupStories.WithInfoTooltip} />

### With Icons

Each `bds-radio` child accepts an icon via the `slot="icon"` slot, displayed to the left of the label text. Icons must be 16×16.

<Canvas of={BdsRadioGroupStories.WithIcons} />
```

---

### Step 2: Create `_variants/RadioButton.mdx`

This file contains the full "Radio Button Variant" section content:

- **Description**: Button-shaped radio option that creates a segmented control appearance when used with `type="radiobutton"`. Best for 2–4 short-label options where the button visual metaphor is clearer than circles.
- **When to use**: Short labels (1–2 words), binary/ternary choices, actions that feel like mode switches (View: Grid | List | Table)
- **Visual differences from circle variant**: No circle indicator, pill/button shape, segmented control layout when horizontal
- **Usage example**:
  ```html
  <bds-radio-group
    type="radiobutton"
    name="view"
    label="Choose view mode"
    orientation="horizontal"
  >
    <bds-radio-button value="grid" label="Grid">
      <em slot="icon" class="bds-icon-grid"></em>
    </bds-radio-button>
    <bds-radio-button value="list" label="List">
      <em slot="icon" class="bds-icon-list"></em>
    </bds-radio-button>
  </bds-radio-group>
  ```
- **Child element props** (`bds-radio-button`):
  - `value` (string) — submitted value when selected
  - `label` (string) — button text
  - `checked` (boolean) — managed by parent group
  - `disabled` (boolean) — propagated from parent group
  - `error` (boolean) — propagated from parent group
  - `name` (string) — set automatically by parent group
  - Slot `icon` (named, optional) — 16×16 icon rendered before label
  - Slot `default` — label fallback when `label` prop is empty
- **Canvas previews**: Reference the new stories (`RadioButton`, `RadioButtonWithIcons`, `RadioButtonDisabled`, `RadioButtonError`)
- **Accessibility note**: Same keyboard navigation as circle variant (Arrow keys select, Tab enters/exits group, roving tabindex). Each `bds-radio-button` has `role="radio"` and `aria-checked`. Hidden native `<input type="radio">` present for form fallback (invisible to AT via `aria-hidden`).

**Full RadioButton.mdx structure:**

````mdx
import { Canvas } from '@storybook/addon-docs/blocks';
import { Callout } from '@/components/docs';
import * as BdsRadioGroupStories from '../bds-radio-group.stories';
## Radio Button Variant

Button-shaped radio option that creates a segmented control appearance when used with `type="radiobutton"`. Best for 2–4 short-label options where the button visual metaphor is clearer than circles.

### When to use

- **Short labels** (1–2 words) like "Grid", "List", "Table"
- **Binary or ternary choices** where options are mutually exclusive
- **Mode switches** or view toggles (e.g., "Day / Week / Month")
- **Toolbar-style controls** where the segmented visual fits the UI context

### Visual differences from Radio (Circular)

- No circle indicator — uses pill/button shape instead
- Segmented control layout when horizontal (borders collapse between adjacent buttons)
- Icon slot optional but commonly used for visual clarity
- Background color changes on selection (lighter tint of primary)

### Usage

<Callout variant="tip" icon="💡">
  Set `type="radiobutton"` on the `bds-radio-group` to activate the segmented
  control styling.
</Callout>

```html
<bds-radio-group
  type="radiobutton"
  name="view"
  label="Choose view mode"
  orientation="horizontal"
>
  <bds-radio-button value="grid" label="Grid">
    <em slot="icon" class="bds-icon-grid"></em>
  </bds-radio-button>
  <bds-radio-button value="list" label="List">
    <em slot="icon" class="bds-icon-list"></em>
  </bds-radio-button>
  <bds-radio-button value="table" label="Table">
    <em slot="icon" class="bds-icon-table"></em>
  </bds-radio-button>
</bds-radio-group>
```
````

### Child Element Props

The `bds-radio-button` element accepts the following attributes:

| Property   | Type      | Default | Description                                   |
| ---------- | --------- | ------- | --------------------------------------------- |
| `value`    | `string`  | `''`    | Submitted value when selected                 |
| `label`    | `string`  | `''`    | Button text                                   |
| `checked`  | `boolean` | `false` | Selection state (managed by parent group)     |
| `disabled` | `boolean` | `false` | Disabled state (propagated from parent group) |
| `error`    | `boolean` | `false` | Error state (propagated from parent group)    |
| `name`     | `string`  | `''`    | Set automatically by parent group             |

**Slots:**

| Slot           | Description                               |
| -------------- | ----------------------------------------- |
| `icon` (named) | Optional 16×16 icon rendered before label |
| `default`      | Label fallback when `label` prop is empty |

### Examples

<Callout variant="tip" icon="💡">
  Click **Show code** in the bottom-right of each preview to see the full implementation.
</Callout>

#### Basic Radio Button

Segmented control with three options, middle one pre-selected.

<Canvas of={BdsRadioGroupStories.RadioButton} />

#### With Icons

Each button includes a 16×16 icon via the `icon` slot.

<Canvas of={BdsRadioGroupStories.RadioButtonWithIcons} />

#### Disabled State

The `disabled` prop on the group disables all buttons.

<Canvas of={BdsRadioGroupStories.RadioButtonDisabled} />

#### Error State

The `error` prop applies error styling to all buttons and shows the error message.

<Canvas of={BdsRadioGroupStories.RadioButtonError} />

### Accessibility

Keyboard navigation and ARIA behavior are identical to the Radio (Circular) variant:

- **Arrow keys** move focus and select the next/previous button (wraps at ends)
- **Tab** enters the group at the checked button (or first non-disabled), then exits
- **Space** selects the focused button
- **Roving tabindex** ensures only one button is tabbable at a time
- Each `bds-radio-button` has `role="radio"` and `aria-checked` reflecting selection state
- Hidden native `<input type="radio" aria-hidden="true">` for form fallback (invisible to AT)

````

---

### Step 3: Modify main `bds-radio-group.mdx`

Refactor the main MDX file to import both variant sections. Replace the "Component preview" section content with imports.

**Changes to make:**

1. **Add imports** at the top (after existing Storybook imports):
   ```mdx
   import RadioCircularDocs from './_variants/RadioCircular.mdx';
   import RadioButtonDocs from './_variants/RadioButton.mdx';
````

2. **Replace the Component preview section** with:

   ```mdx
   <Subtitle>Component preview</Subtitle>

   The following examples showcase the core features and visual options of the Radio Group component across its two variants.

   <RadioCircularDocs />

   <RadioButtonDocs />

   ## States
   ```

3. **Remove** the extracted circular examples (Basic Usage, Horizontal, Pre-selected Value, With Info, With Icons sections)

4. **Keep** all shared sections as-is:
   - States (Disabled, Error)
   - Form Integration
   - Accessibility
   - Properties (ArgTypes)

**Result:** Main MDX becomes a clean orchestrator (~150-200 lines) that imports variant-specific content, with all shared documentation (States, Form Integration, Accessibility, Props) remaining in one place.

---

## Critical Constraints

- **No `@use` in SCSS files** — `$boreal-*` tokens are globally injected via `injectGlobalPaths` in `stencil.config.ts`; adding `@use` causes a Sass double-import error; start directly with selectors
- **Hidden native input required** — both `bds-radio` and `bds-radio-button` include `<input type="radio" aria-hidden="true" tabindex="-1">` for form submission fallback and focus forwarding; it must be visually suppressed via `input[type='radio'] { position: absolute; opacity: 0; ... }` in component SCSS (light DOM does not hide it automatically)
- **No `:host` selectors** — all selectors target element tag names directly
- `bds-radio-Group → navigate to "Radio Button Variant" section in MDX

# → Canvas shows: RadioButton (segmented), RadioButtonWithIcons, RadioButtonDisabled, RadioButtonError

# → Verify: pill shape, NO circle indicator, border-collapsing layout, icon slot, all statese it)

- Do NOT remove or alter the existing `bds-radio` implementation — this plan only adds and extends
- No inline code comments; no `Co-Authored-By` commit trailers
- Interface file: `IRadioButton.ts` (no `Bds` prefix — project convention per memory)

---

## Verification

```bash
# Radio-button tests only
eval "$(fnm env --shell bash)" && fnm use && \
  pnpm --filter boreal-web-components test -- --testPathPattern="bds-radio-button"

# Full radio suite (regression check)
eval "$(fnm env --shell bash)" && fnm use && \
  pnpm --filter boreal-web-components test -- --testPathPattern="bds-radio"

# TypeScript clean check
eval "$(fnm env --shell bash)" && fnm use && \
  pnpm --filter boreal-web-components exec tsc --noEmit

# Storybook visual check
pnpm dev:docs
# Forms/Radio Group → navigate to "Radio Button Variant" section (imported from RadioButton.mdx)
# → Canvas shows: RadioButton, RadioButtonWithIcons, RadioButtonDisabled, RadioButtonError
# → Verify: pill shape, NO circle indicator, segmented control border-collapsing, icon slot, all states
# → Keyboard: same Arrow/Tab/Space behavior as Radio (Circular) variant
```
