---
title: Migrate floatingOptions to flat declarative props in bds-tooltip and bds-popover
status: pending
date: 2026-04-14
output: .ai/research/floating-options-declarative-api-migration.md
---

## Context

Both `bds-tooltip` and `bds-popover` expose their positioning/behaviour configuration through a single
`floatingOptions` JS property (`Partial<FloatingTooltipProp>` / `Partial<FloatingPopoverProp>`).
This is an imperative API: consumers must write JavaScript to set an object, which:

- Is invisible in Storybook's Source panel (JS property bindings are not serialised as attributes)
- Cannot be used from plain HTML / server-rendered templates
- Forces consumers to construct a full object even when setting a single value (e.g. just `placement`)
- Buries commonly-used options inside a nested structure

This document analyses both components and defines a migration to a layered/progressive API:
flat `@Prop()` declarations for all scalar options (declarative layer) while keeping `floatingOptions`
for lifecycle callbacks that can never be expressed as attributes (imperative layer).

**Additionally**, both components use a fragile heuristic-based trigger detection system via `anchoredMixin`
that requires an adjacent sibling pattern and fails for nested structures. This will be refactored to an
explicit slot-based pattern inspired by Colibri Components, adapted for **Stencil without shadow DOM**.

### Key constraints:

- **Stencil does NOT have a `@Query()` decorator** — use `@Element()` + `querySelector()` instead
- **No shadow DOM** — query elements directly from `this.el` (light DOM), not `this.el.shadowRoot`
- **Slot-based composition** — use `<slot>` + `assignedElements()` for explicit trigger resolution

---

## Full `floatingOptions` shape — annotated by declarability

### `bds-tooltip` — `Partial<FloatingTooltipProp>`

| Field              | Type                                            | Declarable?     | Currently used in component?                         |
| ------------------ | ----------------------------------------------- | --------------- | ---------------------------------------------------- |
| `placement`        | `Position` (`'top'\|'bottom'\|'left'\|'right'`) | ✅ string       | Yes — `options` getter, `getPlacement`               |
| `offset`           | `number`                                        | ✅ scalar       | Yes — `options` getter                               |
| `hideArrow`        | `boolean`                                       | ✅ boolean      | Yes — `options` getter, `canShowArrow`               |
| `stayOnHover`      | `boolean`                                       | ✅ boolean      | Yes — `validateHide`                                 |
| `flip`             | `boolean`                                       | ✅ boolean      | No — not forwarded in `options` getter               |
| `shift`            | `boolean`                                       | ✅ boolean      | No — not forwarded in `options` getter               |
| `strategy`         | `Strategy`                                      | ✅ string union | Yes — hardcoded `'fixed'`, not consumer-configurable |
| `arrow`            | `HTMLElement`                                   | ❌ DOM ref      | Internal only — managed via `ref={}`                 |
| `onBeforeShow`     | `(el?) => boolean`                              | ❌ function     | Yes — wired in `hooks` getter                        |
| `onAfterShow`      | `(el?) => void`                                 | ❌ function     | No                                                   |
| `onBeforeHide`     | `(el?) => boolean`                              | ❌ function     | Yes — wired in `hooks` getter                        |
| `onAfterHide`      | `(el?) => void`                                 | ❌ function     | No                                                   |
| `onPositionUpdate` | `(result) => void`                              | ❌ function     | Yes — wired in `hooks` getter                        |
| `mounted`          | `(el?) => void`                                 | ❌ function     | No                                                   |
| `unmounted`        | `(el?) => void`                                 | ❌ function     | No                                                   |

**Scalar fields to promote (5):** `placement`, `offset`, `hideArrow`, `stayOnHover`, `flip`/`shift` (but these two are not forwarded, see Dead API below)

### `bds-popover` — `Partial<FloatingPopoverProp>`

