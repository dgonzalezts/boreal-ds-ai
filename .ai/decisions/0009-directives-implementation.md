# ADR 0009 — Defer directive system in favor of component-level alternatives

**Date:** 2026-04-08
**Status:** Accepted

---

## Context

A directive system applies behavior to DOM elements from the outside using HTML attributes as the configuration surface. The canonical implementation uses a global `MutationObserver` that watches the document for attribute additions and changes; when a known directive attribute appears on any element, a registered callback fires and applies the behavior.

This mechanism is the only way to enhance elements whose source cannot be modified:

- **Native HTML elements** — a `<button>` or `<input>` cannot be given custom props.
- **Third-party components** — external packages cannot be wrapped without potentially interfering with internal layout measurements (data grids, virtualized lists, charts).
- **Server-rendered / CMS-generated HTML** — when HTML arrives pre-rendered and the only control point is a post-load script.

Three behaviors were candidates for directive implementation: **Spinner** (loading overlay on an arbitrary element), **Tooltip** (positional popover on an arbitrary element), and **Dialog / Drawer trigger** (declarative click binding between a trigger element and an overlay component).

**Global trade-offs for a directive system:**

| Gains | Costs |
| ----- | ----- |
| Framework-agnostic — one implementation instead of React / Vue / Angular variants | No TypeScript safety — attribute values are strings; typos and type errors are silent |
| Zero-wrapper injection — no added DOM ancestors | JSON ceiling — non-serializable options (functions, DOM refs, lifecycle hooks) cannot be passed |
| Declarative HTML works in server-side and CMS templates | SSR incompatible — `MutationObserver` depends on `document`, which does not exist in Node.js |
| Reactive to attribute changes automatically | Global observer overhead — fires on every DOM mutation across the entire document |
| Single maintenance surface across all frameworks | Singleton coordination risk in microfrontend architectures |

---

## Options Considered

### Option A — Implement a directive system for all three behaviors

A global `MutationObserver` registers directive handlers for spinner, tooltip, and dialog/drawer trigger. All three behaviors are available via HTML attributes in any framework or template context.

Rejected: the use cases that justify the infrastructure — elements the library does not own, requiring zero wrappers — are covered by simpler alternatives for all three behaviors. Consumer demand for CMS/server-rendered targets is unconfirmed.

### Option B — Implement directives only for behaviors with no viable alternative

Evaluate each behavior individually and ship directives only where component-level alternatives fall short.

- **Spinner**: A slot-based wrapper component solves the problem without a directive. The wrapped element is projected via `<slot>` and is not reparented in the light DOM, so its CSS parent context is preserved. A directive provides a genuine advantage only when the shadow host's presence measurably breaks the wrapped element's internal layout — real but uncommon.
- **Tooltip**: An anchor-binding sibling component (`<button id="btn">…</button>` + `<my-tooltip anchor="btn">…</my-tooltip>`) avoids wrappers and leaves the target element unchanged. A directive would only be needed for CMS/server-rendered HTML where inserting a sibling element is not viable.
- **Dialog / Drawer trigger**: Framework-idiomatic event wiring (`onClick={() => ref.current.show()}` / `@click="dialog.show()"`) is the industry standard. The directive saves two tokens at the cost of a global click listener on every mounted overlay instance, a naming convention split across two files with no shared contract, and zero TypeScript safety.

None of the three behaviors have confirmed use cases the alternatives cannot cover. Rejected: partial implementation still ships the `MutationObserver` infrastructure speculatively.

### Option C — Defer the directive system; ship component-level alternatives

Ship the slot-based spinner wrapper and the anchor-binding tooltip component. Do not implement a directive system unless a consumer reports a concrete case the alternatives cannot resolve. Accepted.

---

## Decision

Do not implement a directive system at this stage. Prefer component-level alternatives for each behavior:

| Behavior                | Preferred alternative               | Revisit if                                                         |
| ----------------------- | ----------------------------------- | ------------------------------------------------------------------ |
| Spinner                 | Slot-based wrapper component        | Consumer confirms wrapper breaks layout on a specific element      |
| Tooltip                 | Anchor-binding sibling component    | Consumer confirms sibling element is not viable for their use case |
| Dialog / Drawer trigger | Consumer wires `onClick` / `@click` | Confirmed demand from non-framework consumers (CMS, vanilla HTML)  |

Deferral is not rejection. If consumer usage reveals cases where the alternatives are genuinely insufficient, the directive system can be added incrementally — starting with the one behavior that triggered the demand, with a concrete test case as the acceptance criterion.

---

## Consequences

- **No global observer overhead** until consumer demand is confirmed.
- **Full TypeScript safety** for all three behaviors via typed component props.
- **SSR compatible** — slot-based and anchor-binding patterns work in Next.js, Nuxt, and Angular Universal.
- **Accessibility prerequisite**: before the dialog and drawer components expose any trigger-binding API, they must first have `role="dialog"`, `aria-modal`, `aria-labelledby`, focus trap, and body scroll lock in place.
- **If a directive ships in future**, the following must be in place before release:
  - SSR guard (`typeof document !== 'undefined'`) on all observer initialization
  - Singleton coordination for microfrontend architectures (cross-bundle `window` flag or shared bundler config)
  - Error logging on malformed JSON attribute values — silent fallback produces invisible no-ops
  - Documentation of the JSON ceiling (non-serializable config options unavailable via directive)
  - Integration tests for the full observer cycle: attribute set → observer fires → behavior applied → attribute changed → behavior updated
  - Explicit unsupported-environment list (SSR runtimes, Salesforce Lightning Web Components)
