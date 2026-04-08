# Directive Systems in Stencil-Based Component Libraries
## A Technical Assessment Based on the Aqua Design System

---

## Executive Summary

This report evaluates whether implementing a **directive system** — attribute-based behavior injection using a `MutationObserver` — is justified in a new Stencil-based component library. The analysis is grounded in the implementation found in `packages/aqua-web-components/src/utils/directives/` and benchmarked against three peer libraries: BEEQ (Endava), IgniteUI, and Colibri.

**Conclusion:** A directive system is **not justified at this stage**. Simpler component-level alternatives (slot-based wrapper, anchor-binding sibling) cover the confirmed use cases with full TypeScript safety and no global observer overhead. The system as implemented in Aqua carries known bugs and missing accessibility foundations that must be addressed before any directive ships.

---

## Deployment Profile

| Factor                          | Status                       | Impact on directive system                                            |
| ------------------------------- | ---------------------------- | --------------------------------------------------------------------- |
| React, Vue, Angular consumers   | Confirmed — primary use case | Justifies unified implementation over 3 framework-native variants     |
| Microfrontend architecture      | Confirmed                    | Singleton pattern critical; module isolation risk must be resolved    |
| Salesforce Lightning Components | Potential use case           | **Likely incompatible** — shadow DOM boundary blocks MutationObserver |
| Vanilla JS                      | Minimal probability          | Covered as a side effect of framework-agnostic design                 |

---

## 1. What Are Directives?

Directives are **framework-agnostic, attribute-based behaviors** applied to arbitrary DOM elements via a global `MutationObserver`. They are distinct from component props: rather than configuring a component you own, directives enhance elements from the outside — native HTML elements, third-party components, or any element in the DOM.

**How the Aqua system works:**

- `setupDirectives(['aq-spinner', 'aq-tooltip'])` is called at app bootstrap; it registers callbacks per directive name and starts a single `MutationObserver` on `document.body`
- The observer fires on `childList` and `attributes` mutations, matching elements that carry registered directive attributes and invoking the associated callback
- Attribute values are serialized as JSON strings and parsed at runtime; plain strings fall back gracefully
- A `WeakMap` prevents double-application when the same element is seen more than once
- A class-level singleton ensures a single observer regardless of how many times `setupDirectives()` is called

---

## 2. Directive Assessment

### `aq-spinner` — Deferred

**Claim:** The directive injects a backdrop and indicator into elements the library does not own (third-party grids, native inputs) without adding DOM ancestors.

**Why deferred:** A slot-based wrapper component covers the same use case. Stencil's `<slot>` does not reparent the slotted element — it remains a direct light DOM child of its original parent. The overlay lives in shadow DOM. The directive only wins in the narrow case where the shadow host's presence measurably breaks a component's internal layout — real but unconfirmed.

**Condition for revisiting:** A consumer confirms that the slot-based wrapper breaks a specific third-party component's layout.

---

### `aq-tooltip` — Deferred

**Claim:** The directive attaches a Tippy.js popover to any element without wrapping it.

**Why deferred:** An anchor-binding sibling component (see Section 5) avoids wrappers entirely and has no JSON ceiling. Tippy.js options like `onShow`, `render`, and `appendTo` are non-serializable — they are silently dropped by `JSON.stringify`, permanently limiting the directive to basic config only. The directive adds a convenience that is outclassed by the typed component API in almost every case.

**Only genuine advantage:** CMS / server-rendered HTML where inserting a sibling element is not viable.

---

### `aq-dialog` / `aq-drawer` — Deferred

**What it actually does (corrected analysis):** The directive injects a namespaced class token (`aq-dialog-{id}`) onto the trigger element. The component completes the binding via a `@Listen('click', { target: 'window' })` handler that opens itself when a click lands on an element carrying the matching class. This is declarative trigger-to-component binding, not a CSS layout variant.

**Why deferred:** The same outcome requires two tokens in any framework:

```tsx
// React
<button onClick={() => dialogRef.current.show()}>Open</button>

// Vue
<button @click="dialog.show()">Open</button>
```

All three peer libraries take this approach. The directive saves those tokens at the cost of a global click listener on every mounted instance (regardless of whether the directive is ever used), a naming convention split across two files with no shared type contract, and several implementation bugs (see Section 4). Accessibility foundations must be addressed first regardless.

---

## 3. The "Elements You Don't Own" Justification

The only scenario where directives provide something component wrappers cannot is applying behavior to elements whose source cannot be modified:

**Category 1 — Native HTML elements:** `<button>`, `<input>`, and other browser-owned elements cannot accept custom props. A directive is the only way to attach library behavior without a wrapper element.

