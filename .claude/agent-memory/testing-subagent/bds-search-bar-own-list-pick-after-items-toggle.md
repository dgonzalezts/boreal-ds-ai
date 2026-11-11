# bds-search-bar — pick that bubbles from a re-rendered items list (EOA-19598)

Branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG`. Fix under test (uncommitted at the time):
`handleSelectChange` accepts a `bdsChange` whose target is the `bds-select` host **or**
`this.itemsListEl` (`.bds-search-bar__list`), and calls `closePopover()` only for the own-list origin.

## Why the bug exists (mechanics worth knowing before writing such a test)

- `bds-select.assignListeners()` binds `bdsChange` on `this.bdsList` **once, in `componentDidLoad`**
  (`bds-select.tsx:397`), and `componentDidMount`-era binds are never refreshed.
- Toggling `items` (`array → undefined → array`) makes the search bar render a **brand-new**
  `bds-list-menu.bds-search-bar__list` element (the select's `<slot name="list">` vnode is replaced by a
  real `<bds-list-menu>`), so the select's listener stays on the detached old node.
- A pick from the new list therefore bubbles straight past the select to the search bar's
  `onBdsChange` listener **with `e.target` = the list, `e.currentTarget` = the `bds-select`**, which the
  pre-fix `e.target !== e.currentTarget` guard dropped silently.
- Proof in the spec: `expect(list).not.toBe(previous)` — the toggle must produce a different element, or
  the scenario is not the bug.
- The `items = undefined` step calls `closePopover()` once on its own (`closeSuggestionsWithoutList()`),
  so **clear the `closePopover` stub after the toggle** before asserting close counts.

## What the revert proof actually shows (do not assume)

Reverting the guard to HEAD (`git show HEAD:<file> > <file>`, then restore by hash) fails exactly:

- `Should commit a pick that bubbles from the items list re-rendered by the toggle`
- `Should neither commit nor emit again when the popover reports bdsClose after a pick` (only because the
  pick never commits)
- `Should commit an empty value when the items list reports a deselection with no detail`

It **passes** in both worlds for a slotted consumer list (`slot="list"`): the select *does* consume the
raw event and re-emit its own `bdsChange` (probe showed `target`/`currentTarget` both `BDS-SELECT`), which
the old guard already accepted. So "a consumer-list bubbled pick must not commit" is **not** true — it
commits once, through the select. A test for the consumer list is a lock against a future tag-based /
"any list" widening, not a bug reproduction. Same for the text-field echo (`onBdsChange={stopChildEventPropagation}`
stops it at the field).

## Partial reverts are a trap

Replacing only the two guard lines leaves `if (fromOwnList) void this.bdsPopover?.closePopover();` pointing
at an undefined identifier → the handler throws a `ReferenceError` after the guard, which looks like
"the select re-emit path stopped working" (0 `valueChange`) in the *unrelated* slotted tests. Always revert
the whole hunk to HEAD bytes and verify with `shasum -a 256` + `git diff --stat`.

## Non-vacuity check for the consumer-list lock

The replacement consumer list only proves the drop if the event really reaches the search bar. Confirmed by
temporarily setting `replacement.className = 'bds-search-bar__list'` — the same test then fails with
`Received: "medellin"`, i.e. `fromOwnList` matched and the handler ran. Keep `expect(select.contains(replacement)).toBe(true)`
in the spec as the standing evidence that the event's bubble path crosses the select.

## mock-doc gaps hit here

- `Element.replaceWith` does not exist → `parent.insertBefore(next, previous); previous.remove();`
- `document.activeElement` must be installed (`installFocusTracker()` defines it, `restore()` deletes it)
  for "focus lands in the input" assertions.

## File-path gotcha (cost a long detour)

`bds-search-bar` spec files are **`.ts`, not `.tsx`** (no JSX anywhere in them). A positional path with the
wrong extension prints `No tests found … Pattern: … - 0 matches` (Stencil exits 1) — and the `read`/`edit`
tools' fuzzy path resolution happily accepts the wrong extension, so edits silently apply to the real file
while `cat`/`cp`/`stat` in the shell fail with `ENOENT`. Always `ls` the exact filename first.
