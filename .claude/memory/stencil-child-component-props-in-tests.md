# Stencil — Child Custom Element Props in `newSpecPage` Tests

## The Core Problem

When a child custom element is **not** listed in the `components` array of `newSpecPage`, Stencil treats it as an unknown HTML element and sets JSX props as **JavaScript properties**, not HTML attributes:

```tsx
// In render():
<bds-typography tooltipText={this.info}>...</bds-typography>
```

In the test, if `BdsTypography` is absent from `components`:

```typescript
const page = await newSpecPage({
  components: [BdsRadioButton],   // BdsTypography NOT listed
  html: `<bds-radio-button info="hint"></bds-radio-button>`,
});
const el = page.root?.querySelector('bds-typography');
el.getAttribute('tooltip-text');  // ❌ null — it's a JS property, not an attribute
(el as any).tooltipText;          // ⚠️  may work, but unreliable — not the right pattern
```

## Why `getAttribute` Fails Even With the Child Registered

Even when the child IS registered, `@Prop()` values are NOT reflected to HTML attributes unless the prop has `reflect: true`. `bds-typography`'s `tooltipText` is declared as:

```typescript
@Prop() readonly tooltipText: string = '';   // no reflect: true
```

So `getAttribute('tooltip-text')` returns `null` in both cases.

## The Correct Pattern: Assert on Rendered Behaviour

Register the child component and assert on the **DOM it produces** rather than its prop values:

```typescript
const page = await newSpecPage({
  components: [BdsRadioButton, BdsTypography],   // ✅ child registered
  html: `<bds-radio-button info="hint"></bds-radio-button>`,
});
const typography = page.root?.querySelector('bds-typography.bds-radio-button__label');

// Assert on the info icon bds-typography renders when tooltipText is set
expect(typography?.querySelector('.bds-typography__info-icon')).toBeTruthy();  // ✅
```

When `info` is empty, `bds-typography` receives `tooltipText={undefined}`, the `&&` guard fires, and the icon is absent:

```typescript
expect(typography?.querySelector('.bds-typography__info-icon')).toBeNull();  // ✅
```

## When You Must Check a Reflected Prop

The only reliable way to observe a non-reflected prop value in tests is to check the rendered DOM output of the child. If there is no visible DOM consequence, the value is effectively unobservable from a test — and surviving Stryker mutants in that conditional should be documented and accepted.

**Example accepted survivor:** `tooltipText={true ? this.info : undefined}` vs `tooltipText={this.info !== '' ? this.info : undefined}` — both produce identical DOM because `''` (empty string, the default) and `undefined` are both falsy in `bds-typography`'s `this.tooltipText && canUseTooltip` guard.

## Which Components Need to Be Added to `components`?

Add a child component to `components` **only when**:
- The test needs to assert on that component's **rendered DOM output** (classes, child elements, ARIA attributes produced by its render function)
- Or it needs its props to reflect properly to attributes

Do NOT add it if only presence/absence of the element tag itself is being asserted — unknown elements render fine for tag-name queries.

**Example: `BdsTypography`**

```typescript
// Needs BdsTypography — asserts on inner .bds-typography__info-icon
components: [BdsRadioButton, BdsTypography],

// Does NOT need BdsTypography — only checks tag existence
components: [BdsRadioButton],
// page.root.querySelector('bds-typography')  → fine without registration
```

## Reference

Discovered during mutation testing of `bds-radio-button` (EOA-10533). The failing tests were `should pass info prop as tooltip-text attribute` and `should render default slot when label prop is empty` — both caused by attempting `getAttribute` on a non-reflected prop of an unregistered child.
