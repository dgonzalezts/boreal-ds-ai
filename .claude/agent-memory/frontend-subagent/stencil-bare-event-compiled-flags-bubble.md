---
name: stencil-bare-event-compiled-flags-bubble
description: Bare @Event() compiles to flags 7 (bubbles+composed+cancellable) in Stencil 4.42.1 — it DOES bubble, contradicting ADR 0003's "all flags false" claim
metadata:
  type: project
---

`ADR 0003` states a bare `@Event()` sets `bubbles`/`composed`/`cancelable` all to `false` (quoting `event-emitter.ts`'s `!!(flags & N)` bitmask). **That is wrong for the installed Stencil version (`@stencil/core@4.42.1`).** Inspecting a compiled dev build (`www/build/bds-calendar-grid.entry.js`) shows every bare event emitted as `d(this,"bdsMonthNavigate",7)` / `d(this,"bdsDayClick",7)` — flags `7` = `Bubbles(4) | Composed(2) | Cancellable(1)`, i.e. **all three true**.

Consequences / how to apply:

- A parent's bare `@Listen('bdsMonthNavigate')` (no target) **does** receive events emitted by a light-DOM child, because the child's `@Event()` bubbles by default. This is why `bds-date-picker`'s host-level `@Listen` worked for years despite the ADR.
- Do not trust the ADR's claim when reasoning about whether an event reaches an ancestor; verify against the compiled entry (`grep 'emit.*\",7)'` style — look for the numeric flag on the `createEvent` call) before assuming a bare event is non-bubbling.
- `composed: true` is irrelevant in light DOM (no shadow boundary), as the ADR itself notes.

**Why:** discovered during EOA-17662 Task 48 — removing the host `@Listen('bdsMonthNavigate')` in favour of per-instance JSX `onBdsMonthNavigate` bindings was only safe to reason about after confirming the event still bubbles (it does, but nothing relies on bubbling once bound directly on the emitting element).

**Promote?** This corrects a documented ADR, so it is cross-cutting — candidate for `.agents/memory/` via knowledge-keeper.
