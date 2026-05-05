---
status: in progress
---

# bds-radio-button Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Prerequisite:** `bds-radio-group` must already be implemented (see `EOA-12334-bds-radio-and-radio-group.md`). This plan adds `bds-radio-button` as a new leaf component and extends the group to handle it.

**Scope:** `bds-radio-button` (leaf component) + extension of `bds-radio-group` to support `type="radiobutton"`.

**Why a separate component (not a CSS-only variant of bds-radio):**

1. **DOM difference** — `bds-radio-button` has no circle indicator (`.bds-radio__button`, `.bds-radio__dot`) in the DOM at all; the absence is structural, not just CSS-hidden.
2. **Different API** — carries a `label` string prop and an `icon` named slot that are meaningless on `bds-radio`.
3. **Segmented control CSS** — the adjacent-sibling border-collapsing layout (`+ bds-radio-button { margin-left: -1px }`) requires a dedicated tag name; CSS `+` combinators cannot target a subset of elements sharing the same tag name.

Evidence: Colibri's `col-radio-button` (`.ai/lib/colibri-components.txt`) has the same structural separation from `col-radio`.

**Tech Stack:** Stencil, TypeScript, SCSS, `boreal-styleguidelines` design tokens, Storybook (Lit HTML stories + MDX docs), Jest / `@stencil/core/testing`.

---

## File tree to create / modify

```
packages/boreal-web-components/src/components/forms/
  bds-radio-button/                         ← NEW (flat sibling of bds-radio-group, not nested)
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

apps/boreal-docs/src/stories/forms/bds-radio-button/   ← NEW
  bds-radio-button.stories.ts
  bds-radio-button.mdx
apps/boreal-docs/src/stories/forms/bds-radio-group/
  bds-radio-group.stories.ts               ← MODIFY (add type=radiobutton stories)
  bds-radio-group.mdx                      ← MODIFY (document radiobutton variant)
```

---

## Task 1: IRadioButton.ts + update IRadioGroup.ts ✅

### Create: `bds-radio-button/types/IRadioButton.ts`

Only consumer-settable props belong in the interface. `name`, `showDivider`, `isFirst`, and `bdsChange` are group-internal or outputs — they are NOT in the interface.

```typescript
export interface RadioButtonChangeDetail {
  checked: boolean;
  value: string;
}

export interface IRadioButton {
  value: string;
  label: string;
  info: string;
  checked: boolean;
  disabled: boolean;
  error: boolean;
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

**Manual test (waiveable):** TypeScript compilation should show no errors after both files are created/modified.

---

## Task 2a: bds-radio-button scaffold + build ✅

**File:** `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.tsx`

Write only the scaffold: `@Component` decorator, `@Element`, all `@Prop`s with JSDoc, `@Event`, and a stub `render()` that returns `<Host />`. Do NOT add `componentDidLoad` or interaction handlers yet.

Also create the placeholder SCSS file:

```scss
bds-radio-button {
}
```

Then run `pnpm --filter boreal-web-components build` to generate `HTMLBdsRadioButtonElement` in `src/components.d.ts`. This type must exist before adding lifecycle code or `this.el.*` calls (otherwise ESLint raises `unsafe-call` errors).

**Manual test (waiveable):** Build completes with no errors; `HTMLBdsRadioButtonElement` appears in `src/components.d.ts`.

---

## Task 2b: lifecycle + interaction ✅

Add `componentDidLoad`, `select()`, `handleClick`, and `handleKeyDown` to the scaffold. Update the stub `render()` to wire `onClick` and `onKeyDown` to the handlers:

```tsx
render() {
  return (
    <Host
      onClick={this.handleClick}
      onKeyDown={this.handleKeyDown}
    />
  );
}
```

**Manual test (waiveable):** No TypeScript or ESLint errors on the file.

---

## Task 2c: render() ✅

Replace the stub `render()` with the full DOM structure:

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

Key decisions:
- `<bds-divider orientation="vertical" />` — conditional on `showDivider && !isFirst`, set by the parent group to create segmented control separators without extra DOM outside Stencil's reconciler.
- Hidden `<input type="radio">` with `aria-hidden="true"` — participates in form submission while keeping ARIA semantics on the host element.
- `<bds-typography variant="label">` — group convention from memory; carries `tooltipText` when `info` is set.

**Manual test (waiveable):** Render `<bds-radio-button label="Option A" value="a">` in a test page; verify label appears and clicking it emits `bdsChange`.

---

## Task 2d: JSDoc audit

Verify `bds-radio-button.tsx` satisfies all rules in `.ai/guidelines/jsdoc-template.md`:

- Every `@Prop()` has an inline `/** */` block immediately above the decorator
- `bdsChange` `@Event()` has an inline `/** */` block and uses `@Event({ bubbles: true })`
- Class-level block has `@slot` for default slot and `icon` named slot
- No prohibited tags (`@attr`, `@property`, `@fires`, `@element`, `@cssprop`, `@internal`, `@part`)

This is a read-and-verify task — likely no code changes needed since JSDoc was written during the scaffold step.

**Manual test (waiveable):** Visual review of the file confirms all JSDoc rules are satisfied.

---

## Task 3: bds-radio-button tests

**Files:** `__test__/bds-radio-button.basics.spec.ts`, `bds-radio-button.a11y.spec.ts`, `bds-radio-button.events.spec.ts`

> Note: The tests below reference `<bds-typography>` for label content and a hidden `<input>` — adjust queries to match the actual rendered DOM.

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

  it("renders hidden native input", async () => {
    const { root } = await newSpecPage({
      components: [BdsRadioButton],
      html: '<bds-radio-button label="Option" value="x"></bds-radio-button>',
    });
    const input = root.querySelector<HTMLInputElement>('input[type="radio"]');
    expect(input).toBeTruthy();
    expect(input.getAttribute("aria-hidden")).toBe("true");
    expect(input.value).toBe("x");
  });
});
```

