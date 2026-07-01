# BUG: `stayOnHover` never keeps the tooltip open, and the Storybook controls for `hideArrow`/`stayOnHover` have no effect

**Severity:** Medium
**Priority:** P2
**Type:** Functional
**Status:** Fixed
**Component(s):** `bds-tooltip`
**Fixed in:**

- `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx` — `mouseleave` listener now reads `e.relatedTarget` instead of `e.target`
- `apps/boreal-docs/src/stories/overlays/bds-tooltip/bds-tooltip.stories.ts` — removed string-quoting around `offset`, `hideArrow`, `stayOnHover` in the `floatingOptions` assignment for both `renderTooltip` and `renderTooltipWithTypography`
  **Introduced by:** Not determined during this session (pre-existing in both files; no specific introducing commit identified)

---

## Environment

- **Framework:** Stencil Web Components (`@telesign/boreal-web-components`)
- **Repro stories:** `Overlays / Tooltip → Default`, `→ HideArrow`, `→ StayOnHover` (Storybook, `overlays-tooltip--default`, `overlays-tooltip--hide-arrow`, `overlays-tooltip--stay-on-hover`)
- **Tooling used to reproduce:** Playwright MCP (live DOM/property inspection before and after each fix)
- **Affected files:**
  - `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx` (root cause, Bug #1)
  - `apps/boreal-docs/src/stories/overlays/bds-tooltip/bds-tooltip.stories.ts` (compounding bug, Bug #2)

---

## Description

Two independent bugs combined to make `bds-tooltip`'s `stayOnHover` option completely non-functional, and to make the `HideArrow` Storybook control a no-op:

1. **Bug #1 (component root cause):** the tooltip's `mouseleave` handler resolved the "where is the pointer going" element from `e.target` instead of `e.relatedTarget`. Since `mouseleave` does not bubble, `e.target` is always the trigger element itself, so `stayOnHover`'s `validateHide()` check could never detect that the pointer had moved into the tooltip content, and the tooltip closed the instant the pointer left the trigger — even when moving directly into the tooltip.
2. **Bug #2 (story bug, compounding and independent):** the interactive Storybook stories assigned `floatingOptions` with `hideArrow` and `stayOnHover` wrapped in string quotes inside a template literal (`hideArrow: '${args.hideArrow}'`), turning the booleans into the literal strings `"true"`/`"false"` — both truthy in JS. This made `stayOnHover` permanently "on" regardless of the control's actual value (masking whether Bug #1's fix or the control itself did anything), and made `hideArrow` permanently truthy, so the tooltip's directional arrow never rendered in any story and the `HideArrow` toggle had zero visible effect.

---

## Steps to Reproduce

**Bug #1 — `stayOnHover` never keeps the tooltip open**

Preconditions:

- Run `pnpm dev:docs` from the monorepo root.
- Open Storybook and navigate to `Overlays → Tooltip → StayOnHover`.

Steps:

1. Hover the mouse over the tooltip trigger element so the tooltip opens.
2. Move the mouse directly from the trigger toward the open tooltip content (not away from it).
3. Observe the tooltip's `display` and `:popover-open` state during the transition.

**Reproduction Rate:** Always (100%, deterministic — not a race condition).

**Bug #2 — `hideArrow`/`stayOnHover` controls have no effect**

Preconditions:

- Same as above.
- Navigate to `Overlays → Tooltip → HideArrow`.

Steps:

1. Toggle the `hideArrow` control between `true` and `false` in the Storybook Controls panel.
2. Hover the trigger to open the tooltip in each state.
3. Inspect the rendered tooltip for the presence of the directional arrow element.
4. Additionally, in the browser console/Playwright, read `document.querySelector('bds-tooltip').floatingOptions` and inspect the types of `offset`, `hideArrow`, `stayOnHover`.

**Reproduction Rate:** Always (100%).

---

## Expected Behavior

- **Bug #1:** With `stayOnHover` enabled, moving the pointer from the trigger directly into the tooltip's floating content should cancel the pending hide and keep the tooltip open (`display: block`, `:popover-open` true) until the pointer leaves the tooltip content itself.
- **Bug #2:** `tooltip.floatingOptions` should hold native types — `offset` as `number`, `hideArrow` and `stayOnHover` as `boolean` — so each Storybook control independently and correctly drives its corresponding behavior. Toggling `hideArrow` to `true` should hide the arrow; toggling it to `false` should show it, independent of the `stayOnHover` state.

---

## Actual Behavior

- **Bug #1:** The tooltip closed immediately when the pointer left the trigger, regardless of where the pointer moved next, even when moving straight into the tooltip content. `validateHide()`'s `this.floatingContent.contains(target)` check was always evaluated against the trigger element (from `e.target`), never the actual destination element, so it always returned `false` and never blocked the hide.
- **Bug #2:** `tooltip.floatingOptions` returned `{ placement: "bottom", offset: "0", hideArrow: "false", stayOnHover: "false" }` — all values coerced to strings by the template literal. Since `"false"` is a non-empty, truthy string in JavaScript, `canShowArrow` (`!this.floatingOptions.hideArrow || false`) was always `false`, so the arrow never rendered in any tooltip story regardless of the control's value. Similarly, `stayOnHover`'s guard was always truthy, so every story behaved as if `stayOnHover` were enabled — independent of the control's real value — which masked Bug #1 in stories other than the dedicated `StayOnHover` story.

---

## Visual Evidence

**Console / property evidence (via Playwright MCP):**

Before fix:

```
tooltip.floatingOptions = { placement: "bottom", offset: "0", hideArrow: "false", stayOnHover: "false" }
```

After fix:

```
tooltip.floatingOptions = { placement: "bottom", offset: 0, hideArrow: false, stayOnHover: false }
```

**Behavioral evidence:**

- Before fix: on the `StayOnHover` story, moving the pointer from the trigger toward the tooltip content caused the tooltip to close mid-transition (`display: none`, `:popover-open` false) before the pointer ever reached the content.
- After fix: the tooltip correctly remained open (`display: block`, `:popover-open` true) while the pointer moved into and stayed within the tooltip content.
- After fix, `Default` (stayOnHover `false`) correctly hides when the pointer leaves toward the content; `HideArrow` (hideArrow `true`) correctly omits the arrow, visibly distinct from `Default`; `StayOnHover` (stayOnHover `true`) correctly stays open via the real, fixed `relatedTarget` logic rather than by accident.

---

## Impact Assessment

| Aspect              | Details                                                                                                                                                                                                                                                                                                                                                |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Users Affected**  | All consumers relying on `stayOnHover: true` to let users interact with tooltip content (e.g. copy text, click a link inside a tooltip); all consumers of the `HideArrow` Storybook story evaluating that control                                                                                                                                      |
| **Frequency**       | Every time (100% reproducible, not intermittent)                                                                                                                                                                                                                                                                                                       |
| **Data Impact**     | None                                                                                                                                                                                                                                                                                                                                                   |
| **Business Impact** | Any tooltip content requiring pointer interaction (links, selectable text) was unusable — the tooltip vanished before the pointer reached it. Documentation/Storybook also gave a false impression that `hideArrow` and `stayOnHover` were broken or no-ops, when in the `hideArrow` case the story itself was masking correct-if-untested arrow logic |
| **Workaround**      | None available to consumers — required a code fix                                                                                                                                                                                                                                                                                                      |

---

## Root Cause

### Bug #1 — `bds-tooltip.tsx:170`

```typescript
// BEFORE fix (broken):
trigger.addEventListener("mouseleave", (e: MouseEvent) =>
  this.hide(e.target as HTMLElement),
);
```

`mouseleave` does not bubble, so `e.target` is always the element the listener is attached to — the trigger itself — never the element the pointer is moving into. `validateHide()` (lines 111-117) is supposed to check `this.floatingContent.contains(target)` to decide whether to cancel a hide when the pointer moves from the trigger into the tooltip content. Because `target` was always the trigger, that containment check could never be true, so `stayOnHover` never actually cancelled a hide.

```typescript
// AFTER fix (correct):
trigger.addEventListener("mouseleave", (e: MouseEvent) =>
  this.hide(e.relatedTarget as HTMLElement),
);
```

`e.relatedTarget` on a `mouseleave` event is the element the pointer is entering, which is exactly what `validateHide()` needs to correctly detect a hover transition into the tooltip content.

### Bug #2 — `bds-tooltip.stories.ts`, `renderTooltip` and `renderTooltipWithTypography` inline `<script>` blocks

```javascript
// BEFORE fix (broken):
tooltip.floatingOptions = {
  placement: "${args.placement}",
  offset: "${args.offset}",
  hideArrow: "${args.hideArrow}",
  stayOnHover: "${args.stayOnHover}",
};
```

Quoting `${args.hideArrow}` and `${args.stayOnHover}` (booleans) and `${args.offset}` (a number) inside a template literal string-interpolates them, producing the JS strings `"true"`/`"false"`/`"0"`. Both `"true"` and `"false"` are non-empty strings and therefore truthy, which broke every boolean check downstream in the component that read `floatingOptions.hideArrow` or `floatingOptions.stayOnHover` directly as a boolean.

```javascript
// AFTER fix (correct):
tooltip.floatingOptions = {
  placement: '${args.placement}',
  offset: ${args.offset},
  hideArrow: ${args.hideArrow},
  stayOnHover: ${args.stayOnHover},
};
```

Quotes were removed from `offset`, `hideArrow`, and `stayOnHover` (kept on `placement`, which is a genuine string), so they retain their native `number`/`boolean` types at runtime.

This bug independently masked whether Bug #1's fix (or the `stayOnHover` control itself) was doing anything in Storybook, since `stayOnHover` was effectively hardcoded "on" for every story regardless of the control's state — and it separately and completely broke the `hideArrow` control, since `canShowArrow` (`!this.floatingOptions.hideArrow || false`) evaluated `!"false"` as `false` in every case.

---

## Fix Applied

Both fixes were applied together, verified independently:

1. `bds-tooltip.tsx:170` — `e.target` → `e.relatedTarget` in the `mouseleave` listener.
2. `bds-tooltip.stories.ts` — removed string quoting around `offset`, `hideArrow`, `stayOnHover` in both `renderTooltip` and `renderTooltipWithTypography`'s inline `floatingOptions` assignment.

**Verified:** Live Playwright MCP reproduction on `Default`, `HideArrow`, and `StayOnHover` stories before and after both fixes:

- `Default` (stayOnHover `false`) now correctly hides when the pointer leaves toward the content.
- `HideArrow` (hideArrow `true`) now correctly omits the arrow, visibly distinct from `Default`.
- `StayOnHover` (stayOnHover `true`) now correctly stays open via the real fixed logic rather than by accident.

**Test coverage added:** 7 new unit tests in `packages/boreal-web-components/src/components/overlays/bds-tooltip/__test__/bds-tooltip-events.spec.ts` covering `validateHide`'s `stayOnHover`/`relatedTarget` branches — these lines were previously uncovered (visible as red/uncovered lines in the Istanbul coverage report) prior to this fix.

### Impact assessment of the fix

| Scenario                                                             | Before fix                                          | After fix                                       | Risk                                                          |
| -------------------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------- |
| `stayOnHover: true`, pointer moves from trigger into tooltip content | Tooltip closes immediately (BUG)                    | Tooltip stays open until pointer leaves content | ✅ Fixed                                                      |
| `stayOnHover: false`, pointer leaves trigger                         | Tooltip closes (accidentally correct due to Bug #2) | Tooltip closes (correctly, via real logic)      | ✅ None — behavior preserved, now for the right reason        |
| `hideArrow: true` in Storybook                                       | Arrow always rendered regardless of control (BUG)   | Arrow correctly hidden                          | ✅ Fixed                                                      |
| `hideArrow: false` in Storybook                                      | Arrow always rendered (coincidentally correct)      | Arrow correctly rendered                        | ✅ None                                                       |
| `offset` control in Storybook                                        | Passed as string `"N"`                              | Passed as native `number`                       | ✅ None identified; consistent with component's expected type |

---

## Regression Risk

Low. Bug #1's fix changes only which element is passed to `hide()` on `mouseleave` — a strictly more correct value for the existing `validateHide()` contract; no other call sites depend on the previous (always-trigger) value. Bug #2's fix only affects Storybook example wiring, not shipped component code, and simply removes incorrect type coercion that had no legitimate use.

---

## Related

- `.agents/memory/mouseleave-relatedtarget-vs-target.md` previously documented Bug #1 as an unfixed known issue as of 2026-04-13; this report supersedes that entry now that the fix has landed.
- Referenced from `ai-work/qa/bug-reports/EOA-10062-bds-tooltip-bug-001.md` ("Related" section), which flagged this same `mouseleave` issue as a known separate, unfixed bug at the time.

---

## QA Verification

- [x] Fix verified via Playwright MCP live reproduction (dev environment / Storybook)
- [x] `Default`, `HideArrow`, `StayOnHover` stories manually re-verified pre/post fix
- [x] New unit tests added covering previously-uncovered `validateHide` branches
- [ ] Fix verified in staging (not yet deployed)
- [ ] Committed to git (pending — status as of report: fixes applied and verified locally, not yet committed)

**Verified By:** Session agent (Claude Code), via Playwright MCP
**Verification Date:** 2026-07-01
