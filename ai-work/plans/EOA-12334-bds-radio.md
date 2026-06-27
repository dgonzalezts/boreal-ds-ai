---
ticket: EOA-12334
component: bds-radio
status: done
created: 2026-05-19
---

# bds-radio + bds-radio-group Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the `bds-radio` (FACE form control) and `bds-radio-group` (orchestrator) compound component pair with three visual variants (radio, radiobutton, radiocard) following the Boreal DS Stencil patterns.

**Architecture:** `bds-radio` is a form-associated custom element that fires a `bdsRadioMount` bubbling event on mount so `bds-radio-group` can register it without querying the DOM imperatively. The group enforces single selection by listening to `bdsChange` from children and unchecking siblings. Visual variants (`radio`, `radiobutton`, `radiocard`) are propagated via the reflected `type` attribute on the group using CSS descendant selectors — no JS injection required.

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
      bds-radio.variants.spec.ts
    types/
      IRadio.ts
  bds-radio-group/
    bds-radio-group.tsx
    bds-radio-group.scss
    __test__/
      bds-radio-group.basics.spec.ts
      bds-radio-group.a11y.spec.ts
      bds-radio-group.events.spec.ts
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

### Step 1: Create IRadio.ts

```typescript
// packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/types/IRadio.ts
import type { EventEmitter } from '@stencil/core/internal';

export interface RadioChangeDetail {
  /** Whether the radio is now checked. */
  checked: boolean;
  /** The value of this radio. */
  value: string;
}

export interface RadioMountDetail {
  /** The host element of the mounting radio. */
  element: HTMLElement;
}

export interface IRadio {
  checked: boolean;
  error: boolean;
  value: string;
  label: string;
  valueChange: EventEmitter<boolean>;
  bdsChange: EventEmitter<RadioChangeDetail>;
}
```

### Step 2: Create IRadioGroup.ts

```typescript
// packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/types/IRadioGroup.ts
import type { EventEmitter } from '@stencil/core/internal';

export interface RadioGroupChangeDetail {
  /** The value of the newly-selected radio. */
  value: string;
}

export type RadioGroupOrientation = 'horizontal' | 'vertical';
export type RadioGroupType = 'radio' | 'radiobutton' | 'radiocard';

export interface IRadioGroup {
  name: string;
  value: string;
  label: string;
  helperText: string;
  orientation: RadioGroupOrientation;
  type: RadioGroupType;
  disabled: boolean;
  required: boolean;
  error: boolean;
  valueChange: EventEmitter<string>;
  bdsChange: EventEmitter<RadioGroupChangeDetail>;
}
```

### Step 3: Commit

```bash
git add packages/boreal-web-components/src/components/forms/bds-radio/
git commit -m "feat(web-components): EOA-12334 add bds-radio type interfaces"
```

---

## Task 2: bds-radio TSX implementation

**Files:**
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.tsx`

### Step 1: Write the full implementation

```tsx
// packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.tsx
import {
  AttachInternals,
  Component,
  Element,
  Event,
  EventEmitter,
  Host,
  Mixin,
  Prop,
  State,
  Watch,
  h,
} from '@stencil/core';

import type { IRadio, RadioChangeDetail, RadioMountDetail } from './types/IRadio';
import { formAssociatedMixin, type IFormControl } from '@/mixins/form-associated.mixin';
import { setFormValue } from '@/utils/form';
import { Attributes, inheritAriaAttributes } from '@/utils/a11y/attributes';

/**
 * Radio button form control. Use inside a `bds-radio-group` for mutual exclusion.
 *
 * @summary A single radio button with label, icon slot, and full form association.
 *
 * @slot icon - Optional 16 × 16 icon displayed before the label text.
 * @slot - Default slot for label content when no `label` prop is provided.
 *
 * @fires valueChange - Emitted when the checked state changes (for 2-way binding / v-model).
 * @fires bdsChange   - Emitted when the user selects this radio. Payload: `{ checked: boolean, value: string }`.
 * @fires bdsRadioMount - Bubbles up on mount so a parent `bds-radio-group` can register this radio.
 */
@Component({
  tag: 'bds-radio',
  styleUrl: 'bds-radio.scss',
  formAssociated: true,
})
export class BdsRadio extends Mixin(formAssociatedMixin) implements IRadio, IFormControl<boolean> {
  private inheritedAttributes: Attributes = {};

  @State() private isDisabled: boolean = false;

  @Element() el!: HTMLBdsRadioElement;

  @AttachInternals() internals!: ElementInternals;

  /** Name of the form control. Usually set by the parent `bds-radio-group`. */
  @Prop({ reflect: true }) readonly name!: string;

  /** Disables the control. */
  @Prop({ reflect: true }) readonly disabled: boolean = false;

  /** Marks the control as required for form submission. */
  @Prop({ reflect: true }) readonly required: boolean = false;

  /** Whether this radio is selected. */
  @Prop({ mutable: true, reflect: true }) checked: boolean = false;

  /** Shows error styling. Usually set by the parent `bds-radio-group`. */
  @Prop({ reflect: true }) readonly error: boolean = false;

  /** Value submitted with the form data when selected. */
  @Prop() readonly value: string = 'on';

  /** Label text. If not provided, use the default slot or the `icon` slot. */
  @Prop() readonly label: string = '';

  /** Emitted when the checked state changes (for 2-way binding / v-model). */
  @Event() valueChange!: EventEmitter<boolean>;

  /** Emitted when the user selects this radio. */
  @Event() bdsChange!: EventEmitter<RadioChangeDetail>;

  /** Bubbles to the nearest `bds-radio-group` so it can register this radio. */
  @Event({ bubbles: true }) bdsRadioMount!: EventEmitter<RadioMountDetail>;

  componentWillLoad() {
    this.isDisabled = this.disabled;
    this.inheritedAttributes = { ...inheritAriaAttributes(this.el) };
    this.syncFormValue();
  }

  componentDidLoad() {
    this.bdsRadioMount.emit({ element: this.el });
  }

  @Watch('checked')
  onCheckedChange() {
    this.syncFormValue();
  }

  @Watch('disabled')
  onDisabledChange(next: boolean) {
    this.isDisabled = next;
  }