| Field                         | Type                                                               | Declarable?     | Currently used in component?                     |
| ----------------------------- | ------------------------------------------------------------------ | --------------- | ------------------------------------------------ |
| `placement`                   | `PopoverPosition` (`'top-start'\|'bottom-start'\|'left'\|'right'`) | ✅ string       | Yes — `options` getter, `getPlacement`           |
| `offset`                      | `number`                                                           | ✅ scalar       | Yes — `options` getter                           |
| `hideArrow`                   | `boolean`                                                          | ✅ boolean      | Yes — `options` getter, `canShowArrow`           |
| `closeOnClick`                | `boolean`                                                          | ✅ boolean      | Yes — `handleFloatingClick`                      |
| `closeOnClickOutside`         | `boolean`                                                          | ✅ boolean      | Yes — `attachClickOutside`, `detachClickOutside` |
| `flip`                        | `boolean`                                                          | ✅ boolean      | No — hardcoded `true` in `options`               |
| `shift`                       | `boolean`                                                          | ✅ boolean      | No — hardcoded `true` in `options`               |
| `strategy`                    | `Strategy`                                                         | ✅ string union | No — hardcoded `'fixed'` in `options`            |
| `arrow`                       | `HTMLElement`                                                      | ❌ DOM ref      | Internal only                                    |
| All `FloatingHooks` callbacks | functions                                                          | ❌ function     | Some wired in `hooks` getter                     |

**Scalar fields to promote (5):** `placement`, `offset`, `hideArrow`, `closeOnClick`, `closeOnClickOutside`

---

## Dead API surface

Both components expose fields through `floatingOptions` that are silently ignored:

- `bds-tooltip`: `flip` and `shift` are in the type but absent from `options` getter
- `bds-popover`: `flip` and `shift` are hardcoded `true`; `strategy` is hardcoded `'fixed'`

These should either be removed from the public type or documented as no-ops. They must not
be promoted to flat props unless the `options` getter is updated to actually forward them.

---

## Existing bugs (both components)

These are independent of the migration but observed during analysis:

| File              | Line | Bug                                                                                                                    |
| ----------------- | ---- | ---------------------------------------------------------------------------------------------------------------------- |
| `bds-tooltip.tsx` | 174  | `trigger.setAttribute('ariaDescribedBy', ...)` — camelCase writes a non-standard attribute; must be `aria-describedby` |
| `bds-popover.tsx` | 249  | Same `ariaDescribedBy` camelCase bug                                                                                   |
| `bds-tooltip.tsx` | 100  | `get getPlacement` — accessor naming convention violation; must be `get placement`                                     |
| `bds-popover.tsx` | 300  | Same `get getPlacement` violation                                                                                      |
| `bds-tooltip.tsx` | 98   | `!this.floatingOptions.hideArrow \|\| false` — `\|\| false` is always redundant                                        |
| `bds-popover.tsx` | 294  | Same redundancy                                                                                                        |

---

## Migration plan

### Approach: Layered (progressive) API

Add flat `@Prop()` declarations for all scalar options. Keep `floatingOptions` for callbacks.
The flat props take precedence; `floatingOptions` scalar values are used as fallback for
backward compatibility, then removed in a future breaking-change release.

### Step 1 — `bds-tooltip`: promote scalar props

Add to `BdsTooltip`:

```ts
@Prop() readonly placement?: Position = 'bottom';
@Prop() readonly offset?: number = 8;
@Prop() readonly hideArrow?: boolean = false;
@Prop() readonly stayOnHover?: boolean = false;
```

Update `options` getter to read flat props first, falling back to `floatingOptions`:

```ts
get options(): FloatingMixinOptions {
  return {
    placement: this.placement ?? this.floatingOptions.placement ?? 'bottom',
    offset: this.offset ?? this.floatingOptions.offset ?? 8,
    arrow: (this.hideArrow ?? this.floatingOptions.hideArrow) ? undefined : this.arrowElement,
    strategy: 'fixed',
  };
}
```

Update `validateHide` similarly for `stayOnHover`.

### Step 2 — `bds-popover`: promote scalar props

Add to `BdsPopover`:

```ts
@Prop() readonly placement?: PopoverPosition = 'bottom-start';
@Prop() readonly offset?: number = 16;
@Prop() readonly hideArrow?: boolean = false;
@Prop() readonly closeOnClick?: boolean = false;
@Prop() readonly closeOnClickOutside?: boolean = true;
```

Update `options` getter and all three methods that read these from `floatingOptions`.

Note: `closeOnClickOutside` defaults to `true` in the current logic (opt-out pattern via `=== false` check).
The flat prop must preserve this default.

### Step 3 — Fix accessor naming on both components

