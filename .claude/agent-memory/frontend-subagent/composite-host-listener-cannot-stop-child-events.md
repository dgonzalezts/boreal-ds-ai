---
name: composite-host-listener-cannot-stop-child-events
description: In a light-DOM composite, stopPropagation must be attached to the child element, never to the composite host (bubble or capture) — a host listener cannot hide a descendant's event from consumers listening on the same host, and a capture-phase stop at the host starves the composite's own inner components.
---

# Composite host listeners cannot stop child events from reaching consumers

Context: `bds-search-bar` (T22, EOA-19597) leaked `bds-text-field`'s `bdsClear` and `bds-select`'s
`valueChange` to host-level consumers alongside its own events.

## The two dead ends

- **Bubble-phase listener on the composite host** — `stopPropagation()` at the host does NOT stop
  other listeners on the *same node*. A consumer does `searchBar.addEventListener('bdsClear', …)`, so
  stopping at the host leaves the leak fully intact.
- **Capture-phase listener on the composite host** — this does work for the consumer (the event never
  reaches the target's bubble phase), but it also stops the event from ever reaching the composite's
  own children: in `bds-search-bar` that means `bds-select` never sees `bds-text-field`'s `bdsClear`
  (`listenClearInput`) or `valueChange` (`stopFieldValueChange`), silently breaking the internal wiring.

## The pattern that works

Attach the guard to the **child element itself** (JSX inline handler, or `addElementListener` on the
child). `stopPropagation()` there stops the event from leaving the child for its ancestors, while
listeners already registered on that same node — the composite's own `bds-select` handlers — still run
because `stopPropagation()` only blocks *propagation*, not same-node delivery.

```tsx
<bds-text-field
  onBdsChange={this.stopChildEventPropagation}
  onBdsClear={this.handleFieldClear} // calls event.stopPropagation() first
  onBdsInput={this.handleFieldInput}
  onValueChange={this.stopChildEventPropagation}
/>
<bds-select onBdsChange={this.handleSelectChange} onValueChange={this.stopChildEventPropagation} />
```

Do NOT route `bdsFocus`/`bdsBlur` through the same guard when the composite host reads them via
`onBdsFocus`/`onBdsBlur` on `<Host>` — that wiring depends on the events bubbling to the host.

## Secondary fact

`bds-select`'s `listenClearInput` does not check its `managed` prop (unlike `listenField`), so any
composite that reimplements the field's clear still gets an echoing `bdsChange('')` + `valueChange('')`
from the select. In `bds-search-bar` that echo makes one X-clear click produce two host `valueChange`
and one `bdsSearch` with `{ value: '' }` — both emitted by the search bar itself, so they are NOT
removable by the child-event guards above and were deliberately left (documented in T47).

Measured after the guard (host listeners, one interaction, identical in slotted and `items` modes):
pick = 1 `bdsSearch` + 1 `valueChange`; X-clear = 1 `bdsClear` + 1 `bdsInput` + 2 `valueChange` + 1
`bdsSearch`; typing 3 chars = 3 `bdsInput` + 4 `valueChange` (3 keystroke + 1 commit); Escape with
text = 1 `bdsClear` + 1 `bdsInput` + 1 `valueChange`.
