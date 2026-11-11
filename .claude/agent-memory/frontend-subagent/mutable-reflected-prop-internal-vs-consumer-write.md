# A mutable reflected prop cannot tell a consumer write from its own (EOA-19597 T48)

`bds-search-bar` keeps its `items`-mode filter in `@State() itemsQuery`, which only its own clear paths reset. A
consumer doing `el.value = ''` therefore cleared the field but left the old filter applied (19 matches, no clear
button). The fix has to know **who** wrote the value: three internal writes (debounced query commit, suggestion pick,
clear) must *not* reconcile the filter, everything else must.

Pattern used — a non-reactive boolean flag around the internal writes, not a value comparison:

```ts
private isInternalValueWrite = false;

private commitValue(next: string): void {
  this.isInternalValueWrite = true;
  try { this.value = next; } finally { this.isInternalValueWrite = false; }
}
```

and in the `@Watch('value')` handler, *after* the existing `typedText === next` guard (which identifies the debounced
commit of what the user is typing):

```ts
const isTypedCommit = this.typedText !== null && this.typedText === next;
if (isTypedCommit || this.isInternalValueWrite || !this.isItemsMode) return;
this.applyItemsQuery(next, false);
```

Notes worth keeping:

- Stencil `@Watch` handlers run **synchronously** inside the property write, so a `try/finally` flag is sound. Verify
  with a probe: a pick (`handleSelectChange`) must leave `itemsQuery` untouched.
- Reconcile **silently**. The live region announces user-driven result counts; a programmatic assignment is not a
  query, so announcing it would spam screen readers (and would re-announce identical counts on state restores).
  Consequence to accept and document: if a consumer pre-filters via `value` and the user then types the *same* string,
  `applyItemsQuery` sees no change and the count is not announced.
- Only reconcile when the query actually changes (`applyItemsQuery` early-returns otherwise) — that keeps a no-op
  assignment from resetting the scroll position, and still resets it (plus `scrollToIndex(0)`) on a real change.
- Guards confirmed quiet on this path: `warnItemsPrecedence`/`warnDuplicateItemValues` only hang off the `items`/`mode`
  watchers; the popover `bdsClose` listener, `isSelecting` and `itemsNavigation.recoverFocus` are untouched (probe:
  0 `openPopover`/`closePopover` calls, focus unchanged, 0 warnings).
- Spec fallout to expect: any spec that used an external `value` assignment as setup now gets an *already filtered*
  list (e.g. "value resolves, then scroll to it" becomes "it is the only mounted item", `aria-setsize="1"`), and a
  suggestion created **by** the value-change update reads `selected === false` in `newSpecPage` (the same item patched
  later, or created by a scroll update, reads `true`) — assert on the window contents / `aria-setsize`, not on
  `selected`.
