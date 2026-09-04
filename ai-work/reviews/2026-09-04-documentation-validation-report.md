# Boreal DS — Documentation Validation Report

**Component:** `bds-color-picker` (EOA-17156)
**Validated against:** `2026-09-04-commit-1481847e-feature-EOA-17156-color-picker-review.md`
**Date:** 2026-09-04
**Scope:** JSDoc completeness, Storybook/MDX gaps, consumer-facing documentation, CSS custom property documentation

---

## 1. CONFIRMED Documentation Gaps

### 1.1 Missing Class-Level JSDoc (ALL 6 components)

Every component is missing its class-level JSDoc block. Per `ai-docs/guidelines/jsdoc-template.md`, the class-level JSDoc has two responsibilities: (1) component description (becomes `description` in `custom-elements.json`) and (2) `@slot` tags. None of the six components have either.

| Component | File | Class JSDoc | Impact |
|-----------|------|:-----------:|--------|
| `bds-color-picker` | `bds-color-picker.tsx:34` | ❌ Missing | No description in CEM; no `@slot` documentation |
| `bds-color-controls` | `bds-color-controls.tsx:7` | ❌ Missing | No description in CEM |
| `bds-color-box` | `bds-color-box.tsx:7` | ❌ Missing | No description in CEM |
| `bds-hue-slider` | `bds-hue-slider.tsx:5` | ❌ Missing | No description in CEM |
| `bds-alpha-slider` | `bds-alpha-slider.tsx:5` | ❌ Missing | No description in CEM |
| `bds-color-format` | `bds-color-format.tsx:8` | ❌ Missing | No description in CEM |

**Severity: High.** Without class-level JSDoc, `custom-elements.json` ships with empty `description` fields for all six components. Framework wrappers (React, Vue, Angular) inherit these empty descriptions, and Storybook's auto-generated docs show no component summary.

### 1.2 Missing Storybook Stories and MDX (confirmed)

**The review's finding #6 (`[missing-stories]`) is CORRECT.** No `.stories.ts` or `.mdx` files exist anywhere on the branch for any of the six components. The glob search returned zero results:

```
packages/boreal-web-components/src/components/forms/bds-color-picker/**/*.stories.ts  → 0 files
apps/boreal-docs/src/stories/**/*color*                                                → 1 file (foundations/colors.mdx — unrelated)
```

**Severity: Critical.** The component is completely undocumented for consumers. This is the single largest documentation gap.

### 1.3 Missing CSS Custom Property Documentation

`--bds-color-picker-width` is declared at `bds-color-picker.scss:8` but has **no `@prop` JSDoc comment** above it. Per `jsdoc-template.md` §"CSS Custom Properties — Document in SCSS, Not in TSX", Stencil reads `@prop` comments from the SCSS file to generate `cssProperties[]` in the manifest.

```scss
// Current (line 8):
--bds-color-picker-width: 100%;

// Required:
/**
 * @prop --bds-color-picker-width: Sets a custom width for the color picker, overriding the default 100%.
 */
--bds-color-picker-width: 100%;
```

Additionally, the prop-level JSDoc on `customWidth` (line 98 of `bds-color-picker.tsx`) says *"Sets a custom width via the `--bds-color-picker-width` CSS custom property"* — but the CSS custom property itself is not documented in SCSS, so it won't appear in the auto-generated CSS properties table.

**Severity: Medium.** Consumers who discover the `customWidth` prop won't find the corresponding CSS custom property in the auto-generated docs.

### 1.4 Undocumented Type Exports

All five event payload types lack JSDoc. These are re-exported from `components.d.ts` and are part of the public consumer API:

| Type | File | JSDoc | Consumers see in CEM |
|------|------|:-----:|---------------------|
| `ColorChangeDetail` | `bds-color-controls/types/types.ts:3` | ❌ | `{ hex: string; rgb: RgbColor; hsl: HslColor; hsb: HsvColor }` — no description |
| `ColorBoxChangeDetail` | `bds-color-box/types/types.ts:1` | ❌ | `{ s: number; v: number }` — no description |
| `HueChangeDetail` | `bds-hue-slider/types/types.ts:1` | ❌ | `{ h: number }` — no description |
| `AlphaChangeDetail` | `bds-alpha-slider/types/types.ts:1` | ❌ | `{ a: number }` — no description |
| `Format` / `TripleFormat` / `ChannelConfig` | `bds-color-format/types/types.ts` | ❌ | No description |

**Severity: Medium.** Consumers importing these types for event handler typing get no inline documentation.

### 1.5 Duplicate Type Definition — `HueChangeDetail`