**Category 2 — Third-party components:** External packages cannot be modified. Wrapping them is often viable, but some components (data grids, charts, virtualized lists) perform internal measurements based on their CSS parent — adding a host element can interfere.

**Category 3 — Server-rendered / CMS HTML:** When HTML arrives pre-rendered and the only control point is a post-load script, there is no JSX boundary to reach for. Attributes can be set imperatively and the observer responds immediately.

**Threshold question:** Does the library have confirmed use cases in any of these three categories? If all target elements are components the team controls, standard component APIs are sufficient.

---

## 4. Risks

| Risk | Detail | Severity |
| ---- | ------ | -------- |
| Global observer overhead | `subtree: true` fires on every DOM mutation in the entire app; measurable in high-frequency UIs | Medium |
| JSON ceiling | Non-serializable options (functions, DOM refs, lifecycle hooks) are silently stripped by `JSON.stringify` | High |
| No TypeScript safety | Typos, wrong types, and missing required fields in attribute values are invisible to the compiler | High |
| Silent parse failures | The attribute-change path in `init.ts` swallows JSON errors without a `console.warn` | Medium |
| SSR incompatible | `document` does not exist in Node.js; crashes in Next.js SSR, Nuxt, Angular Universal, Astro without `typeof document !== 'undefined'` guards | High |
| Microfrontend singleton breakage | Each independently bundled MFE gets its own module scope and its own `InitDirectives` instance — multiple observers fire simultaneously, applying directives multiple times | High |
| Salesforce LWC incompatible | `MutationObserver` on `document.body` cannot cross shadow root boundaries; `querySelectorAll` also stops at shadow roots; LWC sandbox may block attribute setting | Blocker |
| Unconditional click listener | `@Listen('click', { target: 'window' })` runs on every dialog/drawer instance regardless of whether `setupDirectives()` was called | Medium |
| No `id` guard on trigger binding | `<aq-dialog>` with no `id` constructs the class `aq-dialog-` which can match unintended elements | Low |
| Convention-only coupling | The directive and component share no TypeScript type or constant — renaming one side silently breaks the binding | Medium |
| Dead `closest()` selector | The `[aq-dialog]` / `[aq-drawer]` attribute branch in `closest()` is unreachable — `hasDirective` only passes for the class branch | Low |
| Missing a11y foundations | Neither `aq-dialog` nor `aq-drawer` has `role="dialog"`, `aria-modal`, `aria-labelledby`, focus trap, or body scroll lock | Critical |
| Live bug in codebase | `ServerTableSet.vue:228` double-encodes the tooltip value (`JSON.stringify` of a string literal); tooltip receives a string and silently renders nothing | Low |

---

## 5. Peer Library Comparison

None of BEEQ, IgniteUI, or Colibri implements an equivalent directive system.

| Aspect                                   | Aqua DS                               | BEEQ                        | IgniteUI                        | Colibri                         |
| ---------------------------------------- | ------------------------------------- | --------------------------- | ------------------------------- | ------------------------------- |
| External trigger binding (dialog/drawer) | ✅ `aq-dialog="id"` + class injection | ❌ Consumer's job           | ❌ Consumer's job               | ❌ Consumer's job               |
| Apply behavior to any element            | Yes — attribute on any element        | No — must use the component | No — sibling element required   | No — must use the component     |
| Framework-agnostic setup                 | Yes — one vanilla JS observer         | No — Stencil reactivity     | No — Lit reactivity             | No — Lit reactivity             |
| TypeScript safety                        | None — attribute string               | Full — `@Prop()` decorators | Full — `@property()` decorators | Full — `@property()` decorators |
| Non-serializable config                  | Impossible                            | Full support                | Full support                    | Full support                    |
| SSR compatibility                        | No                                    | Yes                         | Yes                             | Yes                             |
| Native `<dialog>` element                | No                                    | Yes                         | Yes (dialog only)               | No                              |
| Focus trap                               | No                                    | No                          | Native dialog                   | Yes (`FocusTrap` utility)       |
| Body scroll lock                         | No                                    | No                          | Native dialog                   | Yes                             |
| MutationObserver usage                   | Core system                           | Internal only               | Internal only                   | Internal only                   |

**Key takeaway:** The external trigger binding pattern is absent from all three peers — they defer it to the consumer. What the peers invest in instead — native `<dialog>`, focus traps, scroll locking — are the gaps Aqua currently has.

---

## 6. Alternatives for New Libraries

### For `aq-tooltip` → Anchor-binding component (IgniteUI pattern)

The tooltip is a sibling element in the DOM, linked to its target by ID reference. The target element is untouched — no wrapper, no structural change. All config is expressed as typed component props, so the full Floating UI / Tippy.js surface (placement, offset, lifecycle hooks, render functions) is available without a JSON ceiling.

