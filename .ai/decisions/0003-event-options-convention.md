# ADR 0003 — `@Event()` options convention: bare decorator is accepted

**Date:** 2026-03-13
**Status:** Accepted

---

## Context

Stencil's `@Event()` decorator accepts an optional `EventOptions` object with three flags:

- `bubbles` — whether the event propagates up the DOM tree
- `composed` — whether the event crosses the shadow DOM boundary
- `cancelable` — whether a listener can call `preventDefault()`

When the decorator is used without options (`@Event()`), the Stencil runtime sets all three flags to `false` via bitmask:

```typescript
// src/runtime/event-emitter.ts (stenciljs/core)
const event = new CustomEvent(name, {
  bubbles:    !!(flags & EVENT_FLAGS.Bubbles),    // false if not set
  composed:   !!(flags & EVENT_FLAGS.Composed),   // false if not set
  cancelable: !!(flags & EVENT_FLAGS.Cancellable), // false if not set
  detail
});
```

The Boreal DS checklist previously required explicit declaration of all three flags on every `@Event()`. This was reviewed against how comparable Stencil-based design systems approach the same question.

---

## Decision drivers

**Two reference design systems were examined:**

| Project | Shadow DOM | `@Event()` with options | `@Event()` bare | Stencil |
|---|---|---|---|---|
| **BEEQ** (Endava) | `shadow: true` | 0 | 88 | Yes |
| **Aqua DS** | `shadow: false` | 0 | 80 | Yes |
| **Boreal DS** | `shadow: false` | 0 | — | Yes |

Both projects use bare `@Event()` consistently across every component, with no exceptions. Neither documents this as an explicit rule — it is an implicit convention arising from their event consumption model.

**Why bare `@Event()` is safe for all three projects:**

All consumers attach event listeners **directly to the component element**, not to ancestor containers:

```javascript
// Aqua DS documented usage pattern
const aqButton = document.getElementById("aqButton");
aqButton.addEventListener('click', (event) => { ... });
```

Direct attachment does not require `bubbles: true`. Bubbling is only needed for event delegation (listening on a parent container). None of the three projects' documented usage patterns rely on delegation.

**`composed` is also irrelevant for Boreal DS** because Boreal uses light DOM (`shadow: false`). There is no shadow DOM boundary for events to cross.

**`cancelable` is a design choice per event.** For toggle events (checkbox, radio), the state mutation has already occurred before the event fires, making `preventDefault()` semantically meaningless. For other event types this should be considered individually, but the default of `false` is safe.

---

## Decision

**Bare `@Event()` is the accepted convention in Boreal DS.**

Explicit `bubbles`, `composed`, and `cancelable` options are not required. This aligns with both BEEQ and Aqua DS, which are the primary reference implementations for this design system.

The `event-implicit-options` rule has been removed from:
- `code_quality_checker.py` — rule no longer fires
- `review_report_generator.py` — removed from checklist section A and rule-to-checklist mapping
- `code_review_checklist.md` — "Event options explicit" item removed
- `common_antipatterns.md` — "Implicit event options" antipattern removed
- `SKILL.md` — rule removed from the enforced rules table

---

## Consequences

**Positive:**
- Boreal DS components are consistent with BEEQ and Aqua DS conventions
- Less boilerplate on every `@Event()` declaration
- No false positives in automated review reports

**Constraint introduced:**
- Consumers **must** attach listeners directly to the component element, not to ancestor containers. This is an implicit API contract that is not enforced by types or tooling.
- If Boreal DS ever introduces a usage pattern that requires event delegation, explicit `bubbles: true` will be needed on affected events and this ADR should be revisited.

---

## References

- Stencil `@Event()` docs: https://stenciljs.com/docs/events
- Stencil core runtime `event-emitter.ts`: `github.com/stenciljs/core`
- BEEQ source reference: `.ai/lib/endava-beeq.txt`
- Aqua DS source reference: `.ai/lib/aqua-ds.txt`