`HueChangeDetail` is defined in **two** separate files:

1. `bds-hue-slider/types/types.ts:1` — `export type HueChangeDetail = { h: number }`
2. `bds-color-picker/types/types.ts:1` — `export type HueChangeDetail = { h: number }`

Both are re-exported via their respective barrel `index.ts` files. `components.d.ts` line 107 imports from `bds-hue-slider/types` (the canonical location). The duplicate in `bds-color-picker/types/types.ts` is dead code that creates confusion about which is authoritative.

**Severity: Low (documentation).** No runtime impact, but confuses anyone tracing the type origin.

### 1.6 Undocumented Interface Files

All six interface files lack JSDoc on both the interface itself and its members:

| Interface | File | JSDoc |
|-----------|------|:-----:|
| `IColorPicker` | `IColorPicker.ts` | ❌ |
| `IColorControls` | `IColorControls.ts` | ❌ |
| `IColorBox` | `IColorBox.ts` | ❌ |
| `IHueSlider` | `IHueSlider.ts` | ❌ |
| `IAlphaSlider` | `IAlphaSlider.ts` | ❌ |
| `IColorFormat` | `IColorFormat.ts` | ❌ |

**Severity: Low.** Interface files are internal contracts (not directly consumed), but they serve as the canonical API reference for contributors. Missing JSDoc here means the next developer modifying these components has no inline documentation.

### 1.7 Undocumented Helper Functions

`color-utils.ts` exports 7 functions and 1 constant. Only `toHexString()` has JSDoc:

| Export | JSDoc | Notes |
|--------|:-----:|-------|
| `DEFAULT_HSV` | ❌ | Default red at full saturation/brightness |
| `normalizeHsva()` | ❌ | Rounds HSVA values to 2 decimal places |
| `parseColor()` | ❌ | Parses any color string to HsvColor; critical for understanding accepted input formats |
| `colorFromHsv()` | ❌ | Wraps colordx constructor |
| `colorDetails()` | ❌ | Builds the `ColorChangeDetail` payload |
| `toHexString()` | ✅ | "Returns a normalized uppercase 6-digit HEX string…" |
| `gradesCustomFormat()` | ❌ | Appends degree symbol |
| `formats` | ❌ | Format configuration registry (hex/rgb/hsl/hsb) |

**Severity: Low.** Helpers are internal, but `parseColor()` in particular is the gateway for understanding what input formats the component accepts — valuable for both contributors and consumers who want to set `value` programmatically.

---

## 2. JSDoc Quality Assessment Per Component

### `bds-color-picker` — Rating: **Good (props/events/methods), Poor (class-level)**

| Category | Count | Documented | Quality Notes |
|----------|:-----:|:----------:|---------------|
| Class-level JSDoc | 1 | 0 | No component description, no `@slot` tags |
| `@Prop()` | 15 | 15 | All have `/** */` directly above decorator ✅ |
| `@Event()` | 6 | 6 | All have JSDoc describing the payload ✅ |
| `@Method()` | 2 | 2 | Both have JSDoc ✅ |

**Prop JSDoc quality notes:**
- `value`: "Current color as a six-digit HEX value." — Clear ✅
- `customWidth`: "Sets a custom width via the `--bds-color-picker-width` CSS custom property." — Good, cross-references the CSS var ✅
- `readOnly`: Uses `{ attribute: 'readonly' }` — JSDoc says "Prevents editing and opening the picker." ✅
- `customValidators`: "Custom validators applied to the field value." — Could note the `IFormValidator` shape ⚠️
- `validationTiming`: "Determines when field validation runs." — Could enumerate valid values (`'blur' | 'change'`) ⚠️

**Event JSDoc quality notes:**
- `valueChange`: "Emits the canonical six-digit HEX string after a committed color change." — Good but doesn't mention Vue `v-model` exception ⚠️
- `bdsChange`: "Emits full color details after a committed color change." — Doesn't describe the `ColorChangeDetail` payload shape ⚠️
- `bdsInput`: "Emits the current HEX value while the color is being edited." — Good ✅
- `bdsFocus`/`bdsBlur`: Clear ✅
- `bdsValidationChange`: Clear ✅

### `bds-color-controls` — Rating: **Good (props/events), Poor (class-level)**

| Category | Count | Documented |
|----------|:-----:|:----------:|
| Class-level JSDoc | 1 | 0 |
| `@Prop()` | 1 | 1 ✅ |
| `@Event()` | 1 | 1 ✅ |

### `bds-color-box` — Rating: **Good (props/events), Poor (class-level)**

