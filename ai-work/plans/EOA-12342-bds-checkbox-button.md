---
ticket: EOA-12342
component: bds-checkbox-button
status: done
created: 2026-05-19
---

# bds-checkbox-button Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Implement `bds-checkbox-button` — a button-shaped checkbox leaf component that renders as a toggleable pill-button, styled identically to `bds-radio-button` but with independent toggle semantics, `role=checkbox`, and individual `tabindex` management.

**Architecture:** `bds-checkbox-button` is a leaf-only component (not form-associated — the future `bds-checkbox-group` will own form state). It shares all visual styles with `bds-radio-button` via a new `_selectable-button.scss` shared partial loaded with `@use` (Approach 2 — the partial declares its own Sass dependencies explicitly; see Task 1 notes). The component emits `bdsChange` with `{ checked: boolean, value: string }` and is designed to work standalone or inside a future group wrapper.

**Tech Stack:** Stencil v4, SCSS (`$boreal-*` tokens, `bds-transition-surface`, `bds-focus-ring`, `bds-hover-shadow`, `bds-active-shadow-inset` mixins), Lit (stories), `@stencil/core/testing` (unit tests), Storybook 8 + MDX.

---

## Files to create / modify

| File                                                                                                                    | Notes                                                                                            |
| ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `packages/boreal-web-components/src/components/forms/_shared/_selectable-button.scss`                                   | New — parameterized mixin shared by radio-button and checkbox-button                             |
| `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.scss`                            | Modify — replace inline styles with `@import` + `@include selectable-button('bds-radio-button')` |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-button/types/ICheckboxButton.ts`                      | New — `CheckboxButtonChangeDetail` and `ICheckboxButton` interface                               |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-button/bds-checkbox-button.tsx`                       | New — component implementation                                                                   |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-button/bds-checkbox-button.scss`                      | New — `@import` + `@include selectable-button('bds-checkbox-button')`                            |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.basics.spec.ts`   | New — render, label, slot, structure tests                                                       |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.a11y.spec.ts`     | New — ARIA role, checked, disabled, tabindex tests                                               |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.events.spec.ts`   | New — toggle, disabled guard, Space key, Enter key tests                                         |
| `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.variants.spec.ts` | New — BEM class application per state tests                                                      |
| `apps/boreal-docs/src/stories/forms/bds-checkbox-button/bds-checkbox-button.stories.ts`                                 | New — Storybook stories                                                                          |
| `apps/boreal-docs/src/stories/forms/bds-checkbox-button/bds-checkbox-button.mdx`                                        | New — MDX documentation                                                                          |

---

## Tasks

### Task 1: Shared SCSS partial + radio-button refactor ✅ `70fef1fc`

> **Decision:** Approach 1 (`@import`) was attempted but failed — Sass's module system does not propagate `@use`-scoped tokens into `@import`-ed files, so `$boreal-*` variables were undefined inside the partial. Approach 2 was implemented instead: the shared partial explicitly `@use`s its own dependencies (`@telesign/boreal-style-guidelines` and `_interactions.scss`), and component SCSS files `@use` the partial with `as *`. This is the standard Sass module pattern and produced a clean build with no warnings.
>
> **Additional change:** `@extend %inline-flex-center` was replaced with inline `display: inline-flex; align-items: center;` in the mixin body, because `@extend` cannot cross `@use` module boundaries.

> ~~**Two approaches are available.** Implement both sequentially, then decide which to keep before committing. Approach 1 is the primary path; Approach 2 is the fallback if Approach 1 produces Sass deprecation warnings that are unacceptable.~~

#### Approach 1 — `@import` to inherit injected scope

**Files:**

- `packages/boreal-web-components/src/components/forms/_shared/_selectable-button.scss` (create)
- `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.scss` (modify)

**Acceptance criteria (Approach 1):**

