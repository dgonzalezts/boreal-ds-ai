---
ticket: —
status: concluded
---

# Research Spike: Shared Virtualization Utility for `bds-table` + `bds-search-bar`

**Date:** 2026-07-06

---

## Goal

`bds-table`'s row virtualization (`EOA-14935`, Task 22) is about to be built directly against `@tanstack/virtual-core`. Separately, `bds-search-bar`'s suggestion list uses `VirtualScrollController`, which only repositions/hides pre-existing DOM children rather than reducing DOM node count (tracked as `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md`). Given both ultimately sit on the same underlying library, is it worth building ONE shared, reusable virtualization utility both components could use — now or as a near-term follow-up — rather than `bds-table` building its own bespoke integration?

This spike explores the API design for such a utility (informed by `bds-table`'s already-planned shape and Vaadin's real-world precedent) and the migration/versioning strategy `bds-search-bar` would need if it ever adopted a windowed-creation model.

---

## Options Evaluated

- **A — Generalize `VirtualScrollController` as-is** to also serve `bds-table`.
- **B — One symmetric shared class** exposing both a read-only "just tell me `getVirtualItems()`" surface (what `bds-table` needs) and a `createElements`/`updateElement` pool-management surface (what a windowed `bds-search-bar` would need).
- **C — Two-layer split:** a small shared low-level factory wrapping `@tanstack/virtual-core`'s `Virtualizer` instantiation/options plumbing, with two thin, consumer-specific adapters built on top of it. **Revised during follow-up review (2026-07-06):** the second adapter doesn't have to be an imperative recycled-pool model — see "JSX-rendering clarification" below.

---

## Findings

### Option A is ruled out (prior research, already documented)