| Category | Count | Documented |
|----------|:-----:|:----------:|
| Class-level JSDoc | 1 | 0 |
| `@Prop()` | 4 | 4 ✅ |
| `@Event()` | 1 | 1 ✅ |

### `bds-hue-slider` — Rating: **Good (props/events), Poor (class-level)**

| Category | Count | Documented |
|----------|:-----:|:----------:|
| Class-level JSDoc | 1 | 0 |
| `@Prop()` | 1 | 1 ✅ |
| `@Event()` | 1 | 1 ✅ |

### `bds-alpha-slider` — Rating: **Good (props/events), Poor (class-level)**

| Category | Count | Documented |
|----------|:-----:|:----------:|
| Class-level JSDoc | 1 | 0 |
| `@Prop()` | 2 | 2 ✅ |
| `@Event()` | 1 | 1 ✅ |

### `bds-color-format` — Rating: **Good (props/events), Poor (class-level)**

| Category | Count | Documented |
|----------|:-----:|:----------:|
| Class-level JSDoc | 1 | 0 |
| `@Prop()` | 2 | 2 ✅ |
| `@Event()` | 2 | 2 ✅ |

---

## 3. Recommended Stories List

Based on the component's capabilities and the `storybook-patterns.md` conventions, the following stories should exist:

### `bds-color-picker.stories.ts`

| Story | Purpose | Key args |
|-------|---------|----------|
| `Default` | Basic usage with label | `label`, `value` |
| `WithInitialValue` | Pre-set color | `value="#3498db"` |
| `WithHelperText` | Field with helper text | `helperText`, `info` |
| `Error` | Error state display | `error`, `errorMessage` |
| `Disabled` | Disabled state | `disabled` |
| `ReadOnly` | Read-only state | `readOnly` |
| `Required` | Required field indicator | `required` |
| `CustomWidth` | Custom CSS width | `customWidth="500px"` |
| `WithOpacity` | Alpha channel usage | `value` with alpha |
| `FormAssociation` | Inside `<form>` with submit/reset | N/A (play function) |

### `bds-color-picker.mdx`

Required sections per `storybook-patterns.md`:
1. **Overview** — what the component does, when to use it
2. **Basic usage** — Default story with copy-paste HTML
3. **Form integration** — form association, validation, reset behavior
4. **Color formats** — hex/rgb/hsl/hsb switching in the picker panel
5. **Accessibility** — keyboard navigation (Tab → Enter/Space opens popover, Arrow keys in color box switch axes), ARIA roles (`role="group"`, `role="img"` on swatch, `aria-roledescription="2D slider"` on inputs), screen reader behavior
6. **CSS custom properties** — `--bds-color-picker-width` usage
7. **Event handling** — `valueChange` vs `bdsChange` distinction, `bdsInput` for live updates
8. **Properties table** — `<ArgTypes>` block covering all 15 props + 6 events
9. **Sub-components** — `<ArgTypes>` blocks for `bds-color-controls`, `bds-color-box`, `bds-hue-slider`, `bds-alpha-slider`, `bds-color-format` (internal components, documented for advanced consumers)

---

## 4. Review Finding Validation

### Review finding #6: `[missing-stories]` — **CONFIRMED**

No `.stories.ts` or `.mdx` files exist. The component is completely undocumented for consumers. This is correctly flagged as **High severity** — I would escalate it to **Critical** since it's a blocker for the merge checklist item "Storybook/MDX/README updated when behavior or APIs change" (currently unchecked in the review).

### Auto-generated `readme.md` — **Not yet generated**

No `readme.md` files exist in the component directories. These are generated by Stencil's `docs-readme` output target during build. Once the build runs, Stencil will generate `readme.md` files from the JSDoc. The current state means:
- The generated readmes will have **empty component descriptions** (no class-level JSDoc)
- The generated readmes will have **empty CSS properties sections** (no `@prop` in SCSS)
- The prop/event tables will populate correctly from the existing per-member JSDoc

### `custom-elements.json` dependency on JSDoc quality — **CONFIRMED**

The CEM output directly depends on JSDoc quality:
- **Class-level JSDoc** → `description` field per component. Currently **empty for all 6 components**.
- **`@Prop()` JSDoc** → `description` in `members[]` and `attributes[]`. Currently **populated** ✅
- **`@Event()` JSDoc** → `description` in `events[]`. Currently **populated** ✅
- **`@Method()` JSDoc** → `description` in `members[]`. Currently **populated** ✅
- **`@prop` in SCSS** → `cssProperties[]`. Currently **empty** (no `@prop` comment on `--bds-color-picker-width`).
- **Type exports** → `declarations[]` with `docs.text`. Currently **empty descriptions** for all 5 payload types.

