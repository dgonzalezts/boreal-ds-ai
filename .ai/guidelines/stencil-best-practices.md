# Stencil Best Practices

## Style Encapsulation: `scoped` vs `shadow` vs none

Stencil provides three style encapsulation modes. Choose the right one based on the component's requirements.

### How `scoped: true` works

`scoped: true` implements **synthetic CSS scoping** at compile time — no native Shadow DOM is used:

1. Stencil generates a unique hash for the component (e.g. `sc-bds-text-field`).
2. It appends a scoped class to every DOM node the component renders.
3. It rewrites every CSS selector to include that class, making styles target only nodes belonging to that component.

The compiled output at runtime looks like:

```html
<bds-text-field class="sc-bds-text-field-h">
  <input class="bds-text-field__control sc-bds-text-field" />
</bds-text-field>
```

```css
/* compiled CSS */
.bds-text-field__control.sc-bds-text-field { ... }
```

---

### The three encapsulation modes compared

|                                     | `shadow: true`                              | `scoped: true`                                 | neither                    |
| ----------------------------------- | ------------------------------------------- | ---------------------------------------------- | -------------------------- |
| **Mechanism**                       | Native browser Shadow DOM                   | Compile-time attribute scoping                 | None                       |
| **DOM type**                        | Shadow root (isolated)                      | Light DOM                                      | Light DOM                  |
| **Style leakage in**                | Blocked (CSS custom props still cross)      | Not fully blocked — specificity wins           | Unrestricted               |
| **Style leakage out**               | Blocked                                     | Blocked (scoped selectors don't match outside) | Unrestricted               |
| **`querySelector` from parent**     | Requires `el.shadowRoot.querySelector(...)` | `el.querySelector(...)` ✅                     | `el.querySelector(...)` ✅ |
| **`:host` selector**                | Works natively                              | Compiled to tag attribute selector             | N/A                        |
| **`::slotted()`**                   | Supported                                   | Not supported                                  | N/A                        |
| **`::part()`**                      | Supported                                   | Not supported                                  | N/A                        |
| **CSS custom props cross boundary** | Yes                                         | Yes                                            | Yes                        |

---

### When to use `scoped: true`

Use `scoped: true` when:

- The component is a **Form-Associated Custom Element (FACE)** — declares `formAssociated: true` and uses `@AttachInternals()`. Scoped keeps the inner `<input>` accessible via `el.querySelector(...)`, which is required for focus delegation patterns like:
  ```tsx
  onFocus={() => (this.el as HTMLElement).querySelector<HTMLInputElement>('input')?.focus()}
  ```
- You need to avoid Shadow DOM compatibility edge cases with browser form validation UI (native validation bubbles, autofill, password managers).
- The component must remain accessible to the document's accessibility tree without an encapsulation boundary.
- BEM class naming provides sufficient practical style isolation for your use case.

### When to use `shadow: true`

Use `shadow: true` when:

- The component does **not** participate in native form submission (no FACE).
- Full style isolation is required — external stylesheets must not be able to reach internal elements.
- You need `::part()` or `::slotted()` for consumer customisation.
- The component renders complex subtrees where specificity conflicts with host page styles are likely.

### When to use neither

Avoid using no encapsulation mode in production components. Reserve it for lightweight utility wrappers or cases where the component intentionally inherits all host page styles.

---

### The key trade-off with `scoped: true`

Scoped CSS only prevents your styles from leaking **out**. External styles with sufficient specificity **can still override** component internals:

```css
/* This WILL affect a scoped component's input */
/* It would NOT with shadow: true */
input {
  background: red;
}
```

**Mitigation**: Always use specific BEM class selectors (e.g. `.bds-text-field__control`) in component SCSS. The extra specificity provides practical protection even without full Shadow DOM isolation.

---

### SSR behaviour

When Stencil serialises a scoped component server-side, it renders a light-DOM tree with a single `<style>` tag injected into `<head>`. Every selector carries the scoped attribute suffix. On hydration, no Shadow DOM attachment is needed — the client diffs against the existing light DOM directly.

---

### CSS custom properties always cross boundaries

Regardless of encapsulation mode, CSS custom properties (`var(--boreal-*)`) cross any Shadow DOM or scoped boundary. The Boreal theming system (set via `data-theme` on `<html>`) works identically with `scoped: true` and `shadow: true`.

---

## FACE Components: `formAssociated: true` with `scoped: true`

For all form-associated components in this codebase, the canonical pattern is:

```tsx
@Component({
  tag: 'bds-[name]',
  styleUrl: 'bds-[name].scss',
  formAssociated: true,
  scoped: true,           // NOT shadow: true — see rationale above
})
export class Bds[Name] extends Mixin(formAssociatedMixin) implements IFormControl<string> {
  @AttachInternals() internals!: ElementInternals;
  // ...
}
```

Key rules:

- `@AttachInternals()` must be declared directly on the component class body — never inside a mixin factory (see `.claude/memory/stencil-face-attach-internals.md`).
- Native FACE prototype members are blocked by Stencil's element proxy; expose them via `@Method()` wrappers (see `.claude/memory/stencil-face-element-proxy-limits.md`).
- Use `el.querySelector(...)` (not `el.shadowRoot.querySelector(...)`) for all inner element access.