- The file must contain a single `@mixin selectable-button($prefix)` with no top-level rules outside the mixin.
- The mixin must **not** contain any `@use` or `@import` directives — it relies on `$boreal-*` tokens and interaction mixins being injected globally by Stencil's `injectGlobalPaths`. This is a hard constraint: adding `@use` here will cause a Sass double-import error at build time.
- The mixin body must mirror the current `bds-radio-button.scss` rules exactly, parameterized by `$prefix`:
  - Base: `display: inline-flex`, `align-items: center`, `justify-content: center`, `width: 100%`, `gap: $boreal-spacing-2xs`, `padding: $boreal-spacing-2xs $boreal-spacing-s`, `border: 1px solid transparent`, `border-radius: $boreal-radius-s`, `background-color: $boreal-ui-default-base`, `color: $boreal-text-default`, `cursor: pointer`, `outline: none`, `@include bds-transition-surface`
  - Hidden `input` rule: `position: absolute; opacity: 0; width: 0; height: 0; margin: 0; pointer-events: none`
  - Hover state (not disabled, not checked, not error): `background-color: $boreal-ui-default-lighter`, `@include bds-hover-shadow(rgba(19, 19, 22, 0.15))`
  - Focus/focus-visible: `z-index: 1`, `background-color: $boreal-ui-default-lighter`, `@include bds-focus-ring($boreal-stroke-focus, $boreal-ui-inverse)`, `outline: none`
  - Active (not disabled, not checked, not error): `z-index: 1`, `background-color: $boreal-ui-default-lighter`, `@include bds-active-shadow-inset($boreal-stroke-focus, $boreal-ui-inverse, rgba(19, 19, 22, 0.15))`
  - `--checked` modifier: `background-color: $boreal-ui-inverse`, `border-color: $boreal-stroke-primary-base`, `color: $boreal-text-primary-base`; hover/focus/active inside checked: `background-color: $boreal-ui-primary-lighter`
  - `--error` modifier: `background-color: $boreal-ui-inverse`, `color: $boreal-text-danger-base`; hover/focus/active inside error: `background-color: $boreal-ui-danger-lighter`; error + checked: `border-color: $boreal-stroke-danger-base`
  - `--disabled` modifier: `cursor: not-allowed`, `pointer-events: none`, `background-color: $boreal-ui-inverse`, `color: $boreal-text-disabled`; disabled + checked: `border-color: $boreal-stroke-primary-light`, `color: $boreal-text-primary-light`
  - `__label` element: `font-family: $boreal-typography-font-family-primary`, `font-size: $boreal-typography-font-size-sm`, `font-weight: $boreal-typography-font-weight-semibold`, `line-height: $boreal-typography-line-height-sm`
  - `__info` element: `@extend %inline-flex-center`
  - `__icon` element: `display: flex; align-items: center; justify-content: center`; `&:empty { display: none }`
  - `__info-icon` element: `display: inline-flex`, `align-items: center`, `justify-content: center`, `font-size: $boreal-typography-font-size-sm`, `line-height: 1`, `color: $boreal-icon-default-ink`
- `bds-radio-button.scss` must be replaced with exactly two lines:
  ```scss
  @import "../_shared/selectable-button";
  @include selectable-button("bds-radio-button");
  ```
- After the change, `pnpm build` on `boreal-web-components` must succeed with no Sass errors.
- Visual output of `bds-radio-button` in Storybook must be pixel-identical to before the refactor.

**Unit tests to cover:** _(none — this task is SCSS-only; visual regression is verified manually)_

**Manual test _(waiveable)_:**

Run: `pnpm dev:components` then open Storybook

- [ ] Navigate to `Forms/Radio Group/Radio Button` → Default story
- [ ] Visually confirm the radio button appearance is unchanged
- [ ] Check `bds-radio-button--checked`, `bds-radio-button--error`, `bds-radio-button--disabled` states still render correctly
- [ ] Open browser DevTools and confirm no Sass/CSS errors in the console
- [ ] Pass: all states look identical to pre-refactor

**Commit (Approach 1):**

```bash
git commit -m "refactor(web-components): EOA-12342 extract shared selectable-button mixin via @import"
```

---

#### Approach 2 — Partial explicitly `@use`s its own dependencies (fallback)

Use this approach if Approach 1 produces Sass `@import`/`@use` mixing deprecation warnings that cannot be suppressed.

**Files:**

- `packages/boreal-web-components/src/components/forms/_shared/_selectable-button.scss` (create — different implementation than Approach 1)
- `packages/boreal-web-components/src/components/forms/bds-radio-button/bds-radio-button.scss` (modify — same two-liner as Approach 1)

**Acceptance criteria:**

- The shared partial declares all its own Sass dependencies explicitly via `@use` at the top of the file, using relative paths. It does not rely on `injectGlobalPaths` for any variable or mixin resolution.
- The partial accepts the same `$prefix` parameter as Approach 1 and produces identical output.
- `bds-radio-button.scss` uses `@use` instead of `@import` to load the partial, with `as *` to avoid namespace prefixes.
- After the change, `pnpm build` succeeds with no Sass errors and no `@import`-related deprecation warnings.
- Visual output of `bds-radio-button` in Storybook must be pixel-identical to Approach 1.

**Trade-offs vs Approach 1:**

- Avoids deprecated `@import` mixing — no deprecation warnings.
- The partial couples itself to the exact file paths of its dependencies. If token or mixin file locations change, the partial must be updated.
- Requires the `boreal-style-guidelines` package path to be resolvable from inside the partial at compile time (relies on `includePaths: ['node_modules']` in `stencil.config.ts`).

**Unit tests to cover:** _(none — SCSS only)_

**Manual test _(waiveable)_:**

Run: `pnpm dev:components` then open Storybook

- [ ] Same visual checklist as Approach 1
- [ ] Build output shows no `@import` deprecation warnings in the Sass compiler output

**Commit (Approach 2):**

```bash
git commit -m "refactor(web-components): EOA-12342 extract shared selectable-button mixin via explicit @use"
```

> **Decision point:** After running both builds, compare the console output. Keep the approach that produces cleaner output. Drop the other branch before moving to Task 2.

---