`VirtualScrollController` manages DOM children a consumer already placed (`MutationObserver` + `querySelectorAll`) — it has no role to play once nodes are produced by a declarative render function (`bds-table`'s `renderBody()`) instead of consumer-authored markup. This was already established via three-agent research cited in `/Users/dgonzalez/.claude/plans/let-s-continue-improving-the-calm-balloon.md` and is not re-litigated here.

### Option B is ruled out — reverse-engineered from `bds-table`'s actual planned shape

`bds-table`'s Task 22 (`ai-work/plans/EOA-14935-bds-table-v2.md`, lines 663–701) already specifies its exact integration: a private `@State() virtualizer: Virtualizer<Element, Element>` instantiated once in `componentDidLoad`, read via `getVirtualItems()`/`getTotalSize()` inside `renderBody()`, which then `.map()`s directly into JSX `<tr>` elements — Stencil's own vdom diffing handles all element creation/destruction. There is no "attach to a host and manage its children" step at all.

A future windowed `bds-search-bar`, by contrast, has no vdom diffing to lean on **today** — because its list items are consumer-authored light-DOM markup, not Stencil-rendered JSX. This led the original pass of this research to assume it would need imperative element creation/recycling, matching Vaadin's `createElements`/`updateElement` shape (confirmed by reading `@vaadin/component-base/src/virtualizer.js`, `vaadin-virtual-list-mixin.js`, `vaadin-grid-mixin.js` directly — a hand-rolled class, no TanStack dependency, wrapping an internal `IronListAdapter` recycled-element-pool engine).

**JSX-rendering clarification (added after follow-up review):** that assumption doesn't hold once `bds-search-bar` stops delegating list markup to the consumer at all. If `bds-search-bar` instead takes a data-array prop (see "opt-in `items` prop" below) and renders its **own** `<bds-list-menu-item>` children via its **own** Stencil JSX (`{visibleItems.map(item => <bds-list-menu-item value={item.value}>{item.label}</bds-list-menu-item>)}`) rather than relying on a consumer-populated `slot="list"`, then Stencil's own vdom diffing creates/destroys those elements automatically — the identical mechanism `bds-table` uses for `<tr>` rows. In that version, `bds-search-bar` would not need the imperative Vaadin-style pool at all; it would use the exact same "`.map()` over `getVirtualItems()`, indexing into a data array" recipe as `bds-table`, and could consume the shared `createBdsVirtualizer()` factory identically, not via a second bespoke adapter.

**What does NOT change regardless of which rendering mechanism is chosen:** `bds-table`'s `<tr>` rows live directly in its own render tree, with nothing mediating them. `bds-search-bar`'s items still have to pass through `<bds-select>`'s slot boundary and `<bds-list-menu>`'s own internal keyboard/focus logic (roving tabindex via `querySelectorAll`, assuming every item is a currently-existing real DOM node). That logic still needs a redesign to handle "the item the user just arrow-keyed to isn't rendered yet" — this accessibility problem is orthogonal to whether JSX-diffing or an imperative pool is used to create the elements, and remains `bds-search-bar`/`bds-list-menu`-specific either way (see point 5, unchanged).

Forcing one class to expose both a read-only surface AND a bespoke pool-management surface (the original Option B) would still be wrong — but that's no longer strictly necessary for `bds-search-bar` if it adopts JSX-rendering. The dead-weight risk from Option B (`bds-table` forced to implement a `createElements`/`updateElement` contract it never uses — precisely the pattern already flagged in Task 22's own citation of Aqua DS's `aq-table-core.tsx`, which declares an unused `virtualizer` state field) only applies if `bds-search-bar` genuinely needs the imperative pool model, which is now an open question rather than a given (see Open Questions).

### Option C — what's genuinely shareable, quantified

Only the raw `Virtualizer` instantiation/options plumbing is consumer-agnostic today — the exact code already living in `VirtualScrollController.setupVirtualizer()` (`virtual-scroll.ts:130-147`): wiring `observeElementRect`/`observeElementOffset`/`elementScroll`, calling `_willUpdate()`/`_didMount()`. This is roughly 20-30 lines, extractable into a `createBdsVirtualizer(config)` factory returning a handle (`getVirtualItems()`, `getTotalSize()`, `measure()`, `scrollToIndex()`, `setCount()`, `destroy()`) — a near-1:1 lift, not new design.

Above that layer, the two consumers' divergence depends on which rendering mechanism `bds-search-bar` picks:
- `bds-table`'s adapter is barely more than a naming convenience over the factory — `componentDidLoad` calls `createBdsVirtualizer(...)`, `renderBody()` maps `getVirtualItems()` back into `sortedData[vi.index]` for JSX. Task 22 could adopt this later as a near-free refactor of its already-planned call sites (`componentDidLoad`/`renderBody()` only — `sortedData`, per-row JSX, and the acceptance-criteria contract are untouched).
- **If `bds-search-bar` adopts JSX-rendering** (per the clarification above — rendering its own `<bds-list-menu-item>` children via its own JSX from a data-array prop), its adapter would be essentially identical in shape to `bds-table`'s: same factory call, same `.map()`-over-`getVirtualItems()` pattern, no pool/`createElement`/`updateElement` machinery needed at all. This is the simpler and more consistent path, and worth defaulting to unless a concrete reason emerges to prefer the imperative pool.
- **If `bds-search-bar` instead needs the imperative pool model** (e.g. to avoid Stencil's render/diff overhead at very large scale, or some other constraint not yet identified), its adapter (`createRecycledPoolVirtualizer`) needs real pool logic: grow a pool via `createElement()`, rewrite content via `updateElement(el, index)` per Vaadin's model, position via `transform: translateY()`, attach/detach from the host. This is new implementation, not an extraction — and should only be chosen if the simpler JSX path is confirmed insufficient.

### `bds-search-bar` migration scope, if ever pursued

- **Blast radius is smaller than initially assumed.** `bds-select.tsx` has no virtualization at all and operates directly on consumer-authored `bds-list-menu-item` children — `VirtualScrollController` is instantiated only inside `bds-search-bar.tsx`. A windowed-creation rearchitecture scoped to `bds-search-bar`'s internals would not require any change to `bds-select.tsx`, `bds-list-menu.tsx`, or `bds-pagination.tsx` (which also slots a `bds-list-menu` for its page-size dropdown) — all three are unaffected as long as `bds-search-bar` continues to hand `bds-select` a `slot="list"` element, just one it generates internally instead of one the consumer authored.
- **True coexistence with the current API is not possible** — both a consumer-authored slot and an internally-recycled pool would need to own the same DOM subtree. The realistic non-breaking path is a new, mutually-exclusive opt-in prop (e.g. `items`/`options`), gated similarly to the existing `mode` prop pattern already used in this component; when absent, today's slot + `VirtualScrollController` path is untouched.
- **Versioning:** the package is pre-1.0 (`0.1.0-alpha.8`), uses `release-it` + conventional commits with no prior deprecation precedent found (no `CHANGELOG.md` exists yet). Recommended path: ship the new prop as a `feat` commit coexisting with the slot path, deprecate the slot in JSDoc/Storybook docs, remove only via an explicit `BREAKING CHANGE:` footer commit.
- **Framework wrappers:** no `vue-output-target.ts`/`react-output-target.ts` changes needed unless the new prop needs its own two-way `v-model` binding (unlikely for a one-way data prop) — Stencil's auto-generated proxies pick up new `@Prop()`s automatically.
- **Accessibility is the real unresolved risk, not versioning.** `bds-list-menu`'s roving-tabindex focus strategy, `bds-select`'s type-ahead, and `bds-search-bar`'s `aria-controls`/`aria-autocomplete="list"` wiring all assume the currently-relevant item is a real, `querySelector`-able DOM node at the moment of interaction. No synthetic/virtual-focus infrastructure (e.g. `aria-activedescendant`-based) exists anywhere in this codebase today — this would be genuinely new implementation and test surface, not a refactor of existing logic.

---

## Recommendation

1. **Do not build anything now.** This remains deferred, consistent with the earlier decision — `bds-table`'s Task 22 ships exactly as planned, using `Virtualizer<Element, Element>` directly with zero dependency on any shared utility.
2. **The `createBdsVirtualizer()` factory (Option C's shared layer) is a reasonable, low-risk future extraction** — it's an ~20-30 line lift of code that already exists in `VirtualScrollController`, not new design. It could be built once Task 22 ships, as an optional refactor target, without forcing `bds-table` to adopt it immediately or coupling its delivery to `bds-search-bar`'s migration.
3. **`bds-search-bar`'s windowed-creation rearchitecture is a separate, larger future ticket**, not bundled with the factory extraction above. Its real cost center is the accessibility redesign (synthetic focus/`aria-activedescendant` model), not the virtualization plumbing itself — that ticket should budget for a dedicated a11y design pass before any implementation, and should explicitly confirm the reduced blast radius (scoped to `bds-search-bar` only, `bds-select`/`bds-list-menu`/`bds-pagination` unaffected).
4. **Default to JSX-rendering, not the imperative pool, if/when that ticket happens.** Per the clarification above, rendering `<bds-list-menu-item>` via `bds-search-bar`'s own JSX (from a data-array prop) lets it share the exact same integration pattern as `bds-table`, not a separate bespoke adapter — simpler to build and more consistent with the rest of this codebase's JSX-first component style. Only fall back to the imperative pool model if JSX-rendering is later found insufficient for a concrete reason (not yet identified).

---

## Open Questions

- Should the `createBdsVirtualizer()` factory extraction be scheduled as a concrete follow-up ticket now, or left purely opportunistic (done only if/when someone touches this code again)?
- What overscan/`estimateSize` defaults should the factory ship with, and should they differ per consumer or be caller-supplied in all cases (current lean: caller-supplied, matching both `VirtualScrollController`'s and Task 22's existing per-consumer values)?
- Who owns designing the `aria-activedescendant`/synthetic-focus model for a windowed `bds-list-menu`-family component, given no prior art exists in this codebase? This is the actual blocking unknown for `bds-search-bar`'s migration, not the virtualization mechanism.
- Is there any real, current product consumer of `bds-search-bar`/`bds-select` passing list sizes large enough to justify prioritizing this migration soon, or does it stay backlog until one appears (per the open gap already noted in the bug report)?
- Is there a concrete reason `bds-search-bar` would need the imperative pool model instead of JSX-rendering (e.g. a measured performance ceiling where Stencil's render/diff cost itself becomes the bottleneck at extreme scale)? Not yet identified — until one surfaces, JSX-rendering should be the default assumption for any future implementation.