```html
<button id="save-btn">Save</button>
<bds-tooltip anchor="save-btn" placement="bottom" trigger="mouseenter">
  Saves your changes
</bds-tooltip>
```

The directive provides a genuine advantage only for CMS / server-rendered HTML where inserting a sibling element is not viable.

---

### For `aq-spinner` → Slot-based wrapper with `show` prop

The wrapped element is projected via `<slot>` and is **not reparented** in the light DOM. The spinner overlay is injected inside the component's shadow DOM. The original element's CSS parent context is fully preserved.

```tsx
@Component({ tag: "bds-spinner", styleUrl: "bds-spinner.scss" })
export class BdsSpinner {
  @Element() el: HTMLElement;
  @Prop() show: boolean = false;
  @Prop() global: boolean = false;

  render() {
    const hasSlot = !!this.el.childNodes.length;
    return (
      <Host class={{ "bds-spinner--has-slot": hasSlot }}>
        {this.show && (
          <div
            class={{ "bds-spinner__overlay": true, "bds-spinner__overlay--global": this.global }}
            role="status"
            aria-live="polite"
          />
        )}
        {hasSlot && <slot />}
      </Host>
    );
  }
}
```

```tsx
// Scoped overlay
<bds-spinner show={isLoading}>
  <AgGridReact rowData={rows} columnDefs={cols} />
</bds-spinner>

// Full viewport overlay
<bds-spinner show={isNavigating} global />
```

**Accessibility baseline** (from Colibri `col-spinner`): `role="status"` + `aria-live="polite"`, visually-hidden `accessibilityText` prop (default `"Loading"`), three sizes (16 / 24 / 48px), `prefers-reduced-motion` guard.

The directive is only preferable if a consumer confirms the shadow host's presence breaks a specific element's internal layout.

---

### For `aq-dialog` / `aq-drawer` → Framework-idiomatic event wiring

The directive injects a namespaced class token and uses a window click listener to open the component. The same result in two tokens:

```tsx
// React
<button onClick={() => dialogRef.current.show()}>Open</button>

// Vue
<button @click="dialog.show()">Open</button>
```

This is the approach every peer library takes. The declarative HTML form has value for CMS / server-rendered templates where no JavaScript is available at authoring time. For React, Vue, and Angular consumers, the framework-idiomatic alternative is strictly better in every dimension.

**Before any trigger-binding work:** `bds-dialog` and `bds-drawer` need `role="dialog"`, `aria-modal`, `aria-labelledby`, focus trap, and body scroll lock first.

---

### If directive ergonomics are required per framework

Framework-native utilities offer a type-safe, SSR-compatible alternative at the cost of separate maintenance surface:

```tsx
// React hook
const spinnerRef = useSpinner({ show: isLoading, isGlobal: false });
<ThirdPartyComponent ref={spinnerRef} />

// Vue directive
<ThirdPartyComponent v-bds-spinner="{ show: isLoading }" />

// Angular directive
<third-party-component [bdsSpinner]="isLoading"></third-party-component>
```

---

## 7. Decision Matrix

| Directive               | Implement? | Preferred approach                                                        |
| ----------------------- | ---------- | ------------------------------------------------------------------------- |
| Spinner                 | Deferred   | Slot-based wrapper; revisit only if consumer confirms layout breakage     |
| Tooltip (basic)         | Deferred   | Anchor-binding sibling component — typed props, no JSON ceiling           |
| Tooltip (advanced)      | No         | Anchor-binding sibling component                                          |
| Dialog / Drawer trigger | Deferred   | Consumer wires `onClick` / `@click`; fix a11y foundations first           |
| Any directive in LWC    | No         | Standalone LWC-compatible component                                       |

---

## 8. Pre-Ship Checklist (if a directive is ever implemented)

| Question                                          | Status for this library              |
| ------------------------------------------------- | ------------------------------------ |
| Multiple frameworks or vanilla JS consumers?      | **Yes — React, Vue, Angular**        |
| Real "elements you don't own" use cases confirmed?| **Not yet — must be confirmed**      |
| SSR is not a requirement?                         | Likely — confirm explicitly          |
| Team accepts no TypeScript safety on values?      | Confirm                              |
| Config stays serializable (no functions/DOM)?     | Yes for basic usage                  |
| Explicit opt-in (`setupDirectives`) acceptable?   | **Yes — host shell owns it**         |
| Testing strategy for observer-based behavior?     | To be defined                        |
| Microfrontend module isolation resolved?          | **Requires bundler config**          |
| Salesforce Lightning support needed?              | **Out of scope — shadow DOM blocks** |
| `console.warn` on malformed attribute values?     | Not yet — must be added              |
| `typeof document !== 'undefined'` guards?         | Not yet — must be added              |