### Task 2: `ICheckboxButton.ts` — types and interfaces ✅ `20b56c8c`

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/types/ICheckboxButton.ts` (create)

**Acceptance criteria:**

- Export `CheckboxButtonChangeDetail` interface with two required fields:
  - `checked: boolean` — the new toggle state after interaction
  - `value: string` — the `value` prop of the button that changed
- Export `ICheckboxButton` interface defining the component's public contract with these members:
  - `value: string`
  - `label: string`
  - `info: string`
  - `checked: boolean`
  - `disabled: boolean`
  - `error: boolean`
- No implementation, no Stencil imports — pure TypeScript interfaces only.
- Pattern mirrors `IRadioButton.ts` at `packages/boreal-web-components/src/components/forms/bds-radio-button/types/IRadioButton.ts`.

**Unit tests to cover:** _(none — types file only)_

**Manual test _(waiveable)_:**

- [ ] `pnpm tsc --noEmit` from `packages/boreal-web-components` passes with no errors

**Commit:**

```bash
git commit -m "feat(web-components): EOA-12342 add ICheckboxButton interface and change detail type"
```

---

### Task 3: Scaffold `bds-checkbox-button.tsx` — props and events only ✅ `b865f859`

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/bds-checkbox-button.tsx` (create)

**Acceptance criteria:**

- `@Component` decorator: `tag: 'bds-checkbox-button'`, `styleUrl: 'bds-checkbox-button.scss'`. Do NOT set `formAssociated: true` — the leaf component is not form-associated.
- Class declaration: `export class BdsCheckboxButton implements ICheckboxButton`
- `@Element() el!: HTMLBdsCheckboxButtonElement`
- Props (all via `@Prop()`):

  | Name       | Type      | Default | mutable | reflect | Description                    |
  | ---------- | --------- | ------- | ------- | ------- | ------------------------------ |
  | `checked`  | `boolean` | `false` | yes     | yes     | Toggle state                   |
  | `disabled` | `boolean` | `false` | no      | yes     | Disables interaction           |
  | `error`    | `boolean` | `false` | no      | yes     | Error styling                  |
  | `value`    | `string`  | `'on'`  | no      | no      | Form value when checked        |
  | `name`     | `string`  | `''`    | no      | yes     | Stamped by parent group        |
  | `label`    | `string`  | `''`    | no      | no      | Label text; falls back to slot |
  | `info`     | `string`  | `''`    | no      | no      | Tooltip text on info icon      |

- Events (via `@Event({ bubbles: true })`):
  - `bdsChange: EventEmitter<CheckboxButtonChangeDetail>` — emitted on every toggle (both check and uncheck)
- `render()` returns `<Host />` stub (empty) — full render will come in Task 4.
- `componentDidLoad()` sets `role`, `aria-checked`, and `tabindex` on `this.el`:
  - `role="checkbox"`
  - `aria-checked="false"`
  - `tabindex`: `"0"` when not disabled, `"-1"` when disabled
- A `@Watch('disabled')` handler keeps `tabindex` in sync when the `disabled` prop changes after mount:
  - Sets `tabindex="0"` on enable, `"-1"` on disable
- All JSDoc blocks must be complete on `@Prop`, `@Event`, and the class-level doc comment.

**Unit tests to cover:** _(deferred to Task 7 — scaffold only here)_

**Manual test _(waiveable)_:**

Run: `pnpm build` in `packages/boreal-web-components`

- [ ] Build succeeds with no TypeScript or Stencil errors
- [ ] `bds-checkbox-button` appears in the generated `components.d.ts`

**Commit:**

```bash
git commit -m "feat(web-components): EOA-12342 scaffold bds-checkbox-button with props and events"
```

---

