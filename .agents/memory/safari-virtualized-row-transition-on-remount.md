# Safari can spuriously animate a freshly-remounted virtualized row's CSS transition

Windowing/virtualization libraries (TanStack Virtual, used by `bds-table`'s `virtual` mode) fully **unmount** rows once they scroll outside the overscan range, and mount a **brand-new** DOM node — not a recycled one — when the same row scrolls back into view. This is true even with correct identity-based VDOM keying (`key={rowId}`, not `key={virtualIndex}`): Stencil only reuses a DOM node across renders where the keyed element still exists in both the previous and next VDOM tree, and a scrolled-out row is absent from the previous tree entirely.

Safari has a WebKit-specific quirk where a freshly-inserted element that already has an attribute-driven CSS transform applied at creation time (e.g. `[aria-expanded='true']` triggering `transform: rotate(180deg)` on a chevron icon) can spuriously animate through its own `transition` on the very first paint, as if the value had changed on an existing element — even though, per spec, a transition should only fire across two already-committed style states, never on initial insertion. Chrome/Firefox do not exhibit this.

Symptom observed on `bds-table`'s virtual-mode row-expand chevron: expanding a row near the bottom, scrolling it out of view, then scrolling back in caused the chevron rotation to look laggy/desynced for a few interactions before "catching up" — while the actual expand/collapse content visibility (which is intentionally instant in virtual mode, gated by `effectiveVirtual` in `toggleExpand()`) was never affected. The underlying `expandedRowIds` state was provably correct throughout; this was a pure paint-timing artifact, not a logic bug.

**`will-change: transform` alone does not reliably fix this.** It was tried first and only partially/inconsistently reduced the symptom.

**Fix that worked**: explicitly set `transition: none` (and `will-change: auto`, since there's no longer an animation to accelerate) on the affected element, scoped only to virtualized rows via a CSS selector keyed off an existing virtual-mode-only DOM signal (`tr[data-index] .bds-table__td-expand-icon`, since `data-index` is only rendered on `<tr>` when a `virtualIndex` is passed). This also happens to make the component more internally consistent — virtual mode's row content already shows/hides instantly by design; the icon rotation is now instant too, everywhere, in every browser (not just Safari — disabling an already-unwanted transition is harmless in browsers that never had the bug).

**Takeaway for any future windowed/virtualized content**: default `transition: none` on elements inside virtualized rows unless smooth animation there is a deliberate requirement, rather than trusting `will-change` to mask a remount-timing quirk.

**Source**: EOA-16000 `bds-table` v4 Safari QA session (Task 2 virtual-mode expand/collapse).