Rename `get getPlacement` → `get placement` on both components.
Update all internal `this.getPlacement` references to `this.placement`.

### Step 4 — Fix aria attribute bug on both components

```ts
// Before (wrong):
trigger.setAttribute("ariaDescribedBy", "tooltip-content");

// After (correct):
trigger.setAttribute("aria-describedby", "tooltip-content");
```

### Step 5 — Remove `|| false` redundancy

```ts
// Before:
get canShowArrow(): boolean { return !this.floatingOptions.hideArrow || false; }

// After:
get canShowArrow(): boolean { return !this.hideArrow; }
```

### Step 6 — Deprecate scalar use of `floatingOptions`

Add a `@Watch('floatingOptions')` that emits a console warning when scalar fields
(`placement`, `offset`, `hideArrow`, etc.) are set through the object prop rather than the
flat prop. Mark the scalar fields of `FloatingTooltipProp` and `FloatingPopoverProp` as
`@deprecated` in JSDoc.

### Step 7 — Update Storybook stories

Replace all `.floatingOptions=${{ placement: 'top' }}` bindings with flat attributes:
`placement="top"`. Document the callback-only use of `floatingOptions` in MDX.

### Step 8 — Refactor trigger detection from anchoredMixin to slot-based pattern

**⚠️ BREAKING CHANGE** — This requires consumers to update their HTML structure from sibling pattern to nested pattern.

**Problem:** Current `anchoredMixin.onBeforeLoad()` uses heuristic DOM traversal (`previousElementSibling`, `closest()`, tag name checks) to find the trigger element. This is fragile and fails for nested structures (e.g., `<em><bds-tooltip>`).

**Solution:** Adopt Colibri's explicit slot-based trigger resolution pattern, adapted for Stencil without shadow DOM:

1. **Remove implicit trigger detection** — Delete `onBeforeLoad()` logic from `anchoredMixin`
2. **Add explicit trigger slot** — Both components get a default `<slot>` for the trigger element
3. **Use `@Element()` decorator** — Get host element reference (Stencil's equivalent to Lit's `@query`)
4. **Query in `componentDidLoad()`** — Find slot and tooltip content after DOM is ready
5. **Handle slot changes** — Attach `onSlotchange` event to detect dynamic trigger updates
6. **Use `assignedElements()`** — Get the actual trigger from slot's assigned elements

**Architecture change:**

```ts
// Before (anchoredMixin pattern - sibling):
<bds-button>Click me</bds-button>
<bds-tooltip>Tooltip text</bds-tooltip>

// After (slot pattern - nested):
<bds-tooltip placement="top">
  <bds-button>Click me</bds-button>
  <span slot="content">Tooltip text</span>
</bds-tooltip>
```

**Key advantages:**

- ✅ Explicit trigger relationship (no DOM heuristics)
- ✅ Works with any HTML element (not just `bds-*` components)
- ✅ Declarative in plain HTML
- ✅ Easier to debug (slot assignment visible in DevTools)
- ✅ Consistent with web standards (slot-based composition)

**Implementation notes for Stencil WITHOUT shadow DOM:**

```ts
@Component({
  tag: 'bds-tooltip',
  styleUrl: 'bds-tooltip.scss',
  shadow: false,  // ← No shadow DOM
})
export class BdsTooltip {
  @Element() el!: HTMLBdsTooltipElement;  // ← Stencil's host element access

  private triggerSlot!: HTMLSlotElement;
  private tooltipContent!: HTMLElement;

  componentDidLoad() {
    // Query directly from host element (light DOM)
    this.triggerSlot = this.el.querySelector('slot:not([name])') as HTMLSlotElement;
    this.tooltipContent = this.el.querySelector('.tooltip-content') as HTMLElement;

    // Attach to initial trigger
    const trigger = this.triggerSlot?.assignedElements()[0] as HTMLElement;
    if (trigger) {
      trigger.addEventListener('mouseenter', this.show);
      trigger.addEventListener('mouseleave', this.hide);
    }
  }

  private handleSlotChange = (e: Event) => {
    const slot = e.target as HTMLSlotElement;
    const newTrigger = slot.assignedElements()[0] as HTMLElement;

    // Detach from old trigger, attach to new
    // ... (see full implementation in conversation context)
  };

  render() {
    return (
      <Host class="bds-tooltip">
        <slot onSlotchange={this.handleSlotChange}></slot>
        <div class="tooltip-content" popover="manual">
          {!this.hideArrow && <div class="tooltip-arrow"></div>}
          <slot name="content"></slot>
        </div>
      </Host>
    );
  }
}
```