### Task 4: Lifecycle, toggle logic, and `render()` ✅ `d23339fc`

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/bds-checkbox-button.tsx` (modify)

**Acceptance criteria:**

- Implement `private toggle()`:
  - Guard: `if (this.disabled) return`
  - Flip `this.checked = !this.checked`
  - Update `aria-checked` on `this.el` to the new value as a string
  - Emit `this.bdsChange.emit({ checked: this.checked, value: this.value })`
- Implement `private handleClick = () => this.toggle()`
- Implement `private handleKeyDown = (event: KeyboardEvent)`:
  - `Space` key only: call `event.preventDefault()` then `this.toggle()`
  - All other keys: no-op
- Implement `private get classMap(): StyleModifiers`:
  ```
  'bds-checkbox-button': true,
  'bds-checkbox-button--checked': this.checked,
  'bds-checkbox-button--error': this.error,
  'bds-checkbox-button--disabled': this.disabled,
  ```
- Replace the stub `render()` with full DOM:
  - `<Host class={this.classMap} onClick={this.handleClick} onKeyDown={this.handleKeyDown}>`
  - Hidden `<input type="checkbox" name={this.name} value={this.value} checked={this.checked} disabled={this.disabled} aria-hidden="true" tabIndex={-1} onFocus={() => (this.el as HTMLElement).focus()} />`
  - `<span class="bds-checkbox-button__icon"><slot name="icon" /></span>` — `&:empty { display: none }` handles hiding via CSS
  - `<span class="bds-checkbox-button__label">{this.label || <slot />}</span>`
  - Conditional info block (same pattern as `bds-radio-button`): only rendered when `this.info` is truthy:
    - `<span class="bds-checkbox-button__info">`
    - `<span class="bds-checkbox-button__info-icon bds-icon-info-circle" aria-hidden="true" />`
    - `<bds-tooltip>{this.info}</bds-tooltip>`

**Unit tests to cover:** _(deferred to Task 7)_

**Manual test _(waiveable)_:**

Run: `pnpm dev:components` — open browser at the Stencil dev server

- [ ] Add `<bds-checkbox-button label="Option A" value="a"></bds-checkbox-button>` to a test page
- [ ] Clicking the button toggles the `--checked` class on and off (inspect DevTools)
- [ ] Pressing Space while focused toggles checked state
- [ ] Pressing Enter does nothing
- [ ] `aria-checked` attribute flips between `"true"` and `"false"` on each toggle
- [ ] `disabled` attribute sets `tabindex="-1"` and prevents toggle on click
- [ ] `info="hint text"` renders the info icon with tooltip

**Commit:**

```bash
git commit -m "feat(web-components): EOA-12342 implement toggle logic and render for bds-checkbox-button"
```

---

### Task 5: SCSS ✅ `7ca88abc`

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/bds-checkbox-button.scss` (create)

**Acceptance criteria:**

- File contains exactly two lines:
  ```scss
  @import "../_shared/selectable-button";
  @include selectable-button("bds-checkbox-button");
  ```
- No other rules, no `@use`, no token references — all visual styles are delegated to the shared mixin.
- After build, the component renders with the same pill-button appearance as `bds-radio-button`.

**Unit tests to cover:** _(none — SCSS only)_

**Manual test _(waiveable)_:**

Run: `pnpm dev:components`

- [ ] `bds-checkbox-button` default state: same visual as `bds-radio-button` default
- [ ] `--checked`: primary border + inverse background
- [ ] `--error`: danger text color; error + checked: danger border
- [ ] `--disabled`: disabled text color, `cursor: not-allowed`
- [ ] Focus ring appears on keyboard navigation (`Tab` to focus)
- [ ] Hover shadow visible on mouse-over (unchecked, not disabled, not error)
- [ ] Pass: no CSS errors in console

**Commit:**

```bash
git commit -m "feat(web-components): EOA-12342 add SCSS for bds-checkbox-button via shared mixin"
```

---

### Task 6: JSDoc audit ✅ `e83772da`

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/bds-checkbox-button.tsx` (modify)

**Acceptance criteria:**

- Class-level JSDoc block: describes that this is a button-shaped checkbox, the toggle behavior, the relationship to a future `bds-checkbox-group`, and documents `@slot` (default) and `@slot icon`.
- Every `@Prop()` has a JSDoc line.
- The `bdsChange` `@Event()` has a JSDoc line explaining when it fires and what its payload contains.
- No implementation detail comments in the method bodies (per project convention).
- Pattern mirrors the class-level JSDoc in `bds-radio-button.tsx`.

**Unit tests to cover:** _(none — docs audit only)_

**Manual test _(waiveable)_:**

- [ ] Run `pnpm build` — no TypeScript errors
- [ ] Storybook ArgTypes panel (after Task 8) shows descriptions for all props

**Commit:**

```bash
git commit -m "docs(web-components): EOA-12342 complete JSDoc for bds-checkbox-button props, events, and class"
```

---

### Task 7: Unit tests ✅ `adcf80db`

**Files:**

- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.basics.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.a11y.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.events.spec.ts` (create)
- `packages/boreal-web-components/src/components/forms/bds-checkbox-button/__test__/bds-checkbox-button.variants.spec.ts` (create)

**Acceptance criteria:**

All spec files must import `{ newSpecPage }` from `@stencil/core/testing` and `{ BdsCheckboxButton }` from `'../bds-checkbox-button'`. No `attachInternals()` helper is needed (component is not form-associated).

**`bds-checkbox-button.basics.spec.ts`** — `describe('bds-checkbox-button basics')`:

- Renders the host element with `role="checkbox"`
- Renders label text when `label` prop is set — query `.bds-checkbox-button__label`, assert `textContent`
- Renders default slot content when no `label` prop — pass slot children in HTML, assert label span contains them
- Renders the icon span `.bds-checkbox-button__icon`
- Renders hidden `<input type="checkbox">`
- Renders info icon and tooltip when `info` prop is set

**`bds-checkbox-button.a11y.spec.ts`** — `describe('bds-checkbox-button a11y')`:

- `aria-checked="false"` by default
- `aria-checked="true"` when `checked` attribute is set
- `role="checkbox"` is set in `componentDidLoad`
- `tabindex="0"` when not disabled
- `tabindex="-1"` when disabled
- `tabindex` updates to `"-1"` when `disabled` prop is changed after mount (via `@Watch`)
- `tabindex` updates back to `"0"` when `disabled` is removed after mount

