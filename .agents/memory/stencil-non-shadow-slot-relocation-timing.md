# Non-Shadow Stencil: Default-Slot Children Are Relocated Before `componentDidLoad`

## The Constraint

Any Stencil component that omits `shadow: true` (light DOM / non-shadow mode) runs Stencil's non-shadow slot polyfill. On the component's *first render*, the polyfill physically relocates the host's original default-slot light-DOM children out of being direct children of the host element and into the rendered `<slot>` placeholder's position (e.g. into a wrapper `<span>`). This relocation completes *before* `componentDidLoad` fires.

Consequence: any check that inspects the host's direct `childNodes` to detect default-slot content — such as the existing `hasSlotContent(el)` utility in `packages/boreal-web-components/src/utils/dom/elements.ts` (non-recursive, reads `el.childNodes` directly) — will **always** report "empty" when called from `componentDidLoad`, regardless of what the consumer actually wrote in markup.

## Repro

```ts
newSpecPage({ components: [BdsButton], html: '<bds-button name="x">Delete item</bds-button>' });
```

Inspecting `page.root.outerHTML` after the first render shows the text `"Delete item"` nested inside `.bds-button__content-text`; `page.root.childNodes` only contains a comment marker, a whitespace text node, and the rendered `<button>` — the original text node is no longer a direct child of the host.

## Real Bug Found

`bds-button`'s `checkAccessibleName()` diagnostic (added for accessibility auditing, ticket AI-001) called `hasSlotContent(this.el)` from `componentDidLoad()`. A valid `<bds-button>Delete item</bds-button>` (no `label` prop, real slotted text) incorrectly fired the "no accessible name found" `console.warn`, because by the time `componentDidLoad` ran the slotted text had already been relocated.

## Fix

Move any direct-childNodes slot-content check to `componentWillLoad()` — it runs *before* the first render/relocation, so `this.el`'s children are still in their original, pre-relocation light-DOM form.

## What Is Unaffected

Named-slot detection via `querySelector` (e.g. `this.el.querySelector('[slot="icon"]')`) is safe in either lifecycle hook. `querySelector` searches the whole subtree recursively and finds the element regardless of relocation depth — the `slot` attribute survives relocation, only the parent element changes. Only checks against the host's *direct* `childNodes` (like `hasSlotContent`'s default-slot check) are affected by the timing.

## Rule of Thumb

Any non-shadow Stencil component that inspects `this.el`'s direct children to detect default-slot content must do so in `componentWillLoad`, never `componentDidLoad`.

Source: AI-001 `bds-button` accessibility diagnostics session. `hasSlotContent` had no prior real consumer before this task.

## Related but Distinct: CSS `:empty` Is Unaffected by This Timing Issue, and Works Correctly

`bds-button.scss` has `&:empty { display: none; }` on `.bds-button__content-icon`, `-text`, and `-badge` — each wrapping a `<slot>` in JSX. This looks superficially like the same bug (both check "is this slot empty"), but it is not: CSS selectors are evaluated live against whatever the DOM looks like at any given moment, so there is no "checked too early/before relocation" problem the way there is for a JS check run inside a specific lifecycle hook.

Verified empirically (`newSpecPage` + `page.waitForChanges()`, inspecting real childNode structure across empty / icon-only / text-only / all-three-filled scenarios): Stencil's non-shadow slot polyfill leaves behind exactly one **zero-length text node** as an anchor marker in each wrapper span, in place of the original `<slot>` — never a `<slot>` element, a comment, or a whitespace-containing text node. Per the CSS Selectors spec, `:empty` explicitly excludes zero-length text nodes from consideration (only comments/PIs are ignored outright, but a `""`-length text node also doesn't count against emptiness). So a wrapper containing only this marker still matches `:empty`; a wrapper that gained real slotted content (an element node, or non-empty text) no longer matches. All three wrapper rules in `bds-button.scss` work correctly today, not just the icon one.

**The risk to track, not fix:** this behavior depends on an internal, undocumented detail of Stencil's non-shadow slot polyfill (that it always leaves exactly one zero-length marker text node, in this exact form) — not a documented part of Stencil's public API contract. A future Stencil version could change that polyfill's internal implementation and silently break `:empty`-based empty-state collapsing across `bds-button` and the ~20 other components using the same `:empty` + `<slot>` pattern (`bds-checkbox`, `bds-card`, `bds-dialog`, `bds-tag`, `bds-toast-item`, `bds-banner`, etc.) — with no compile error, only a visual regression. Decision made in AI-003 (2026-07-15): keep the CSS-only approach as-is (it's simpler and matches this codebase's actual idiom of CSS-class-driven slot-presence styling — no component here uses JS-state-driven conditional *JSX omission* keyed to detected slot content; `bds-card`'s `hasHeader`/`hasFooter` only toggle CSS modifier classes on an always-rendered wrapper, the same category of solution as `:empty`). If a future Stencil upgrade breaks empty-slot collapsing anywhere in this codebase, check the polyfill's marker-node behavior first — this is the most likely root cause.

Source: AI-003 `bds-button` slot-rendering review session, 2026-07-15.
