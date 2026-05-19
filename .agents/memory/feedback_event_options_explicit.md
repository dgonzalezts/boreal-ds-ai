---
name: Stencil — @Event() bare decorator is the accepted convention
description: Bare @Event() with no options is the project convention, aligned with BEEQ and Aqua DS. Explicit bubbles/composed/cancelable is no longer required.
type: feedback
---

Bare `@Event()` with no explicit `bubbles`, `composed`, or `cancelable` is the accepted and enforced convention in Boreal DS.

**Why:** Reviewed against the two primary Stencil reference implementations (BEEQ: 88 bare `@Event()`; Aqua DS: 80 bare `@Event()`). Both use bare `@Event()` universally. Consumers attach listeners directly to the component element — bubbling is only needed for event delegation, which none of these projects use. `composed` is irrelevant because Boreal uses light DOM. See ADR `.ai/decisions/0003-event-options-convention.md` for full rationale.

**How to apply:** Never add `{ bubbles, composed, cancelable }` to an `@Event()` decorator unless there is an explicit, documented reason to deviate. The bare form is correct.