**Key differences from Colibri (Lit):**

- ❌ No `@query()` decorator in Stencil — use `@Element()` + `querySelector()`
- ❌ No `shadowRoot` — query directly from `this.el` (light DOM)
- ✅ `assignedElements()` works the same way
- ✅ Slot change events work the same way

### Step 9 — Update `bds-popover` with same slot-based pattern

Apply identical architectural changes to `bds-popover.tsx`:

- Add default slot for trigger
- Add named `content` slot for popover body
- Use `@Element()` + `componentDidLoad()` for element queries
- Handle slot changes for dynamic trigger updates
- Remove dependency on `anchoredMixin` heuristics

---

## Consumer Migration Guide (Steps 8-9 Breaking Changes)

### Before (sibling pattern):

```html
<!-- Tooltip -->
<bds-button>Hover me</bds-button>
<bds-tooltip>Tooltip text</bds-tooltip>

<!-- Popover -->
<bds-button>Click me</bds-button>
<bds-popover>Popover content</bds-popover>
```

### After (nested slot pattern):

```html
<!-- Tooltip -->
<bds-tooltip placement="top">
  <bds-button>Hover me</bds-button>
  <span slot="content">Tooltip text</span>
</bds-tooltip>

<!-- Popover -->
<bds-popover placement="bottom-start">
  <bds-button>Click me</bds-button>
  <div slot="content">Popover content</div>
</bds-popover>
```

### React consumers:

```tsx
// Before
<>
  <BdsButton>Hover me</BdsButton>
  <BdsTooltip>Tooltip text</BdsTooltip>
</>

// After
<BdsTooltip placement="top">
  <BdsButton>Hover me</BdsButton>
  <span slot="content">Tooltip text</span>
</BdsTooltip>
```

### Vue consumers:

```vue
<!-- Before -->
<bds-button>Hover me</bds-button>
<bds-tooltip>Tooltip text</bds-tooltip>

<!-- After -->
<bds-tooltip placement="top">
  <bds-button>Hover me</bds-button>
  <span slot="content">Tooltip text</span>
</bds-tooltip>
```

### Codemod opportunity:

A regex-based codemod could automate most of this migration by:

1. Finding sibling `<bds-tooltip>`/`<bds-popover>` elements
2. Wrapping the preceding element as the first child
3. Moving tooltip/popover content to a named `content` slot

---

## What stays in `floatingOptions`

After migration, `floatingOptions` should only carry lifecycle callbacks:

```ts
// Tooltip
floatingOptions: {
  onBeforeShow: (el) => boolean,
  onBeforeHide: (el) => boolean,
  onPositionUpdate: (result) => void,
  // etc.
}

// Popover — same callbacks
```

The `arrow: HTMLElement` field should be removed from the public-facing type entirely —
it is an internal implementation detail.

---

## `bds-flag` — `customFlags` prop migration

### Problem

The `customFlags: ICountry[]` prop requires consumers to construct a full 8-field object array
to accomplish any customisation — even adding a single custom country entry.
The current `CustomFlag` story illustrates the pain:

```html
<bds-flag id="custom-flag" country="99" label></bds-flag>
<script>
  document.querySelector("#custom-flag").customFlags = [
    {
      iso2: "custom",
      iso3: "CST",
      name: "My Custom Country",
      country: "99",
      flag_4x3: "https://flagcdn.com/w320/co.png",
      capital: "Custom City",
      continent: "",
      flag_1x1: "",
      iso: false,
    },
  ];
</script>
```

This is invisible in Storybook's Source panel (`.property` binding), requires JavaScript
even in plain-HTML contexts, and forces consumers to supply fields (`capital`, `continent`,
`flag_1x1`) that the component never reads.

---

### Approach comparison

#### Option A — Flat props for single-entry customisation

Add individual `@Prop()` declarations for each ICountry field, scoped to a `customFlag` prefix:

```html
<bds-flag
  country="99"
  label
  custom-flag-iso2="custom"
  custom-flag-iso3="CST"
  custom-flag-name="My Custom Country"
  custom-flag-code="99"
  custom-flag-src="https://flagcdn.com/w320/co.png"
></bds-flag>
```

| Pros                                                                    | Cons                                                            |
| ----------------------------------------------------------------------- | --------------------------------------------------------------- |
| Fully declarative — works from plain HTML and server-rendered templates | Only supports **one** custom entry per component instance       |
| Visible in Storybook Controls panel and Source panel                    | Attribute names are longer than the object field names          |
| No JS required for the common single-custom-flag case                   | Consumers needing multiple entries must still use `customFlags` |
| Compatible with React JSX and Vue template attribute syntax             | Two parallel APIs to document and maintain                      |

#### Option B — Keep `customFlags` array only (status quo)

| Pros                                              | Cons                                                                           |
| ------------------------------------------------- | ------------------------------------------------------------------------------ |
| Supports N custom entries per instance            | Requires JavaScript — unusable from plain HTML                                 |
| Data shape matches `ICountry` exactly — type-safe | Invisible in Storybook Source panel (`.property=${}` not serialised as attr)   |
| Single API surface                                | Forces all 8 fields even when 3 are relevant                                   |
|                                                   | Fields the component never reads (`capital`, `continent`, `flag_1x1`) leak out |

#### Decision: Layered approach (A over B)

Add flat props for the **single-entry** use case. Retain `customFlags` for multi-entry use.
When both are set on the same instance, `customFlags` takes precedence (existing behavior preserved).

---

### Dead API surface

- `ICountry.flag_1x1` — defined in the interface but never accessed in `flagUrl()`. Consumers
  who populate this field receive no visual effect.
- `ICountry.capital` / `ICountry.continent` — present in the interface, never consumed by
  the component.

These should be deprecated on `ICountry` so consumers are not confused by required fields that do nothing.

---

### Bonus: `flagBaseUrl` scalar prop

`FLAG_BASE_URL` is a hardcoded module constant (`./constants/flags/4x3/`). The CDN alternative
(`https://aqua-ds-doc-storybook.s3.us-east-1.amazonaws.com/flags/4x3/`) is commented out above it.
Consumers who want to serve flags from a CDN currently have no declarative path to do so.
A `flag-base-url` attribute solves this independently of the custom-entry problem.

---

### Migration plan

#### Step 1 — Add single-entry flat props to `BdsFlag`

```ts
/** ISO2 code for a single custom entry (e.g. `"custom"`). */
@Prop() readonly customFlagIso2?: string;

/** ISO3 code for the custom entry. */
@Prop() readonly customFlagIso3?: string;

/** Display name for the custom entry. */
@Prop() readonly customFlagName?: string;

/**
 * The `country` field value for the custom entry.
 * Must match the value set on the `country` prop when `identifier="code"`.
 */
@Prop() readonly customFlagCode?: string;

/** URL of the flag image for the custom entry (equivalent to `flag_4x3`). */
@Prop() readonly customFlagSrc?: string;
```

#### Step 2 — Add `flagBaseUrl` flat prop

```ts
/**
 * Base URL used to resolve flag SVG assets.
 * Overrides the bundled path. The component appends `{iso2}.svg` to this value.
 * @default undefined — falls back to the bundled asset path
 */
@Prop() readonly flagBaseUrl?: string;
```

#### Step 3 — Update `getCountry()` to inject the flat-prop entry

When `customFlagIso2` is set, synthesise an `ICountry` entry and prepend it to the lookup list
so it takes precedence over both `customFlags` array entries and the built-in catalog:

```ts
private getCountry(): ICountry {
  const synthetic: ICountry | null =
    this.customFlagIso2
      ? {
          iso2: this.customFlagIso2,
          iso3: this.customFlagIso3 ?? '',
          name: this.customFlagName ?? '',
          country: this.customFlagCode ?? '',
          flag_4x3: this.customFlagSrc ?? '',
          iso: false,
        }
      : null;

  const localCountries: ICountry[] = [
    ...(synthetic ? [synthetic] : []),
    ...allCountries,
    ...(this.customFlags ?? []),
    GLOBAL,
  ];

  const searchBy = (this.identifier === FlagIdentifier.CODE ? 'country' : this.identifier) as keyof ICountry;
  const value = this.identifier === FlagIdentifier.ISO3
    ? this.country.toUpperCase()
    : this.country.toLowerCase();

  return localCountries.find(c => c[searchBy] === value) ?? { country: '', iso2: '', iso3: '', name: '', flag_4x3: '', iso: false };
}
```

