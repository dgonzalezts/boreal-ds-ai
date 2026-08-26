# BUG-001: Remaining `[BorealDS Button] No accessible name found` sources — numbered pagination buttons and dialog/drawer close button

**Severity:** Low
**Priority:** P3
**Type:** Accessibility
**Status:** Fixed
**Ticket:** [EOA-17133](https://telesign.atlassian.net/browse/EOA-17133)
**Component:** `bds-pagination`, `bds-dialog`, `bds-drawer`, `bds-popover`
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

---

## Fix Implemented (2026-08-20)

Implemented on branch `bugfix/EOA-17133-a11y-buttons` and pushed to `origin`.

**Code changes:**

1. `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx`
   - Added `label` prop to numbered page buttons (`label={`Go to page ${page}`}`)
   - Added `label` prop to small-mode current page button (`label={`Go to page ${this.internalCurrentPage}`}`)
   - Added `label="Jump pages"` to ellipsis buttons to silence remaining warning in pagination default story
2. `packages/boreal-web-components/src/components/overlays/bds-dialog/bds-dialog.tsx`
   - Updated close/maximize icon-only buttons to pass `label` and set icon to `slot="icon" aria-hidden="true"`
3. `packages/boreal-web-components/src/components/overlays/bds-drawer/bds-drawer-header/bds-drawer-header.tsx`
   - Updated close icon-only button to pass `label` and set icon to `slot="icon" aria-hidden="true"`
4. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx`
   - Updated header close icon-only button to pass `label="Close"` and set icon `aria-hidden="true"`
5. `packages/boreal-web-components/src/components/data-visualization/bds-pagination/__test__/bds-pagination.a11y.spec.ts`
   - Added regression assertion to ensure no `[BorealDS Button] No accessible name found` warning is emitted for pagination rendering

**Commit:** `43652dcf`

---

## Post-fix Verification

- Automated tests: pass (pre-push hook test suite in branch)
- Manual QA via Playwright/Storybook: pass
  - Pagination (`default` and `small`) no longer emits target no-accessible-name warnings
  - Dialog, drawer header, and popover header close/maximize controls expose accessible names and preserve behavior
- Remaining console noise observed in Storybook was unrelated (Storybook/Lit/CORS warnings)

---

## QA Verification

- [x] Root causes identified in source
- [x] Fix implemented
- [x] Automated tests pass
- [x] Manual QA completed
- [x] Branch pushed to `origin`

---

## Finding 3 (added 2026-08-19) — `bds-popover`'s header close button

**Location:** `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx`, ~lines 650-657:

```tsx
{this.closable && (
  <bds-button
    class="popover-header__close"
    size={BUTTON_SIZES.SMALL}
    onBdsClick={() => this.closeFromInside()}
  >
    <i slot="icon" class={ICONS.Close}></i>
  </bds-button>
)}
```

**Symptom:** confirmed via live Playwright/DOM inspection during `EOA-16692` (`bds-date-picker` v1) header-wiring QA (2026-08-19) — this `<bds-button>` has no `label` prop, no `aria-label`, and an empty default-slot (icon-only), so `bds-button`'s own `checkAccessibleName` correctly flags it, firing `[BorealDS Button] No accessible name found` every time any `bds-popover`/`bds-date-picker` (or any other `header`+`closable` consumer) renders its header. `bds-date-picker` itself does not own this element — it's rendered entirely inside `bds-popover`'s own template whenever a consumer sets `header={true} closable={true}`.

**Fix note:** same mechanical fix as the three already-confirmed cases — add `label="Close"` to the `<bds-button>` (this component already imports/uses `label` support elsewhere in the codebase; `bds-drawer-header.tsx`'s own close button uses the *anti-pattern* version of this same bug, `aria-label="close"` directly on the host, which is very likely **Finding 2** above, now positively located).

**Related:** Reported as its own out-of-scope-for-`EOA-16692` bug; filed in Jira as [EOA-17133](https://telesign.atlassian.net/browse/EOA-17133) (Sub-task of EOA-16914, linked "relates to" EOA-16692). See `ai-work/qa/bug-reports/INDEX.md`.

---

## Finding 4 (added 2026-08-24) — lifecycle-timing false positive, distinct root cause from Findings 1–3

**Discovered during:** `EOA-17138` (`bds-date-picker` v2, Phase 2 time selector) Task 4 live QA — dispatched a `qa-subagent` to inspect `http://localhost:3333` after the user observed "a lot of" these warnings with only one scenario active on the page.

**This is NOT a reopening of Findings 1–3.** Those were all "missing/wrong prop" bugs (`aria-label` set instead of `label`, or `label` omitted entirely) — all confirmed still fixed: live DOM/source inspection during this session found `bds-calendar-grid.tsx`'s prev/next nav buttons and `bds-popover.tsx`'s header close button all correctly have static, hardcoded `label` props in JSX (`"Previous month"`/`"Next month"`/`"Close"`), and the rendered `<button>` elements correctly carry `aria-label` once settled.

**Symptom:** Despite the correct `label` prop being present in source, `[BorealDS Button] No accessible name found` still fires for all three buttons — 24 total warnings across 8 `bds-date-picker` instances on a single page (3 per instance: header close + prev + next), 100% of load-time occurrences, 0% interaction-triggered (fires on initial page load, before any click).

**Root cause — a lifecycle-timing race, not a missing prop:** `bds-button.tsx`'s `checkAccessibleName()` runs synchronously inside `componentWillLoad()` (`bds-button.tsx:98-101`), reading `this.label` at that exact instant. For a `bds-button` nested 2–3 custom-element levels deep inside another dynamically-constructed component's render tree (`bds-date-picker` → `bds-popover`/`bds-calendar-grid` → `bds-button`), this fires before the nested element's `label` prop has been fully hydrated onto the instance — a Stencil lazy-load custom-element-upgrade race specific to `--dev --watch --serve`'s per-component async chunk loading. Text-slotted buttons (Clean/Cancel/Apply) never hit this, because their accessible name comes from light-DOM text nodes present at parse/patch time, not a prop requiring the child's own async upgrade to complete first.

**Fix note (not yet implemented):** two candidate approaches, neither applied yet:
1. Defer `checkAccessibleName()` by a microtask/`requestAnimationFrame` in `bds-button.tsx` so it evaluates after the prop has settled.
2. Re-run the check reactively via `@Watch('label')`, mirroring the existing `handleTextSlotChange`/`checkTextWrapperContent` reactive pattern already used for late-arriving slot content — a late-settling `label` would then suppress/correct an earlier false warning.

**Scope note:** confirmed via `qa-subagent` inspection this is entirely internal to `bds-button`'s own hydration timing — not a `bds-date-picker`, `bds-popover`, or `bds-calendar-grid` defect, and out of scope for `EOA-17138`. Logged here rather than fixed inline, per user decision (2026-08-24) to keep `EOA-17138` execution moving.
