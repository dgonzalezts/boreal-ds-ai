---
name: bds-search-bar-t30-t31-regression-mechanics
description: How to reproduce and pin the bds-search-bar empty-dropdown (T30) and blank-field-on-blur (T31) defects in newSpecPage, and why several of their guards pass both pre- and post-fix
metadata:
  type: project
---

Regression specs for EOA-19597 T30/T31 (2026-10-26). The mechanics below are not obvious from the
component source and decide whether a new test actually fails without the fix.

**Reproducing T30 (window never mounts on a post-mount `items` assignment).** It reproduces in
mock-doc, no browser needed:

```ts
const page = await newSpecPage({ components: SEARCH_BAR_COMPONENTS, template: () => h('bds-search-bar', {}) });
await flushMicrotasks();
await page.waitForChanges();
page.root.items = buildSuggestions(30);     // schedules a retry in the fixed code
await flushMicrotasks();
await page.waitForChanges();
await settleFrames(page);                   // real timers: rAF here is setTimeout(cb, 0)
```

Pre-fix result: `windowItems(root) === []`, spacers `['0px','0px']`, `.bds-list-menu__content`
exists but is never observed. Post-fix: 13 items, `['0px','476px']`. Do NOT assert the content
element exists as the pre-condition — it does exist by the time `waitForChanges()` resolves; the
mount already bailed earlier in the same render, which is the whole bug.

- `jest.spyOn(VirtualWindow.prototype, 'mount')` (import `@/utils/dom/virtualWindow`) counts one
  mount across the retry loop. Restore it in `finally`.
- Cancellation is only observable through internals: a retry that survives a dispose would call
  `mountVirtualWindow()` and bail because `virtualWindow` is `undefined`, so "no mount happened"
  cannot distinguish cancelled from bailed-out. Assert `instance.mountRetryFrame === null` and
  `instance.mountRetryFrames === 0` after clearing `items`, in addition to the no-mount assertions.

**Reproducing T31 (blank field after blur).** The blank only appears when the *select's own* `value`
is still `''` when `resetValueField()` runs — i.e. the commit has not been re-rendered into
`bds-select` yet. So the test must type with the debounce **pending**:

```ts
jest.useFakeTimers();
try {
  field.dispatchEvent(new CustomEvent('bdsInput', { detail: { value, event: new Event('input') } }));
} finally {
  jest.useRealTimers();          // the fake timer never fires, so the query stays pending
}
await page.waitForChanges();
input.dispatchEvent(new Event('blur'));
```

`typeQuery` (which advances the debounce) does NOT reproduce it: by blur time the search bar has
already re-rendered `value`, so `resetValueField()` takes its no-write branch. Consequence for
expectations: a *matching* value typed with a pending debounce (`item-3`) shows its label after
blur and passes pre-fix (the field text changes, so Stencil re-patches); free text (`Item 3x`) is
the failing case because the post-commit text equals the pre-blur text, so the blank write is never
overwritten.

**Simulating a real popover hide.** `stubPopover()` replaces `getVisibility`/`openPopover`/
`closePopover`, so nothing actually hides and `resetValueField()` is never reached. Drive both
halves in browser order — `hideElement()` emits `bdsClose` before `onAfterHide` runs:

```ts
popover.dispatchEvent(new CustomEvent('bdsClose'));
(popover as unknown as { floatingOptions: { onAfterHide: () => boolean } }).floatingOptions.onAfterHide();
```

`floatingOptions.onAfterShow()` is likewise how to make `bds-select.popoverVisible` true before an
Escape-from-item test (the select's Escape handler no-ops otherwise). Note Escape-from-item routes
through the popover-close path, which drops `typedText`, so that case shows the label, not the typed
text — matching T12, not "preserve the typed text".

**The repeated-cycles test must start with free text.** After a matching pick the select's `value`
is non-empty, so later free-text blurs do not hit the blank branch; putting free text first (and
again after a clear) is what makes the cycle test fail pre-fix.

**Running `tsc` with the component tsconfig.** `with-node.sh` resets cwd to the repo root, so
`npx tsc --noEmit -p tsconfig.json` silently type-checks the whole monorepo (~3,500 errors). Use an
absolute `-p /…/packages/boreal-web-components/tsconfig.json`, or
`pnpm --filter boreal-web-components exec tsc --noEmit -p tsconfig.json` (pnpm runs it in the
package). The clean baseline is 5 errors: 4 in `bds-tooltip-events.spec.ts`, 1 in
`bds-dialog.behavior.spec.ts`.

## T43 — commit-time `valueChange` (added 2026-10-26)

`applyQuery` (list mode) now emits `valueChange` only when the commit changes `value`
(`bds-search-bar.tsx:273-284`). Specs live in `bds-search-bar.events.spec.ts` →
`describe('valueChange emission on commit')`.

**Fake-timer clocks are per-`useFakeTimers()` call, so a scheduled debounce cannot be advanced
later.** `jest.useRealTimers()` uninstalls the clock and drops everything queued on it; the next
`jest.useFakeTimers()` is a *fresh* clock. Therefore:

- "the debounce fires" → dispatch `bdsInput` **and** `jest.advanceTimersByTime(500)` inside one
  fake-timer block (this is what the shared `typeQuery` helper does).
- "the query stays pending" → dispatch inside a block that only restores real timers (this is what
  the file-local `typePendingQuery` and the T31 tests rely on). The instance's `debounceTimer` stays
  non-null, which is exactly what `commitTypedQuery()`'s guard needs.
- "the cancelled timer must not fire a second event" → dispatch, `valueChange.mockClear()`, dispatch
  `blur` (which commits and cancels), **then** advance 500 inside the same block. Advancing after the
  blur is what makes a surviving timer observable.

**Prove the commit actually ran in a "must emit nothing" test.** An equality-guard test passes
trivially if the debounce never fires. Pair `expect(valueChange).not.toHaveBeenCalled()` with
`expect(status.textContent).toBe('1 result')` — `applyItemsQuery` only announces when the query
changed, so the live region is the side-effect proof that the commit executed.

**Slotted-mode mirrors need the popover stubbed.** Typing a non-empty value calls
`reopenSuggestions()`; with the real popover that reaches `openPopover()` → `IntersectionObserver is
not defined` and kills the whole Jest worker (not just the test). `stubPopoverMethod(popover,
'getVisibility', true)` short-circuits before `openPopover`.

**Pre-fix failure set (what makes these tests load-bearing).** Reverting the guard to a bare
`this.value = value;` fails exactly 6: the repeated-blur-cycles test plus the five positive
emission tests (debounce, blur-before-debounce, popover-close, erase-to-empty, slotted debounce). The
two "emit nothing" tests pass both ways by construction — they kill the *opposite* mutant (removing
the equality guard), not the missing-emit one.

