# JSDoc Template for Boreal Web Components

This template reflects the Boreal Stencil setup and the Custom Elements Manifest (CEM) analyzer behavior.

Reference: [Stencil — Generating Documentation in CEM format](https://stenciljs.com/docs/docs-custom-elements-manifest)

---

## How the CEM is Generated

Stencil uses the `docs-custom-elements-manifest` output target (configured in `stencil.config.ts`). This runs the CEM analyzer with the Stencil plugin, which reads decorators directly from the TypeScript AST.

| Source                         | What the plugin generates automatically                                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `@Prop()` decorator            | `attributes[]` entry (kebab-case name) + `members[]` entry (camelCase name), with type, default, `readonly`, and cross-reference |
| Inline `/** */` on `@Prop()`   | `description` field in both entries                                                                                              |
| `@Event()` decorator           | `events[]` entry                                                                                                                 |
| Inline `/** */` on `@Event()`  | `description` field in the event entry                                                                                           |
| `@Method()` decorator          | `members[]` method entry                                                                                                         |
| Inline `/** */` on `@Method()` | `description` field                                                                                                              |
| `@slot` in class JSDoc         | `slots[]` entry                                                                                                                  |
| `@prop` comment in SCSS        | `cssProperties[]` entry                                                                                                          |

---

## Core Rules

- **Every `@Prop()` must have inline JSDoc** (`/** */`) directly above the decorator — this is enforced by `stencil/required-jsdoc: 'error'`.
- **Do not use `@attr`, `@property`, `@fires`, `@summary`, `@method`, or `@element`** in the class-level JSDoc block. The Stencil plugin generates all of these from decorators. These tags are redundant and produce no additional output.
- **Do not use `@cssprop` in the TSX class JSDoc.** CSS custom properties must be documented with `@prop` comments in the SCSS file instead — that is where Stencil reads them from.
- **Do not use `@internal` on a component class JSDoc.** It silently removes the entire component from `custom-elements.json` and from generated React/Vue wrappers.
- **Use `@file` (not `@fileoverview`)** for module-level documentation.
- **Do not use `@part` (CSS Shadow Parts).** This project uses light DOM — there is no shadow boundary and no `part` attribute.

---

## What Belongs in the Class JSDoc Block

The class-level JSDoc block has exactly two responsibilities:

1. **Component description** — the first paragraph becomes the `description` field in the manifest. Keep it concise.
2. **`@slot` tags** — the only tag the Stencil plugin cannot infer from the render function. Document every slot.

```ts
/**
 * Banner component for displaying important messages with status variants.
 *
 * @slot - Default slot for the banner body content.
 * @slot title - Slot for the banner title text.
 * @slot actions - Slot for action buttons or links.
 */
```

Nothing else. No `@attr`, `@property`, `@cssprop`, `@fires`, `@summary`, `@method`.

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
- **Type annotation is only required when there is no default value.** TypeScript infers the type from the initializer (`disabled = false` → `boolean`). Explicit annotations are needed only for required props (`name!: string`) and optional props with no default (`formId?: string`). See `.ai/guidelines/stencil-best-practices.md` → `@Prop() Type Declaration and Default Value Rules` for the full decision table.

---

## Event JSDoc (Place on the `@Event()` field)

```ts
/** Emitted when the user closes the banner. */
@Event()
bdsClose!: EventEmitter<void>;
```

Rules:

- Use the `bds{Action}` prefixed camelCase naming convention.
- Use bare `@Event()` for consumer-facing events — no explicit options required (see ADR `.ai/decisions/0003-event-options-convention.md`).
- **Exception:** events caught by a parent component via `@Listen()` must use `@Event({ bubbles: true })`. `@Listen()` relies on bubbling — without it the event never reaches the parent's listener.
- Do not reuse native DOM event names (`click`, `change`, `input`, etc.).

### Event emission rules

Events must only be emitted in response to **user interactions**, not programmatic changes. This prevents infinite loops and keeps data flow predictable.

| Scenario                          | Emit? | Reason                                    |
| --------------------------------- | ----- | ----------------------------------------- |
| User clicks / types / selects     | ✅    | Direct user interaction                   |
| Property changed programmatically | ❌    | Not user-initiated; emitting causes loops |
| Public `@Method()` called         | ❌    | API call, not a user action               |
| Internal state update             | ❌    | Implementation detail                     |
| Initialization / lifecycle hooks  | ❌    | Framework lifecycle, not a user action    |

### Cancelable events

Cancelable events use the `-ing` suffix (before the action) paired with a plain name (after the action).

```ts
/** Emitted before the dialog opens. Call `event.preventDefault()` to cancel. */
@Event({ cancelable: true })
bdsOpening!: EventEmitter<void>;

/** Emitted after the dialog has opened. */
@Event()
bdsOpen!: EventEmitter<void>;
```

Inside the handler, check `defaultPrevented` before proceeding:

```ts
async open() {
  const event = this.bdsOpening.emit();
  if (event.defaultPrevented) return;
  this.isOpen = true;
  this.bdsOpen.emit();
}
```

| Event pair   | Cancelable | Suffix | When emitted                   |
| ------------ | ---------- | ------ | ------------------------------ |
| `bdsOpening` | ✅         | `ing`  | Before action (can be stopped) |
| `bdsOpen`    | ❌         | —      | After action (already done)    |
| `bdsClosing` | ✅         | `ing`  | Before action (can be stopped) |
| `bdsClose`   | ❌         | —      | After action (already done)    |

### Event detail typing

| Pattern             | When to use                 | Example                                                                            |
| ------------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| Simple primitive    | Single scalar value         | `EventEmitter<string>`                                                             |
| Inline object       | Two or three related fields | `EventEmitter<{ id: string; label: string }>`                                      |
| Named interface     | Reusable or complex payload | `EventEmitter<SelectDetail>`                                                       |
| Element reference   | Exposing the source element | `EventEmitter<HTMLElement>`                                                        |
| Discriminated union | Multiple event variants     | `EventEmitter<{ type: 'success'; data: T } \| { type: 'error'; message: string }>` |

Only include relevant data in the detail — do not serialize the entire component state.

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

## CSS Custom Properties — Document in SCSS, Not in TSX

Stencil reads CSS custom property documentation from `@prop` JSDoc comments **in the SCSS file**, not from `@cssprop` tags in the component class JSDoc. The comment must appear above the variable **declaration** inside the component's tag selector block.

```scss
/* ✅ Correct — Stencil reads this and generates cssProperties[] in the manifest */
bds-dialog {
  /**
   * @prop --bds-dialog-width: Custom width when no preset size is active.
   * @prop --bds-dialog-height: Custom height when no preset size is active.
   */
  --bds-dialog-width: auto;
  --bds-dialog-height: auto;
}
```

```ts
/* ❌ Wrong — @cssprop in the TSX class JSDoc produces nothing in the manifest */
/**
 * @cssprop --bds-dialog-width - Custom width for the dialog.
 */
@Component({ tag: 'bds-dialog' })
export class BdsDialog { ... }
```

Additional rules:

- Declare the variable with its default value in the same block as the `@prop` comment. Do not scatter defaults as fallback values in `var(--name, default)` calls elsewhere.
- Internal implementation variables (e.g. `--_col-base`, `--_row-span`) must use the `--_` underscore prefix convention and must **not** have `@prop` documentation — they are not public API.

---

## Example (Boreal-Styled)

```ts
/**
 * Checkbox component for boolean selection with three visual states.
 *
 * @slot - Label content when no `label` prop is provided.
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
  bdsChange!: EventEmitter<{ checked: boolean; value: string }>;
}
```

---

## Common Pitfalls to Avoid

- Using `@element`, `@method`, or class-level `@internal`.
- Omitting JSDoc on `@Prop()` or placing it below the decorator.
- Using `@fileoverview` instead of `@file`.
- Adding explicit `bubbles/composed/cancelable` to `@Event()` — bare `@Event()` is the convention.
- Naming events with native DOM names (`click`, `input`, `change`).
- Writing `@cssprop` in the TSX class JSDoc — use `@prop` in the SCSS file instead.
- Writing `@attr` or `@property` in the class JSDoc — the Stencil plugin generates both from `@Prop()` decorators.
- Documenting internal `--_*` CSS variables with `@prop` — they are not public API.
- Using fallback values in `var(--custom-prop, default)` instead of declaring the variable with its default in the tag selector block.
