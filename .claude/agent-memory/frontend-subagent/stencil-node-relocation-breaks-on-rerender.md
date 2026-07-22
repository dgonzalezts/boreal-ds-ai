---
name: stencil-node-relocation-breaks-on-rerender
description: "A ref-based pattern that discovers a light-DOM node via querySelector, then appendChild's it elsewhere, must cache the discovered node — re-querying the original location on a later render finds nothing, because appendChild moved it away"
metadata:
  type: project
---

Boreal DS components project light-DOM content into a non-shadow child (e.g. `bds-table` moving a `slot="footer"` child of `bds-table-column` into a `<tfoot>` `<td>` via a `ref` callback + `appendChild`, since `bds-table-column` is `display:none` and has no shadow root to natively project through).

**The bug:** if the "does this content exist" check (e.g. a `hasFooter` getter) re-derives its answer by querying the node's *original* parent (`col.children`) on every render, it breaks after the first successful move. `appendChild` removes a node from its previous parent as part of inserting it at the new location — so on the second render, `col.children` no longer contains it, the presence check flips to `false`, and Stencil's VDOM diff then **removes** the previously-rendered container (`<tfoot>` in this case) from the real DOM, taking the moved content with it. Any later render (row selection, sort, any unrelated `@State` change) permanently loses the projected content.

**Reproduced concretely:** in `bds-table.tsx` (EOA-15507 Task 3), a naive `footerNode(col)` that did `Array.from(col.children).find(...)` on every call passed all "first render" tests but failed a "content survives a later unrelated re-render" test — `<tfoot>` vanished after clicking a row checkbox. Confirmed by temporarily reverting the fix and watching the regression test fail, then restoring it.

**How to apply:** cache the discovered node by a stable key (e.g. `colKey`) the first time it's found, in a `private readonly _xNodes = new Map<string, Element>()` instance field. All later lookups check the cache first and only fall back to a fresh DOM query if the key isn't cached yet. The `ref` callback then re-appends the cached node every render (harmless — `appendChild` of an already-correctly-placed node is a no-op relocation), but the "does it exist" check stays `true` forever once discovered, independent of where the node currently lives in the DOM.

This applies to any future "move a user-supplied light-DOM node into a different rendered location" feature in this codebase, not just table footers — e.g. any new slot-like content projected out of a non-shadow child component.

See also [[stencil-mockdoc-no-scope-selector]], discovered in the same feature.
