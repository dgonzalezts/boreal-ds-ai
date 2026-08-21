# Reducer-style `@State()` spread updates re-render even when nothing changed

Rebuilding a `@State()` field (or a mutable `@Prop()`) via the idiomatic immutable-update shape — `this.foo = { ...this.foo, x: y }`, or a plain reducer function `return { ...draft, x: y }` — always allocates a *new* object reference, so Stencil re-renders the component even when `y` happens to equal the existing value. The visible symptom (or lack of one) makes this easy to miss in normal QA: the rendered *output* looks identical before and after, so a screenshot- or DOM-assertion-based test suite passes cleanly while the component silently re-renders on every redundant interaction. It only surfaces as flicker, lost scroll/focus, wasted work in an expensive `render()`, or an animation restarting on a no-op click.

**Found in `bds-date-picker`'s original implementation, in two related but distinct forms:**

1. **State-shape bug** — `selectDay()` (a plain reducer-style utility in `utils/draft-state.ts`, not even a class method) unconditionally returned `{ ...draft, selectedDate: isoDate }`. Reselecting the *already-selected* day produced a brand-new `draft` reference and a redundant re-render, even though nothing observable changed.
2. **Idempotency bug** — `listenClickTrigger()` reset the draft (`this.draft = cloneDraftFromValue(this.value)`) and reopened the popover on *every* trigger click, including a second click while the popover was already open. This is not a reference-stability issue in the state shape itself — it's a handler that doesn't check whether it's already in the target state before repeating its full side-effecting action, which incidentally also caused the displayed calendar month to reset back to the committed value's month.

Both bugs were invisible to the existing test suite and to normal exploratory QA — the app "worked" in every obvious sense. They were only found by deliberately testing the *repeat-interaction* case (click the same trigger twice, reselect the same day) and confirming via a temporary `console.count('render')` inside `render()` that the second, no-op interaction still triggered a render.

**Fix pattern (state shape):** guard the update with an equality check, returning the *existing* reference when nothing logically changed:

```ts
// ❌ before
export function selectDay(draft: DatePickerDraftState, isoDate: string): DatePickerDraftState {
  return { ...draft, selectedDate: isoDate };
}

// ✅ after
export function selectDay(draft: DatePickerDraftState, isoDate: string): DatePickerDraftState {
  if (draft.selectedDate === isoDate) return draft;
  return { ...draft, selectedDate: isoDate };
}
```

**Fix pattern (idempotent handler):** guard the handler itself against redundant re-invocation of its full side-effecting action when already in the target state:

```ts
// ✅ after
private listenClickTrigger = () => {
  if (this.popoverVisible) return;
  this.draft = cloneDraftFromValue(this.value);
  this.bdsPopover?.showPopover();
};
```

`popoverVisible` is a `@State()` field wired via the popover's `onAfterShow`/`onAfterHide` floating-UI callbacks — not derived from any DOM query, so it stays correct even before the popover's own animation settles.

**Verification method — and a confirmed dead end:** a temporary `console.count('render')` statement inside `render()`, exercised via Playwright or manual repeat-clicking, is the only reliable way to confirm a render did or didn't happen (no DOM/screenshot difference exists to check instead). A prototype-monkey-patch approach — `customElements.get('bds-date-picker').prototype.render = wrapped` to count renders externally without touching the source — was tried and **does not work**: Stencil's compiled runtime does not dispatch through a dynamically-overridable prototype method, so the patched wrapper is silently never invoked. Don't spend time re-attempting this; use the inline `console.count()` and remove it before committing.

**Testing:** assert reference equality (`.toBe()`, not `.toEqual()`) on a no-op reducer call, and assert an idempotent handler's imperative side effect (e.g. a spied `showPopover()`) fires exactly once across two identical trigger events. See `bds-date-picker.events.spec.ts`'s "reselecting the same day keeps same draft reference" / "repeat click doesn't call `showPopover` again" tests.

**Tooling added as a result:** `code_quality_checker.py`'s new `unstable-state-reference` heuristic rule flags a self-referencing `{ ...x, ... }` spread (return-style or `this.x = ` assignment-style) with no preceding `if` guard referencing the same identifier in the ~12 preceding lines. It is regex-based and approximate (a nudge for human review, not a definitive verdict) — validated against a broad codebase sample at 4 findings across 232 files (`bds-checkbox-group.tsx`, `bds-table.tsx`, `bds-stepper.tsx` ×2), all genuine candidates for review, not false positives. Also added: `ai-docs/guidelines/code-review-checklist.md` § Universal "Performance" sub-items, `ai-docs/guidelines/stencil-best-practices.md` § "Reference-Stable State Updates", `frontend-subagent.md` Working Principle, `qa-subagent.md` § "Repeat-Interaction Testing (Idempotency)", `qa-test-planner` skill's new "Idempotency / Redundant-render" test type, and `testing-knowledge` skill's § "Testing Reference-Stable State Updates".

**Source**: EOA-16692 `bds-date-picker` v1 code review follow-up session.
