---
status: in progress
---

# bds-radio + bds-radio-group Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Scope:** `bds-radio` (leaf, circle variant) + `bds-radio-group` (form-associated orchestrator).
`bds-radio-button` and `bds-radio-card` are out of scope — see their own plans.

**Architecture:**

- `bds-radio-group` is the **sole FACE** component (`formAssociated: true`, `@AttachInternals()`). It owns `setFormValue`, `setValidity`, and `formResetCallback`.
- `bds-radio` is NOT form-associated. It fires a `bdsMount` bubbling event on mount so the group can register it without imperative DOM queries.
- The group enforces single selection by listening to `bdsChange` from children and unchecking siblings.
- The `LEAF_TAGS` constant in the group is designed to be extended in subsequent plans (`bds-radio-button`, etc.).

**Tech Stack:** Stencil, TypeScript, SCSS, `boreal-styleguidelines` design tokens, Storybook (Lit HTML stories + MDX docs), Jest / `@stencil/core/testing`.

**Public API boundary:** `bds-radio` is a **private building block** — it is not a standalone usable component and must not be documented in Storybook on its own. Only `bds-radio-group` is the public API. `bds-radio` has no story file and no MDX file. For a single binary choice, consumers should use `bds-checkbox` instead.

---

## File tree to create

```
packages/boreal-web-components/src/components/forms/bds-radio/
  bds-radio/
    bds-radio.tsx
    bds-radio.scss
    __test__/
      bds-radio.basics.spec.ts
      bds-radio.a11y.spec.ts
      bds-radio.events.spec.ts
    types/
      IRadio.ts
  bds-radio-group/
    bds-radio-group.tsx
    bds-radio-group.scss
    __test__/
      bds-radio-group.basics.spec.ts
      bds-radio-group.a11y.spec.ts
      bds-radio-group.events.spec.ts
      bds-radio-group.keyboard.spec.ts
    types/
      IRadioGroup.ts

apps/boreal-docs/src/stories/forms/bds-radio-group/
  bds-radio-group.stories.ts
  bds-radio-group.mdx
```

---

## Task 1: Type interfaces _(tracker #1 — completed)_

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/types/IRadio.ts`
- `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/types/IRadioGroup.ts`

### IRadio.ts

```typescript
import type { EventEmitter } from "@stencil/core/internal";

export interface RadioChangeDetail {
  checked: boolean;
  value: string;
}

export interface RadioMountDetail {
  element: HTMLElement;
}

export interface IRadio {
  checked: boolean;
  disabled: boolean;
  error: boolean;
  value: string;
  name: string;
  label: string;
  bdsChange: EventEmitter<RadioChangeDetail>;
  bdsMount: EventEmitter<RadioMountDetail>;
}
```

### IRadioGroup.ts

```typescript
import type { EventEmitter } from "@stencil/core/internal";

export interface RadioGroupChangeDetail {
  value: string;
}

export interface IRadioGroup {
  name: string;
  value: string;
  label: string;
  helperText: string;
  errorMessage: string;
  info: string;
  orientation: "horizontal" | "vertical";
  type: "radio";
  disabled: boolean;
  required: boolean;
  error: boolean;
  bdsChange: EventEmitter<RadioGroupChangeDetail>;
  valueChange: EventEmitter<string>;
}
```

> **Note:** `type` is scoped to `'radio'` for this plan. It will be extended to `'radio' | 'radiobutton'` in the `bds-radio-button` plan.

---

## Task 2: bds-radio scaffold _(tracker #10 — completed)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.tsx`

Class shell with all `@Prop` and `@Event` declarations. `render()` returns a stub `<Host />` until Task 4 replaces it.

```typescript
import { Component, Element, Event, EventEmitter, Host, Prop, h } from '@stencil/core';
import type { IRadio, RadioChangeDetail, RadioMountDetail } from './types/IRadio';

@Component({
  tag: 'bds-radio',
  styleUrl: 'bds-radio.scss',
})
export class BdsRadio implements IRadio {
  @Element() el!: HTMLBdsRadioElement;

  /** Whether this radio is selected. Managed by bds-radio-group; can be set directly when used standalone. */
  @Prop({ mutable: true, reflect: true }) checked: boolean = false;

  /** Disables the radio, preventing interaction and selection. */
  @Prop({ reflect: true }) readonly disabled: boolean = false;

  /** Value submitted with the form when this radio is selected. */
  @Prop() readonly value: string = 'on';

  /** Name attribute stamped by the parent bds-radio-group. Set directly when used standalone. */
  @Prop({ mutable: true }) name: string = '';

  /** Label text displayed next to the radio indicator. Falls back to the default slot when empty. */
  @Prop() readonly label: string = '';

  /** Shows error styling on the radio indicator. Propagated by bds-radio-group. */
  @Prop({ reflect: true }) readonly error: boolean = false;

  /**
   * Emitted when the user selects this radio. Bubbles so bds-radio-group can
   * listen via @Listen('bdsChange') and enforce single selection.
   */
  @Event({ bubbles: true }) bdsChange!: EventEmitter<RadioChangeDetail>;

  /** Emitted after componentDidLoad so the parent bds-radio-group can register this element. */
  @Event({ bubbles: true }) bdsMount!: EventEmitter<RadioMountDetail>;

  render() { return <Host />; }
}
```