Priority order: **flat-prop entry → `customFlags` array → built-in catalog → GLOBAL**.

#### Step 4 — Update `flagUrl()` to use `flagBaseUrl`

```ts
private flagUrl(flag: string): string {
  const custom = this.customFlags?.find(c => c.iso2.toLowerCase() === flag);
  if (custom?.flag_4x3 !== undefined) return custom.flag_4x3;

  const base = this.flagBaseUrl ?? FLAG_BASE_URL;
  if (base.startsWith('http')) {
    return `${base}${flag}.svg`;
  }
  return `${window.location.origin}${getAssetPath(`${base}${flag}.svg`)}`;
}
```

#### Step 5 — Add new fields to `IFlag`

```ts
export interface IFlag extends ComponentInterface {
  label: boolean;
  shortName: boolean;
  callSign: boolean;
  alignFlag: AlignFlag;
  identifier: FlagIdentifier;
  shape: Shape;
  country: string;
  flagBaseUrl?: string;
  customFlagIso2?: string;
  customFlagIso3?: string;
  customFlagName?: string;
  customFlagCode?: string;
  customFlagSrc?: string;
  customFlags: ICountry[];
}
```

#### Step 6 — Deprecate dead fields on `ICountry`

```ts
export interface ICountry {
  iso2: string;
  iso3: string;
  iso: boolean;
  name: string;
  country: string;
  flag_4x3: string;
  /** @deprecated Not read by the component. Will be removed in the next major release. */
  flag_1x1?: string;
  /** @deprecated Not read by the component. Will be removed in the next major release. */
  capital?: string;
  /** @deprecated Not read by the component. Will be removed in the next major release. */
  continent?: string;
}
```

#### Step 7 — Update Storybook story

Replace the `CustomFlag` story's `.customFlags=${}` JS binding with flat attribute bindings.
Add `customFlagIso2`, `customFlagIso3`, `customFlagName`, `customFlagCode`, `customFlagSrc`,
and `flagBaseUrl` to `StoryArgs` and `argTypes` with appropriate controls and `category: 'Advanced'`.

The `customFlags` argType retains `control: false` with a note directing advanced multi-entry
consumers to set the JS property directly.

The `CustomFlag` story becomes:

```ts
export const CustomFlag: Story = {
  args: {
    country: "99",
    label: true,
    customFlagIso2: "custom",
    customFlagIso3: "CST",
    customFlagName: "My Custom Country",
    customFlagCode: "99",
    customFlagSrc: "https://flagcdn.com/w320/co.png",
  },
  render: (args) => html`
    <bds-flag
      country="${args.country}"
      ?label="${args.label}"
      custom-flag-iso2="${args.customFlagIso2}"
      custom-flag-iso3="${args.customFlagIso3}"
      custom-flag-name="${args.customFlagName}"
      custom-flag-code="${args.customFlagCode}"
      custom-flag-src="${args.customFlagSrc}"
    ></bds-flag>
  `,
};
```

### What stays in `customFlags`

`customFlags` is retained without deprecation for the multi-entry use case:

- Overriding flag images for multiple specific countries in one declaration
- Injecting a batch of new country entries not present in the default catalog

These require a structured array and remain inherently imperative.

---

## Files to modify