**`bds-checkbox-button.events.spec.ts`** — `describe('bds-checkbox-button events')`:

- Emits `bdsChange` with `{ checked: true, value: 'a' }` on first click (unchecked → checked)
- Emits `bdsChange` with `{ checked: false, value: 'a' }` on second click (checked → unchecked)
- Does NOT emit `bdsChange` when disabled and clicked
- Emits `bdsChange` on Space key press
- Does NOT emit `bdsChange` on Enter key press
- `checked` prop is `true` after one click, `false` after two clicks
- `aria-checked` attribute reflects toggle state after each click

**`bds-checkbox-button.variants.spec.ts`** — `describe('bds-checkbox-button variants')`:

- `checked` prop → host has `bds-checkbox-button--checked` class
- `error` prop → host has `bds-checkbox-button--error` class
- `disabled` prop → host has `bds-checkbox-button--disabled` class
- No props → host only has `bds-checkbox-button` base class (none of the above modifiers)

**Manual test _(waiveable)_:**

Run: `pnpm test --filter boreal-web-components`

- [ ] All spec files pass with 0 failures
- [ ] No skipped tests

**Commit:**

```bash
git commit -m "test(web-components): EOA-12342 add unit tests for bds-checkbox-button"
```

---

### Task 8: Storybook story ✅ `9c3b2470`

> **Implementation notes:** Story title set to `'Forms/Checkbox Group/Checkbox Button'` to nest under the future group in the sidebar. The `Checked` story was named `WithValue` (aligned with how the radio-button stories name pre-selected state). The render function wraps 3 buttons in a plain `<div style="display: inline-flex; gap: 8px;">` per the standalone-first approach documented above.

**Files:**

- `apps/boreal-docs/src/stories/forms/bds-checkbox-button/bds-checkbox-button.stories.ts` (create)

**Acceptance criteria:**

- `title`: `'Forms/Checkbox Group/Checkbox Button'`
- `component`: `'bds-checkbox-button'`
- `parameters.docs.source`: `{ excludeDecorators: true, transform: formatHtmlSource }`
- `StoryArgs` type includes:
  - `name`, `value`, `label`, `info` — `control: 'text'`
  - `disabled`, `error` — `control: 'boolean'`
  - `showIcon`, `showInfo` — `control: 'boolean'`, described as "Storybook control only — not a component prop"
  - `onBdsChange` — `action: 'bdsChange emitted'`
- `argTypes` table categories:
  - Core: `name`, `value`
  - Appearance: `label`, `info`
  - State: `disabled`, `error`
  - Slots: `showIcon`, `showInfo`
  - Events: `onBdsChange`
- Default `args`: `name: 'checkbox-button-group'`, `value: 'on'`, `label: ''`, `info: ''`, `disabled: false`, `error: false`, `showIcon: false`, `showInfo: false`
- Single reusable `renderCheckboxButton` function returns a lit `html` template with a group of 3 `<bds-checkbox-button>` elements, one per option (A, B, C).
- Named story exports:
  - `Default` — 3 buttons, label set, no pre-checked
  - `Checked` — first button has `checked` attribute
  - `WithIcons` — `showIcon: true`
  - `WithItemTooltips` — `showInfo: true`
  - `Disabled` — `disabled: true`
  - `Error` — `error: true`
  - Each story includes a JSDoc comment describing what it demonstrates.
- Pattern mirrors `bds-radio-button.stories.ts` at `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-button/bds-radio-button.stories.ts`.

**Manual test _(waiveable)_:**

Run: `pnpm storybook` in `apps/boreal-docs`

- [ ] `Forms/Checkbox Group/Checkbox Button` appears in the Storybook sidebar
- [ ] All 6 stories render without console errors
- [ ] Controls panel shows all arg types with correct categories and types
- [ ] Clicking a button in the Default story toggles the checked state visually
- [ ] `bdsChange emitted` appears in the Actions panel on each click

**Commit:**

```bash
git commit -m "feat(docs): EOA-12342 add Storybook stories for bds-checkbox-button"
```

---

### Task 9: MDX documentation ✅ `9c3b2470`

**Files:**

- `apps/boreal-docs/src/stories/forms/bds-checkbox-button/bds-checkbox-button.mdx` (create)

**Acceptance criteria:**

- Imports: `Meta`, `Canvas`, `ArgTypes`, `Title`, `Subtitle` from `@storybook/addon-docs/blocks`; `LinkTo` from `@storybook/addon-links/react`; `Callout`, `DocsLinkTo` from `@/components/docs`; `* as BdsCheckboxButtonStories` from `./bds-checkbox-button.stories`
- `<Meta of={BdsCheckboxButtonStories} />`
- `<Title of={BdsCheckboxButtonStories} />`
- Intro paragraph: describes this as a button-shaped checkbox option, explains toggle semantics (independent multi-select, not mutually exclusive), and notes that `bds-checkbox-button` is a building block designed for use inside a group.
- `<Callout variant="info">` noting the component is a leaf building block intended to work inside a `bds-checkbox-group` (coming soon).
- **How to use it** section: setup snippet (`defineCustomElements`) + usage HTML snippet showing 3 `<bds-checkbox-button>` elements in a group wrapper.
- **When to use it** section (bullet list):
  - When users need to select multiple options independently
  - When a visually compact toggle-button style is preferred over stacked checkboxes
  - When options are short labels (1–3 words) that fit side by side