---

## Task 3: bds-radio lifecycle + interaction _(tracker #11 — in progress)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.tsx`

Add to the class body (before `render()`):

- `componentDidLoad` — stamps `role`, `aria-checked`, `tabindex`, emits `bdsMount`
- `select()` — guards against disabled/already-checked; sets `checked`, updates `aria-checked`, emits `bdsChange`
- `handleClick` — arrow function delegating to `select()`
- `handleKeyDown` — Space key triggers `select()`; `preventDefault()` blocks page scroll

```typescript
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
```

**Manual test (waiveable):**

- Render `<bds-radio label="Option A" value="a"></bds-radio>` in isolation
- After mount, inspect element — expect `role="radio"`, `aria-checked="false"`, `tabindex="-1"`
- Click → `aria-checked` becomes `"true"`, `bdsChange` fires in DevTools
- Click again → no second event (already checked guard)
- Keyboard Space → also triggers selection on an unchecked radio

---

## Task 4: bds-radio render() _(tracker #12)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.tsx`

Replace the stub `render() { return <Host />; }` with the full DOM structure. Also update the import to add `Listen` — `onClick` and `onKeyDown` are wired via JSX props on `<Host>`, not `@Listen`, so the import stays the same. Attach `onClick={this.handleClick}` and `onKeyDown={this.handleKeyDown}` to `<Host>`.

Hidden native `<input type="radio">` carries `aria-hidden="true"` and `tabIndex={-1}` — it exists solely so the browser's FormData picks up the name/value pair when the component is used outside a `bds-radio-group` in a plain `<form>`.

```typescript
render() {
  return (
    <Host
      class={{
        'bds-radio': true,
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
      <span class="bds-radio__button">
        <span class="bds-radio__dot" />
      </span>
      <span class="bds-radio__content">
        <span class="bds-radio__icon"><slot name="icon" /></span>
        <span class="bds-radio__label">{this.label || <slot />}</span>
      </span>
    </Host>
  );
}
```

**Manual test (waiveable):**

- Render `<bds-radio label="Option A" value="a"></bds-radio>`
- Verify: circle indicator (`.bds-radio__button`) + dot (`.bds-radio__dot`) + label text visible
- Check DevTools: `<input type="radio" aria-hidden="true">` present and hidden
- `slot name="icon"` accepts a 16×16 icon element without breaking layout

---

## Task 4b: bds-radio JSDoc audit

**File:** `bds-radio/bds-radio.tsx`

Verify `bds-radio.tsx` satisfies all rules in `.ai/guidelines/jsdoc-template.md`:

- [ ] Class-level JSDoc block present with component description and `@slot` tags for both slots (`default`, `icon`).
- [ ] Every `@Prop()` has an inline `/** */` block immediately above the decorator (enforced by `stencil/required-jsdoc: 'error'`, but verify manually).
- [ ] Every `@Event()` has an inline `/** */` block.
- [ ] `bdsChange` and `bdsMount` use `@Event({ bubbles: true })` — not bare `@Event()` — because `bds-radio-group` catches them via `@Listen()`.
- [ ] No `@attr`, `@property`, `@fires`, `@element`, `@cssprop`, or `@internal` in the class-level block.
- [ ] No `@part` tags (light DOM, no shadow boundary).
- [ ] CSS custom properties (if any) are documented with `@prop` in `bds-radio.scss`, not `@cssprop` in the TSX.

---

## Task 5: bds-radio tests _(tracker #3)_

**Files:** `__test__/bds-radio.basics.spec.ts`, `bds-radio.a11y.spec.ts`, `bds-radio.events.spec.ts`

### bds-radio.basics.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadio } from "../bds-radio";

