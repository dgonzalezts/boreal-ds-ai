---
status: pending
---

# bds-radio + bds-radio-group Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Scope:** `bds-radio` (leaf, circle variant) + `bds-radio-group` (form-associated orchestrator).  
`bds-radio-button` and `bds-radio-card` are out of scope — see their own plans.

**Architecture:**
- `bds-radio-group` is the **sole FACE** component (`formAssociated: true`, `@AttachInternals()`). It owns `setFormValue`, `setValidity`, and `formResetCallback`.
- `bds-radio` is NOT form-associated. It fires a `bdsRadioMount` bubbling event on mount so the group can register it without imperative DOM queries.
- The group enforces single selection by listening to `bdsChange` from children and unchecking siblings.
- The `LEAF_TAGS` constant in the group is designed to be extended in subsequent plans (`bds-radio-button`, etc.).

**Tech Stack:** Stencil, TypeScript, SCSS, `boreal-styleguidelines` design tokens, Storybook (Lit HTML stories + MDX docs), Jest / `@stencil/core/testing`.

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

apps/boreal-docs/src/stories/forms/bds-radio/
  bds-radio.stories.ts
  bds-radio.mdx
apps/boreal-docs/src/stories/forms/bds-radio-group/
  bds-radio-group.stories.ts
  bds-radio-group.mdx
```

---

## Task 1: Type interfaces

**Files:**
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/types/IRadio.ts`
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/types/IRadioGroup.ts`

### IRadio.ts

```typescript
import type { EventEmitter } from '@stencil/core/internal';

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
  label: string;
  bdsChange: EventEmitter<RadioChangeDetail>;
  bdsRadioMount: EventEmitter<RadioMountDetail>;
}
```

### IRadioGroup.ts

```typescript
import type { EventEmitter } from '@stencil/core/internal';

export interface RadioGroupChangeDetail {
  value: string;
}

export interface IRadioGroup {
  name: string;
  value: string;
  label: string;
  helperText: string;
  orientation: 'horizontal' | 'vertical';
  type: 'radio';
  disabled: boolean;
  required: boolean;
  error: boolean;
  bdsChange: EventEmitter<RadioGroupChangeDetail>;
  valueChange: EventEmitter<string>;
}
```

> **Note:** `type` is scoped to `'radio'` for this plan. It will be extended to `'radio' | 'radiobutton'` in the `bds-radio-button` plan.

---

## Task 2: bds-radio TSX

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.tsx`

`bds-radio` is NOT form-associated. It carries `role="radio"` and `tabindex` on the host. `select()` guards with `if (this.disabled || this.checked) return` — radios do not toggle off. Space key triggers selection. On mount, fires `bdsRadioMount` so the group can register it.

```typescript
import { Component, Element, Event, EventEmitter, Host, Prop, h } from '@stencil/core';
import type { IRadio, RadioChangeDetail, RadioMountDetail } from './types/IRadio';

@Component({
  tag: 'bds-radio',
  styleUrl: 'bds-radio.scss',
  scoped: false,
})
export class BdsRadio implements IRadio {
  @Element() el!: HTMLBdsRadioElement;

  @Prop({ mutable: true, reflect: true }) checked: boolean = false;
  @Prop({ reflect: true }) readonly disabled: boolean = false;
  @Prop() readonly value: string = 'on';
  @Prop() readonly label: string = '';
  @Prop({ reflect: true }) readonly error: boolean = false;

  @Event() bdsChange!: EventEmitter<RadioChangeDetail>;
  @Event({ bubbles: true, composed: true }) bdsRadioMount!: EventEmitter<RadioMountDetail>;

  componentDidLoad() {
    this.el.setAttribute('role', 'radio');
    this.el.setAttribute('aria-checked', String(this.checked));
    this.el.setAttribute('tabindex', '-1');
    this.bdsRadioMount.emit({ element: this.el });
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
          'bds-radio': true,
          '--checked': this.checked,
          '--error': this.error,
          '--disabled': this.disabled,
        }}
        onClick={this.handleClick}
        onKeyDown={this.handleKeyDown}
      >
        <span class="bds-radio__button">
          <span class="bds-radio__dot" />
        </span>
        <span class="bds-radio__content">
          <span class="bds-radio__label">{this.label || <slot />}</span>
        </span>
      </Host>
    );
  }
}
```