  formAssociatedCallback(): void {
    this.syncFormValue();
  }

  formResetCallback(): void {
    this.checked = false;
    setFormValue(this.internals, null);
  }

  formStateRestoreCallback(state: unknown, _mode: string): void {
    this.checked = state === this.value;
    this.syncFormValue();
  }

  override formDisabledCallback(disabled: boolean) {
    this.isDisabled = disabled;
  }

  private syncFormValue() {
    setFormValue(this.internals, this.checked ? this.value : null);
  }

  private select() {
    if (this.isDisabled || this.checked) return;

    this.checked = true;
    this.valueChange.emit(true);
    this.bdsChange.emit({ checked: true, value: this.value });
  }

  private handleClick = () => {
    this.select();
  };

  private handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === ' ') {
      e.preventDefault();
      this.select();
    }
  };

  render() {
    const classes = {
      'bds-radio': true,
      'bds-radio--checked': this.checked,
      'bds-radio--error': this.error,
      'bds-radio--disabled': this.isDisabled,
    };

    return (
      <Host
        class={classes}
        {...this.inheritedAttributes}
        role="radio"
        aria-checked={this.checked ? 'true' : 'false'}
        aria-disabled={this.isDisabled ? 'true' : null}
        tabindex={this.isDisabled ? -1 : 0}
        onClick={this.handleClick}
        onKeyDown={this.handleKeyDown}
      >
        <span class="bds-radio__button">
          <span class="bds-radio__dot"></span>
        </span>
        <span class="bds-radio__content">
          <span class="bds-radio__icon">
            <slot name="icon"></slot>
          </span>
          <span class="bds-radio__label">{this.label ? this.label : <slot />}</span>
        </span>
      </Host>
    );
  }
}
```

### Step 2: Verify TypeScript compiles

Run from the workspace root (after `fnm use`):
```bash
eval "$(fnm env --shell bash)" && fnm use && pnpm --filter boreal-web-components exec tsc --noEmit
```

Expected: no errors.

### Step 3: Commit

```bash
git add packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.tsx
git commit -m "feat(web-components): EOA-12334 implement bds-radio FACE component"
```

---

## Task 3: bds-radio unit tests

**Files:**
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/__test__/bds-radio.basics.spec.ts`
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/__test__/bds-radio.a11y.spec.ts`
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/__test__/bds-radio.events.spec.ts`
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/__test__/bds-radio.variants.spec.ts`

### Step 1: Write bds-radio.basics.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../bds-radio';
import { assertExists, attachInternals, suppressConsoleError } from '@/utils';

describe('bds-radio basics', () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it('should render the radio element', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    expect(page.root).toBeTruthy();
    expect(page.root?.getAttribute('role')).toBe('radio');
  });

  it('should render the button and content spans', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    assertExists(page.root?.querySelector('.bds-radio__button'), 'button span not found');
    assertExists(page.root?.querySelector('.bds-radio__content'), 'content span not found');
  });

  it('should render with label prop', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio label="Option A"></bds-radio>`,
    });

    const label = page.root?.querySelector('.bds-radio__label');
    assertExists(label, 'label span not found');
    expect(label.textContent).toContain('Option A');
  });

  it('should default checked to false', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    expect(page.root?.getAttribute('aria-checked')).toBe('false');
  });
});
```

### Step 2: Write bds-radio.a11y.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../bds-radio';
import { attachInternals, suppressConsoleError } from '@/utils';

describe('bds-radio a11y', () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it('should have aria-checked="false" by default', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    expect(page.root?.getAttribute('aria-checked')).toBe('false');
  });

  it('should have aria-checked="true" when checked', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio checked></bds-radio>`,
    });

    expect(page.root?.getAttribute('aria-checked')).toBe('true');
  });

  it('should have tabindex="0" by default', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    expect(page.root?.getAttribute('tabindex')).toBe('0');
  });

  it('should have tabindex="-1" and aria-disabled="true" when disabled', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio disabled></bds-radio>`,
    });

    expect(page.root?.getAttribute('tabindex')).toBe('-1');
    expect(page.root?.getAttribute('aria-disabled')).toBe('true');
  });

  it('should have role="radio"', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    expect(page.root?.getAttribute('role')).toBe('radio');
  });
});
```

### Step 3: Write bds-radio.events.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../bds-radio';
import { assertExists, attachInternals, suppressConsoleError } from '@/utils';

describe('bds-radio events', () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it('should select on click and emit bdsChange', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio value="a"></bds-radio>`,
    });

    const spy = jest.fn();
    page.doc.addEventListener('bdsChange', spy);

    const radio = page.body.querySelector('bds-radio');
    assertExists(radio, 'radio not found');
    radio.click();
    await page.waitForChanges();

    expect(spy).toHaveBeenCalledTimes(1);
    expect(page.root?.getAttribute('aria-checked')).toBe('true');
    expect(spy.mock.calls[0][0].detail).toEqual({ checked: true, value: 'a' });
  });

  it('should not emit bdsChange when already checked', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio checked></bds-radio>`,
    });

    const spy = jest.fn();
    page.doc.addEventListener('bdsChange', spy);

    const radio = page.body.querySelector('bds-radio');
    assertExists(radio, 'radio not found');
    radio.click();
    await page.waitForChanges();

    expect(spy).toHaveBeenCalledTimes(0);
  });

  it('should not select when disabled', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio disabled></bds-radio>`,
    });

    const spy = jest.fn();
    page.doc.addEventListener('bdsChange', spy);

    const radio = page.body.querySelector('bds-radio');
    assertExists(radio, 'radio not found');
    radio.click();
    await page.waitForChanges();

    expect(spy).toHaveBeenCalledTimes(0);
    expect(page.root?.getAttribute('aria-checked')).toBe('false');
  });

  it('should select on Space key', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    const spy = jest.fn();
    page.doc.addEventListener('bdsChange', spy);

    const radio = page.body.querySelector('bds-radio');
    assertExists(radio, 'radio not found');
    radio.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', bubbles: true }));
    await page.waitForChanges();

    expect(spy).toHaveBeenCalledTimes(1);
  });

  it('should NOT select on Enter key', async () => {
    const page = await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    const spy = jest.fn();
    page.doc.addEventListener('bdsChange', spy);

    const radio = page.body.querySelector('bds-radio');
    assertExists(radio, 'radio not found');
    radio.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    await page.waitForChanges();

    expect(spy).toHaveBeenCalledTimes(0);
  });

  it('should emit bdsRadioMount on componentDidLoad', async () => {
    const spy = jest.fn();
    document.addEventListener('bdsRadioMount', spy);

    await newSpecPage({
      components: [BdsRadio],
      html: `<bds-radio></bds-radio>`,
    });

    document.removeEventListener('bdsRadioMount', spy);
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
```

### Step 4: Write bds-radio.variants.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../bds-radio';
import { attachInternals, suppressConsoleError } from '@/utils';

describe('bds-radio variants', () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  const configurations = [
    { attr: 'checked', expected: 'bds-radio--checked' },
    { attr: 'error', expected: 'bds-radio--error' },
    { attr: 'disabled', expected: 'bds-radio--disabled' },
  ];

  configurations.forEach(({ attr, expected }) => {
    it(`should apply ${expected} when ${attr} is set`, async () => {
      const page = await newSpecPage({
        components: [BdsRadio],
        html: `<bds-radio ${attr}></bds-radio>`,
      });

      expect(page.root?.classList.contains(expected)).toBe(true);
    });
  });
});
```

### Step 5: Run tests

```bash
eval "$(fnm env --shell bash)" && fnm use && pnpm --filter boreal-web-components test -- --testPathPattern="bds-radio"
```

Expected: all tests pass.

### Step 6: Commit

```bash
git add packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/__test__/
git commit -m "test(web-components): EOA-12334 add bds-radio unit tests"
```

---

## Task 4: bds-radio SCSS styles

**Files:**
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.scss`