describe("bds-radio basics", () => {
  it("renders with default props", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="Option"></bds-radio>',
    });
    expect(root).toBeTruthy();
    expect(root.getAttribute("role")).toBe("radio");
    expect(root.getAttribute("aria-checked")).toBe("false");
  });

  it("reflects checked state", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio checked label="Option"></bds-radio>',
    });
    expect(root.classList.contains("--checked")).toBe(true);
  });

  it("reflects disabled state", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio disabled label="Option"></bds-radio>',
    });
    expect(root.classList.contains("--disabled")).toBe(true);
  });

  it("reflects error state", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio error label="Option"></bds-radio>',
    });
    expect(root.classList.contains("--error")).toBe(true);
  });

  it("renders circle indicator and label", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="My Label"></bds-radio>',
    });
    expect(root.querySelector(".bds-radio__button")).toBeTruthy();
    expect(root.querySelector(".bds-radio__dot")).toBeTruthy();
    expect(root.querySelector(".bds-radio__label").textContent).toBe(
      "My Label",
    );
  });
});
```

### bds-radio.a11y.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadio } from "../bds-radio";

describe("bds-radio a11y", () => {
  it("has role=radio", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(root.getAttribute("role")).toBe("radio");
  });

  it("aria-checked is false by default", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(root.getAttribute("aria-checked")).toBe("false");
  });

  it("aria-checked updates to true on click", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(root.getAttribute("aria-checked")).toBe("true");
  });

  it("has tabindex attribute after mount", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(root.hasAttribute("tabindex")).toBe(true);
  });
});
```

### bds-radio.events.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadio } from "../bds-radio";

describe("bds-radio events", () => {
  it("emits bdsChange with correct payload on click", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A" value="a"></bds-radio>',
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0].detail).toEqual({ checked: true, value: "a" });
  });

  it("does not emit bdsChange when already checked", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio checked label="A" value="a"></bds-radio>',
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy).not.toHaveBeenCalled();
  });

  it("does not emit bdsChange when disabled", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio disabled label="A" value="a"></bds-radio>',
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy).not.toHaveBeenCalled();
  });

  it("emits bdsChange on Space key", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A" value="a"></bds-radio>',
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
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(spy).toHaveBeenCalledTimes(1);
    document.removeEventListener("bdsMount", spy);
  });
});
```

---

## Task 6: bds-radio SCSS _(tracker #4)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.scss`

Classic circle radio styles only. No radiobutton or radiocard descendant blocks — those belong in their own component SCSS files.

```scss
bds-radio {
  display: inline-flex;
  align-items: center;
  gap: $boreal-spacing-2xs;
  cursor: pointer;
  outline: none;

  input[type="radio"] {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
    margin: 0;
    pointer-events: none;
  }

  &.--disabled {
    cursor: not-allowed;
    pointer-events: none;
  }

  .bds-radio__button {
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid $boreal-stroke-default-light;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.2s ease;
  }

  .bds-radio__dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background-color: transparent;
    transition: background-color 0.2s ease;
  }

  &:hover:not(.--disabled) .bds-radio__button {
    border-color: $boreal-ui-success-dark;
  }

  &:focus-visible .bds-radio__button,
  &:focus .bds-radio__button {
    box-shadow: 0 0 0 2px $boreal-stroke-focus;
  }

  &.--checked {
    .bds-radio__button {
      border-color: $boreal-ui-success-base;
    }

    .bds-radio__dot {
      background-color: $boreal-ui-success-base;
    }

    &:hover:not(.--disabled) .bds-radio__button {
      border-color: $boreal-ui-success-dark;
    }

    &:hover:not(.--disabled) .bds-radio__dot {
      background-color: $boreal-ui-success-dark;
    }
  }

  &.--error .bds-radio__button {
    border-color: $boreal-stroke-danger-base;
  }

  &.--disabled {
    .bds-radio__button {
      border-color: $boreal-stroke-default-light;
      background-color: $boreal-bg-neutral;
    }

    .bds-radio__label {
      color: $boreal-text-disabled;
    }

    &.--checked .bds-radio__button {
      border-color: $boreal-ui-primary-light;
    }

    &.--checked .bds-radio__dot {
      background-color: $boreal-ui-primary-light;
    }
  }

  .bds-radio__content {
    display: flex;
    align-items: center;
    gap: $boreal-spacing-3xs;
  }

  .bds-radio__icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .bds-radio__label {
    font-size: $boreal-typography-font-size-sm;
    font-weight: $boreal-typography-font-weight-regular;
    line-height: $boreal-typography-line-height-sm;
    color: $boreal-text-default;
  }
}
```

---

## Task 7: bds-radio-group scaffold _(tracker #13)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx`

Create the file with: imports, `LEAF_TAGS` constant, `LeafElement` type alias, `@Component` decorator, class declaration with `@AttachInternals`, `@Element`, `@State`, all `@Prop`, all `@Event`, the `radioElements` getter, and the `@Method` wrappers. No lifecycle, no listeners, no render logic yet — `render()` returns a stub `<Host />`.

