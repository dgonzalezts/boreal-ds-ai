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
    bds-radio-group.tsx                     ← MODIFY (add 'radiobutton' type, extend LEAF_TAGS, divider propagation)
    types/
      IRadioGroup.ts                        ← MODIFY (extend type union, add showDivider)

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

export interface IRadioButton {
  checked: boolean;
  disabled: boolean;
  error: boolean;
  value: string;
  name: string;
  label: string;
  info: string;
  /** Set by parent bds-radio-group. Controls whether this button renders a leading bds-divider. */
  showDivider: boolean;
  /** Set by parent bds-radio-group. Suppresses the leading divider on the first button. */
  isFirst: boolean;
  bdsChange: EventEmitter<RadioButtonChangeDetail>;
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

## Task 2a: bds-radio-button scaffold

**File:** `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.tsx`

`bds-radio-button` is NOT form-associated. It uses the same event contract as `bds-radio` (`bdsChange`) so the group handles both uniformly.

Key differences from `bds-radio`:

- No circle indicator — neither `.bds-radio__button` nor `.bds-radio__dot` appear in the DOM
- `icon` named slot rendered before the label
- `info` prop forwards tooltip text to `bds-typography`
- `showDivider` / `isFirst` props (set by the parent group) control the leading `bds-divider`
- The hidden native `<input type="radio">` is still included for form submission fallback and focus forwarding

**Important:** `@Element() el!: HTMLBdsRadioButtonElement` references a Stencil-generated type that does not exist until the first build. Write the scaffold and run the build step before adding lifecycle methods that call `this.el.setAttribute(...)`.

Class shell with all `@Prop` and `@Event` declarations. `render()` returns a stub `<Host />` until Task 2c replaces it.

```typescript
import { Component, Element, Event, EventEmitter, Host, Prop, h } from '@stencil/core';
import type { IRadioButton, RadioButtonChangeDetail } from './types/IRadioButton';

/**
 * Button-shaped radio option for use inside `bds-radio-group[type="radiobutton"]`.
 * Creates a segmented control appearance when grouped. Not form-associated — the parent
 * `bds-radio-group` owns form state and single-selection enforcement.
 *
 * @slot - Label content when no `label` prop is provided.
 * @slot icon - Optional icon rendered to the left of the label.
 */
@Component({
  tag: 'bds-radio-button',
  styleUrl: 'bds-radio-button.scss',
})
export class BdsRadioButton implements IRadioButton {
  @Element() el!: HTMLBdsRadioButtonElement;

  /** Whether this button is selected. Managed by bds-radio-group; can be set directly when used standalone. */
  @Prop({ mutable: true, reflect: true }) checked: boolean = false;

  /** Disables the button, preventing interaction and selection. */
  @Prop({ reflect: true }) readonly disabled: boolean = false;

  /** Shows error styling on the button. Propagated by bds-radio-group. */
  @Prop({ reflect: true }) readonly error: boolean = false;

  /** Value submitted with the form when this button is selected. */
  @Prop() readonly value: string = 'on';

  /** Name attribute stamped by the parent bds-radio-group via setAttribute. Set directly when used standalone. */
  @Prop({ reflect: true }) readonly name: string = '';

  /** Label text displayed inside the button. Falls back to the default slot when empty. */
  @Prop() readonly label: string = '';

  /** Tooltip text shown on an info icon next to the label. */
  @Prop() readonly info: string = '';

  /** Set by parent bds-radio-group. Renders a leading bds-divider when true. */
  @Prop() readonly showDivider: boolean = false;

  /** Set by parent bds-radio-group. Suppresses the leading divider on the first button in the group. */
  @Prop() readonly isFirst: boolean = false;

  /** Emitted when the user selects this button. Listened to by the parent bds-radio-group to enforce single selection. */
  @Event({ bubbles: true }) bdsChange!: EventEmitter<RadioButtonChangeDetail>;

  render() { return <Host />; }
}
```

After writing the scaffold, trigger a build so Stencil generates `HTMLBdsRadioButtonElement` in `src/components.d.ts`:

```bash
eval "$(fnm env --shell bash)" && fnm use && pnpm --filter boreal-web-components build
```

**Manual test (waiveable):**

- Run the build command above — expect zero errors and a new `HTMLBdsRadioButtonElement` entry in `packages/boreal-web-components/src/components.d.ts`
- Run `pnpm --filter boreal-web-components exec tsc --noEmit` — zero TypeScript errors
- Verify the IDE no longer shows "unsafe member access" lint errors on `this.el.*` calls

---

## Task 2b: bds-radio-button lifecycle + interaction

**File:** `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.tsx`

Add to the class body (before `render()`):

- `componentDidLoad` — stamps `role`, `aria-checked`, `tabindex` onto the host element
- `select()` — guards against disabled/already-checked; sets `checked`, updates `aria-checked`, emits `bdsChange`
- `handleClick` — arrow function delegating to `select()`
- `handleKeyDown` — Space key triggers `select()`; `preventDefault()` blocks page scroll

```typescript
componentDidLoad() {
  this.el.setAttribute('role', 'radio');
  this.el.setAttribute('aria-checked', String(this.checked));
  this.el.setAttribute('tabindex', '-1');
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
```

**Manual test (waiveable):**

- Run `pnpm --filter boreal-web-components exec tsc --noEmit` — zero errors
- After mount, inspect a rendered `<bds-radio-button>` — expect `role="radio"`, `aria-checked="false"`, `tabindex="-1"` on the host
- Click → `aria-checked` becomes `"true"`, `bdsChange` fires in DevTools console
- Click again → no second event (already-checked guard)
- Keyboard Space → also triggers selection on an unchecked button

---

## Task 2c: bds-radio-button render()

**File:** `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.tsx`

Replace the stub `render() { return <Host />; }` with the full DOM structure. Wire `onClick={this.handleClick}` and `onKeyDown={this.handleKeyDown}` on `<Host>`. Include the conditional `bds-divider`, the hidden native `<input>`, the icon slot, and `bds-typography` for the label.

```tsx
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
      {this.showDivider && !this.isFirst && <bds-divider orientation="vertical" />}
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
      <bds-typography
        class="bds-radio-button__label"
        variant="label"
        tooltipText={this.info !== '' ? this.info : undefined}
      >
        {this.label || <slot />}
      </bds-typography>
    </Host>
  );
}
```

**Manual test (waiveable):**

- Render `<bds-radio-button label="Option A" value="a"></bds-radio-button>` in isolation
- Verify **no** `.bds-radio__button` or `.bds-radio__dot` element exists in the DOM
- Verify the hidden `<input type="radio">` IS present with `aria-hidden="true"` and `tabindex="-1"`
- Verify label renders; click emits `bdsChange`; Space also triggers selection
- Render with `<svg slot="icon">…</svg>` — icon appears before the label
- Render inside `<bds-radio-group type="radiobutton">` with siblings — segmented border layout applies

---

## Task 2d: bds-radio-button JSDoc audit

**File:** `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.tsx`

`bds-radio-button` is NOT form-associated. It uses the same event contract as `bds-radio` (`bdsChange`) so the group handles both uniformly.

Key differences from `bds-radio`:

- No circle indicator — neither `.bds-radio__button` nor `.bds-radio__dot` appear in the DOM
- `icon` named slot rendered conditionally before the label
- The hidden native `<input type="radio">` is still included (same as `bds-radio`) for form submission fallback and focus forwarding

```typescript
import { Component, Element, Event, EventEmitter, Host, Prop, h } from '@stencil/core';
import type { IRadioButton, RadioButtonChangeDetail } from './types/IRadioButton';

@Component({
  tag: 'bds-radio-button',
  styleUrl: 'bds-radio-button.scss',
})
export class BdsRadioButton implements IRadioButton {
  @Element() el!: HTMLBdsRadioButtonElement;

  @Prop({ mutable: true, reflect: true }) checked: boolean = false;
  @Prop({ reflect: true }) readonly disabled: boolean = false;
  @Prop() readonly value: string = 'on';
  @Prop({ reflect: true }) readonly name: string = '';
  @Prop() readonly label: string = '';
  @Prop({ reflect: true }) readonly error: boolean = false;
  @Prop() readonly info: string = '';

  @Event() bdsChange!: EventEmitter<RadioButtonChangeDetail>;

  componentDidLoad() {
    this.el.setAttribute('role', 'radio');
    this.el.setAttribute('aria-checked', String(this.checked));
    this.el.setAttribute('tabindex', '-1');
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
        <bds-typography
          class="bds-radio-button__label"
          variant="label"
          tooltipText={this.info !== '' ? this.info : undefined}
        >
          {this.label || <slot />}
        </bds-typography>
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

  it("renders bds-typography with tooltip when info is provided", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="Option" info="Helpful tooltip"></bds-radio-button>',
    });
    const typography = root.querySelector("bds-typography");
    expect(typography).toBeTruthy();
    expect(typography.getAttribute("tooltip-text")).toBe("Helpful tooltip");
  });

  it("renders bds-typography without tooltip when info is empty", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="Option"></bds-radio-button>',
    });
    const typography = root.querySelector("bds-typography");
    expect(typography).toBeTruthy();
    expect(typography.hasAttribute("tooltip-text")).toBe(false);
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
});
```

---

## Task 4: Extend bds-radio-group to handle bds-radio-button

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

No other logic changes needed for the core group behaviour — all group methods (`navigateTo`, `updateTabIndexes`, `handleRadioChange`, `handleKeyDown`) already include the `LEAF_TAGS` guard and operate on `LeafElement[]`. Both leaf types will be handled correctly once the constant, getter, and type prop are updated.

### Change 5 — Divider propagation (PRIMARY: Option A — self-dividing leaf)

> **This is the primary approach.** Use the imperative fallback only if Option A produces rendering issues during manual testing.

The divider between adjacent buttons is rendered **by the leaf component itself** (`bds-radio-button`), not injected by the group. Each `bds-radio-button` owns a leading `<bds-divider orientation="vertical">` in its vDOM, controlled by two props set by the group:

- `showDivider: boolean` — mirrors the group's `showDivider` prop
- `isFirst: boolean` — set to `true` on the first button; suppresses the leading divider without CSS

This follows the identical pattern already used for `disabled` and `error` propagation and keeps all divider DOM inside Stencil's reconciler, eliminating re-render safety concerns.

#### Change 5a — IRadioGroup.ts: add showDivider

```typescript
// Add to IRadioGroup interface
showDivider: boolean;
```

#### Change 5b — bds-radio-group.tsx: new prop

```typescript
/** Controls whether a vertical divider is rendered between adjacent bds-radio-button elements. Only applies when type="radiobutton". */
@Prop({ reflect: true }) readonly showDivider: boolean = true;
```

#### Change 5c — bds-radio-group.tsx: new @Watch and propagation helper

```typescript
@Watch('showDivider')
onShowDividerChange(val: boolean) {
  this.propagateDividerProps();
}

private propagateDividerProps(): void {
  this.radioElements.forEach((el, i) => {
    if ('showDivider' in el) {
      (el as HTMLBdsRadioButtonElement).showDivider = this.showDivider;
      (el as HTMLBdsRadioButtonElement).isFirst = i === 0;
    }
  });
}
```

#### Change 5d — bds-radio-group.tsx: call propagateDividerProps in componentDidLoad and handleSlotChange

```typescript
// In componentDidLoad(), after updateTabIndexes():
this.propagateDividerProps();

// In handleSlotChange (currently: private handleSlotChange = () => this.updateLayoutCount()):
private handleSlotChange = () => {
  this.updateLayoutCount();
  this.propagateDividerProps();
};
```

#### Change 5e — bds-radio-button.tsx: new props and render

Add to `BdsRadioButton`:

```typescript
/** Set by parent bds-radio-group. Renders a leading bds-divider when true. */
@Prop() showDivider: boolean = false;

/** Set by parent bds-radio-group. Suppresses the leading divider on the first button in the group. */
@Prop() isFirst: boolean = false;
```

In `render()`, add the conditional divider as the first child inside `<Host>`:

```tsx
{
  this.showDivider && !this.isFirst && <bds-divider orientation="vertical" />;
}
```

#### Change 5f — SCSS: outer container border, not individual button borders

The segmented control uses a **single shared border on the group's `.bds-radio-group__options` wrapper**, not individual borders on each button. This avoids double-border artifacts, `:first-of-type`/`:last-of-type` radius tricks, and conflicting per-button border overrides.

**In `bds-radio-button.scss`** — add inside the group context (individual borders and radius are stripped):

```scss
bds-radio-group[type="radiobutton"] {
  bds-radio-button {
    border: none;
    border-radius: 0;
  }
}
```

**In `bds-radio-group.scss`** — add a new block (the wrapper becomes the single bordered container):

```scss
bds-radio-group[type="radiobutton"] {
  .bds-radio-group__options {
    display: inline-flex;
    border: 1px solid $boreal-stroke-default-light;
    border-radius: $boreal-radius-s;
    overflow: hidden;
  }

  &.--error .bds-radio-group__options {
    border-color: $boreal-stroke-danger-base;
  }

  &.--disabled .bds-radio-group__options {
    border-color: $boreal-stroke-default-light;
  }
}
```

`overflow: hidden` on the wrapper ensures the first/last button backgrounds are clipped to the rounded corners without needing per-button radius overrides. Error and disabled border-color are handled at the container level, not per-button.

#### Tests to add for the divider (in bds-radio-button.basics.spec.ts)

```typescript
it("renders bds-divider when showDivider=true and isFirst=false", async () => {
  const { root } = await newSpecPage({
    components: [BdsRadioButton],
    html: '<bds-radio-button label="B" show-divider></bds-radio-button>',
  });
  expect(root.querySelector("bds-divider")).toBeTruthy();
});

it("does not render bds-divider when isFirst=true", async () => {
  const { root } = await newSpecPage({
    components: [BdsRadioButton],
    html: '<bds-radio-button label="A" show-divider is-first></bds-radio-button>',
  });
  expect(root.querySelector("bds-divider")).toBeNull();
});

it("does not render bds-divider when showDivider=false", async () => {
  const { root } = await newSpecPage({
    components: [BdsRadioButton],
    html: '<bds-radio-button label="B"></bds-radio-button>',
  });
  expect(root.querySelector("bds-divider")).toBeNull();
});
```

---

### Change 5 — Divider propagation (FALLBACK: imperative DOM injection)

> **Use only if Option A fails during manual testing** — e.g. if `bds-divider` inside the leaf's vDOM causes unexpected layout in the flex row context, or if the `isFirst` prop creates unresolvable timing issues on slot changes.
>
> This approach keeps `showDivider` and `isFirst` off the leaf interface at the cost of injecting raw DOM nodes outside Stencil's reconciler. A `data-injected` guard prevents duplicates on re-trigger.

#### Fallback Change 5a — IRadioGroup.ts: add showDivider (same as primary)

```typescript
showDivider: boolean;
```

#### Fallback Change 5b — bds-radio-group.tsx: new prop (same as primary)

```typescript
/** Controls whether vertical dividers are injected between adjacent bds-radio-button elements. Only applies when type="radiobutton". */
@Prop({ reflect: true }) readonly showDivider: boolean = true;
```

#### Fallback Change 5c — bds-radio-group.tsx: insertDividers method

```typescript
@Watch('showDivider')
onShowDividerChange() {
  this.insertDividers();
}

private insertDividers(): void {
  this.el.querySelectorAll('bds-divider[data-injected]').forEach(d => d.remove());
  if (this.type !== 'radiobutton' || !this.showDivider) return;

  const buttons = Array.from(
    this.el.querySelectorAll<HTMLBdsRadioButtonElement>(':scope > bds-radio-button')
  );
  buttons.forEach((btn, i) => {
    if (i === 0) return;
    const divider = document.createElement('bds-divider') as HTMLBdsDividerElement;
    divider.orientation = 'vertical';
    divider.setAttribute('data-injected', '');
    btn.before(divider);
  });
}
```

#### Fallback Change 5d — call insertDividers in componentDidLoad and handleSlotChange

```typescript
// In componentDidLoad():
this.insertDividers();

// handleSlotChange:
private handleSlotChange = () => {
  this.updateLayoutCount();
  this.insertDividers();
};
```

#### Fallback SCSS — same outer container approach as primary

Same as Change 5f in the primary approach above — strip button borders in group context, add container border to `.bds-radio-group__options`.

**Manual test (waiveable):**

- Render `<bds-radio-group type="radiobutton" name="g">` with multiple `<bds-radio-button>` children
- Verify segmented control visual: pill borders, `bds-divider` vertical separators between buttons
- Verify `show-divider="false"` removes all separators
- Verify single selection (clicking one deselects others)
- Verify Arrow keys navigate and select
- Verify Tab enters the group at the checked (or first non-disabled) button

---

## Task 5: bds-radio-button SCSS

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.scss`
- `packages/boreal-web-components/src/components/forms/bds-radio-group/bds-radio-group.scss`

No `@use` import in either file — `$boreal-*` tokens are globally injected via `injectGlobalPaths`. Start directly with selectors.

**Design model:** `bds-radio-button` always has its own border when used standalone. Inside `bds-radio-group[type='radiobutton']`, individual borders are stripped and a single shared border wraps the `__options` container instead. `bds-divider` elements (rendered by Task 4's propagation) provide the visual separation between buttons.

### bds-radio-button.scss

```scss
bds-radio-button {
  display: inline-flex;
  align-items: center;
  gap: $boreal-spacing-2xs;
  padding: $boreal-spacing-2xs $boreal-spacing-s;
  border: 1px solid $boreal-stroke-default-light;
  border-radius: $boreal-radius-s;
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
  bds-radio-button {
    border: none;
    border-radius: 0;
  }
}
```

### bds-radio-group.scss additions

Append to the existing `bds-radio-group.scss` file:

```scss
bds-radio-group[type="radiobutton"] {
  .bds-radio-group__options {
    display: inline-flex;
    border: 1px solid $boreal-stroke-default-light;
    border-radius: $boreal-radius-s;
    overflow: hidden;
  }

  &.--error .bds-radio-group__options {
    border-color: $boreal-stroke-danger-base;
  }

  &.--disabled .bds-radio-group__options {
    border-color: $boreal-stroke-default-light;
  }
}
```

`overflow: hidden` clips button backgrounds to the rounded corners without per-button radius overrides. Error and disabled border changes live on the container, not per-button.

**Manual test (waiveable):** After Task 4 is implemented, render `<bds-radio-group type="radiobutton">` with 3 `<bds-radio-button>` children; verify: single outer border with rounded corners, no double borders between buttons, dividers visible between buttons, checked state background fills the button, error/disabled border color on the container, standalone `<bds-radio-button>` (outside group) retains its own pill border.

---

## Task 6: Storybook stories

**File to modify:**

- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts`

**No standalone `bds-radio-button` stories** — it is a private building block. All stories showing `bds-radio-button` must be inside the `bds-radio-group` story file, using `type="radiobutton"`.

Add the following stories to `bds-radio-group.stories.ts`:

1. **RadioButton** — `type="radiobutton"`, horizontal segmented control appearance with 3 `<bds-radio-button>` children, one pre-selected
2. **RadioButtonWithIcons** — same as above but with icon slot filled on each button
3. **RadioButtonWithTooltips** — `type="radiobutton"` with `info` prop on individual buttons to show per-option tooltips
4. **RadioButtonNoDivider** — `type="radiobutton"` with `show-divider="false"` to demonstrate divider-less segmented control
5. **RadioButtonDisabled** — `type="radiobutton"` with `disabled` prop on the group
6. **RadioButtonError** — `type="radiobutton"` with `error` prop and `errorMessage`

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

| Property      | Type      | Default | Description                                                |
| ------------- | --------- | ------- | ---------------------------------------------------------- |
| `value`       | `string`  | `''`    | Submitted value when selected                              |
| `label`       | `string`  | `''`    | Button text                                                |
| `info`        | `string`  | `''`    | Tooltip text shown on info icon next to the button label   |
| `checked`     | `boolean` | `false` | Selection state (managed by parent group)                  |
| `disabled`    | `boolean` | `false` | Disabled state (propagated from parent group)              |
| `error`       | `boolean` | `false` | Error state (propagated from parent group)                 |
| `name`        | `string`  | `''`    | Set automatically by parent group                          |
| `showDivider` | `boolean` | `false` | Set by parent group. Renders leading bds-divider when true |
| `isFirst`     | `boolean` | `false` | Set by parent group. Suppresses divider on first button    |

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

#### With Tooltips

Each button can have its own `info` tooltip to provide additional context for that specific option.

<Canvas of={BdsRadioGroupStories.RadioButtonWithTooltips} />

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