### Step 1: Write the styles

Three variants are rendered via CSS descendant selectors from the parent group's reflected `type` attribute. Default styles cover the `radio` type.

```scss
// packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.scss

bds-radio {
  display: inline-flex;
  align-items: center;
  gap: $boreal-spacing-2xs;
  cursor: pointer;
  outline: none;
  user-select: none;

  .bds-radio__button {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid $boreal-stroke-default-light;
    background: transparent;
    transition: border-color 0.15s ease, background-color 0.15s ease;
  }

  .bds-radio__dot {
    display: block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: transparent;
    transition: background-color 0.15s ease;
  }

  .bds-radio__content {
    display: flex;
    align-items: center;
    gap: $boreal-spacing-2xs;
  }

  .bds-radio__icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;

    &:empty {
      display: none;
    }
  }

  .bds-radio__label {
    font-family: $boreal-typography-font-family-primary;
    font-size: $boreal-typography-font-size-sm;
    font-weight: $boreal-typography-font-weight-regular;
    line-height: $boreal-typography-line-height-sm;
    color: $boreal-text-default;
  }

  // ---------------------------------------------------------------------------
  // Interaction states
  // ---------------------------------------------------------------------------

  &:hover .bds-radio__button {
    border-color: $boreal-stroke-default-dark;
  }

  &:focus-visible .bds-radio__button {
    border-color: $boreal-stroke-focus;
    outline: 2px solid $boreal-stroke-focus;
    outline-offset: 1px;
  }

  &:active .bds-radio__button {
    background: $boreal-bg-neutral;
  }

  // ---------------------------------------------------------------------------
  // Checked
  // ---------------------------------------------------------------------------

  &.bds-radio--checked {
    .bds-radio__button {
      border-color: $boreal-ui-success-base;
    }

    .bds-radio__dot {
      background: $boreal-ui-success-base;
    }

    &:hover .bds-radio__button {
      border-color: $boreal-ui-success-dark;

      .bds-radio__dot {
        background: $boreal-ui-success-dark;
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Error
  // ---------------------------------------------------------------------------

  &.bds-radio--error {
    .bds-radio__button {
      border-color: $boreal-stroke-danger-base;
    }

    &.bds-radio--checked {
      .bds-radio__button {
        border-color: $boreal-stroke-danger-base;
      }

      .bds-radio__dot {
        background: $boreal-stroke-danger-base;
      }
    }
  }

  // ---------------------------------------------------------------------------
  // Disabled
  // ---------------------------------------------------------------------------

  &.bds-radio--disabled {
    pointer-events: none;
    cursor: default;

    .bds-radio__button {
      border-color: $boreal-stroke-default-light;
      background: $boreal-bg-neutral;
    }

    .bds-radio__label {
      color: $boreal-text-disabled;
    }

    &.bds-radio--checked {
      .bds-radio__button {
        border-color: $boreal-ui-primary-light;
      }

      .bds-radio__dot {
        background: $boreal-ui-primary-light;
      }
    }
  }
}

// ---------------------------------------------------------------------------
// RadioButton variant  (bds-radio-group[type="radiobutton"] bds-radio)
// ---------------------------------------------------------------------------

bds-radio-group[type='radiobutton'] bds-radio {
  padding: $boreal-spacing-xs $boreal-spacing-s;
  border: 1px solid $boreal-stroke-default-light;
  border-radius: 4px;

  .bds-radio__button {
    display: none;
  }

  .bds-radio__label {
    font-weight: $boreal-typography-font-weight-semibold;
    color: $boreal-text-default-darker;
  }

  &:hover {
    border-color: $boreal-stroke-default-dark;
    background: $boreal-bg-neutral;
  }

  &.bds-radio--checked {
    border-color: $boreal-ui-success-base;
    background: $boreal-bg-primary-lighter;

    .bds-radio__label {
      color: $boreal-ui-success-base;
    }
  }

  &.bds-radio--disabled {
    border-color: $boreal-stroke-default-light;
    background: $boreal-bg-neutral;
  }

  &.bds-radio--error {
    border-color: $boreal-stroke-danger-base;
  }
}

// ---------------------------------------------------------------------------
// RadioCard variant  (bds-radio-group[type="radiocard"] bds-radio)
// ---------------------------------------------------------------------------

bds-radio-group[type='radiocard'] bds-radio {
  flex-direction: column;
  align-items: flex-start;
  padding: $boreal-spacing-s;
  border: 1px solid $boreal-stroke-default-light;
  border-radius: 8px;
  width: 100%;

  .bds-radio__button {
    display: none;
  }

  .bds-radio__content {
    flex-direction: column;
    gap: $boreal-spacing-2xs;
  }

  .bds-radio__label {
    font-weight: $boreal-typography-font-weight-semibold;
    color: $boreal-text-default-darker;
  }

  &:hover {
    border-color: $boreal-stroke-default-dark;
    background: $boreal-bg-neutral;
  }

  &.bds-radio--checked {
    border-color: $boreal-ui-success-base;
    background: $boreal-bg-primary-lighter;
  }

  &.bds-radio--disabled {
    border-color: $boreal-stroke-default-light;
    background: $boreal-bg-neutral;
  }

  &.bds-radio--error {
    border-color: $boreal-stroke-danger-base;
  }
}
```