```typescript
import { AttachInternals, Component, Element, Event, EventEmitter, Host, Listen, Method, Mixin, Prop, State, Watch, h } from '@stencil/core';
import type { IRadioGroup, RadioGroupChangeDetail } from './types/IRadioGroup';
import { formAssociatedMixin, type IFormControl } from '@/mixins/form-associated.mixin';
import { createId } from '@/utils';

type LeafElement = HTMLBdsRadioElement;

const LEAF_TAGS = ['BDS-RADIO'];

@Component({
  tag: 'bds-radio-group',
  styleUrl: 'bds-radio-group.scss',
  formAssociated: true,
})
export class BdsRadioGroup extends Mixin(formAssociatedMixin) implements IRadioGroup, IFormControl<string> {
  @AttachInternals() internals!: ElementInternals;
  @Element() el!: HTMLBdsRadioGroupElement;

  private readonly _id = createId('bds-radio-group');

  @State() private isDisabled: boolean = false;

  /** Name of the form control; submitted as the field key in FormData. */
  @Prop({ reflect: true }) readonly name!: string;

  /** Currently selected radio value. Synced to children on change. */
  @Prop({ mutable: true }) value: string = '';

  /** Group label rendered above the radio options. */
  @Prop() readonly label: string = '';

  /** Helper text rendered below the radio options. Shown in default state; replaced by errorMessage in error state. */
  @Prop() readonly helperText: string = '';

  /** Error message rendered below the radio options when error is true. Replaces helperText. */
  @Prop() readonly errorMessage: string = '';

  /** Tooltip text shown on the group label info icon. */
  @Prop() readonly info: string = '';

  /** Layout direction of the radio options. */
  @Prop({ reflect: true }) readonly orientation: 'horizontal' | 'vertical' = 'vertical';

  /** Identifies this group as a radio group. Scoped to 'radio'; extended in bds-radio-button plan. */
  @Prop({ reflect: true }) readonly type: 'radio' = 'radio';

  /** Disables all child radios and prevents selection. Also mirrored to isDisabled @State for form-level disable support. */
  @Prop({ reflect: true }) readonly disabled: boolean = false;

  /** Marks the group as required for form submission. Triggers validity error when no radio is selected. */
  @Prop({ reflect: true }) readonly required: boolean = false;

  /** Shows error styling on the group helper text. Propagated to all child radios. */
  @Prop({ reflect: true }) readonly error: boolean = false;

  /** Emitted when the selected radio changes. Payload includes the new value. */
  @Event() bdsChange!: EventEmitter<RadioGroupChangeDetail>;

  /** Emitted when the selected radio changes. Used for v-model two-way binding in Vue. */
  @Event() valueChange!: EventEmitter<string>;

  private get radioElements(): LeafElement[] {
    return Array.from(this.el.querySelectorAll<LeafElement>('bds-radio'));
  }

  @Method()
  async checkValidity(): Promise<boolean> {
    return this.internals.checkValidity();
  }

  @Method()
  async reportValidity(): Promise<boolean> {
    return this.internals.reportValidity();
  }

  render() { return <Host />; }
}
```

---

## Task 8: bds-radio-group child listeners _(tracker #14)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx`

Add to the class body (before `render()`):

- `handleRadioMount` — guards with `LEAF_TAGS`; stamps `name`, `disabled`, `error`, `checked` onto the newly mounted child
- `handleRadioChange` — guards with `LEAF_TAGS`; unchecks all siblings; updates `this.value`; syncs `internals.setFormValue`; emits both group events

```typescript
@Listen('bdsMount')
handleRadioMount(event: CustomEvent<{ element: HTMLElement }>) {
  const target = event.target as HTMLElement;
  if (!LEAF_TAGS.includes(target.tagName)) return;
  const child = event.detail.element as LeafElement;
  child.setAttribute('name', this.name);
  if (this.isDisabled) child.disabled = true;
  if (this.error) child.error = true;
  if (this.value && child.value === this.value) child.checked = true;
}

@Listen('bdsChange')
handleRadioChange(event: CustomEvent<{ checked: boolean; value: string }>) {
  const target = event.target as HTMLElement;
  if (!LEAF_TAGS.includes(target.tagName)) return;

  this.radioElements
    .filter(el => el !== target)
    .forEach(el => {
      el.checked = false;
      el.setAttribute('aria-checked', 'false');
    });

  this.value = event.detail.value;
  this.internals.setFormValue(this.value);
  this.updateTabIndexes(target as LeafElement);
  this.updateFormValidity();
  this.bdsChange.emit({ value: this.value });
  this.valueChange.emit(this.value);
}
```

---

## Task 9: bds-radio-group keyboard navigation _(tracker #15)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx`

Add to the class body:

- `handleKeyDown` — guard with `LEAF_TAGS`; Arrow keys call `navigateTo()` and `preventDefault()` (blocks page scroll)
- `navigateTo()` — filters disabled elements; wraps around circularly; selects next, updates `aria-checked` on all, syncs form value, calls `focus()`
- `updateTabIndexes()` — sets all to `tabindex="-1"`, promotes the active element to `tabindex="0"`