| File                                                                       | Change                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/components/overlays/bds-tooltip/bds-tooltip.tsx`                      | Add 4 flat props; **refactor to slot-based trigger pattern**; add `@Element()`, `componentDidLoad()`, `handleSlotChange()`; update `render()` with `<Host>` + slots; update `options`, `validateHide`, `canShowArrow`, `getPlacement`; fix aria attr                                                    |
| `src/components/overlays/bds-tooltip/types/ITooltip.ts`                    | Add flat prop fields                                                                                                                                                                                                                                                                                    |
| `src/components/overlays/bds-popover/bds-popover.tsx`                      | Add 5 flat props; **refactor to slot-based trigger pattern**; add `@Element()`, `componentDidLoad()`, `handleSlotChange()`; update `render()` with `<Host>` + slots; update `options`, `canShowArrow`, `getPlacement`, `attachClickOutside`, `detachClickOutside`, `handleFloatingClick`; fix aria attr |
| `src/components/overlays/bds-popover/types/IPopover.ts`                    | Add flat prop fields                                                                                                                                                                                                                                                                                    |
| `src/mixins/anchored.mixin.ts`                                             | **Remove heuristic trigger detection** — delete `onBeforeLoad()` DOM traversal logic; components now handle trigger resolution via slots                                                                                                                                                                |
| `src/services/floating/interfaces/Props.ts`                                | Deprecate scalar fields on `FloatingTooltipProp` / `FloatingPopoverProp`; remove `arrow` from public interface                                                                                                                                                                                          |
| `apps/boreal-docs/src/stories/overlays/bds-tooltip/bds-tooltip.stories.ts` | Replace object bindings with flat attrs; **update all story render functions to use nested slot pattern** (`<bds-tooltip><button>...<span slot="content">`)                                                                                                                                             |
| `apps/boreal-docs/src/stories/overlays/bds-tooltip/bds-tooltip.mdx`        | **Update usage examples** to show nested slot pattern for vanilla JS, React, and Vue                                                                                                                                                                                                                    |
| `apps/boreal-docs/src/stories/overlays/bds-popover/bds-popover.stories.ts` | Replace object bindings with flat attrs; **update all story render functions to use nested slot pattern**                                                                                                                                                                                               |
| `apps/boreal-docs/src/stories/overlays/bds-popover/bds-popover.mdx`        | **Update usage examples** to show nested slot pattern for vanilla JS, React, and Vue                                                                                                                                                                                                                    |
| `src/components/forms/bds-flag/bds-flag.tsx`                               | Add 5 `customFlag*` flat props + `flagBaseUrl`; update `getCountry()` to inject synthetic entry; update `flagUrl()` for `flagBaseUrl`                                                                                                                                                                   |
| `src/components/forms/bds-flag/interfaces/IFlag.ts`                        | Add `customFlagIso2`, `customFlagIso3`, `customFlagName`, `customFlagCode`, `customFlagSrc`, `flagBaseUrl` fields                                                                                                                                                                                       |
| `src/components/forms/bds-flag/interfaces/ICountry.ts`                     | Deprecate `flag_1x1`, `capital`, `continent`; make them optional                                                                                                                                                                                                                                        |
| `apps/boreal-docs/src/stories/forms/bds-flag/bds-flag.stories.ts`          | Replace `CustomFlag` story `.customFlags=${}` binding with flat attribute bindings; add new argTypes                                                                                                                                                                                                    |

---

## Verification

### Flat props (Steps 1-7)

- Run `pnpm build` from workspace root — no TypeScript errors
- Open Storybook and confirm `placement`, `offset`, `hideArrow` appear in the Controls panel as editable fields
- Confirm auto-generated source snippet in the Source panel shows the flat attributes
- Verify `aria-describedby` is present (kebab-case) in the rendered DOM via DevTools
- Existing `floatingOptions` object usage still works (backward compat fallback)

### Slot-based trigger pattern (Steps 8-9)

- **Nested pattern works** — `<bds-tooltip><button>Click</button><span slot="content">Text</span></bds-tooltip>` renders correctly
- **Trigger detection** — Tooltip/popover correctly identifies the first child as trigger (no span wrapper needed)
- **Dynamic slot changes** — Replacing trigger element via JS correctly detaches old listeners and attaches to new trigger
- **Light DOM queries** — `this.el.querySelector('slot')` finds slot element (no `shadowRoot` needed)
- **Works with any element** — Trigger can be `<button>`, `<a>`, `<bds-button>`, `<em>`, or any HTML element
- **Positioning accuracy** — Tooltip positions relative to actual trigger element, not wrapper or parent
- **No console errors** — No "trigger not found" or positioning warnings in browser console

### bds-flag changes

- Open the Flag story `CustomFlag` and confirm `custom-flag-*` controls appear in the Controls panel
- Verify the Source panel shows the declarative attribute syntax — no `<script>` block
- Confirm the `customFlags` JS array prop still works and takes precedence over the flat-prop entry
- Set `flag-base-url` to the S3 CDN URL and verify flags load from that origin in the Default story