- **When not to use it** section (bullet list):
  - Only one option can be selected at a time (use `bds-radio-group`)
  - Single binary toggle (use `bds-checkbox`)
  - Long labels that won't fit in a pill button
- **Component preview** section with `<Callout variant="tip">` about Show code, followed by `<Canvas>` for Default, Checked, Disabled, Error stories.
- **States** section with Disabled and Error `<Canvas>` blocks.
- **Accessibility** section (bullet list):
  - `role="checkbox"` on each button; `aria-checked` reflects toggle state
  - `tabindex="0"` on each enabled button (individual focus stops, not roving tabindex)
  - `tabindex="-1"` on disabled buttons
  - Space key toggles the focused button; Enter has no effect
  - Screen readers announce label + checked state on focus and change
- **Properties** section: `<ArgTypes of={BdsCheckboxButtonStories} />`
- **Interact with the component** section: `<LinkTo>` pointing to the Default story canvas.
- Pattern mirrors `apps/boreal-docs/src/stories/forms/bds-radio-group/bds-radio-button/bds-radio-button.mdx`.

**Manual test _(waiveable)_:**

Run: `pnpm storybook` in `apps/boreal-docs`

- [ ] Click `Forms/Checkbox Group/Checkbox Button` in the sidebar → Docs tab loads without errors
- [ ] All sections render correctly (headings, callouts, canvas blocks)
- [ ] ArgTypes table shows all props with descriptions
- [ ] "Interact with the component" link navigates to the Default story canvas

**Commit:**

```bash
git commit -m "docs(docs): EOA-12342 add MDX documentation for bds-checkbox-button"
```

---

## Stories and docs: standalone-first approach (Phase 1)

Tasks 8 and 9 used a standalone-first approach because `bds-checkbox-group` was not yet available. Phase 2 (Tasks 10–16 below) integrates form association and updates docs to a group-first model.

---

## Phase 2: Form Association

`bds-checkbox-button` is upgraded to a Form-Associated Custom Element so it can participate in native HTML forms both standalone and inside `bds-checkbox-group`. The implementation pattern mirrors `bds-checkbox-card` exactly.

### Task 10: Loosen `useFormCheckbox` type to accept components without `indeterminate`

**File:** `packages/boreal-web-components/src/components/forms/bds-checkbox/utils/checkbox-form-association.ts`

Replace the `ICheckbox & IFormControl<boolean>` parameter type with an inline structural type where `indeterminate` is optional. Existing callers (`bds-checkbox`, `bds-checkbox-card`) already satisfy the looser type — no changes to those components needed.

**Acceptance criteria:**

- `useFormCheckbox` compiles when called from `bds-checkbox-button` (no `indeterminate` prop).
- Existing callers and their unit tests pass unchanged.

**Commit:**

```bash
git commit -m "refactor(web-components): EOA-12342 make indeterminate optional in useFormCheckbox type"
```

---

### Task 11: Add `required` to `ICheckboxButton`

**File:** `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox-button/types/ICheckboxButton.ts`

Add `required: boolean` to the `ICheckboxButton` interface to match the FACE public contract. Internal state fields (`el`, `internals`, `isInvalid`, `isDisabled`) are not added — they are checked structurally by the helper.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-12342 add required to ICheckboxButton interface"
```

---

### Task 12: Upgrade `bds-checkbox-button.tsx` to FACE

**File:** `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox-button/bds-checkbox-button.tsx`

Reference: `bds-checkbox-card.tsx` — follow it line for line.

**Changes:**

- `@Component`: add `formAssociated: true`
- Class: `extends Mixin(formAssociatedMixin) implements ICheckboxButton, IFormControl<boolean>`
- Add on the class body: `@AttachInternals() internals`, `@State() isDisabled`, `@State() isInvalid`
- Add `required` prop: `@Prop({ reflect: true }) readonly required: boolean = false`
- Add `valueChange: EventEmitter<boolean>` event
- Wire `private formCheckbox = useFormCheckbox(this, this.value)`
- `componentWillLoad`: `this.isDisabled = this.disabled`
- `componentDidLoad`: call `this.formCheckbox.syncFormValue()`
- Add `@Watch('checked') onCheckedChange()` → `this.formCheckbox.syncFormValue()`
- Update `@Watch('disabled')`: set `this.isDisabled = disabled` (replaces `setAttribute`)
- Implement all four form callbacks delegating to `this.formCheckbox`
- `@Listen('invalid') handleInvalid(event)`: call `event.preventDefault()` then `this.isInvalid = true` — follow `bds-checkbox`, not `bds-checkbox-card` (card omits `preventDefault`, a known oversight)
- Add `@Method() checkValidity()` and `@Method() reportValidity()`
- `toggle()`: guard with `isDisabled`; emit `valueChange` alongside `bdsChange`
- Add `isError` getter: `(this.error && !this.isDisabled) || this.isInvalid`
- Update `classMap`: use `isDisabled` and `isError`
- Move ARIA to `<Host>` JSX (`role`, `aria-checked`, `aria-disabled`, `aria-required`, `aria-invalid`, `tabIndex`) — remove `setAttribute` calls from lifecycle hooks

**Acceptance criteria:**

- `pnpm build` passes with no errors.
- Existing unit tests (Task 7) pass after updating guards from `this.disabled` to `this.isDisabled`.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-12342 upgrade bds-checkbox-button to form-associated custom element"
```