WAI-ARIA mandate: only one radio in the group has `tabindex=0` at any time (roving tabindex). Arrow keys both move focus AND select.

```typescript
@Listen('keydown')
handleKeyDown(event: KeyboardEvent) {
  const target = event.target as HTMLElement;
  if (!LEAF_TAGS.includes(target.tagName)) return;

  switch (event.key) {
    case 'ArrowDown':
    case 'ArrowRight':
      this.navigateTo(target as LeafElement, true);
      event.preventDefault();
      break;
    case 'ArrowUp':
    case 'ArrowLeft':
      this.navigateTo(target as LeafElement, false);
      event.preventDefault();
      break;
  }
}

private navigateTo(current: LeafElement, forward: boolean) {
  const elements = this.radioElements.filter(el => !el.disabled);
  const idx = elements.indexOf(current);
  const next = elements[(elements.length + idx + (forward ? 1 : -1)) % elements.length];
  if (!next) return;

  next.checked = true;
  next.setAttribute('aria-checked', 'true');
  this.radioElements.filter(el => el !== next).forEach(el => {
    el.checked = false;
    el.setAttribute('aria-checked', 'false');
  });
  this.value = next.value;
  this.internals.setFormValue(this.value);
  this.updateTabIndexes(next);
  this.updateFormValidity();
  this.bdsChange.emit({ value: this.value });
  this.valueChange.emit(this.value);
  (next as HTMLElement).focus();
}

private updateTabIndexes(active: LeafElement | null) {
  this.radioElements.forEach(el => el.setAttribute('tabindex', '-1'));
  if (active) active.setAttribute('tabindex', '0');
}
```

---

## Task 10: bds-radio-group @Watch + form lifecycle _(tracker #16)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx`

Add to the class body:

- `componentWillLoad` — seeds `isDisabled` from `disabled` prop (runs before first render; children not yet mounted)
- `@Watch('disabled')` + `override formDisabledCallback` — both update `isDisabled` @State and propagate to children. `formDisabledCallback` is called by the browser when the associated `<fieldset disabled>` or `<form>` disables the element — `override` is required because `formAssociatedMixin` already provides a base implementation; the group extends it by also propagating to children
- `@Watch('error')` — propagates error state to all children
- `@Watch('value')` — syncs `checked` on all children when value is set programmatically
- `formResetCallback` — clears value/checked on all children; restores keyboard entry-point
- `formAssociatedCallback` — syncs initial form value and validity when element is first associated with a form
- `formStateRestoreCallback` — restores value from browser session history or autofill
- `updateFormValidity()` — private; sets `valueMissing` when `required` and no value selected

```typescript
componentWillLoad() {
  this.isDisabled = this.disabled;
}

@Watch('disabled')
onDisabledChange(next: boolean) {
  this.isDisabled = next;
  this.radioElements.forEach(el => (el.disabled = next));
}

override formDisabledCallback(disabled: boolean) {
  this.isDisabled = disabled;
  this.radioElements.forEach(el => (el.disabled = disabled));
}

@Watch('error')
watchError(val: boolean) {
  this.radioElements.forEach(el => (el.error = val));
}

@Watch('value')
watchValue(val: string) {
  this.radioElements.forEach(el => {
    el.checked = el.value === val;
    el.setAttribute('aria-checked', String(el.checked));
  });
  const checked = this.radioElements.find(el => el.checked);
  if (checked) this.updateTabIndexes(checked);
}

formResetCallback() {
  this.value = '';
  this.radioElements.forEach(el => {
    el.checked = false;
    el.setAttribute('aria-checked', 'false');
  });
  this.internals.setFormValue(null);
  this.updateFormValidity();
  const first = this.radioElements.find(el => !el.disabled);
  if (first) this.updateTabIndexes(first);
}

formAssociatedCallback() {
  this.internals.setFormValue(this.value || null);
  this.updateFormValidity();
}

formStateRestoreCallback(state: string) {
  this.value = state;
  this.internals.setFormValue(state);
}

private updateFormValidity() {
  if (this.required && !this.value) {
    this.internals.setValidity({ valueMissing: true }, 'Please select an option.');
  } else {
    this.internals.setValidity({});
  }
}
```

---

## Task 11: bds-radio-group componentDidLoad + render() _(tracker #17)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx`

Add `componentDidLoad`, `updateLayoutCount`, `handleSlotChange`, and replace the stub `render()`.

**`componentDidLoad`** handles three responsibilities:

1. "Last checked wins" — if multiple children have `[checked]` in initial markup, only the last one stays checked (matches native `<input type="radio">` browser behaviour)
2. `updateLayoutCount()` — sets `--layout-count` CSS custom property for the horizontal grid
3. Roving tabindex init — promotes the checked radio (or first non-disabled) to `tabindex=0`

