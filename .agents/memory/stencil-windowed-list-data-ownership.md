---
name: stencil-windowed-list-data-ownership
description: "A windowed Stencil list must own filtering, keyboard navigation, label lookup and the empty state on the data side — bds-list-menu's linear navigation and bds-select's item queries only ever see the mounted window."
---

# Windowed lists move filtering, keyboard navigation and label lookup to the data layer

**The rule.** Any component that mounts only a window of `bds-list-menu-item` elements owns four things itself: which entries match the query, where keyboard focus goes, what text a committed `value` displays, and whether the list is empty. `bds-list-menu` and `bds-select` are DOM-coupled by design and only ever see mounted elements, so neither can be trusted at a window edge or for an off-window value. `bds-search-bar`'s `items` prop is the reference implementation (items mode mounts only the window); slotted mode stays fully mounted and keeps the existing DOM paths.

**Why the child components cannot do it** (verified in source):

| Code | What it sees |
| --- | --- |
| `bds-list-menu` `childItems` (`querySelectorAll('bds-list-menu-item')`) and its `setLinearNavigation({ wrap: true })` | mounted, non-hidden, non-disabled items only — ArrowUp/ArrowDown cannot leave the window |
| `bds-select.handleArrowNavigation` → `bdsList.focusFromTriggerKey` | ArrowUp prefers the **last mounted** item, not the last entry of the data list |
| `bds-select` `searcherElement()` | `listenField()` returns at `bds-select.tsx:615` when `managed`, before the `searcherElement()` call — a managed select does no filtering at all |
| `bds-select.loadValue()` | returns early when no mounted option matches `value`, so the display label must come from the data array |
| `bds-list-menu.renderEmptyState()` | `empty \|\| childItems.length === 0`, evaluated only when the menu renders |

`bds-search-bar` already renders `<bds-select managed>` and already owns a DOM filter (`searchOwnData`), which is why items mode can extend that ownership instead of teaching the children about data.

**The `empty` state must be driven from data.** `bds-list-menu` re-renders only when its own props change; slot children arriving later do not re-evaluate `childItems`, so an empty label can linger beside real items. Set `empty={filtered.length === 0}` from the parent and hide the stale label with a rule scoped to windowed mode — `.bds-search-bar--items .bds-search-bar__list:not([empty]) .bds-list-menu__content > bds-typography { display: none; }` in `bds-search-bar.scss`.

**Filters match the item's text *or* its `value`, case-insensitively.** Both paths: `searchOwnData` compares `textContent` or the `value` attribute (`bds-search-bar.tsx:325-330`) and the items filter compares `label` or `value` (`:827-832`). Do not document either as value-only.

**`VirtualWindow` is the one shared wrapper.** `src/utils/dom/virtualWindow/` (exported through `utils/dom/index.ts`) wraps the TanStack `Virtualizer` lifecycle only — create/update/unmount, microtask-coalesced `onChange`, `getItems`/`getLeadingSize`/`getTrailingSize`/`measureElement`/`scrollToIndex` — with no Stencil imports. Both `bds-table` (rows) and `bds-search-bar` (suggestions) use it. Do not hand-roll a second `Virtualizer` wiring and do not revive `VirtualScrollController` (deleted in EOA-19597 T13).

**Checklist for composing a windowed list from data:**

- Render only `getItems()`; key each item by a stable value (`key={item.value}`).
- Spacers are real siblings inside the list, `aria-hidden`, height-only (`margin`/`padding`/`border: 0`) — never `position: absolute`, never `display: none` on the items themselves.
- Put the windowed items in one stable wrapper — see `stencil-windowed-list-keyed-diff-focus.md`.
- Each mounted item carries `aria-setsize` (filtered count) and `aria-posinset` (absolute index + 1); without them a screen reader announces only the window size.
- Announce the result count in a polite live region, including zero.
- Single-select, flat, fixed row height is the supported v1 shape; do not imply groups, multiselect or variable heights.

**Why positional `display:none` virtualization was rejected.** `VirtualScrollController` repositioned children that were already in the light DOM. Custom elements upgrade synchronously when connected, so all N items had already paid construction and first render before the controller ran; hiding and translating them reduced paint cost but never DOM count, and the design pinned a fixed 28 px estimate that overlaps as soon as an item wraps. Nothing inside that contract can reach true windowing, and combining `display: none` with per-item measurement is the `TanStack/virtual#823` bug class. The full analysis, the rejected alternatives and the before/after numbers live here — do not restate them:

- Bug report: `ai-work/qa/bug-reports/2026-07-06-bds-search-bar-bug-001.md` (Finding 1 cause, Finding 2 verdict, measurements).
- Spikes: `ai-work/research/2026-10-21-virtual-list-approach-a-positional.md`, `-b-shared-util.md`, `-c-component-owned.md`.
- Plan: `ai-work/plans/EOA-19597-bds-search-bar-virtual-suggestions.md`.

Related: `stencil-windowed-list-keyed-diff-focus.md`, `bds-select-managed-mode-field-ownership.md`, `safari-virtualized-row-transition-on-remount.md`.

**Source:** EOA-19597 (2026-10), reference implementation `bds-search-bar` items mode plus `utils/dom/virtualWindow/`.