### Step 2: Commit

```bash
git add packages/boreal-web-components/src/components/forms/bds-radio/bds-radio/bds-radio.scss
git commit -m "style(web-components): EOA-12334 add bds-radio SCSS styles and variants"
```

---

## Task 5: bds-radio-group TSX implementation

**Files:**
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx`

### Step 1: Write the full implementation

```tsx
// packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx
import { Component, Element, Event, EventEmitter, Host, Listen, Prop, Watch, h } from '@stencil/core';

import type {
  IRadioGroup,
  RadioGroupChangeDetail,
  RadioGroupOrientation,
  RadioGroupType,
} from './types/IRadioGroup';
import type { RadioChangeDetail, RadioMountDetail } from '../bds-radio/types/IRadio';

/**
 * Container that manages a group of `bds-radio` elements, enforcing single selection.
 *
 * @summary A radio group that wraps `bds-radio` elements in a `role="radiogroup"` container.
 *
 * @slot - Default slot for `bds-radio` elements.
 *
 * @fires valueChange - Emitted when the selected value changes (for 2-way binding / v-model).
 * @fires bdsChange   - Emitted when the user selects a radio. Payload: `{ value: string }`.
 */
@Component({
  tag: 'bds-radio-group',
  styleUrl: 'bds-radio-group.scss',
})
export class BdsRadioGroup implements IRadioGroup {
  private labelId = `bds-rg-label-${Math.random().toString(36).slice(2, 9)}`;

  @Element() el!: HTMLBdsRadioGroupElement;

  /** Name propagated to every child `bds-radio`. Required for form submission. */
  @Prop({ reflect: true }) readonly name!: string;

  /** Currently selected value. Setting this prop selects the matching radio. */
  @Prop({ mutable: true }) value: string = '';

  /** Label displayed above the options. */
  @Prop() readonly label: string = '';

  /** Helper text displayed below the options. */
  @Prop() readonly helperText: string = '';

  /** Layout direction of the options. */
  @Prop({ reflect: true }) readonly orientation: RadioGroupOrientation = 'vertical';

  /**
   * Visual variant applied to all child radios.
   * `radio` = classic circle, `radiobutton` = segmented button, `radiocard` = card layout.
   */
  @Prop({ reflect: true }) readonly type: RadioGroupType = 'radio';

  /** Disables all child radios. */
  @Prop({ reflect: true }) readonly disabled: boolean = false;

  /** Marks all child radios as required. */
  @Prop({ reflect: true }) readonly required: boolean = false;

  /** Applies error styling to all child radios. */
  @Prop({ reflect: true }) readonly error: boolean = false;

  /** Emitted when the selected value changes (for 2-way binding / v-model). */
  @Event() valueChange!: EventEmitter<string>;

  /** Emitted when the user selects a new radio. */
  @Event() bdsChange!: EventEmitter<RadioGroupChangeDetail>;

  componentWillLoad() {
    this.syncChildren();
  }

  @Watch('value')
  onValueChange() {
    this.syncChildren();
  }

  @Watch('disabled')
  onDisabledChange() {
    this.updateChildrenDisabled();
  }

  @Watch('error')
  onErrorChange() {
    this.updateChildrenError();
  }

  @Listen('bdsRadioMount')
  handleRadioMount(event: CustomEvent<RadioMountDetail>) {
    const radio = event.target as HTMLBdsRadioElement & {
      name: string;
      checked: boolean;
      disabled: boolean;
      error: boolean;
    };
    radio.name = this.name;
    radio.checked = radio.value === this.value;
    if (this.disabled) radio.disabled = true;
    if (this.error) radio.error = true;
  }

  @Listen('bdsChange')
  handleRadioChange(event: CustomEvent<RadioChangeDetail>) {
    const target = event.target as HTMLBdsRadioElement;
    if (!target.checked) return;

    this.value = target.value;
    this.syncChildren();

    this.valueChange.emit(this.value);
    this.bdsChange.emit({ value: this.value });
  }

  private get radios(): HTMLBdsRadioElement[] {
    return Array.from(this.el.querySelectorAll('bds-radio'));
  }

  private syncChildren() {
    this.radios.forEach(radio => {
      (radio as HTMLBdsRadioElement & { checked: boolean }).checked = radio.value === this.value;
    });
  }

  private updateChildrenDisabled() {
    this.radios.forEach(radio => {
      (radio as HTMLBdsRadioElement & { disabled: boolean }).disabled = this.disabled;
    });
  }

  private updateChildrenError() {
    this.radios.forEach(radio => {
      (radio as HTMLBdsRadioElement & { error: boolean }).error = this.error;
    });
  }

  render() {
    return (
      <Host
        class={{
          'bds-radio-group': true,
          'bds-radio-group--disabled': this.disabled,
          'bds-radio-group--error': this.error,
        }}
        role="radiogroup"
        aria-labelledby={this.label ? this.labelId : null}
        aria-disabled={this.disabled ? 'true' : null}
      >
        {this.label && (
          <span class="bds-radio-group__label" id={this.labelId}>
            {this.label}
            {this.required && <span class="bds-radio-group__required" aria-hidden="true"> *</span>}
          </span>
        )}
        <div class="bds-radio-group__options">
          <slot></slot>
        </div>
        {this.helperText && (
          <span class="bds-radio-group__helper">{this.helperText}</span>
        )}
      </Host>
    );
  }
}
```

### Step 2: Verify TypeScript compiles

```bash
eval "$(fnm env --shell bash)" && fnm use && pnpm --filter boreal-web-components exec tsc --noEmit
```

### Step 3: Commit

```bash
git add packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.tsx
git commit -m "feat(web-components): EOA-12334 implement bds-radio-group orchestrator"
```

---

## Task 6: bds-radio-group unit tests

**Files:**
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/__test__/bds-radio-group.basics.spec.ts`
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/__test__/bds-radio-group.a11y.spec.ts`
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/__test__/bds-radio-group.events.spec.ts`