---

## 5. Consumer-Facing Documentation Issues

### 5.1 `ColorChangeDetail` type — importable but undocumented ✅/❌

**Importable:** Yes. Re-exported from `components.d.ts:96`. Consumers can write:
```ts
import type { ColorChangeDetail } from '@telesign/boreal-web-components';
```

**Documented:** No. The type has no JSDoc, so IDE hover tooltips show only the raw shape `{ hex: string; rgb: RgbColor; hsl: HslColor; hsb: HsvColor }` with no explanation of what each field represents or when this type is used.

### 5.2 Event payload types — importable but undocumented ✅/❌

All four payload types (`ColorChangeDetail`, `ColorBoxChangeDetail`, `HueChangeDetail`, `AlphaChangeDetail`) are re-exported from `components.d.ts` and importable. None have JSDoc descriptions.

### 5.3 `valueChange` vs `bdsChange` distinction — partially documented ⚠️

The JSDoc differentiates them:
- `valueChange`: "Emits the canonical six-digit HEX string after a committed color change."
- `bdsChange`: "Emits full color details after a committed color change."

**Missing:** No explanation of *when* to use which. The `valueChange` Vue `v-model` exception (documented in MEMORY.md) is not mentioned in the JSDoc. Consumers reading only the auto-generated docs won't know:
1. `valueChange` carries a `string` (HEX only)
2. `bdsChange` carries a `ColorChangeDetail` object (hex + rgb + hsl + hsb)
3. `valueChange` is the Vue `v-model` integration point
4. Both fire at the same time for the same user action

### 5.4 `--bds-color-picker-width` CSS custom property — not documented in CEM ❌

The prop JSDoc on `customWidth` references it, but the SCSS `@prop` comment is missing. This means:
- It won't appear in `custom-elements.json` `cssProperties[]`
- It won't appear in the auto-generated `readme.md` CSS properties table
- Framework wrapper docs won't list it
- Consumers must read the source to discover it

### 5.5 `bds-color-format` native `onChange` — documentation concern ⚠️

The review flags `bds-color-format.tsx:185` using `onChange` (native DOM event) instead of `onBdsChange` on a `<bds-number-field>`. From a documentation perspective, if this is intentional, it should be documented why. If it's a bug (as the review suggests), fixing it may change the event behavior consumers observe.

---

## 6. Summary

### Documentation Readiness Score: **NOT READY**

| Category | Status | Blocking? |
|----------|:------:|:---------:|
| Per-member JSDoc (props/events/methods) | ✅ Complete | No |
| Class-level JSDoc (all 6 components) | ❌ Missing | Yes — empty CEM descriptions |
| CSS custom property `@prop` in SCSS | ❌ Missing | Yes — invisible in CEM |
| Storybook stories (`.stories.ts`) | ❌ Missing | Yes — no consumer docs |
| MDX documentation | ❌ Missing | Yes — no narrative docs |
| Type export JSDoc | ❌ Missing | No — importable but undocumented |
| Interface file JSDoc | ❌ Missing | No — internal only |
| Helper function JSDoc | ⚠️ Partial | No — `toHexString()` only |
| `valueChange`/`bdsChange` consumer guidance | ⚠️ Partial | No — confusing but functional |
| Duplicate `HueChangeDetail` type | ⚠️ Code quality | No — confusing but harmless |

### Required fixes before merge (documentation-specific)

1. **Add class-level JSDoc** to all 6 components — at minimum a one-line description. `bds-color-picker` also needs `@slot` tags if it uses slots (it doesn't appear to, based on `render()`, but the class JSDoc is still required for the description).
2. **Add `@prop` comment** for `--bds-color-picker-width` in `bds-color-picker.scss`.
3. **Create `.stories.ts` and `.mdx`** files for at minimum `bds-color-picker` (the consumer-facing root component). Sub-component stories are optional but recommended.
4. **Add JSDoc to `ColorChangeDetail`** and the other 4 payload types — consumers import these.

### Recommended fixes (non-blocking)

5. Add JSDoc to interface files for contributor documentation.
6. Add JSDoc to `parseColor()` and other exported helpers.
7. Remove the duplicate `HueChangeDetail` from `bds-color-picker/types/types.ts`.
8. Enhance `valueChange` JSDoc to mention the Vue `v-model` use case.
9. Enhance `bdsChange` JSDoc to describe the `ColorChangeDetail` payload shape.