**`render()`** uses `isDisabled` (not `disabled`) for `typographyState` so form-level disable is reflected in label/helper colour.

```typescript
componentDidLoad() {
  const checkedChildren = this.radioElements.filter(el => el.checked);
  if (checkedChildren.length > 1) {
    checkedChildren.slice(0, -1).forEach(el => (el.checked = false));
  }
  this.updateLayoutCount();
  const checked = this.radioElements.find(el => el.checked);
  this.updateTabIndexes(checked ?? this.radioElements.find(el => !el.disabled) ?? null);
  this.updateFormValidity();
}

private updateLayoutCount() {
  this.el.style.setProperty('--layout-count', `${this.radioElements.length}`);
}

private handleSlotChange = () => this.updateLayoutCount();

render() {
  const labelId = `${this._id}-label`;
  const helperId = `${this._id}-helper`;
  const typographyState = this.isDisabled ? 'disabled' : this.error ? 'error' : 'default';
  const helperContent = this.error && this.errorMessage !== '' ? this.errorMessage : this.helperText;

  return (
    <Host
      class={{
        'bds-radio-group': true,
        '--disabled': this.isDisabled,
        '--error': this.error,
        '--required': this.required,
      }}
      role="radiogroup"
      aria-labelledby={this.label ? labelId : undefined}
      aria-describedby={helperContent !== '' ? helperId : undefined}
      aria-invalid={this.error ? 'true' : undefined}
      aria-required={this.required ? 'true' : undefined}
    >
      {this.label && (
        <bds-typography
          id={labelId}
          variant="label"
          state={typographyState}
          required={this.required}
          tooltipText={this.info !== '' ? this.info : undefined}
        >
          {this.label}
        </bds-typography>
      )}
      <div class="bds-radio-group__options">
        <slot onSlotchange={this.handleSlotChange} />
      </div>
      {helperContent !== '' && (
        <bds-typography id={helperId} variant="helper" state={typographyState}>
          {helperContent}
        </bds-typography>
      )}
    </Host>
  );
}
```

**Manual test (waiveable):**

- Render a `<bds-radio-group name="g" label="Choose" required>` with three radios
- Verify: label renders above options, helper text below
- Select one radio → `bdsChange` and `valueChange` both fire; siblings deselected
- Arrow keys navigate and select; wraps at ends; skips disabled children
- `required` with no selection → browser shows "Please select an option" on form submit

---

## Task 11b: bds-radio-group JSDoc audit

**File:** `bds-radio-group/bds-radio-group.tsx`

Verify `bds-radio-group.tsx` satisfies all rules in `.ai/guidelines/jsdoc-template.md`:

- [ ] Class-level JSDoc block present with component description and `@slot` tags for all slots (`default`, and any named slots defined in `render()`).
- [ ] Every `@Prop()` has an inline `/** */` block immediately above the decorator.
- [ ] `valueChange` `@Event()` has an inline `/** */` block. Confirm it uses bare `@Event()` — it is a consumer-facing event, not an internal coordination event.
- [ ] No `@attr`, `@property`, `@fires`, `@element`, `@cssprop`, or `@internal` in the class-level block.
- [ ] No `@part` tags (light DOM, no shadow boundary).
- [ ] CSS custom properties (if any) are documented with `@prop` in `bds-radio-group.scss`, not `@cssprop` in the TSX.
- [ ] `override formDisabledCallback` has a JSDoc block describing what it propagates to children.

---

## Task 12: bds-radio-group tests _(tracker #6)_

**Files:** `__test__/bds-radio-group.basics.spec.ts`, `bds-radio-group.a11y.spec.ts`, `bds-radio-group.events.spec.ts`, `bds-radio-group.keyboard.spec.ts`

### bds-radio-group.basics.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadio } from "../../bds-radio/bds-radio";
import { BdsRadioGroup } from "../bds-radio-group";
import { attachInternals, suppressConsoleError } from "@/utils";