---

### Task 13: Register `bds-checkbox-button` in `vue-output-target.ts`

**File:** `packages/boreal-web-components/targets/vue-output-target.ts`

Add `'bds-checkbox-button'` to the `elements` array in `componentModels`. This wires `valueChange` to `v-model` in Vue.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-12342 register bds-checkbox-button in Vue componentModels"
```

---

### Manual QA checkpoint (after Tasks 10–13, before Task 14)

Run `pnpm dev:components` from the monorepo root and open `http://localhost:3333` (or the port shown in the terminal). The playground at `packages/boreal-web-components/src/index.html` contains three QA sections:

**1. Visual States** — verify BEM modifier rendering:

- [x] Default: pill buttons render with default styling
- [x] Checked: `--checked` modifier applies primary border + inverse background
- [x] Error: `--error` modifier applies danger text/border
- [x] Disabled: `--disabled` modifier applies muted styling; clicking has no effect
- [x] With icon: icon slot renders; empty icon slot is hidden

**2. Standalone Form** — verify FACE participation:

- [x] Submit unchecked with `required` → browser/native validation blocks submission (no output)
- [x] Check the button and submit → output shows `{ "terms": "accepted" }`
- [x] Click Reset → button unchecks, output clears
- [x] Fieldset-disabled variant → button renders as disabled (via `formDisabledCallback`)

**3. Group Form** — verify group orchestration:

- [x] Submit with no selection + `required` → group shows error message "Please select at least one feature"
- [x] Select options and submit → output shows `{ "features": ["dark-mode", "notifications"] }` (only selected values)
- [x] Click Reset → all buttons uncheck, error clears
- [x] Horizontal orientation → buttons render in a row
- [x] Disabled group → all buttons non-interactive
- [x] Error group → all buttons show error styling

---

### Task 14: Extract shared group layout SCSS into `_selectable-group.scss`

**Files:**

- `packages/boreal-web-components/src/components/forms/_shared/_selectable-group.scss` (create)
- `packages/boreal-web-components/src/components/forms/bds-radio-group/bds-radio-group.scss` (replace)
- `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox-group/bds-checkbox-group.scss` (replace)

`bds-radio-group.scss` and `bds-checkbox-group.scss` are structurally identical — only the prefix names differ. A shared mixin eliminates the duplication, paralleling the `_selectable-button.scss` approach for leaf components.

**Key constraint:** The partial must NOT include `@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *`. Both group SCSS files receive `$boreal-*` tokens via Stencil's `injectGlobalPaths`. Loading the partial with `@import` (not `@use`) shares that injected scope with the partial, making an explicit token import unnecessary.

The `@prop --layout-count` JSDoc comment lives **inside the mixin**, above the `var(--layout-count, 1)` usage. Stencil scrapes `@prop` from compiled SCSS output, so it appears in both components' generated metadata from a single definition.

**Mixin signature:**

```scss
@mixin selectable-group($prefix, $button-type, $child-selector) { ... }
```

**Callers:**

```scss
// bds-radio-group.scss
@import '../_shared/selectable-group';
@include selectable-group('bds-radio-group', 'radiobutton', 'bds-radio-button');

// bds-checkbox-group.scss
@import '../../_shared/selectable-group';
@include selectable-group('bds-checkbox-group', 'checkboxbutton', 'bds-checkbox-button');
```

Also remove the dead `:host { display: block; }` from `bds-checkbox-group.scss` — it is a Light DOM component, so the `:host` selector has no effect. `bds-radio-group.scss` never had this rule.

**Acceptance criteria:**

- `_selectable-group.scss` contains only the mixin, no top-level `@use` or `@import`
- `bds-radio-group.scss` and `bds-checkbox-group.scss` are each two lines
- `pnpm build --filter boreal-web-components` passes with no Sass errors
- Visual output of both group components is pixel-identical to before the refactor

**Manual test _(waiveable)_:**

Run: `pnpm dev:components`

- [ ] Visual States section renders correctly (default, checked, error, disabled, icon slot)
- [ ] Standalone Form section validates and submits correctly
- [ ] Group Form section (vertical required, horizontal, disabled, error) all render correctly
- [ ] No Sass/CSS errors in browser console

**Commit:**