### bds-radio-button.a11y.spec.ts

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsRadioButton } from "../bds-radio-button";

describe("bds-radio-button a11y", () => {
  it("has role=radio", async () => {
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

  it("has tabindex attribute after mount", async () => {
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

**Manual test (waiveable):** Run `pnpm --filter boreal-web-components test -- --testPathPattern="bds-radio-button"` and verify all tests pass.

---

## Task 4: bds-radio-button SCSS

**File:** `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.scss`

No `@use` import — `$boreal-*` tokens are globally injected by `injectGlobalPaths` in `stencil.config.ts`. Start directly with the selector.

Pill-shaped button container. The adjacent-sibling border-collapsing CSS (segmented control layout) is scoped to `bds-radio-group[type='radiobutton']` context.

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
    display: none;
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

**Manual test (waiveable):** Open the Storybook or a test page; verify pill shape, hover/focus/checked/disabled/error visual states, and segmented border-collapsing when inside `<bds-radio-group type="radiobutton">`.

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

**Files:**

- `apps/boreal-docs/src/stories/forms/bds-radio-button/bds-radio-button.stories.ts` — standalone stories
- Update `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.stories.ts` — add `type=radiobutton` story

Follow the existing Lit HTML story convention (see other forms stories).

**bds-radio-button standalone stories must cover:** all states (default, checked, disabled, error), with icon slot.

**bds-radio-group + radiobutton story must cover:**

- `type=radiobutton` — segmented control appearance (horizontal, border-collapsing)
- Disabled group
- Error state

**Manual test (waiveable):** Open Storybook; navigate to Forms/RadioButton; verify all story variants render correctly without console errors.

---

## Task 7: MDX documentation

**Files:**

- `apps/boreal-docs/src/stories/forms/bds-radio-button/bds-radio-button.mdx` — NEW
- Update `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-group.mdx` — add radiobutton variant section

### bds-radio-button.mdx must include:

- Component description: button-shaped radio option for use inside `bds-radio-group[type="radiobutton"]`
- Props table
- Slots table: `icon` (named, optional), default slot (label fallback)
- Events table: `bdsChange`
- Usage note: must be used inside `<bds-radio-group type="radiobutton">` for correct keyboard behavior and segmented layout
- Accessibility note: `role="radio"`, `aria-checked`, keyboard navigation is managed by the parent group

### bds-radio-group.mdx additions:

- New `type="radiobutton"` variant section: what it looks like, when to use it (segmented control for mutually exclusive options with visual button affordance)
- Code example showing `<bds-radio-group type="radiobutton">` with `<bds-radio-button>` children

**Manual test (waiveable):** Open Storybook; navigate to the RadioButton docs page; verify all sections render and the code examples are accurate.

---

## Critical Constraints

- **No `@use` import in SCSS files** — `$boreal-*` tokens are globally injected via `injectGlobalPaths` in `stencil.config.ts`; adding `@use` causes a double-import Sass error
- **No `:host` selectors** — all selectors target element tag names directly
- `bds-radio-button` is NOT form-associated — no `@AttachInternals()` on the leaf
- Only `bds-radio-group` retains `@AttachInternals()` (already on its class body — do not move it)
- Do NOT remove or alter the existing `bds-radio` implementation — this plan only adds and extends
- No inline code comments; no `Co-Authored-By` commit trailers
- Interface file: `IRadioButton.ts` (no `Bds` prefix — project convention per memory)
- **Flat file structure** — `bds-radio-button/` is a direct sibling of `bds-radio-group/` under `forms/`, NOT nested inside `bds-radio/`

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
# Forms/RadioButton → pill shape, NO circle indicator, icon slot, all states
# Forms/RadioGroup  → type=radiobutton shows segmented control layout (border-collapsing),
#                     horizontal orientation, disabled + error variants
# Keyboard (group)  → same Arrow/Tab/Space behavior as radio variant
```