describe("bds-radio-group basics", () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it("enforces single selection", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll("bds-radio");
    ra.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(ra.checked).toBe(true);
    rb.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(rb.checked).toBe(true);
    expect(ra.checked).toBe(false);
  });

  it("propagates name to children on mount", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="mygroup">
          <bds-radio value="a" label="A"></bds-radio>
        </bds-radio-group>
      `,
    });
    const radio = root.querySelector("bds-radio") as any;
    expect(radio.name).toBe("mygroup");
  });

  it("propagates disabled to children", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g" disabled>
          <bds-radio value="a" label="A"></bds-radio>
        </bds-radio-group>
      `,
    });
    await waitForChanges();
    const radio = root.querySelector("bds-radio");
    expect(radio.disabled).toBe(true);
  });

  it("resolves last-checked-wins on initial markup", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" checked label="A"></bds-radio>
          <bds-radio value="b" checked label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll("bds-radio");
    expect(ra.checked).toBe(false);
    expect(rb.checked).toBe(true);
  });
});
```

### bds-radio-group.a11y.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadio } from "../../bds-radio/bds-radio";
import { BdsRadioGroup } from "../bds-radio-group";
import { attachInternals, suppressConsoleError } from "@/utils";

describe("bds-radio-group a11y", () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it("has role=radiogroup", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: '<bds-radio-group name="g"></bds-radio-group>',
    });
    expect(root.getAttribute("role")).toBe("radiogroup");
  });

  it("sets aria-labelledby when label is present", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: '<bds-radio-group name="g" label="Choose one"></bds-radio-group>',
    });
    expect(root.getAttribute("aria-labelledby")).toBe("bds-radio-group-label");
  });

  it("sets aria-required when required", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: '<bds-radio-group name="g" required></bds-radio-group>',
    });
    expect(root.getAttribute("aria-required")).toBe("true");
  });

  it("only one radio has tabindex=0", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const focusable = Array.from(root.querySelectorAll("bds-radio")).filter(
      (el) => el.getAttribute("tabindex") === "0",
    );
    expect(focusable.length).toBe(1);
  });
});
```

### bds-radio-group.events.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadio } from "../../bds-radio/bds-radio";
import { BdsRadioGroup } from "../bds-radio-group";
import { attachInternals, suppressConsoleError } from "@/utils";

describe("bds-radio-group events", () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it("emits bdsChange with selected value", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="x" label="X"></bds-radio>
        </bds-radio-group>
      `,
    });
    const spy = jest.fn();
    root.addEventListener("bdsChange", spy);
    root.querySelector("bds-radio").dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy.mock.calls[0][0].detail).toEqual({ value: "x" });
  });

  it("emits valueChange with selected value string", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="y" label="Y"></bds-radio>
        </bds-radio-group>
      `,
    });
    const spy = jest.fn();
    root.addEventListener("valueChange", spy);
    root.querySelector("bds-radio").dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    expect(spy.mock.calls[0][0].detail).toBe("y");
  });
});
```

### bds-radio-group.keyboard.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadio } from "../../bds-radio/bds-radio";
import { BdsRadioGroup } from "../bds-radio-group";
import { attachInternals, suppressConsoleError } from "@/utils";

describe("bds-radio-group keyboard navigation", () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it("ArrowDown selects next and moves tabindex", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll("bds-radio");
    ra.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    ra.dispatchEvent(
      new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }),
    );
    await waitForChanges();
    expect(rb.checked).toBe(true);
    expect(ra.checked).toBe(false);
    expect(rb.getAttribute("tabindex")).toBe("0");
    expect(ra.getAttribute("tabindex")).toBe("-1");
  });

  it("ArrowDown wraps from last to first", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll("bds-radio");
    rb.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    rb.dispatchEvent(
      new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }),
    );
    await waitForChanges();
    expect(ra.checked).toBe(true);
    expect(rb.checked).toBe(false);
  });

  it("ArrowUp selects previous", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll("bds-radio");
    rb.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    rb.dispatchEvent(
      new KeyboardEvent("keydown", { key: "ArrowUp", bubbles: true }),
    );
    await waitForChanges();
    expect(ra.checked).toBe(true);
    expect(rb.checked).toBe(false);
  });

  it("skips disabled radios during navigation", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" disabled label="B"></bds-radio>
          <bds-radio value="c" label="C"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, , rc] = root.querySelectorAll("bds-radio");
    ra.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    ra.dispatchEvent(
      new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }),
    );
    await waitForChanges();
    expect(rc.checked).toBe(true);
    expect(ra.checked).toBe(false);
  });

  it("restores tabindex=0 to first non-disabled radio after form reset", async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll("bds-radio");
    rb.dispatchEvent(new MouseEvent("click"));
    await waitForChanges();
    (root as any).formResetCallback?.();
    await waitForChanges();
    expect(ra.getAttribute("tabindex")).toBe("0");
    expect(rb.getAttribute("tabindex")).toBe("-1");
  });
});
```

---