**Manual test (waiveable):**
- Render `<bds-radio label="Option A" value="a"></bds-radio>` in isolation
- Verify it renders a circle indicator + label text
- Click → sets `checked` attribute, emits `bdsChange` (check DevTools)
- Space key while focused → also triggers selection
- Second click on already-checked radio → no event emitted

---

## Task 3: bds-radio tests

**Files:** `__test__/bds-radio.basics.spec.ts`, `bds-radio.a11y.spec.ts`, `bds-radio.events.spec.ts`

### bds-radio.basics.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../bds-radio';

describe('bds-radio basics', () => {
  it('renders with default props', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="Option"></bds-radio>',
    });
    expect(root).toBeTruthy();
    expect(root.getAttribute('role')).toBe('radio');
    expect(root.getAttribute('aria-checked')).toBe('false');
  });

  it('reflects checked state', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio checked label="Option"></bds-radio>',
    });
    expect(root.classList.contains('--checked')).toBe(true);
  });

  it('reflects disabled state', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio disabled label="Option"></bds-radio>',
    });
    expect(root.classList.contains('--disabled')).toBe(true);
  });

  it('reflects error state', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio error label="Option"></bds-radio>',
    });
    expect(root.classList.contains('--error')).toBe(true);
  });

  it('renders circle indicator and label', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="My Label"></bds-radio>',
    });
    expect(root.querySelector('.bds-radio__button')).toBeTruthy();
    expect(root.querySelector('.bds-radio__dot')).toBeTruthy();
    expect(root.querySelector('.bds-radio__label').textContent).toBe('My Label');
  });
});
```

### bds-radio.a11y.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../bds-radio';

describe('bds-radio a11y', () => {
  it('has role=radio', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(root.getAttribute('role')).toBe('radio');
  });

  it('aria-checked is false by default', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(root.getAttribute('aria-checked')).toBe('false');
  });

  it('aria-checked updates to true on click', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    root.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(root.getAttribute('aria-checked')).toBe('true');
  });

  it('has tabindex attribute after mount', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(root.hasAttribute('tabindex')).toBe(true);
  });
});
```

### bds-radio.events.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../bds-radio';

describe('bds-radio events', () => {
  it('emits bdsChange with correct payload on click', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A" value="a"></bds-radio>',
    });
    const spy = jest.fn();
    root.addEventListener('bdsChange', spy);
    root.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0].detail).toEqual({ checked: true, value: 'a' });
  });

  it('does not emit bdsChange when already checked', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio checked label="A" value="a"></bds-radio>',
    });
    const spy = jest.fn();
    root.addEventListener('bdsChange', spy);
    root.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(spy).not.toHaveBeenCalled();
  });

  it('does not emit bdsChange when disabled', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio disabled label="A" value="a"></bds-radio>',
    });
    const spy = jest.fn();
    root.addEventListener('bdsChange', spy);
    root.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(spy).not.toHaveBeenCalled();
  });

  it('emits bdsChange on Space key', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A" value="a"></bds-radio>',
    });
    const spy = jest.fn();
    root.addEventListener('bdsChange', spy);
    root.dispatchEvent(new KeyboardEvent('keydown', { key: ' ' }));
    await waitForChanges();
    expect(spy).toHaveBeenCalledTimes(1);
  });

  it('emits bdsRadioMount on componentDidLoad', async () => {
    const spy = jest.fn();
    document.addEventListener('bdsRadioMount', spy);
    await newSpecPage({
      components: [BdsRadio],
      html: '<bds-radio label="A"></bds-radio>',
    });
    expect(spy).toHaveBeenCalledTimes(1);
    document.removeEventListener('bdsRadioMount', spy);
  });
});
```

---

## Task 4: bds-radio SCSS

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.scss`

Classic circle radio styles only. No radiobutton or radiocard descendant blocks — those belong in their own component SCSS files.

```scss
@use 'boreal-styleguidelines' as *;

bds-radio {
  display: inline-flex;
  align-items: center;
  gap: $boreal-spacing-2xs;
  cursor: pointer;
  outline: none;

  &.--disabled {
    cursor: not-allowed;
    pointer-events: none;
  }

  .bds-radio__button {
    flex-shrink: 0;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 2px solid $boreal-stroke-default-light;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.2s ease;
  }

  .bds-radio__dot {
    width: 8px;
    height: 8px;
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
    gap: $boreal-spacing-2xs;
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

## Task 5: bds-radio-group TSX

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx`

