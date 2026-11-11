# bds-search-bar T48/T49/T50 regression mechanics (EOA-19597, 2026-10-26)

## T49 — the mock-doc `nextSibling` shim, and how to keep it honest

Transitioning a live `items` bar to `mode="search"` hangs `waitForChanges()` in `newSpecPage` because Stencil's
testing runtime reverses slot relocation with a `while (node = node.nextSibling)` walk, and mock-doc's getter
returns the parent's **first child** when the node is absent from `parentNode.childNodes` (Stencil keeps a
parallel `__childNodes`). The fix is a spec-local property shim on the prototype that owns the descriptor:

```ts
let owner: object | null = Object.getPrototypeOf(document.createElement('div'));
while (owner !== null && Object.getOwnPropertyDescriptor(owner, 'nextSibling') === undefined) {
  owner = Object.getPrototypeOf(owner);
}
const original = Object.getOwnPropertyDescriptor(owner, 'nextSibling')?.get;
Object.defineProperty(owner, 'nextSibling', {
  configurable: true,
  get(this: Node) {
    if (this.parentNode === null) return null;
    if ((this.parentNode.childNodes as unknown as Node[]).indexOf(this) === -1) return null;
    return original.call(this);
  },
});
```

Install per test, restore in `finally`. Nodes Stencil *did* patch (`patchNextSibling`) carry an own property, so
the prototype shim only changes the broken case.

**Prove the shim is load-bearing, with a bounded run.** Neuter the `indexOf === -1` guard (keep everything else)
and run only that test under the shell's `timeout`, e.g.
`timeout 180 .agents/scripts/with-node.sh pnpm --filter @pxglobal/boreal-web-components run test -- <spec> -t "<name>"`
→ exit **124**. Jest's own `--testTimeout` cannot help: the loop starves timers, so neither the timeout nor a
racing `setTimeout` ever fires. Never try it without a wall-clock wrapper.

## T48 — `value` assignment reconciliation

- **A pick is the only path where `value` and `itemsQuery` legitimately diverge**, so it is the only observable
  proof that `isInternalValueWrite` exists. Without the flag: pick → watcher reconciles → list collapses to the
  picked value.
- **`item-1` is a filter-coincidence trap.** Query `'item-1'` matches `item-1`, `item-10`…`item-19` = **11**
  results, which is exactly what a `'Item 1'` query also yields — a pick test keyed on `'item-1'` passes even
  with the flag removed. Use a value with no prefix siblings (`'item-5'` of 30) so filtered length is 1 vs 11.
- **"external value equals the current query" is unreachable by plain assignment** when `value` already equals
  it (Stencil skips an unchanged prop). The realistic setup is: type a query → pick (value diverges) → assign the
  query back. That is what makes the no-scroll-jerk assertion meaningful.
- Silent reconcile (`applyItemsQuery(next, false)`) keeps the live region at its previous text, so
  "does not announce" is asserted as *unchanged* status text (e.g. still `'11 results'` after the list is back to
  30), not as `''`.

### What each revert actually breaks

| Revert | Fails |
| --- | --- |
| watcher back to `if (typedText === next) return; typedText = null; hasValue = …` | `items › external value assignments › Should reset the items filter and the scroll without announcing…`; `events › Should filter the list to a programmatic value assigned after mount`; `events › Should emit nothing when the committed query equals the current value` (status flips back to `'1 result'`) |
| drop `|| this.isInternalValueWrite` from the watcher guard | `items › Should keep the scroll position when an assigned value matches the query already applied`; `items › Should keep the applied query when a suggestion pick commits a different value`; plus two pre-existing `events` pick tests |
| `aria-controls` back to unconditional `updateElementAttr(…, this.resolveListboxId())` | `a11y › Should set aria-autocomplete="list" and omit aria-controls when no list renders in mode="list"`; `a11y › Should never write an empty aria-controls on a bar that has no list, even after focusing the input`; `a11y › Should remove the aria-controls reference when the items list disappears` (the slotted→`mode="search"` removal passes either way — the `else` branch always existed) |

## Documented fixture limitation: `selected` on the item created *by* the assignment

When an external `value` is what narrows the list, the matching `bds-list-menu-item` is created in that same
render while `bds-select` (`managed`) has already found no mounted option, so the fresh item renders **without**
`selected` even though `value` matches. Assert window contents / `aria-setsize` / resolved label instead; a
`selected` assertion there is guaranteed to fail.
