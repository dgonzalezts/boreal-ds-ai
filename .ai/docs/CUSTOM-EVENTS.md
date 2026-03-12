# Custom Events in Boreal DS — Why `@Event()` Over `emitEvent`

## Summary

All custom events in Boreal DS components **must** be declared using Stencil's `@Event()` decorator. The `emitEvent` utility is not an alternative — it bypasses the Stencil compiler pipeline and produces untyped, framework-incompatible events.

---

## The Core Problem with `emitEvent`

The `emitEvent` utility works by calling `new CustomEvent(name, { detail, bubbles, composed })` and dispatching it from the host element at runtime. It is invisible to the Stencil compiler.

This has three concrete consequences:

### 1. No entry in `components.d.ts`

Stencil generates a typed manifest (`components.d.ts`) from the `@Event()` declarations it finds at compile time. Events dispatched via `emitEvent` are not registered — they do not appear in the manifest.

```ts
// emitEvent — not in components.d.ts, not typed, invisible to the compiler
emitEvent('change', this.el, { value: this.value }, event);

// @Event() — registered in components.d.ts, fully typed, compiler-aware
@Event({ bubbles: true, composed: true, cancelable: true })
bdsInputChange!: EventEmitter<{ value: string; event: InputEvent }>;
```

### 2. No framework wrapper bindings

Stencil's output targets (`@stencil/react-output-target`, `@stencil/angular-output-target`) generate per-framework bindings by reading `@Event()` declarations. Without a declaration, no binding is generated.

| Event approach | React | Angular | Vanilla JS |
|---|---|---|---|
| `emitEvent('change', ...)` | Must use `ref.addEventListener(...)` | Must use `(change)` with unknown type | Works but untyped |
| `@Event() bdsInputChange` | `onBdsInputChange` prop, fully typed | `(bdsInputChange)` binding, typed | `addEventListener('bdsInputChange', ...)` |

### 3. Broken type contract when reusing native event names

If `emitEvent` is called with a native event name like `'click'` or `'change'`, the dispatched event is a `CustomEvent` — not the native `MouseEvent` or `InputEvent` the name implies. Consumers writing typed handlers receive the wrong type silently.

```ts
// emitEvent with native name — type mismatch
emitEvent('click', this.el, { value: 42 }, originalEvent);

// Consumer expects MouseEvent, gets CustomEvent — types are wrong
element.addEventListener('click', (e: MouseEvent) => {
  console.log(e.clientX); // undefined — this is actually a CustomEvent
});
```

---

## Enriching Event Details with `@Event()`

A common motivation for `emitEvent` was the ability to pass custom data in the `detail` object. `@Event()` supports this fully through the `EventEmitter<T>` generic. The generic `T` is unconstrained — it can be any shape.

### Simple payload

```ts
@Event({ bubbles: true, composed: true, cancelable: true })
bdsButtonClick!: EventEmitter<{ event: MouseEvent }>;

// Emit
this.bdsButtonClick.emit({ event });

// Consumer
element.addEventListener('bdsButtonClick', (e: CustomEvent<{ event: MouseEvent }>) => {
  console.log(e.detail.event.clientX);
});
```

### Rich payload with multiple custom props

```ts
@Event({ bubbles: true, composed: true, cancelable: true })
bdsSelectChange!: EventEmitter<{
  value: string;
  label: string;
  previousValue: string;
  event: Event;
}>;

// Emit
this.bdsSelectChange.emit({
  value: this.value,
  label: this.selectedLabel,
  previousValue: this.previousValue,
  event,
});

// Consumer — full autocomplete and type safety on event.detail
element.addEventListener('bdsSelectChange', (e: CustomEvent) => {
  console.log(e.detail.value);         // string
  console.log(e.detail.label);         // string
  console.log(e.detail.previousValue); // string
});
```

### React consumer (generated from `@Event()`)

```tsx
<BdsSelect
  onBdsSelectChange={(e) => {
    // e is typed as CustomEvent<{ value: string; label: string; previousValue: string; event: Event }>
    console.log(e.detail.value);
    console.log(e.detail.label);
  }}
/>
```

The `onBdsSelectChange` prop — with its full `detail` type — is generated automatically by Stencil's React output target from the `@Event()` declaration. `emitEvent` cannot produce this.

---

## Controlling Propagation

`@Event()` options control event behavior explicitly. All three must always be declared — never rely on undocumented defaults.

| Option | Value | Reason |
|---|---|---|
| `bubbles` | `true` | Events must reach parent elements and framework roots |
| `composed` | `true` | Future-proofs against Shadow DOM migration; currently a no-op in light DOM |
| `cancelable` | `true` or `false` | `true` when consumers need to call `.preventDefault()` to opt out of a default action |

When `cancelable: true`, the component can check whether the consumer opted out:

```ts
private handleClick = (event: MouseEvent) => {
  event.preventDefault(); // prevent native browser action

  if (this.disabled || this.loading) {
    event.stopPropagation();
    return;
  }

  const emitted = this.bdsButtonClick.emit({ event });
  if (emitted.defaultPrevented) {
    event.stopPropagation(); // consumer opted out — stop native propagation too
  }
};
```

---

## Naming Convention

Event names must follow the `bds` + component noun + action pattern in camelCase. This avoids collisions with native browser events and React's synthetic event system.

| Native name (avoid) | Boreal DS name (use) | React binding (generated) |
|---|---|---|
| `click` | `bdsButtonClick` | `onBdsButtonClick` |
| `change` | `bdsInputChange` | `onBdsInputChange` |
| `focus` | `bdsInputFocus` | `onBdsInputFocus` |
| `blur` | `bdsSelectBlur` | `onBdsSelectBlur` |

This convention follows the established pattern of Ionic (`ionClick`, `ionChange`, `ionFocus`) — the largest production Stencil-based design system.

---

## Quick Reference

```ts
// ✅ Correct — typed, compiler-aware, framework-compatible
@Event({ bubbles: true, composed: true, cancelable: true })
bdsInputChange!: EventEmitter<{ value: string; event: InputEvent; isValid: boolean }>;

this.bdsInputChange.emit({ value: this.value, event, isValid: this.checkValidity() });

// ❌ Wrong — untyped, no manifest entry, no framework binding
emitEvent('change', this.el, { value: this.value }, event);
```