FACE on the group (BEEQ pattern). Key responsibilities:

1. `@Listen('bdsRadioMount')` — stamp `name`, `checked`, `disabled`, `error` on child; set initial `tabindex`
2. `@Listen('bdsChange')` — enforce single selection; update `this.value`; call `internals.setFormValue`; emit group events; update tabindexes
3. `@Listen('keydown')` — roving tabindex arrow-key navigation (wraps, skips disabled)
4. `@Watch('disabled')` + `@Watch('error')` — propagate to all children
5. `@Watch('value')` — sync children `checked` states
6. `componentDidLoad` — "last checked wins" conflict resolution; set initial `--layout-count`
7. `slotchange` handler — update `--layout-count`
8. `formResetCallback` — clear value/checked; restore keyboard entry-point tabindex

`LEAF_TAGS` is defined as a constant so it can be extended when `bds-radio-button` is added in a subsequent plan.

```typescript
import { AttachInternals, Component, Element, Event, EventEmitter, Host, Listen, Prop, Watch, h } from '@stencil/core';
import type { IRadioGroup, RadioGroupChangeDetail } from './types/IRadioGroup';

type LeafElement = HTMLBdsRadioElement;

const LEAF_TAGS = ['BDS-RADIO'];

@Component({
  tag: 'bds-radio-group',
  styleUrl: 'bds-radio-group.scss',
  formAssociated: true,
  scoped: false,
})
export class BdsRadioGroup implements IRadioGroup {
  @AttachInternals() internals!: ElementInternals;
  @Element() el!: HTMLBdsRadioGroupElement;

  @Prop({ reflect: true }) readonly name!: string;
  @Prop({ mutable: true }) value: string = '';
  @Prop() readonly label: string = '';
  @Prop() readonly helperText: string = '';
  @Prop({ reflect: true }) readonly orientation: 'horizontal' | 'vertical' = 'vertical';
  @Prop({ reflect: true }) readonly type: 'radio' = 'radio';
  @Prop({ reflect: true }) readonly disabled: boolean = false;
  @Prop({ reflect: true }) readonly required: boolean = false;
  @Prop({ reflect: true }) readonly error: boolean = false;

  @Event() bdsChange!: EventEmitter<RadioGroupChangeDetail>;
  @Event() valueChange!: EventEmitter<string>;

  private get radioElements(): LeafElement[] {
    return Array.from(this.el.querySelectorAll<LeafElement>('bds-radio'));
  }

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

  @Listen('bdsRadioMount')
  handleRadioMount(event: CustomEvent<{ element: HTMLElement }>) {
    const child = event.detail.element as LeafElement;
    (child as any).name = this.name;
    if (this.disabled) child.disabled = true;
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

  @Watch('disabled')
  watchDisabled(val: boolean) {
    this.radioElements.forEach(el => (el.disabled = val));
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
  }

  formStateRestoreCallback(state: string) {
    this.value = state;
    this.internals.setFormValue(state);
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

  private updateFormValidity() {
    if (this.required && !this.value) {
      this.internals.setValidity({ valueMissing: true }, 'Please select an option.');
    } else {
      this.internals.setValidity({});
    }
  }

  private updateLayoutCount() {
    this.el.style.setProperty('--layout-count', `${this.radioElements.length}`);
  }

  private handleSlotChange = () => this.updateLayoutCount();

  render() {
    return (
      <Host
        class={{
          'bds-radio-group': true,
          '--disabled': this.disabled,
          '--error': this.error,
          '--required': this.required,
        }}
        role="radiogroup"
        aria-labelledby={this.label ? 'bds-radio-group-label' : undefined}
        aria-required={this.required ? 'true' : undefined}
      >
        {this.label && (
          <span class="bds-radio-group__label" id="bds-radio-group-label">
            {this.label}
          </span>
        )}
        <div class="bds-radio-group__options">
          <slot onSlotchange={this.handleSlotChange} />
        </div>
        {this.helperText && (
          <span class="bds-radio-group__helper">{this.helperText}</span>
        )}
      </Host>
    );
  }
}
```