## Task 13: bds-radio-group SCSS _(tracker #7)_

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.scss`

Grid layout using `--layout-count` CSS custom property (set by JS on `slotchange`) for horizontal orientation.

```scss
bds-radio-group {
  display: flex;
  flex-direction: column;
  gap: $boreal-spacing-2xs;

  .bds-radio-group__options {
    display: grid;
    grid-template-columns: 1fr;
    gap: $boreal-spacing-xs;
  }

  &[orientation="horizontal"] .bds-radio-group__options {
    grid-template-columns: repeat(var(--layout-count, 1), auto);
    gap: $boreal-spacing-ml;
    justify-content: start;
  }
}
```

---

## Task 14: Vue v-model registration _(tracker #18)_

**File to modify:** `packages/boreal-web-components/targets/vue-output-target.ts`

Add one entry to the `componentModels` array so `@stencil/vue-output-target` generates a v-model-enabled proxy for `bds-radio-group`:

```typescript
{
  elements: ['bds-radio-group'],
  event: 'valueChange',
  targetAttr: 'value',
},
```

This follows the identical pattern used by `bds-text-field`. The `valueChange` event is already emitted in `handleRadioChange` and `navigateTo` in the group TSX — no component changes are needed, only the config entry.

Per `.claude/memory/stencil-form-control-interfaces.md`: this must land in the same PR as the finished component.

**Manual test (waiveable):**

After rebuilding `boreal-vue`, verify in a Vue template:

```vue
<BdsRadioGroup v-model="selected" name="test">
  <BdsRadio value="a" label="A" />
  <BdsRadio value="b" label="B" />
</BdsRadioGroup>
```

Selecting a radio should update `selected` without an explicit `@valueChange` listener.

---

## Task 15: Storybook stories _(tracker #8)_

**File:**

- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts`

`bds-radio` has **no story file** — it is a private building block and must not appear as a standalone Storybook entry. All stories render `bds-radio-group` containing `bds-radio` children.

Follow the existing Lit HTML story convention in this repo (see other forms stories for the import pattern and `argTypes` shape).

**bds-radio-group stories must cover:**

- Default `type=radio`, vertical (default) and horizontal orientation
- Error state (group-level `error` prop)
- Disabled state (group-level `disabled` prop)
- Required state with form reset demonstration

---

## Task 16: MDX documentation _(tracker #9)_

**File:**

- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.mdx`

`bds-radio` has **no MDX file** — it is a private building block. A single MDX file documents the complete radio experience through `bds-radio-group`.

The MDX doc must include:

- Component description and intended use
- **When not to use:** for a single binary choice, use `bds-checkbox` instead
- `bds-radio-group` props (type, default, description)
- `bds-radio` child element props in a secondary "Child element props" section (label, value, disabled, error; default slot for label content; `slot="icon"` for 16×16 icon)
- All emitted events (`bdsChange`, `valueChange` on the group)
- **bds-radio-group — Keyboard interaction table:**

  | Key                    | Action                                                             |
  | ---------------------- | ------------------------------------------------------------------ |
  | Tab                    | Enters group at focused radio (checked one, or first non-disabled) |
  | Tab                    | Exits group to next focusable element outside group                |
  | ArrowDown / ArrowRight | Moves focus to next radio AND selects it; wraps                    |
  | ArrowUp / ArrowLeft    | Moves focus to previous radio AND selects it; wraps                |
  | Space                  | Selects the currently focused radio (no-op if already selected)    |

- **bds-radio-group — Form integration note:** how to read `value` in a `<form>` via `FormData`; mention that the group is the FACE component (other radios are plain elements); `v-model` works via the `valueChange` event
- **bds-radio-group — Accessibility note:** `role="radiogroup"` + `role="radio"` hierarchy, `aria-checked`, roving tabindex explained

---

## Critical Constraints

- **No `:host` selectors** — all selectors target element tag names directly (`bds-radio { … }`)
- **`@AttachInternals()` on `bds-radio-group` class body only** — never in a mixin factory (see `.claude/memory/stencil-face-attach-internals.md`)
- Individual leaf components are NOT form-associated — no FACE lifecycle, no `isDisabled` `@State()` mirror needed
- `disabled` and `error` on leaf components are plain `@Prop({ reflect: true })` — no state mirror
- No `@use` in SCSS files — `$boreal-*` tokens are globally injected via `injectGlobalPaths` in `stencil.config.ts`; adding `@use` causes a Sass double-import error (see `.claude/memory/stencil-sass-inject-global-paths-constraint.md`)
- No inline code comments; no `Co-Authored-By` commit trailers
- Interface files: `IRadio.ts`, `IRadioGroup.ts` (no `Bds` prefix in file names — project convention per memory)

---

## Verification

```bash
# All radio tests
eval "$(fnm env --shell bash)" && fnm use && \
  pnpm --filter boreal-web-components test -- --testPathPattern="bds-radio"

# TypeScript clean check
eval "$(fnm env --shell bash)" && fnm use && \
  pnpm --filter boreal-web-components exec tsc --noEmit

# Storybook visual check
pnpm dev:docs
# Forms/Radio       → circle indicator, label, all states (default/hover/focus/checked/error/disabled)
# Forms/RadioGroup  → vertical (default), horizontal, error, disabled, required
# Keyboard (group)  → Tab enters group at first non-disabled radio; ArrowDown/Right selects next;
#                     wraps around; skips disabled; ArrowUp/Left selects previous; Space selects focused
```
