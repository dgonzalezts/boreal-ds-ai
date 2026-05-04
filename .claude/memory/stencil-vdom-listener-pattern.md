# Stencil — vDOM Listener vs `@Listen` for Component-Scoped Events

## Rule

Use **vDOM inline listeners** (`onKeyDown={this.handleKeyDown}` on `<Host />` or any rendered element) for all events that are component-scoped and rely on DOM bubbling. Use `@Listen` only when its exclusive options (`target`, `capture`, `passive`) are needed.

## Why

- `@Listen('keydown')` with no options triggers the `prefer-vdom-listener` ESLint rule.
- vDOM listener event names are TypeScript type-checked; `@Listen` event names are plain strings — typos compile silently.
- Both approaches are auto-managed by Stencil's lifecycle (no manual `addEventListener`/`removeEventListener` needed).

## Correct pattern

```tsx
// Handler as class arrow function to preserve `this`
private handleKeyDown = (event: KeyboardEvent) => { ... };

// vDOM listener on Host — type-safe, ESLint-compliant
render() {
  return <Host onKeyDown={this.handleKeyDown} />;
}
```

## When `@Listen` IS correct

Only use `@Listen` when you need one of these options that the vDOM approach cannot provide:

```tsx
// target — listen on window/document/body
@Listen('scroll', { target: 'window', passive: true })
handleScroll(ev: Event) { ... }

// capture phase
@Listen('click', { capture: true })
handleClick(ev: MouseEvent) { ... }
```

## Anti-patterns

```tsx
// ❌ Bare @Listen for a component-scoped keyboard event
@Listen('keydown')
handleKeyDown(ev: KeyboardEvent) { ... }

// ❌ Silencing the lint rule with an empty options object — workaround, not a fix
@Listen('keydown', {})
handleKeyDown(ev: KeyboardEvent) { ... }

// ❌ Imperative wiring for component-scoped events — manual leak risk
connectedCallback() { this.el.addEventListener('keydown', this.handleKeyDown); }
disconnectedCallback() { this.el.removeEventListener('keydown', this.handleKeyDown); }
```

## References

- GitHub issue: https://github.com/stenciljs/eslint-plugin/issues/10
- Stencil docs on `@Listen` options (target, passive, capture): https://stenciljs.com/docs/events#target
- Usage in this codebase: `bds-radio-group.tsx` — `onKeyDown={this.handleKeyDown}` on `<Host />`
