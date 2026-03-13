# JSDoc Template for Boreal Web Components

This template reflects the Boreal Stencil setup and the Custom Elements Manifest (CEM) analyzer behavior enforced by `eslint.config.ts`.

---

## Core Rules

- **Every `@Prop()` must have JSDoc** directly above the decorator.
- **Do not use `@element` or `@method`** on class JSDoc. They are ignored by the CEM analyzer.
- **Do not use `@internal` on a component class JSDoc.** It removes the component from `custom-elements.json`.
- **Use `@file` (not `@fileoverview`)** for module-level documentation.
- **Document events on the `@Event()` field** with a JSDoc block, not on the class.

---

## Component Class JSDoc (Recommended)

Use a short description and any high-level usage notes. Keep it minimal.

```ts
/**
 * Banner component used to display important messages with status variants.
 *
 * @summary Displays a dismissible banner with a title, body, and optional actions.
 *
 * @slot title - Slot for the banner title text.
 * @slot - Default slot for the banner body content.
 * @slot actions - Slot for action buttons or links.
 */
```

---

## Module-Level JSDoc (`@file`)

```ts
/**
 * @file Entry point for the component package.
 *
 * Use this file to export utilities and types only.
 */
```

---

## Prop JSDoc (Required for Every `@Prop()`)

```ts
/** Visual style variant. */
@Prop({ reflect: true }) readonly variant: BannerVariant = 'info';

/** Shows a close button that allows users to dismiss the banner. */
@Prop() readonly enableClose: boolean = false;

/** Internal mutable prop for component-controlled state. */
@Prop({ mutable: true }) idComponent: string = '';
```

Notes:

- `readonly` is mandatory for `@Prop()` declarations.
- If `mutable: true` is used, mutate internally with a narrow cast instead of `as any`.

---

## Event JSDoc (Place on the `@Event()` field)

```ts
/** Emitted when the user closes the banner. */
@Event()
bdsBannerClose!: EventEmitter<void>;
```

Rules:

- Use the `bds{Component}{Action}` prefixed camelCase naming convention.
- Use bare `@Event()` — no explicit options required (see ADR `.ai/decisions/0003-event-options-convention.md`).
- Do not reuse native DOM event names (`click`, `change`, `input`, etc.).

---

## Method JSDoc (Place on the method)

```ts
/**
 * Programmatically close the banner and emit `bdsBannerClose`.
 */
@Method()
async closeBanner(): Promise<void> {
  this.handleClose();
}
```

Do not add `@method` tags at the class level.

---

## Optional CEM Tags (Use Only When Applicable)

Use these tags in the **class JSDoc** when they are truly supported and needed.

```ts
@slot title - Slot for the title content.
@csspart container - Main banner container.
@cssprop --bds-banner-background - Background color token.
@attr {string} variant - Reflected attribute for the visual variant.
@property {string} variant - Property for the visual variant.
```

Notes:

- Prefer one of `@attr` or `@attribute` (not both). Same for `@prop` / `@property`.
- If an attribute is not reflected, document only the property.

---

## Example (Boreal-Styled)

```ts
/**
 * Checkbox component for boolean selection with an optional label.
 *
 * @summary A form control with checked and indeterminate states.
 *
 * @slot - Label content when no `label` prop is provided.
 *
 * @attr {boolean} checked - Reflected checked state.
 * @attr {boolean} indeterminate - Reflected indeterminate state.
 * @attr {string} value - Value submitted with form data when checked.
 *
 * @property {string} label - Label displayed next to the checkbox.
 */
@Component({
  tag: "bds-checkbox",
  styleUrl: "bds-checkbox.scss",
  formAssociated: true,
})
export class BdsCheckbox {
  /** Whether the checkbox is selected. */
  @Prop({ mutable: true, reflect: true }) checked: boolean = false;

  /** Whether the checkbox is indeterminate. */
  @Prop({ mutable: true, reflect: true }) indeterminate: boolean = false;

  /** Value submitted with the form when checked. */
  @Prop() readonly value: string = "on";

  /** Label displayed next to the checkbox. */
  @Prop() readonly label: string = "";

  /** Emitted when the checked state changes (for 2-way binding / v-model). */
  @Event()
  bdsCheckboxChange!: EventEmitter<{ checked: boolean; value: string }>;
}
```

---

## Common Pitfalls to Avoid

- Using `@element`, `@method`, or class-level `@internal`.
- Omitting JSDoc on `@Prop()` or placing it below the decorator.
- Using `@fileoverview` instead of `@file`.
- Adding explicit `bubbles/composed/cancelable` to `@Event()` — bare `@Event()` is the convention.
- Naming events with native DOM names (`click`, `input`, `change`).
