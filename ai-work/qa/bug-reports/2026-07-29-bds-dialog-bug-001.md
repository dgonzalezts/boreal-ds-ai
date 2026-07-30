# BUG-001: `bds-dialog` closes when clicking anywhere inside its own content, not just the backdrop

**Severity:** High
**Priority:** P1
**Type:** Functional / Regression
**Status:** Open
**Component:** `bds-dialog` (`packages/boreal-web-components/src/components/.../bds-dialog/bds-dialog.tsx`)
**Discovered during:** `bds-table` v4 planning research (ticket `EOA-16000`), while scoping Task 13's filter-drawer/column-visibility-dropdown stories and auditing existing dialog usage
**Affects:** Every consumer of `bds-dialog` with `backdropClose` enabled and any interactive/clickable content inside the dialog — in this codebase, at minimum the `bds-table` stories `BulkEdit`, `BulkDeleteWithUndo`, and `WithAddRow`

---

## Environment

- **Component:** `bds-dialog` (`packages/boreal-web-components/src/components/.../bds-dialog/bds-dialog.tsx`)
- **Shared mixin:** `backdrop.mixin.ts` (`packages/boreal-web-components/src/.../mixins/backdrop.mixin.ts`)
- **Affected stories:** `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts` — `BulkEdit`, `BulkDeleteWithUndo`, `WithAddRow`
- **Introduced in:** commit `5c9fb4e4` (2026-07-06, `fix(web-components): EOA-14934 bds-dialog add showElement/hideElement native overrides`)
- **Last confirmed still broken:** at least through commit `0131d9ed` (2026-07-17)

---

## Description

`bds-dialog` renders `<dialog onClick={e => this.handleBackdropClick(e)}>`. Native `<dialog>` click events bubble to the `<dialog>` element itself regardless of where inside the dialog the click originated — clicking a button, a text field, or any other content inside the dialog fires the same `click` handler as clicking the true backdrop area outside the dialog's content box.

`handleBackdropClick`/`isBackdropClick` live in the shared `backdrop.mixin.ts`. The mixin's default `isBackdropClick` always returns `true`, and its own JSDoc documents that any native `<dialog>`-based component **must** override it with a target check (`e.target === this.dialogElement`) specifically because of this bubbling behavior. `bds-dialog.tsx` currently has no such override, so with `backdropClose` enabled, clicking anywhere inside the dialog's own content closes it.

Because keyboard interaction (Tab, Enter, native focus handling) doesn't route through this same click-bubbling path, the dialog is only reliably usable via keyboard — any mouse click on interior content risks closing it. This makes `bds-dialog` effectively unusable with a mouse whenever `backdropClose` is enabled and the dialog contains any clickable content, which is the common case (buttons, form fields, links).

---

## Steps to Reproduce

1. Open Storybook → Data Visualization → Table → `BulkEdit` story (or `BulkDeleteWithUndo` / `WithAddRow`)
2. Trigger the bulk-edit action so the `bds-dialog` opens (confirm `backdropClose` is enabled, which it is in this story)
3. Click anywhere inside the dialog's own content — e.g. the text field, a label, or empty padding area within the dialog box (not the page area outside it)
4. Observe: the dialog closes immediately, as if the backdrop (outside the dialog) had been clicked
5. Repeat using only keyboard navigation (Tab to focus a field, type, Tab to the submit button, Enter) — the dialog behaves correctly and does not close

---

## Expected Behavior

Per `backdrop.mixin.ts`'s own documented contract, only a genuine click on the backdrop (outside the dialog's own content box) should close the dialog when `backdropClose` is `true`. Clicking anywhere inside the dialog's rendered content must never close it.

---

## Actual Behavior

Any click that bubbles to the `<dialog>` element — which includes every click inside the dialog's own content, not just the true backdrop — is treated as a backdrop click and closes the dialog when `backdropClose` is `true`.

---

## Root Cause

Confirmed via `git show` on the introducing commit, not speculative:

- `bds-dialog.tsx` previously had exactly the required override:
  ```typescript
  private isBackdropClick(e: MouseEvent): boolean {
    return e.target === this.dialogElement;
  }
  ```
  present as of commit `094eb9f7`.
