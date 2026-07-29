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

## Follow-up: Detecting Genuinely Late-Arriving Content (Not Just Avoiding the componentDidLoad Trap)

The `componentWillLoad`-only fix above is correct for content present at initial mount, but it cannot detect content that legitimately arrives *after* mount — e.g. `bds-table`'s formatter-produced `bds-button` cells, where a cached DOM node gets moved into a new `<td>` across re-renders, or a `bds-pagination` page-number button whose slotted text isn't yet a direct host child at the exact moment its own `componentWillLoad`/`componentWillRender` runs. For that case, `componentWillLoad` is *too early* — you need a real post-mount check, and two more constraints apply that the original fix above doesn't cover:

1. **Never re-check the raw host (`this.el.childNodes`) after the first render, even from `componentDidLoad`.** By that point `this.el`'s direct children are a mix of the component's *own rendered output* (e.g. the internal `<button>` wrapper) and any not-yet-relocated original content. A generic `hasSlotContent(this.el)` call at this stage produces false positives — it will treat the component's own rendered root element as if it were slotted content, since that root has no `slot` attribute either. Post-mount, always check the *settled internal wrapper* instead (e.g. `this.el.querySelector('.bds-button__content-text')`), never the host.

2. **A write to `@State`/`@Prop` must not happen synchronously inside `componentDidLoad()` — and this includes writes triggered by `onSlotchange`-style Stencil light-DOM slot-callback handlers, not just writes made directly in `componentDidLoad`'s own body.** Stencil's dev-mode instrumentation sets an internal bitflag (`2048` in the minified runtime, see `index-*.js`'s `rt(s,"componentDidLoad",...)` call site) immediately before invoking `componentDidLoad` and clears it immediately after the call returns — synchronously, before any microtask scheduled inside it runs. Deferring the actual state write via `void Promise.resolve().then(() => { this.hasTextContent = ...; })` reliably falls outside that window and avoids the `"...changed during componentDidLoad()..."` warning, without losing the "wait for the parent's full synchronous patch to settle" guarantee a microtask provides. But there is a **second, separate flag** (`1024` in the same runtime, for "changed during rendering") that fires if a slot-callback handler (like `onSlotchange={this.handleTextSlotChange}` in JSX) performs its write *synchronously* — Stencil's own non-shadow slot-relocation logic can invoke that handler synchronously as part of applying a render, for newly-mounted elements. Any handler wired this way needs the *same* microtask deferral as `componentDidLoad`, or you will see the "changed during rendering" variant instead. Both call sites must be fixed together — fixing only `componentDidLoad` and missing the slot-change handler (or vice versa) just swaps one dev-mode warning for the other while the underlying bug (and any visual symptom, like a hidden icon via `.is-empty { display: none }`) persists.

## Second Related Bug: `hasSlotContent`'s Element Check Fails in Stencil's `mock-doc` Test Environment

`hasSlotContent`'s original implementation checked `node.slot === ''` to detect an unnamed-slot element child. Stencil's `mock-doc` (the DOM implementation `newSpecPage` uses) does not implement the `.slot` **property** getter/setter — it only reflects the `slot` **attribute**. So `node.slot` reads `undefined` in every test, never `''`, even when no `slot` attribute is present — meaning the element branch of `hasSlotContent` silently always returned `false` in every unit test that exercised it, regardless of the real browser behavior. This had no prior real test coverage (per the AI-001 note above, "`hasSlotContent` had no prior real consumer"), so the gap was invisible until a test specifically exercised an icon-only default-slot scenario. Fix: check `!node.hasAttribute('slot')` instead of `node.slot === ''` — the attribute check is correct and stable in both real browsers and `mock-doc`.

Source: bds-table formatter-cache flash-bug session, 2026-07-27. See also `stencil-dev-server-stale-lazy-chunk.md` — a separate, unrelated staleness issue hit while investigating this same bug (a stale dev-server build artifact, not a code defect) that cost significant debugging time before being correctly ruled out.