---

## Task 6: bds-radio-group tests

**Files:** `__test__/bds-radio-group.basics.spec.ts`, `bds-radio-group.a11y.spec.ts`, `bds-radio-group.events.spec.ts`, `bds-radio-group.keyboard.spec.ts`

### bds-radio-group.basics.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../../bds-radio/bds-radio';
import { BdsRadioGroup } from '../bds-radio-group';

describe('bds-radio-group basics', () => {
  it('enforces single selection', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll('bds-radio');
    ra.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(ra.checked).toBe(true);
    rb.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(rb.checked).toBe(true);
    expect(ra.checked).toBe(false);
  });

  it('propagates name to children on mount', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="mygroup">
          <bds-radio value="a" label="A"></bds-radio>
        </bds-radio-group>
      `,
    });
    const radio = root.querySelector('bds-radio') as any;
    expect(radio.name).toBe('mygroup');
  });

  it('propagates disabled to children', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g" disabled>
          <bds-radio value="a" label="A"></bds-radio>
        </bds-radio-group>
      `,
    });
    await waitForChanges();
    const radio = root.querySelector('bds-radio');
    expect(radio.disabled).toBe(true);
  });

  it('resolves last-checked-wins on initial markup', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" checked label="A"></bds-radio>
          <bds-radio value="b" checked label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll('bds-radio');
    expect(ra.checked).toBe(false);
    expect(rb.checked).toBe(true);
  });
});
```

### bds-radio-group.a11y.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../../bds-radio/bds-radio';
import { BdsRadioGroup } from '../bds-radio-group';

describe('bds-radio-group a11y', () => {
  it('has role=radiogroup', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: '<bds-radio-group name="g"></bds-radio-group>',
    });
    expect(root.getAttribute('role')).toBe('radiogroup');
  });

  it('sets aria-labelledby when label is present', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: '<bds-radio-group name="g" label="Choose one"></bds-radio-group>',
    });
    expect(root.getAttribute('aria-labelledby')).toBe('bds-radio-group-label');
  });

  it('sets aria-required when required', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: '<bds-radio-group name="g" required></bds-radio-group>',
    });
    expect(root.getAttribute('aria-required')).toBe('true');
  });

  it('only one radio has tabindex=0', async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const focusable = Array.from(root.querySelectorAll('bds-radio')).filter(
      el => el.getAttribute('tabindex') === '0'
    );
    expect(focusable.length).toBe(1);
  });
});
```

### bds-radio-group.events.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../../bds-radio/bds-radio';
import { BdsRadioGroup } from '../bds-radio-group';

describe('bds-radio-group events', () => {
  it('emits bdsChange with selected value', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="x" label="X"></bds-radio>
        </bds-radio-group>
      `,
    });
    const spy = jest.fn();
    root.addEventListener('bdsChange', spy);
    root.querySelector('bds-radio').dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(spy.mock.calls[0][0].detail).toEqual({ value: 'x' });
  });

  it('emits valueChange with selected value string', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="y" label="Y"></bds-radio>
        </bds-radio-group>
      `,
    });
    const spy = jest.fn();
    root.addEventListener('valueChange', spy);
    root.querySelector('bds-radio').dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    expect(spy.mock.calls[0][0].detail).toBe('y');
  });
});
```

### bds-radio-group.keyboard.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../../bds-radio/bds-radio';
import { BdsRadioGroup } from '../bds-radio-group';

describe('bds-radio-group keyboard navigation', () => {
  it('ArrowDown selects next and moves tabindex', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll('bds-radio');
    ra.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    ra.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
    await waitForChanges();
    expect(rb.checked).toBe(true);
    expect(ra.checked).toBe(false);
    expect(rb.getAttribute('tabindex')).toBe('0');
    expect(ra.getAttribute('tabindex')).toBe('-1');
  });

  it('ArrowDown wraps from last to first', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll('bds-radio');
    rb.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    rb.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
    await waitForChanges();
    expect(ra.checked).toBe(true);
    expect(rb.checked).toBe(false);
  });

  it('ArrowUp selects previous', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll('bds-radio');
    rb.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    rb.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
    await waitForChanges();
    expect(ra.checked).toBe(true);
    expect(rb.checked).toBe(false);
  });

  it('skips disabled radios during navigation', async () => {
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
    const [ra, , rc] = root.querySelectorAll('bds-radio');
    ra.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    ra.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
    await waitForChanges();
    expect(rc.checked).toBe(true);
    expect(ra.checked).toBe(false);
  });

  it('restores tabindex=0 to first non-disabled radio after form reset', async () => {
    const { root, waitForChanges } = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="g">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });
    const [ra, rb] = root.querySelectorAll('bds-radio');
    rb.dispatchEvent(new MouseEvent('click'));
    await waitForChanges();
    (root as any).formResetCallback?.();
    await waitForChanges();
    expect(ra.getAttribute('tabindex')).toBe('0');
    expect(rb.getAttribute('tabindex')).toBe('-1');
  });
});
```