```bash
git commit -m "refactor(web-components): EOA-12342 extract shared selectable-group SCSS mixin"
```

---

### Task 15: Unit tests — form association

**File:** `packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox-button/__test__/bds-checkbox-button.form.spec.ts` (new)

Add form-association test cases:

- `formAssociatedCallback` → calls `syncFormValue`
- `formResetCallback` → resets `checked` to `false`, clears `isInvalid`
- `formDisabledCallback(true/false)` → sets `isDisabled` correctly
- `@Watch('checked')` change → triggers `syncFormValue`
- `toggle()` → emits `valueChange` with `boolean` payload alongside `bdsChange`
- `toggle()` when `isDisabled` → no events emitted
- `checkValidity` / `reportValidity` → delegate to `internals`

Pattern reference: `bds-checkbox.spec.ts`.

**Commit:**

```bash
git commit -m "test(web-components): EOA-12342 add form association unit tests for bds-checkbox-button"
```

---

### Task 15: Storybook stories — relocate + group/form stories

**Files:**

- Move `apps/boreal-docs/src/stories/forms/bds-checkbox-button/bds-checkbox-button.stories.ts` → `apps/boreal-docs/src/stories/forms/bds-checkbox-group/bds-checkbox-button/bds-checkbox-button.stories.ts`
- Delete the now-empty `apps/boreal-docs/src/stories/forms/bds-checkbox-button/` directory

**Changes to the stories file after move:**

- Import `FormDemo` (`@/components/story/FormDemo`) and `hljs`
- Extend `StoryArgs`: add `helperText`, `errorMessage`, `orientation`, `required`, `onValueChange`
- Add `WithinGroup` story (primary usage): wraps 3 buttons in `<bds-checkbox-group>`; group-level controls: `name`, `label`, `info`, `orientation`, `required`, `disabled`, `error`, `helperText`, `errorMessage`
- Add `InteractiveFormExampleGroup` story (recommended): `<form-demo>` + `<bds-checkbox-group required>` with 3 buttons; demonstrates submit, required validation, and reset
- Add `InteractiveFormExample` story (standalone, advanced): `<form-demo>` + single `<bds-checkbox-button name=... required>`

Reference: `bds-checkbox.stories.ts` for `WithinGroup`, `InteractiveFormExampleGroup`, and `InteractiveFormExample` patterns.

**Commit:**

```bash
git commit -m "feat(docs): EOA-12342 relocate and extend bds-checkbox-button stories with group and form examples"
```

---

### Task 16: MDX documentation — group-first update

**File:** `apps/boreal-docs/src/stories/forms/bds-checkbox-group/bds-checkbox-button/bds-checkbox-button.mdx` (moved from `forms/bds-checkbox-button/`)

**Changes:**

- Remove the outdated `<Callout>` saying "bds-checkbox-group is in development"
- Add `WithinGroup` canvas in Component Preview as the primary usage example
- Add **Form Integration** section (after States, before Accessibility):
  - **Recommended: Within a Group** — `<bds-checkbox-group>` snippet + `InteractiveFormExampleGroup` canvas with note to visit Canvas tab for interactive version
  - **Standalone (advanced)** — `<Callout variant="warning">` discouraging standalone form use; minimal standalone snippet; `InteractiveFormExample` canvas
- Update Table of Contents to include Form Integration
- Update Properties section to include `required`

Reference: `bds-checkbox.mdx` for the Form Integration section structure.

**Commit:**

```bash
git commit -m "docs(docs): EOA-12342 update bds-checkbox-button MDX with group-first documentation"
```

---

## Verification (end-to-end)

### Phase 1

1. **Build**: `pnpm build --filter boreal-web-components` — no Sass or TypeScript errors.
2. **Type check**: `pnpm tsc --noEmit` in `packages/boreal-web-components` — zero errors.
3. **Unit tests**: `pnpm test --filter boreal-web-components` — all spec files pass.
4. **Storybook**: `pnpm storybook` in `apps/boreal-docs` — `Forms/Checkbox Group/Checkbox Button` sidebar entry present; all 6 stories render; Actions panel captures `bdsChange` events.
5. **Radio-button regression**: After Task 1 refactor, `Forms/Radio Group/Radio Button` stories are visually identical to before.
6. **Accessibility**: DevTools Accessibility panel on a `bds-checkbox-button` — verify `role=checkbox`, `aria-checked`, `tabindex=0`.

### Phase 2

1. **Unit tests**: `pnpm test --filter boreal-web-components --testPathPattern=bds-checkbox-button` — all spec files pass including new form spec.
2. **Storybook**: Navigate to `Forms / Checkbox Group / Checkbox Button` — `WithinGroup` story shows group controls working (disabled, error, required propagate); `InteractiveFormExampleGroup` canvas shows submit/validation/reset; `InteractiveFormExample` canvas shows standalone form participation.
3. **Vue v-model**: After `pnpm build` in `packages/boreal-web-components`, confirm `bds-checkbox-button` appears in `boreal-vue/lib/components.ts` with `modelValue` / `onValueChange` binding.