Note: these tests exercise the group in isolation (no child radios — the group doesn't
depend on children at render time). Child coordination is tested in the events spec.

### Step 1: Write bds-radio-group.basics.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadioGroup } from '../bds-radio-group';

describe('bds-radio-group basics', () => {
  it('should render the group element', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan"></bds-radio-group>`,
    });

    expect(page.root).toBeTruthy();
    expect(page.root?.getAttribute('role')).toBe('radiogroup');
  });

  it('should render label when prop is set', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan" label="Select a plan"></bds-radio-group>`,
    });

    const label = page.root?.querySelector('.bds-radio-group__label');
    expect(label).toBeTruthy();
    expect(label?.textContent).toContain('Select a plan');
  });

  it('should not render label when prop is empty', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan"></bds-radio-group>`,
    });

    expect(page.root?.querySelector('.bds-radio-group__label')).toBeNull();
  });

  it('should render helper text when prop is set', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan" helper-text="Choose one option"></bds-radio-group>`,
    });

    const helper = page.root?.querySelector('.bds-radio-group__helper');
    expect(helper).toBeTruthy();
    expect(helper?.textContent).toContain('Choose one option');
  });

  it('should render required indicator when required', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan" label="Plan" required></bds-radio-group>`,
    });

    const req = page.root?.querySelector('.bds-radio-group__required');
    expect(req).toBeTruthy();
  });
});
```

### Step 2: Write bds-radio-group.a11y.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadioGroup } from '../bds-radio-group';

describe('bds-radio-group a11y', () => {
  it('should have role="radiogroup"', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan"></bds-radio-group>`,
    });

    expect(page.root?.getAttribute('role')).toBe('radiogroup');
  });

  it('should set aria-labelledby when label is provided', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan" label="Select plan"></bds-radio-group>`,
    });

    const labelledBy = page.root?.getAttribute('aria-labelledby');
    expect(labelledBy).toBeTruthy();

    const labelEl = page.root?.querySelector(`#${labelledBy}`);
    expect(labelEl).toBeTruthy();
  });

  it('should not set aria-labelledby when no label', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan"></bds-radio-group>`,
    });

    expect(page.root?.getAttribute('aria-labelledby')).toBeNull();
  });

  it('should set aria-disabled when disabled', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup],
      html: `<bds-radio-group name="plan" disabled></bds-radio-group>`,
    });

    expect(page.root?.getAttribute('aria-disabled')).toBe('true');
  });
});
```

### Step 3: Write bds-radio-group.events.spec.ts

```typescript
import { newSpecPage } from '@stencil/core/testing';
import { BdsRadio } from '../../../bds-radio/bds-radio';
import { BdsRadioGroup } from '../bds-radio-group';
import { attachInternals, suppressConsoleError } from '@/utils';

describe('bds-radio-group events', () => {
  suppressConsoleError();

  beforeAll(() => {
    attachInternals();
  });

  it('should enforce single selection — deselect previous when new radio selected', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="plan" value="basic">
          <bds-radio value="basic" label="Basic"></bds-radio>
          <bds-radio value="pro" label="Pro"></bds-radio>
        </bds-radio-group>
      `,
    });

    const [basic, pro] = Array.from(page.body.querySelectorAll('bds-radio'));

    expect(basic.getAttribute('aria-checked')).toBe('true');
    expect(pro.getAttribute('aria-checked')).toBe('false');

    pro.click();
    await page.waitForChanges();

    expect(basic.getAttribute('aria-checked')).toBe('false');
    expect(pro.getAttribute('aria-checked')).toBe('true');
  });

  it('should emit bdsChange with the new value on selection', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="plan">
          <bds-radio value="a" label="A"></bds-radio>
          <bds-radio value="b" label="B"></bds-radio>
        </bds-radio-group>
      `,
    });

    const spy = jest.fn();
    page.doc.addEventListener('bdsChange', spy);

    const [radioA] = Array.from(page.body.querySelectorAll('bds-radio'));
    radioA.click();
    await page.waitForChanges();

    const calls = spy.mock.calls.filter(
      (c: [CustomEvent]) => c[0].target === page.body.querySelector('bds-radio-group')
    );
    expect(calls.length).toBeGreaterThan(0);
    expect(calls[0][0].detail).toEqual({ value: 'a' });
  });

  it('should propagate name to child radios on mount', async () => {
    const page = await newSpecPage({
      components: [BdsRadioGroup, BdsRadio],
      html: `
        <bds-radio-group name="delivery">
          <bds-radio value="fast" label="Fast"></bds-radio>
          <bds-radio value="slow" label="Slow"></bds-radio>
        </bds-radio-group>
      `,
    });

    const radios = Array.from(page.body.querySelectorAll('bds-radio'));
    radios.forEach(r => expect(r.getAttribute('name')).toBe('delivery'));
  });
});
```

### Step 4: Run tests

```bash
eval "$(fnm env --shell bash)" && fnm use && pnpm --filter boreal-web-components test -- --testPathPattern="bds-radio"
```

Expected: all tests pass.

### Step 5: Commit

```bash
git add packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/__test__/
git commit -m "test(web-components): EOA-12334 add bds-radio-group unit tests"
```

---

## Task 7: bds-radio-group SCSS styles

**Files:**
- Create: `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.scss`

### Step 1: Write the styles

```scss
// packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.scss