---

## Task 7: bds-radio-group SCSS

**File:** `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.scss`

Grid layout using `--layout-count` CSS custom property (set by JS on `slotchange`) for horizontal orientation.

```scss
@use 'boreal-styleguidelines' as *;

bds-radio-group {
  display: flex;
  flex-direction: column;
  gap: $boreal-spacing-2xs;

  .bds-radio-group__label {
    font-size: $boreal-typography-font-size-xs;
    font-weight: $boreal-typography-font-weight-semibold;
    line-height: $boreal-typography-line-height-xs;
    color: $boreal-text-default-darker;
  }

  .bds-radio-group__options {
    display: grid;
    grid-template-columns: 1fr;
    gap: $boreal-spacing-xs;
  }

  &[orientation='horizontal'] .bds-radio-group__options {
    grid-template-columns: repeat(var(--layout-count, 1), auto);
    gap: $boreal-spacing-ml;
    justify-content: start;
  }

  .bds-radio-group__helper {
    font-size: $boreal-typography-font-size-xs;
    font-weight: $boreal-typography-font-weight-regular;
    line-height: $boreal-typography-line-height-xs;
    color: $boreal-text-default-light;
  }

  &.--error .bds-radio-group__helper {
    color: $boreal-text-danger;
  }
}
```

---

## Task 8: Storybook stories

**Files:**
- `apps/boreal-docs/src/stories/forms/bds-radio/bds-radio.stories.ts`
- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts`

Follow the existing Lit HTML story convention in this repo (see other forms stories for the import pattern and `argTypes` shape).

**bds-radio-group stories must cover:**
- Default `type=radio`, vertical (default) and horizontal orientation
- Error state (group-level `error` prop)
- Disabled state (group-level `disabled` prop)
- Required state with form reset demonstration

---

## Task 9: MDX documentation

**Files:**
- `apps/boreal-docs/src/stories/forms/bds-radio/bds-radio.mdx`
- `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.mdx`

Each MDX doc must include:
- Component description and intended use
- All available props (type, default, description)
- All available slots (bds-radio: default slot for label content)
- All emitted events
- **bds-radio-group — Keyboard interaction table:**

  | Key | Action |
  |-----|--------|
  | Tab | Enters group at focused radio (checked one, or first non-disabled) |
  | Tab | Exits group to next focusable element outside group |
  | ArrowDown / ArrowRight | Moves focus to next radio AND selects it; wraps |
  | ArrowUp / ArrowLeft | Moves focus to previous radio AND selects it; wraps |
  | Space | Selects the currently focused radio (no-op if already selected) |

- **bds-radio-group — Form integration note:** how to read `value` in a `<form>` via `FormData`; mention that the group is the FACE component (other radios are plain elements)
- **bds-radio-group — Accessibility note:** `role="radiogroup"` + `role="radio"` hierarchy, `aria-checked`, roving tabindex explained

---

## Critical Constraints

- **No `:host` selectors** — all selectors target element tag names directly (`bds-radio { … }`)
- **`@AttachInternals()` on `bds-radio-group` class body only** — never in a mixin factory (see `.claude/memory/stencil-face-attach-internals.md`)
- Individual leaf components are NOT form-associated — no FACE lifecycle, no `isDisabled` `@State()` mirror needed
- `disabled` and `error` on leaf components are plain `@Prop({ reflect: true })` — no state mirror
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