- It was deleted in the very next commit, `5c9fb4e4` (2026-07-06, "fix(web-components): EOA-14934 bds-dialog add showElement/hideElement native overrides"). That commit's diff shows a contiguous code block containing both `isBackdropClick` and an unrelated `handleIsOpenChange` watcher being moved/reordered together as part of adding the `showElement`/`hideElement` native overrides; only `handleIsOpenChange` was restored in its new position — `isBackdropClick` was dropped in the process.
- This has the shape of a copy-paste/reorder mistake, not an intentional design change. Nothing in that commit's diff or message touches keyboard handling, focus trapping, ESC-key behavior, or ARIA semantics — the focus-trap (`setFocusTrap(() => this.dialogElement)`) and `KeyboardController`-driven ESC handling are untouched and unrelated to the removed override.
- `dialogElement` itself is unchanged by that commit — still the same `HTMLDialogElement` ref used by `showElement`/`hideElement` — so the deleted override's `e.target === this.dialogElement` check remains valid today; nothing about the ref changed to invalidate it.
- The override was never reintroduced through at least commit `0131d9ed` (2026-07-17).
- **Cross-component comparison confirms this is `bds-dialog`-specific, not a shared-mixin defect:** `bds-drawer` also uses `backdrop.mixin.ts` and never needed its own override, because its backdrop-click handler is bound to a dedicated `<div class="bds-drawer__backdrop">` sibling element rather than the drawer's own content container — clicks inside the drawer body never reach that div, so the mixin's default (`always true`) is correct for `bds-drawer` by construction. `bds-dialog` binds the handler directly on `<dialog onClick={...}>`, where all content clicks bubble to the same element — exactly the case the mixin's own JSDoc calls out as requiring an override.

No related plan, memory, or PR-description rationale was found anywhere in `.agents/memory/` or `ai-work/plans/` — the commit message only describes adding `showElement`/`hideElement`, with no mention of backdrop-click behavior at all.

**Assessment: accidental regression, not a deliberate tradeoff.**

---

## Suggested Fix

Reinstate the override in `bds-dialog.tsx`:

```typescript
private isBackdropClick(e: MouseEvent): boolean {
  return e.target === this.dialogElement;
}
```

No other changes should be needed — `dialogElement`, `handleBackdropClick`, and the mixin's calling contract are all unchanged since the override was removed.

---

## Regression-Test Plan

Add to `bds-dialog`'s spec suite (e.g. `bds-dialog.spec.ts`, alongside existing backdrop/`backdropClose` tests if any exist — check first per this repo's utility-reuse convention):

- Given `backdropClose={true}` and the dialog open, when a click event's `target` is an element inside the dialog's content (not the `<dialog>` element itself), then `isBackdropClick`/`handleBackdropClick` does not close the dialog.
- Given `backdropClose={true}` and the dialog open, when a click event's `target` is the `<dialog>` element itself (the true backdrop area), then the dialog closes.
- Given `backdropClose={false}`, neither case closes the dialog (existing behavior, regression guard).
- Add this as an explicit mutation-testing target if `bds-dialog` is ever included in a future Stryker config, since an `undefined-check`-style mutant on `e.target === this.dialogElement` would be trivial to introduce silently again without a passing/failing test pinned to this exact behavior.

---

## Related

- Discovered while researching `ai-work/plans/EOA-16000-bds-table-v4.md` Task 13 (opt-in filter/column-visibility toolbar props) — that plan's filter-drawer story uses `bds-drawer` (unaffected) rather than `bds-dialog`, but existing `bds-table` stories (`BulkEdit`, `BulkDeleteWithUndo`, `WithAddRow`) already use `bds-dialog` and are affected by this bug today, independent of `EOA-16000`.
- Introducing commit: `5c9fb4e4` ("fix(web-components): EOA-14934 bds-dialog add showElement/hideElement native overrides"), 2026-07-06.
- Shared mixin: `backdrop.mixin.ts`.
- Unaffected sibling component for comparison: `bds-drawer` (dedicated backdrop `<div>`, not bound to content container).
