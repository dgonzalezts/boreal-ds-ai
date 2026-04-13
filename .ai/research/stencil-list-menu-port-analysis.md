# Research: Porting col-list-menu Architecture to Stencil

**Date:** 2026-04-09  
**Scope:** `col-list-menu` + `col-list-menu-item` (Colibri Lit implementation)  
**Question:** Can the same compound component pattern be implemented in a Stencil-based library?

---

## Current Lit Implementation Overview

### Component structure

- `ColListMenu` extends `ThemedComponent` → `LitElement`
- `ColListMenuItem` extends `FormComponent` → `ThemedComponent` → `LitElement`

### Inheritance chain roles

| Base class | What it adds |
|---|---|
| `LitElement` | Lit reactive rendering engine |
| `ThemedComponent` | Per-component design token overrides via CSS custom properties |
| `FormComponent` | `ElementInternals` form association (`formAssociated: true`) |

### What `@lit/context` carries

`listMenuContext` passes `{ role, multiSelectable, menuItems }` from parent to children. Each field serves a distinct purpose:

| Field | Used for |
|---|---|
| `role` | Child picks render branch: `renderOptionRole()` vs `renderMenuItemButton/Link()` |
| `multiSelectable` | `ListMenuController.getAriaSelected()` returns `null` unless role is `option` |
| `menuItems` | `handleKeyDown` traverses siblings for ArrowUp/Down keyboard navigation |

### Reactive Controllers

- `ListMenuController` — pure logic: tabIndex, ariaSelected, role mapping, keyboard nav
- `LinkHandlerController` — pure logic: URL sanitization, target/rel attributes, external link detection

Both are stateless logic extractors that implement Lit's `ReactiveController` interface.

---

## Question 1: Is the context approach the right one?

**Yes, for Lit specifically.** `@lit/context` is the idiomatic solution for parent-child compound components in the Lit ecosystem. It provides:

- **Reactivity** — children re-render automatically when context changes
- **Loose coupling** — children don't need to know the parent's tag name
- **Declarative** — no imperative DOM manipulation

Colibri uses this pattern consistently across two systems: the List Menu system and the Site Menu system (which shares state across 7 components). The Radio Group component, by contrast, uses a different pattern (sibling-to-sibling via window events) because it has no parent container.

---

## Question 2: Can context be used in Stencil?

**No good path exists.** The options:

| Option | Status |
|---|---|
| `@lit/context` directly | Lit-specific reactivity system; anti-pattern in Stencil |
| `@stencil/state-tunnel` | Archived December 2022 |
| `@stencil/store` | Designed for global/app state, not compound component pairing |

**Recommended replacement: child queries parent.**

Since we're using component composition (parent wraps children via `<slot>`), the DOM tree *is* the context. Children can access parent configuration directly:

```typescript
// In col-list-menu-item
private get parentMenu(): HTMLColListMenuElement | null {
  return this.el.closest('col-list-menu');
}

private get menuRole(): 'option' | 'menuitem' {
  return this.parentMenu?.role === 'menu' ? 'menuitem' : 'option';
}

private get siblings(): HTMLColListMenuItemElement[] {
  return Array.from(
    this.parentMenu?.querySelectorAll('col-list-menu-item') ?? []
  ).filter(item => !item.disabled);
}
```

