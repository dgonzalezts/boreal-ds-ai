# BUG: `data-hidearrow` attribute name is inverted from its actual meaning in `bds-popover` and `bds-tooltip`

**Severity:** Low
**Priority:** P3
**Type:** UI (naming/readability defect, not a rendering bug)
**Status:** Fixed
**Ticket:** [EOA-17085](https://telesign.atlassian.net/browse/EOA-17085)
**Component(s):** `bds-popover`, `bds-tooltip`
**Discovered during:** `EOA-16692` (`bds-date-picker` v1) — Task 14 manual QA, flagged as out-of-scope for that ticket since it lives entirely in shared/foundational components, not `bds-date-picker` itself.

---

## Environment

- **Framework:** Stencil Web Components (`@telesign/boreal-web-components`)
- **Tooling used to reproduce:** Direct code inspection (`bds-popover.tsx`, `bds-tooltip.tsx`) + a Jest `newSpecPage` debug spec to inspect the serialized DOM output
- **Affected files:**
  - `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` (lines 547-549, 634-635)
  - `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx` (lines 95-96, 243)
  - `packages/boreal-web-components/src/components/overlays/bds-tooltip/__test__/bds-tooltip-basics.spec.ts` (lines 24, 74 — assertions that inadvertently pass despite the inversion)

---

## Description

Both `bds-popover` and `bds-tooltip` render a DOM attribute literally named `data-hidearrow`, but its value is bound to a `canShowArrow` getter — the exact opposite concept:

```tsx
// bds-popover.tsx
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow;
}
...
data-hidearrow={this.canShowArrow}
```

```tsx
// bds-tooltip.tsx (separate, near-duplicate implementation)
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow || false;
}
...
data-hidearrow={this.canShowArrow}
```

So `data-hidearrow` is **present in the DOM precisely when the arrow IS shown**, and absent when it's hidden — the attribute's name says "hide arrow" but its presence means "arrow visible." Anyone inspecting the DOM (or writing a new consumer/test against this attribute) would reasonably read `data-hidearrow` present as "the arrow is hidden," which is backwards.

This is purely a naming/readability defect, not a functional one: the attribute isn't used for any CSS styling (confirmed via `grep` — no `[data-hidearrow]` selector exists in any `.scss` file), and no consumer component (`bds-select`, `bds-dropdown`, `bds-date-picker`, or any other `bds-popover`/`bds-tooltip` consumer) reads it. It also isn't caught by existing tests, for a second, compounding reason described below.

---

## Steps to Reproduce

Preconditions:

- None — reproducible via static code reading, or via any rendered `bds-popover`/`bds-tooltip` instance with default `floatingOptions` (arrow shown).

Steps:

1. Render any `bds-popover` or `bds-tooltip` instance with default `floatingOptions` (i.e., `hideArrow` unset/`false`, meaning the arrow **is** shown).
2. Inspect the rendered host element's attributes (via DevTools, or `element.outerHTML`/`getAttribute('data-hidearrow')` in a test).
3. Observe that `data-hidearrow` is **present** on the element (as an empty-string attribute, e.g. `data-hidearrow=""`) even though the arrow is visibly rendered.
4. Toggle `floatingOptions.hideArrow` to `true` (arrow hidden) and re-inspect: `data-hidearrow` is now **absent**.

**Reproduction Rate:** Always (100%, deterministic — this is how the getter/attribute binding is written, not a race condition).

---

## Expected Behavior

The attribute's name should match its meaning: present (or `true`) when the arrow is actually hidden, or — better — rename it to describe what it actually tracks (e.g. `data-arrow-visible`, bound directly to `canShowArrow` with no name/value inversion) so DOM inspection and any future consumer/test reflects reality without a mental double-negative.

---

## Actual Behavior

`data-hidearrow` is present in the DOM when the arrow is shown, and absent when the arrow is hidden — inverted from what its name implies.

**Why existing tests don't catch this:** Stencil serializes a JSX boolean `true` assigned to a generic (non-ARIA-special-cased) attribute as an **empty-string attribute** (`data-hidearrow=""`), confirmed via a debug `newSpecPage` render:

```
OUTERHTML: <div id="tooltip-content" ... data-hidearrow style="...">...
data-hidearrow attr: ""
```

`element.getAttribute('data-hidearrow')` therefore returns the string `""`, which is JavaScript-falsy. `bds-tooltip-basics.spec.ts:24`'s `expect(inner.getAttribute('data-hidearrow')).toBeFalsy()` consequently **passes** even though the attribute is technically present — the assertion is really only checking "is this an empty string or null," which happens to be true regardless of the naming inversion, not verifying the semantic correctness of the attribute's name.

---

## Visual Evidence

**Console/property evidence (via a debug Jest `newSpecPage` render of `bds-tooltip` with default `floatingOptions`, i.e. arrow shown):**

```
OUTERHTML: <div id="tooltip-content" part="tooltip-content" class="tooltip-content" popover="manual"
  role="tooltip" aria-hidden="false" data-placement="top" data-hidearrow style="left: NaNpx; top: NaNpx;">
  <div class="tooltip-arrow" part="arrow" style="left: NaNpx;"></div> Text content
</div>

data-hidearrow attr: ""
```

Note the arrow (`.tooltip-arrow`) is rendered in the same output where `data-hidearrow` is present — directly demonstrating the inversion.

---

## Impact Assessment

| Aspect               | Details                                                                                                          |
| -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Users Affected**   | None (end users) — no visual/functional/a11y impact. Potentially confusing for future developers/QA inspecting the DOM or writing new tests/consumers against this attribute. |
| **Frequency**        | Always (100%, by design of the current code)                                                                     |
| **Data Impact**      | None                                                                                                              |
| **Business Impact**  | Minimal — cosmetic/readability only, no shipped behavior is affected                                             |
| **Workaround**       | N/A — nothing is broken; the attribute simply has a misleading name                                              |

---

## Root Cause

### `bds-popover.tsx:547-549, 634-635`

```tsx
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow;
}
...
data-hidearrow={this.canShowArrow}
```

### `bds-tooltip.tsx:95-96, 243` (separate, near-duplicate implementation)

```tsx
get canShowArrow(): boolean {
  return !this.floatingOptions.hideArrow || false;
}
...
data-hidearrow={this.canShowArrow}
```

Both components bind an attribute literally named `data-hidearrow` to a getter (`canShowArrow`) whose name and meaning are the logical negation of the attribute name. This is most likely an unintentional naming carryover from the `hideArrow` prop/option name, without renaming the derived DOM attribute to match the inverted (`canShowArrow`) value it actually holds.

---

## Suggested Fix

Rename the DOM attribute in both files to something that matches `canShowArrow`'s actual meaning, e.g.:

```tsx
data-arrow-visible={this.canShowArrow}
```

(or any non-inverted name — exact naming is a minor style choice, not prescribed here).

**Files to change:**

1. `bds-popover.tsx:635` — rename the attribute
2. `bds-tooltip.tsx:243` — rename the attribute (separate implementation, same fix)
3. `bds-tooltip-basics.spec.ts:24,74` — update the 2 existing assertions to the new attribute name (and consider asserting actual presence/absence rather than relying on the falsy-empty-string coincidence, to make the semantic intent explicit)

No `bds-popover` test currently references `data-hidearrow` at all (confirmed via `grep` across `bds-popover/__test__/`), so no updates needed there. No SCSS, Storybook source, or React/Vue wrapper references this attribute (confirmed via `grep` across the workspace — only compiled `storybook-static/` build artifacts reference the old name, which regenerate automatically on the next Storybook build).

**Estimated effort:** ~15-30 minutes hands-on (2 one-line renames + 2 test-assertion updates), plus a full existing-test-suite re-run given `bds-popover` (3 direct consumers) and `bds-tooltip` (7 direct consumers) are shared/foundational components — regression risk is low, but the blast radius sits outside `bds-date-picker`, so this warrants its own small ticket rather than folding into `EOA-16692`.

---

## Regression Risk

Low. The attribute isn't read by any CSS, test, or consumer component today — a rename is additive/isolated. The only required updates are the 2 existing test assertions in `bds-tooltip-basics.spec.ts` that reference the attribute name directly.

---

## Related

- Discovered during `EOA-16692` (`bds-date-picker` v1), Task 14 manual QA — see `ai-work/plans/EOA-16692-bds-date-picker-v1.md`, Task 14's status note.
- Not related to any previously filed `bds-tooltip`/`bds-popover` bug report in this directory.

---

## QA Verification

- [x] Reproduced via direct code inspection (`bds-popover.tsx`, `bds-tooltip.tsx`)
- [x] Confirmed via a debug `newSpecPage` render showing `data-hidearrow` present while the arrow is visibly rendered
- [x] Confirmed no SCSS/consumer/wrapper code depends on this attribute (safe to rename)
- [x] Fix implemented and verified

**Verified By:** Session agent (OpenCode), via direct code inspection + Jest `newSpecPage` debug render
**Verification Date:** 2026-08-18

---

## Fix Implemented (2026-08-20)

Implemented on branch `bugfix/EOA-17085-popover-tooltip-arrow-attr` and pushed to `origin`.

**Code changes:**

1. `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx`
   - Renamed `data-hidearrow={this.canShowArrow}` to `data-arrow-visible={this.canShowArrow}`
2. `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx`
   - Renamed `data-hidearrow={this.canShowArrow}` to `data-arrow-visible={this.canShowArrow}`
3. `packages/boreal-web-components/src/components/overlays/bds-tooltip/__test__/bds-tooltip-basics.spec.ts`
   - Updated assertions to `data-arrow-visible`
4. `packages/boreal-web-components/src/components/overlays/bds-popover/__test__/bds-popover-variants.spec.ts`
   - Added explicit assertions for `data-arrow-visible` presence when arrow is shown and absence when hidden

**Commit:** `e84e405c`

## Post-fix Verification

- Automated tests: pass (pre-push hook test suite in branch)
- Manual QA via Playwright/Storybook: pass
  - `data-arrow-visible` present when arrow renders
  - `data-arrow-visible` absent when `floatingOptions.hideArrow = true`
  - Arrow rendering and popover/tooltip interaction behavior unchanged