bds-radio-group {
  display: flex;
  flex-direction: column;
  gap: $boreal-spacing-2xs;

  .bds-radio-group__label {
    font-family: $boreal-typography-font-family-primary;
    font-size: $boreal-typography-font-size-xs;
    font-weight: $boreal-typography-font-weight-semibold;
    line-height: $boreal-typography-line-height-xs;
    color: $boreal-text-default-darker;
  }

  .bds-radio-group__required {
    color: $boreal-stroke-danger-base;
  }

  .bds-radio-group__options {
    display: grid;
    grid-template-columns: 1fr;
    gap: $boreal-spacing-xs;
  }

  .bds-radio-group__helper {
    font-family: $boreal-typography-font-family-primary;
    font-size: $boreal-typography-font-size-xs;
    font-weight: $boreal-typography-font-weight-regular;
    line-height: $boreal-typography-line-height-xs;
    color: $boreal-text-default-light;
  }

  &[orientation='horizontal'] {
    .bds-radio-group__options {
      grid-auto-flow: column;
      grid-template-columns: unset;
      gap: $boreal-spacing-ml;
    }
  }

  &.bds-radio-group--error {
    .bds-radio-group__helper {
      color: $boreal-stroke-danger-base;
    }
  }
}
```

### Step 2: Commit

```bash
git add packages/boreal-web-components/src/components/forms/bds-radio/bds-radio-group/bds-radio-group.scss
git commit -m "style(web-components): EOA-12334 add bds-radio-group SCSS styles"
```

---

## Task 8: Storybook stories

**Files:**
- Create: `apps/boreal-docs/src/stories/forms/bds-radio/bds-radio.stories.ts`
- Create: `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts`

### Step 1: Write bds-radio.stories.ts

```typescript
// apps/boreal-docs/src/stories/forms/bds-radio/bds-radio.stories.ts
import { html, nothing } from 'lit';
import { formatHtmlSource } from '@/utils/formatters';
import type { BorealStory, BorealStoryMeta } from '@/types/stories';

type StoryArgs = {
  checked: boolean;
  error: boolean;
  disabled: boolean;
  required: boolean;
  value: string;
  name: string;
  label: string;
  onBdsChange: (e: CustomEvent) => void;
  onValueChange: (e: CustomEvent) => void;
};
type Story = BorealStory<StoryArgs>;

const meta = {
  title: 'Forms/Radio',
  component: 'bds-radio',
  parameters: {
    docs: {
      source: { excludeDecorators: true, transform: formatHtmlSource },
    },
  },
  argTypes: {
    checked: {
      control: 'boolean',
      description: 'Whether this radio is selected.',
      table: { category: 'State', type: { summary: 'boolean' }, defaultValue: { summary: 'false' } },
    },
    error: {
      control: 'boolean',
      description: 'Applies the error visual state.',
      table: { category: 'State', type: { summary: 'boolean' }, defaultValue: { summary: 'false' } },
    },
    disabled: {
      control: 'boolean',
      description: 'Disables the radio.',
      table: { category: 'State', type: { summary: 'boolean' }, defaultValue: { summary: 'false' } },
    },
    required: {
      control: 'boolean',
      description: 'Marks the radio as required.',
      table: { category: 'State', type: { summary: 'boolean' }, defaultValue: { summary: 'false' } },
    },
    value: {
      control: 'text',
      description: 'Value submitted with the form when selected.',
      table: { category: 'Core', type: { summary: 'string' }, defaultValue: { summary: 'on' } },
    },
    name: {
      control: 'text',
      description: 'Form control name.',
      table: { category: 'Core', type: { summary: 'string' } },
    },
    label: {
      control: 'text',
      description: 'Label text. If omitted, use the default slot.',
      table: { category: 'Appearance', type: { summary: 'string' } },
    },
    onBdsChange: {
      action: 'bdsChange emitted',
      description: 'Emitted when selected. Payload: `{ checked: boolean, value: string }`.',
      table: { category: 'Events' },
    },
    onValueChange: {
      action: 'valueChange emitted',
      description: 'Emitted when checked state changes (v-model binding). Payload: `boolean`.',
      table: { category: 'Events' },
    },
  },
  args: {
    checked: false,
    error: false,
    disabled: false,
    required: false,
    value: 'option-a',
    name: 'radio',
    label: 'Option A',
  },
} satisfies BorealStoryMeta<StoryArgs>;

export default meta;

const renderRadio: Story['render'] = args => html`
  <bds-radio
    name=${args.name}
    value=${args.value || nothing}
    label=${args.label || nothing}
    ?checked=${args.checked}
    ?error=${args.error}
    ?disabled=${args.disabled}
    ?required=${args.required}
    @bdsChange=${args.onBdsChange}
    @valueChange=${args.onValueChange}
  ></bds-radio>
`;

export const Default: Story = { render: renderRadio };

export const Checked: Story = {
  args: { checked: true, label: 'Selected option' },
  render: renderRadio,
};

export const Error: Story = {
  args: { error: true, label: 'Invalid option' },
  render: renderRadio,
};

export const Disabled: Story = {
  args: { disabled: true, label: 'Unavailable option' },
  render: renderRadio,
};

export const DisabledChecked: Story = {
  args: { disabled: true, checked: true, label: 'Unavailable (selected)' },
  render: renderRadio,
};
```

### Step 2: Write bds-radio-group.stories.ts

```typescript
// apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts
import { html, nothing } from 'lit';
import { formatHtmlSource } from '@/utils/formatters';
import type { BorealStory, BorealStoryMeta } from '@/types/stories';

type StoryArgs = {
  name: string;
  value: string;
  label: string;
  helperText: string;
  orientation: 'horizontal' | 'vertical';
  type: 'radio' | 'radiobutton' | 'radiocard';
  disabled: boolean;
  required: boolean;
  error: boolean;
  onBdsChange: (e: CustomEvent) => void;
  onValueChange: (e: CustomEvent) => void;
};
type Story = BorealStory<StoryArgs>;