This pattern is widely used in production web component libraries (Shoelace, FAST, Apple's custom elements).

---

## Question 3: Is component composition (parent + child) the right approach?

**Yes, unconditionally.** The composition model is not optional here — it is required by ARIA semantics:

- `role="listbox"` must be a DOM ancestor of `role="option"`
- `role="menu"` must be a DOM ancestor of `role="menuitem"`

The slot-based composition model (`<col-list-menu>` containing slotted `<col-list-menu-item>` elements) translates directly and identically to Stencil.

---

## Question 4: Does "child queries parent" scale to large item counts?

### `closest('col-list-menu')`

Traverses up the DOM tree to find the parent ancestor. Cost is O(DOM depth), typically 5–15 levels regardless of item count. **Effectively O(1)** — not a concern at any item count.

### `querySelectorAll('col-list-menu-item')`

Called during `handleKeyDown` on every keydown event. Cost is **O(n items)** per keystroke.

| | Child queries parent | Context (Lit/cached) |
|---|---|---|
| `querySelectorAll` timing | Per keydown event | Per parent render cycle |
| Array reuse | No — fresh each time | Yes — cached in context |
| At 10 items | Imperceptible | Imperceptible |
| At 1000 items | Measurable under rapid key-repeat | Faster |

### Practical ceiling

A menu with 1000 items is a UX failure before it is a performance failure. For realistic menu sizes (5–100 items), both approaches are indistinguishable. If large item counts are required (command palette, virtual scroll), the architecture would shift entirely — 1000 real DOM nodes would never be rendered simultaneously.

### Mitigation if needed

Cache the items list on the parent and invalidate on `slotchange`:

```typescript
// col-list-menu
private _cachedItems: HTMLColListMenuItemElement[] = [];

componentDidLoad() {
  this.el.shadowRoot?.querySelector('slot')
    ?.addEventListener('slotchange', () => {
      this._cachedItems = Array.from(
        this.el.querySelectorAll('col-list-menu-item')
      );
    });
}

get menuItems() {
  return this._cachedItems;
}
```

Children call `this.parentMenu.menuItems` — O(1) array read, equivalent to the context approach.

---

## Recommended Stencil Implementation Sketch

### `col-list-menu`

```typescript
@Component({ tag: 'col-list-menu', shadow: true })
export class ColListMenu {
  @Element() el: HTMLElement;

  @Prop({ reflect: true }) role: 'listbox' | 'menu' = 'listbox';
  @Prop() multiSelectable: boolean = false;
  @Prop() ariaLabel: string = 'List Menu';

  render() {
    return (
      <div
        role={this.role}
        aria-label={this.ariaLabel}
        aria-multiselectable={this.multiSelectable && this.role === 'listbox'}
      >
        <slot name="banner" />
        <slot name="header" />
        <slot />
        <slot name="footer" />
      </div>
    );
  }
}
```

### `col-list-menu-item`

```typescript
@Component({ tag: 'col-list-menu-item', shadow: true })
export class ColListMenuItem {
  @Element() el: HTMLElement;

  @Prop({ reflect: true }) selected: boolean = false;
  @Prop({ reflect: true }) disabled: boolean = false;
  @Prop() value: string = '';
  @Prop() href: string = '';
  @Prop() variant: 'button' | 'label' = 'button';

  @Event() listMenuItemClick: EventEmitter<{
    value: string;
    selected: boolean;
    href?: string;
  }>;

  private get parentMenu(): HTMLColListMenuElement | null {
    return this.el.closest('col-list-menu');
  }

  private get menuRole(): 'option' | 'menuitem' {
    return this.parentMenu?.role === 'menu' ? 'menuitem' : 'option';
  }

  private get siblings(): HTMLColListMenuItemElement[] {
    return Array.from(
      this.parentMenu?.querySelectorAll('col-list-menu-item') ?? []
    ).filter(item => !item.disabled);
  }

  // render() — same three branches as Lit version, translated to JSX
}
```

### Reactive Controllers → utility functions

Lit's `ReactiveController` interface is Lit-specific. In Stencil, extract the same logic as plain functions with no lifecycle binding:

```typescript
// list-menu.utils.ts
export function getAriaSelected(role: string, selected: boolean): string | null {
  return role === 'option' ? String(selected) : null;
}

export function getTabIndex(disabled: boolean): number {
  return disabled ? -1 : 0;
}

export function handleKeyNavigation(
  e: KeyboardEvent,
  items: Element[],
  currentIndex: number,
  onClick: () => void
): void {
  // Arrow key logic
}
```

### Base class equivalents

| Lit | Stencil |
|---|---|
| `ThemedComponent` (design tokens) | Shared `applyTokens(el, tokens)` utility called in `componentDidLoad` + `componentDidUpdate` |
| `FormComponent` (`ElementInternals`) | Stencil supports `formAssociated: true` + `attachInternals()` natively since v4 |

---

## Key Differences to Be Aware Of

| Topic | Lit | Stencil |
|---|---|---|
| `@queryAssignedElements` | Built-in decorator | Use `querySelectorAll` manually |
| Mutation reactivity | Lit tracks deep property changes | Requires reference changes (`[...arr]`) |
| Templates | `html` tagged template literals | JSX/TSX |
| Controller pattern | Reactive Controllers (standard interface) | Plain utility functions or Extends/Mixins |
| Context | `@lit/context` (first-class) | Child queries parent (idiomatic) |
| Slot change detection | `@queryAssignedElements` reactive | `slotchange` event listener |
| Form association | Via `FormComponent` base + `attachInternals()` | Native via `formAssociated: true` in `@Component` |

---

## Single Component vs Compound Components

An alternative architecture collapses both `col-list-menu` and `col-list-menu-item` into one component, with items passed as a data array prop instead of slotted DOM children.

### Pros

| Benefit | Detail |
|---|---|
| No communication overhead | All state (role, items, focus index) is local — no context, no DOM querying |
| Simpler implementation | One file, one lifecycle, one test suite |
| Atomic state transitions | "Deselect all, select this" is a single synchronous operation |
| Best keyboard nav performance | Items array is always in memory — O(1) index lookup, no `querySelectorAll` ever |
| Easier serialization | Items are plain JS objects; diffable, storable, transmittable |

### Cons

| Limitation | Detail |
|---|---|
| **No content projection** | Items can only contain what the schema supports. Arbitrary HTML (icons, badges, checkboxes, nested buttons) is impossible without accepting `innerHTML` strings — an XSS risk. This is the dealbreaker for a design system. |
| Requires JavaScript to use | Data props cannot be set from plain HTML or server-rendered templates. Compound components work declaratively with zero JS. |
| Schema bloat | Every new item feature (link variant, router flag, slot elements) requires a schema change and a component update. |
| No per-item form association | `ElementInternals` can only be attached once per component. Individual items cannot be separate form-associated elements. |
| No per-item styling | Consumers cannot target individual items via `::slotted()` or `::part()`. All items are opaque shadow DOM internals. |
| Not extensible | Teams cannot add custom item types or extend item behavior without forking the component. |
| No independent item reuse | `col-list-menu-item` cannot be used in other contexts (e.g., a standalone action row). |

### Industry standard

Every major web component design system — Shoelace, FAST (Microsoft), Material Web (Google), Ionic, Carbon (IBM) — uses compound components for menu/list patterns. Content projection is the common reason.

### When single component is appropriate

- Application-level components with a fixed, simple item schema
- Internal tooling where extensibility is not a requirement
- Dropdown selects with plain string options only
- Usage exclusively inside a JS framework where object prop passing is natural

### Verdict

For a **design system library**, use compound components. The single component trades away content projection, declarative HTML usage, per-item form association, and extensibility — all core requirements for a library consumed by multiple teams. The communication complexity (child-queries-parent in Stencil) is a one-time implementation cost; the limitations of a data-driven single component are a permanent constraint on every consumer.

---

## Conclusion

The compound component model (`col-list-menu` wrapping `col-list-menu-item` via slots) is the correct architecture for both frameworks and should be preserved unchanged.

The `@lit/context` mechanism is a Lit-specific optimization for reactive parent-child state sharing. In Stencil, it is replaced by the **child-queries-parent** pattern, which:
- Requires no additional libraries
- Is idiomatic in the web component ecosystem
- Performs identically at realistic menu sizes
- Can be trivially optimized with a parent-side cache if needed

The three render branches, keyboard navigation logic, ARIA attribute management, and slot structure all translate directly to Stencil with minimal adaptation.
