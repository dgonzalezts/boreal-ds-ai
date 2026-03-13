# Stencil — Custom Event Naming Convention

## Rule

All custom events in Boreal DS components must use prefixed camelCase names. The required format is:

```
bds + {ComponentNoun} + {Action}
```

Examples: `bdsButtonClick`, `bdsInputChange`, `bdsSelectOpen`.

Never use a native DOM event name (e.g. `click`, `change`, `input`) as the value passed to `@Event()`.

## Why Native Event Names Break the Contract

Using a native event name like `click` creates three distinct failure modes:

1. **Type-contract violation.** Consumers who write `element.addEventListener('click', handler)` expect the handler to receive a `MouseEvent`. A custom event named `click` delivers a `CustomEvent`, which breaks any code that accesses `MouseEvent`-specific properties (`clientX`, `button`, etc.).

2. **Duplicate event dispatch.** If the native `click` event also bubbles (it will, unless explicitly stopped), the host element dispatches two separate events named `click`: the native one and the custom one. Event listeners fire twice with different event objects.

3. **Framework binding collision.** React's `onClick` synthetic event handler maps to the native `click` event. A `@Event()` named `click` causes Stencil's React output target to generate `onClick` as a prop, creating an unresolvable name conflict with the synthetic event.

## Framework Binding Output

Prefixed names produce unambiguous, non-colliding framework bindings:

| Framework | Generated binding |
|---|---|
| React | `onBdsButtonClick` |
| Angular | `(bdsButtonClick)` |
| Vue | `@bds-button-click` |

## Canonical Pattern

```ts
@Event()
bdsButtonClick!: EventEmitter<{ event: MouseEvent }>;
```

## Reference

This convention mirrors the established Ionic pattern (`ionClick`, `ionChange`, etc.) and is validated by the Stencil BEEQ reference implementation at `.ai/lib/endava-beeq.txt`.