const meta = {
  title: 'Forms/RadioGroup',
  component: 'bds-radio-group',
  parameters: {
    docs: {
      source: { excludeDecorators: true, transform: formatHtmlSource },
    },
  },
  argTypes: {
    name: {
      control: 'text',
      description: 'Form control name shared with all child radios.',
      table: { category: 'Core', type: { summary: 'string' } },
    },
    value: {
      control: 'text',
      description: 'Currently selected value.',
      table: { category: 'Core', type: { summary: 'string' } },
    },
    label: {
      control: 'text',
      description: 'Label displayed above the options.',
      table: { category: 'Appearance', type: { summary: 'string' } },
    },
    helperText: {
      control: 'text',
      description: 'Helper text displayed below the options.',
      table: { category: 'Appearance', type: { summary: 'string' } },
    },
    orientation: {
      control: { type: 'select' },
      options: ['vertical', 'horizontal'],
      description: 'Layout direction of the options.',
      table: {
        category: 'Appearance',
        type: { summary: '"vertical" | "horizontal"' },
        defaultValue: { summary: 'vertical' },
      },
    },
    type: {
      control: { type: 'select' },
      options: ['radio', 'radiobutton', 'radiocard'],
      description: 'Visual variant applied to child radios.',
      table: {
        category: 'Appearance',
        type: { summary: '"radio" | "radiobutton" | "radiocard"' },
        defaultValue: { summary: 'radio' },
      },
    },
    disabled: {
      control: 'boolean',
      description: 'Disables all child radios.',
      table: { category: 'State', type: { summary: 'boolean' }, defaultValue: { summary: 'false' } },
    },
    required: {
      control: 'boolean',
      description: 'Marks all child radios as required.',
      table: { category: 'State', type: { summary: 'boolean' }, defaultValue: { summary: 'false' } },
    },
    error: {
      control: 'boolean',
      description: 'Applies error styling to all child radios.',
      table: { category: 'State', type: { summary: 'boolean' }, defaultValue: { summary: 'false' } },
    },
    onBdsChange: {
      action: 'bdsChange emitted',
      description: 'Emitted on selection change. Payload: `{ value: string }`.',
      table: { category: 'Events' },
    },
    onValueChange: {
      action: 'valueChange emitted',
      description: 'Emitted on selection change (v-model binding). Payload: `string`.',
      table: { category: 'Events' },
    },
  },
  args: {
    name: 'plan',
    value: '',
    label: 'Select a plan',
    helperText: 'You can change this later.',
    orientation: 'vertical',
    type: 'radio',
    disabled: false,
    required: false,
    error: false,
  },
} satisfies BorealStoryMeta<StoryArgs>;

export default meta;

const renderGroup: Story['render'] = args => html`
  <bds-radio-group
    name=${args.name}
    value=${args.value || nothing}
    label=${args.label || nothing}
    helper-text=${args.helperText || nothing}
    orientation=${args.orientation}
    type=${args.type}
    ?disabled=${args.disabled}
    ?required=${args.required}
    ?error=${args.error}
    @bdsChange=${args.onBdsChange}
    @valueChange=${args.onValueChange}
  >
    <bds-radio value="basic" label="Basic"></bds-radio>
    <bds-radio value="pro" label="Pro"></bds-radio>
    <bds-radio value="enterprise" label="Enterprise"></bds-radio>
  </bds-radio-group>
`;

export const Default: Story = { render: renderGroup };

export const WithValue: Story = {
  args: { value: 'pro' },
  render: renderGroup,
};

export const Horizontal: Story = {
  args: { orientation: 'horizontal' },
  render: renderGroup,
};

export const RadioButton: Story = {
  args: { type: 'radiobutton', orientation: 'horizontal' },
  render: renderGroup,
};

export const RadioCard: Story = {
  args: { type: 'radiocard' },
  render: renderGroup,
};

export const Error: Story = {
  args: { error: true, helperText: 'Please select an option.' },
  render: renderGroup,
};

export const Disabled: Story = {
  args: { disabled: true, value: 'basic' },
  render: renderGroup,
};

export const Required: Story = {
  args: { required: true, label: 'Select a plan (required)' },
  render: renderGroup,
};
```

### Step 3: Start Storybook and verify visually

```bash
eval "$(fnm env --shell bash)" && fnm use && pnpm dev:docs
```

Open `http://localhost:6006` and navigate to `Forms/Radio` and `Forms/RadioGroup`. Verify:
- Default radio renders circle + label
- RadioButton variant shows button-style controls
- RadioCard variant shows card layout
- Horizontal orientation arranges items in a row
- Error state shows red styling
- Disabled state is non-interactive

### Step 4: Commit

```bash
git add apps/boreal-docs/src/stories/forms/bds-radio/ apps/boreal-docs/src/stories/forms/bds-radio-group/
git commit -m "docs(web-components): EOA-12334 add Storybook stories for bds-radio and bds-radio-group"
```

---

## Task 9: MDX documentation

**Files:**
- Create: `apps/boreal-docs/src/stories/forms/bds-radio/bds-radio.mdx`
- Create: `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.mdx`

### Step 1: Write bds-radio.mdx

```mdx
import { Meta, Canvas, ArgTypes, Title, Subtitle } from '@storybook/addon-docs/blocks';
import LinkTo from '@storybook/addon-links/react';
import { Callout, DocsLinkTo } from '@/components/docs';
import * as BdsRadioStories from './bds-radio.stories';

<Meta of={BdsRadioStories} />

<Title of={BdsRadioStories} />

The `bds-radio` component is a single radio button form control. It is designed to be used inside a `bds-radio-group`, which handles mutual exclusion, name propagation, and group-level states. The radio is accessible by default with proper ARIA roles and keyboard navigation.

<Callout variant="info" icon="ℹ️">
  Use `bds-radio` inside a `bds-radio-group`. Using a standalone `bds-radio` outside a group requires you to manage `name` and selection manually.
</Callout>

<Subtitle>Table of contents</Subtitle>

- [How to use it](#how-to-use-it)
- [Component preview](#component-preview)
- [States](#states)
- [Accessibility](#accessibility)
- [Properties](#properties)
- [Interact with the component](#interact-with-the-component)

<Subtitle>How to use it</Subtitle>

1. Register the Boreal DS components once in your app entry point.

    ```ts
    import { defineCustomElements } from '@telesign/boreal-web-components/loader';
    defineCustomElements();
    ```

2. Use `bds-radio` inside a `bds-radio-group`.

    ```html
    <bds-radio-group name="plan" label="Select a plan">
      <bds-radio value="basic" label="Basic"></bds-radio>
      <bds-radio value="pro" label="Pro"></bds-radio>
    </bds-radio-group>
    ```

<Subtitle>Component preview</Subtitle>

### Default

<Canvas of={BdsRadioStories.Default} />

### Checked

<Canvas of={BdsRadioStories.Checked} />

## States

### Error

<Canvas of={BdsRadioStories.Error} />

### Disabled

<Canvas of={BdsRadioStories.Disabled} />

### Disabled & Checked

<Canvas of={BdsRadioStories.DisabledChecked} />

<Subtitle>Accessibility</Subtitle>

- **ARIA**: `role="radio"` with `aria-checked` (`"true"` or `"false"`). `aria-disabled="true"` when disabled.
- **Keyboard**: `Tab` to focus, `Space` to select. Arrow key navigation is managed by the parent `bds-radio-group`.
- **Best practices**: Always use inside a `bds-radio-group` which provides `role="radiogroup"` and `aria-labelledby`.

<Subtitle>Properties</Subtitle>

<ArgTypes of={BdsRadioStories} />

<Subtitle>Interact with the component</Subtitle>

To interact with the component, navigate to the <LinkTo title={BdsRadioStories.default.title} story="default">Default</LinkTo> section.
```

