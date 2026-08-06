# BUG-001: Remaining `[BorealDS Button] No accessible name found` sources — numbered pagination buttons and dialog/drawer close button

**Severity:** Low
**Priority:** P3
**Type:** Accessibility
**Status:** Open
**Component:** `bds-pagination` (numbered page buttons), `bds-dialog`/`bds-drawer` (close button) — exact close-button owner not yet isolated
**Discovered during:** Live QA verification of `bds-table` Storybook docs maintainability refactor (2026-08-06), while chasing down `[BorealDS Button] No accessible name found` console noise
**Affects:** Any consumer rendering more than one page of `bds-pagination` (numbered page buttons appear), and any consumer of `bds-dialog`/`bds-drawer` with `closable` (the built-in close button)

---

## Background

This session already fixed three confirmed instances of the same root bug — `bds-button`'s `checkAccessibleName` (`bds-button.tsx`) only recognizes the `label` **prop**, visible default-slot text, or `aria-label`/`aria-labelledby` on the icon slot's child; an `aria-label` attribute set directly on the `<bds-button>` host satisfies none of these:

1. `apps/boreal-docs/.../bds-table.stories.ts` — `WithActionsColumn`'s dynamically-created action buttons (fixed, `aria-label` → `label`).
2. `bds-table.tsx` — internal Filter/Column-visibility toolbar buttons (fixed, `aria-label` → `label`, `bds-table.toolbar.spec.ts` updated, 14 assertions).
3. `bds-pagination.tsx` — first/previous/next/last nav buttons (fixed, `aria-label` → `label` + added missing `slot="icon"`/`aria-hidden`, 3 spec files updated, 22 assertions).

Live QA (on `WithFilterDrawer`/`WithServerSideMode`) confirmed fix #3 resolved the 4 nav-button warnings, but found 2 more still firing — same underlying pattern, different call sites, deliberately left **out of scope** for this session per user decision (2026-08-06) to stop expanding this a11y sweep and return to the originally-scoped Storybook stories maintainability plan.

---

## Finding 1 — `bds-pagination`'s numbered page buttons

**Location:** `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx`, the full-pages variant (~line 386, `aria-label={`Go to page ${page}`}`) and the small-pages variant (~line 404, same pattern).

**Symptom:** unlike the icon-only nav buttons, these buttons DO render visible text (the page number, e.g. `{page}`) in what looks like the default slot — by a naive reading of `bds-button.tsx`'s `checkAccessibleName`, `hasDefaultSlotContent` should already be `true` here and the warning shouldn't fire. Live QA (JS property/console inspection in a running browser) contradicts that: the warning **does** fire for these buttons.

**Known gap:** the exact mechanism wasn't diagnosed in this session — worth checking whether `bds-button`'s `checkTextWrapperContent()` (which looks for a `.bds-button__content-text` wrapper element and calls a `hasSlotContent()` utility) requires something more specific than a bare JSX text child to recognize slotted content, especially given `bds-button` has no `shadow: true` (Light DOM) — native `<slot>` projection semantics don't apply the same way outside a shadow root, so Boreal's own slot-emulation mechanism (wherever that lives) may not be picking up this particular child correctly. This needs source-level investigation before a fix is written, not just the `aria-label` → `label` swap used for the icon-only cases (since these buttons' whole point is to show the page number as visible text, not to rely on a screen-reader-only `label`).

**Fix note:** the `aria-label={\`Go to page ${page}\`}` itself is a reasonable *enhancement* (richer screen-reader text than the bare number) and shouldn't simply be deleted — the real bug is that the visible `{page}` text isn't being recognized as satisfying the accessible-name check on its own, which is a `bds-button` (or its slot-detection utility) issue, not purely a `bds-pagination` one.

## Finding 2 — dialog/drawer close button

**Location:** not yet isolated to a specific file — observed via console noise on `WithFilterDrawer` (which opens a `bds-drawer`) as a native `aria-label="close"` wrapper around an unlabeled inner `bds-button`. Needs a source-level check of `bds-dialog`'s and/or `bds-drawer`'s `closable` close-button rendering (likely both, if they share a pattern) for the same host-level `aria-label` anti-pattern already fixed elsewhere.

**Fix note:** likely the same mechanical fix as the confirmed cases (`aria-label` → `label` on the `<bds-button>`, plus `slot="icon"`/`aria-hidden` on its icon child if missing) — but confirm by reading the actual render code first, same as the three already-fixed cases, rather than assuming.

---

## Recommended Next Steps

1. Read `bds-button.tsx`'s `checkTextWrapperContent()`/`hasSlotContent()` mechanism to understand why visible page-number text doesn't satisfy the check — this may reveal a fourth, more fundamental bug in `bds-button` itself (or its Light-DOM slot utility) rather than two more one-off consumer fixes.
2. Grep the whole component library for the same `aria-label="..."` (as a literal JSX attribute, not a real prop) pattern on `<bds-button>` elements — the three fixes this session were each found reactively (one led to discovering the next); a proactive full-library grep would likely surface all remaining instances in one pass rather than one console-warning at a time.
3. Scope test impact before fixing (each of the three prior fixes needed test updates in 1–3 spec files; expect the same here).