### Step 2: Write bds-radio-group.mdx

```mdx
import { Meta, Canvas, ArgTypes, Title, Subtitle } from '@storybook/addon-docs/blocks';
import LinkTo from '@storybook/addon-links/react';
import { Callout, DocsLinkTo } from '@/components/docs';
import * as BdsRadioGroupStories from './bds-radio-group.stories';

<Meta of={BdsRadioGroupStories} />

<Title of={BdsRadioGroupStories} />

The `bds-radio-group` component manages a set of `bds-radio` elements, enforcing mutual exclusion (single selection) and propagating shared state (name, disabled, error) to all children. It supports three visual variants via the `type` prop and two layout orientations.

<Subtitle>Table of contents</Subtitle>

- [How to use it](#how-to-use-it)
- [Visual variants](#visual-variants)
- [Orientations](#orientations)
- [States](#states)
- [Form Integration](#form-integration)
- [Accessibility](#accessibility)
- [Properties](#properties)
- [Interact with the component](#interact-with-the-component)

<Subtitle>How to use it</Subtitle>

1. Register components at app entry point (see `bds-radio` docs for details).

2. Wrap `bds-radio` elements in `bds-radio-group`.

    ```html
    <bds-radio-group name="plan" label="Select a plan" helper-text="Choose one option.">
      <bds-radio value="basic" label="Basic"></bds-radio>
      <bds-radio value="pro" label="Pro"></bds-radio>
      <bds-radio value="enterprise" label="Enterprise"></bds-radio>
    </bds-radio-group>
    ```

3. Listen to `bdsChange` for selection events.

    ```html
    <script>
      const group = document.querySelector('bds-radio-group');
      group.addEventListener('bdsChange', (e) => {
        console.log('Selected:', e.detail.value);
      });
    </script>
    ```

<Subtitle>Component preview</Subtitle>

### Default

<Canvas of={BdsRadioGroupStories.Default} />

### With pre-selected value

<Canvas of={BdsRadioGroupStories.WithValue} />

## Visual variants

The `type` prop changes the visual rendering of all child radios without changing their logic.

### Radio (default)

Classic circle-and-label layout.

<Canvas of={BdsRadioGroupStories.Default} />

### RadioButton

Segmented button style — ideal for compact, mutually exclusive options like filter controls.

<Canvas of={BdsRadioGroupStories.RadioButton} />

### RadioCard

Card-based layout — ideal for presenting options with rich content or descriptions.

<Canvas of={BdsRadioGroupStories.RadioCard} />

## Orientations

### Horizontal

<Canvas of={BdsRadioGroupStories.Horizontal} />

## States

### Error

<Canvas of={BdsRadioGroupStories.Error} />

### Disabled

<Canvas of={BdsRadioGroupStories.Disabled} />

### Required

<Canvas of={BdsRadioGroupStories.Required} />

## Form Integration

`bds-radio` is a form-associated custom element. When the user selects a radio inside a group,
the selected radio's `value` is submitted under the group's `name`.

```html
<form id="preferences">
  <bds-radio-group name="plan" required>
    <bds-radio value="basic" label="Basic"></bds-radio>
    <bds-radio value="pro" label="Pro"></bds-radio>
  </bds-radio-group>
  <button type="submit">Submit</button>
</form>
```

<Subtitle>Accessibility</Subtitle>

- **ARIA**: `role="radiogroup"` on the host. `aria-labelledby` points to the rendered label element when `label` is set. `aria-disabled="true"` when disabled.
- **Keyboard**: `Tab` to focus the group. `Space` on a focused radio selects it.
- **Best practices**: Always provide a `label` so screen readers can announce the group's purpose.

<Subtitle>Properties</Subtitle>

<ArgTypes of={BdsRadioGroupStories} />

<Subtitle>Interact with the component</Subtitle>

Navigate to the <LinkTo title={BdsRadioGroupStories.default.title} story="default">Default</LinkTo> section.
```

### Step 3: Verify Storybook renders docs pages without errors

```bash
eval "$(fnm env --shell bash)" && fnm use && pnpm dev:docs
```

Open the Docs tab for `Forms/Radio` and `Forms/RadioGroup` — confirm all sections render.

### Step 4: Commit

```bash
git add apps/boreal-docs/src/stories/forms/bds-radio/ apps/boreal-docs/src/stories/forms/bds-radio-group/
git commit -m "docs(web-components): EOA-12334 add MDX documentation for bds-radio and bds-radio-group"
```

---

## Final checklist

- [ ] All `bds-radio` tests pass
- [ ] All `bds-radio-group` tests pass
- [ ] Storybook: Default, Checked, Error, Disabled states render correctly
- [ ] Storybook: RadioButton and RadioCard variants visually distinct
- [ ] Storybook: Horizontal orientation lays options in a row
- [ ] MDX docs pages render without React errors
- [ ] TypeScript: `pnpm --filter boreal-web-components exec tsc --noEmit` exits clean
- [ ] No `:host` selector used anywhere (light DOM)
- [ ] No inline code comments added
- [ ] No `Co-Authored-By` trailer in any commit message
