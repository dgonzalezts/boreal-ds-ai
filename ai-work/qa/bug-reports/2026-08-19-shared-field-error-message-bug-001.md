# BUG: `errorMessage` never overrides the built-in validation message unless `error` is also manually forced `true`

**Severity:** Medium
**Priority:** P2
**Type:** Functional
**Status:** Fixed
**Ticket:** [EOA-17093](https://telesign.atlassian.net/browse/EOA-17093)
**Component(s):** `bds-text-field`, `bds-tag-field`, `bds-number-field` (shared root cause: `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx`)
**Discovered during:** `EOA-16692` (`bds-date-picker` v1) — investigating why a `bds-date-picker` playground scenario's slotted `<bds-text-field required error-message="Please pick a date.">` never showed the custom message. Flagged as out-of-scope for that ticket since it's a pre-existing defect in shared, foundational form components, not `bds-date-picker` itself.

---

## Environment

- **Framework:** Stencil Web Components (`@telesign/boreal-web-components`)
- **Tooling used to reproduce:** Storybook (`pnpm dev:docs`, `localhost:6006`) + direct code inspection
- **Affected files:**
  - `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx` (root cause, single shared helper)
  - `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx` (consumer, stale JSDoc)
  - `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx` (consumer, stale JSDoc)
  - `packages/boreal-web-components/src/components/forms/bds-number-field/bds-number-field.tsx` (consumer, stale JSDoc)
  - `apps/boreal-docs/src/stories/forms/bds-text-field/bds-text-field.stories.ts` — 3 stories affected (`WithCustomValidationMessage`, `WithMinLength`, `WithPattern`)

---

## Description

All three FACE form components with an `errorMessage` prop (`bds-text-field`, `bds-tag-field`, `bds-number-field`) share the same `deriveFieldRenderState()` helper to decide what footer text to render:

```ts
// renderFieldParts.tsx
const helperContent =
  host.error && host.errorMessage !== ''
    ? host.errorMessage
    : host.validationError && host.validationMessage !== ''
      ? host.validationMessage
      : host.helperText;
```

`error` is a plain, manually-set `@Prop()` — none of the three components ever set it internally in response to their own built-in validation (`required`/`minLength`/`pattern`/`maxTags`/`min`/`max`, etc.). Those built-in validators only ever populate `validationError`/`validationMessage` (a separate pair of internal `@State()` fields), which the helper's `errorMessage`-branch never reads.

**Net effect:** a consumer who sets `required` + `error-message="My custom message"` (without also manually forcing `error="true"`) will, upon a genuine validation failure (e.g. blurring an empty required field), see the hardcoded built-in default message (e.g. `"This field is required. Please fill it out."`), never their own custom text. This directly contradicts the evident intent of every Storybook example that uses `errorMessage` this way, and contradicts the working precedent already established in `bds-checkbox-group.tsx` (see "Related" below), which correctly ties `errorMessage` to *real* validity via its own `isInvalid` state (set by the native `invalid` event), not a separate static flag.

Setting `error="true"` alongside `errorMessage` does make the custom text show — but as a permanently-forced state, completely disconnected from the field's actual validity (confirmed: typing a valid value into a field with `error="true"` set and blurring does not clear the message).

---

## Steps to Reproduce

**Preconditions:**
- Run `pnpm dev:docs` from the monorepo root; open Storybook at `http://localhost:6006`.

**Steps (any of the following, all reproduce identically):**

1. Navigate to `Forms/Text Field` → `WithCustomValidationMessage` (args: `required: true`, `errorMessage: 'This is a custom error message — please fill in this field.'`, no `error` set).
2. Click into the `Username` field, then Tab/blur without typing anything.
3. Observe the rendered footer text.

**Reproduction Rate:** Always (100%, deterministic).

---

## Expected Behavior

The footer should show the custom `errorMessage` ("This is a custom error message — please fill in this field.") once real `required`-validation fails on blur — matching every Storybook story's evident intent and matching `bds-checkbox-group`'s own working precedent.

---

## Actual Behavior

The footer shows the hardcoded built-in default: **"This field is required. Please fill it out."** — the custom `errorMessage` is silently ignored.

Confirmed via live Storybook testing across all three affected components:

| Component | Story/scenario | Custom `errorMessage` shown? |
|---|---|---|
| `bds-text-field` | `WithCustomValidationMessage` (required, no `error`) | ❌ No — hardcoded default shown |
| `bds-text-field` | `WithMinLength` (minLength, no `error`) | ❌ No — hardcoded default shown |
| `bds-text-field` | `WithPattern` (pattern, no `error`) | ❌ No — hardcoded default shown |
| `bds-tag-field` | `Required` + `errorMessage` set via Controls, `error: false` | ❌ No — hardcoded default shown |
| `bds-tag-field` | Same, with `error: true` also set | ✅ Yes — but permanently, disconnected from real validity |
| `bds-number-field` | `CustomErrorMessage` (`error: true` set statically) | ✅ Yes — but permanently, disconnected from real validity (confirmed: typing a valid number + blur does not clear it) |
| `bds-number-field` | `Required` (no `error`/`errorMessage`) | N/A — hardcoded default shown (no custom message was set) |

---

## Visual Evidence

**`bds-text-field` / `WithCustomValidationMessage`, after blur:**
- `bds-text-field.error` property → `false` (confirmed, matches story args)
- `bds-text-field.errorMessage` property → set, but never rendered
- Rendered `<bds-typography variant="helper">` text: `"This field is required. Please fill it out."`

**`bds-number-field` / `CustomErrorMessage`, before and after typing a valid value + blur:**
| Step | Rendered footer text |
|---|---|
| On load (empty) | "Please provide an amount before continuing." |
| After typing `42` (valid) + blur | "Please provide an amount before continuing." (**unchanged** — proves the message is static, not validity-driven) |

---

## Impact Assessment

| Aspect | Details |
| --- | --- |
| **Users Affected** | Any consumer relying on `errorMessage` to customize validation feedback for `required`/`minLength`/`maxLength`/`pattern`/`min`/`max`/tag-count constraints across these three components — the message they configure is silently ignored unless they also manually force `error="true"` (in which case it becomes permanently stuck regardless of real validity). |
| **Frequency** | Always (100%, deterministic) |
| **Data Impact** | None |
| **Business Impact** | Confusing/incorrect UX — consumers configuring a helpful, specific validation message (e.g. "Username must be at least 5 characters.") instead see a generic hardcoded fallback, or (if they work around it with `error="true"`) a message that never updates even after the user fixes their input. |
| **Workaround** | None that preserves correct behavior — setting `error="true"` "fixes" message visibility at the cost of permanently forcing the error state regardless of real validity. |

---

## Root Cause

`renderFieldParts.tsx`, `deriveFieldRenderState()`:

```ts
const helperContent =
  host.error && host.errorMessage !== ''
    ? host.errorMessage
    : host.validationError && host.validationMessage !== ''
      ? host.validationMessage
      : host.helperText;
```

The `errorMessage`-display branch is gated solely on `host.error` (a static, manually-set prop), never on `host.validationError` (the real, live FACE-validity state populated by each component's own built-in validators). Since none of the three consuming components ever set `this.error = true` internally in response to their own validation, the custom message and real validation are structurally disconnected.

---

## Suggested Fix

Widen the gating condition to also consider real validation failure:

```diff
  const helperContent =
-   host.error && host.errorMessage !== ''
+   (host.error || host.validationError) && host.errorMessage !== ''
      ? host.errorMessage
      : host.validationError && host.validationMessage !== ''
        ? host.validationMessage
        : host.helperText;
```

This is the **only** code change needed — it's a single shared helper used by exactly 3 components (confirmed via codebase search, no other consumers), so it fixes all three simultaneously. It preserves:
- The existing "manually forced, permanent error" use case (`error: true` alone, no real validation involved).
- The existing hardcoded-default fallback (`validationMessage`) for consumers who don't set a custom `errorMessage`.

**Additional changes needed to fully land this fix** (not just the 1-line code change):

1. **JSDoc** (3 files, 1 line each) — each component's `@Prop() errorMessage` comment ("Message shown below the input when `error` is `true`. Replaces `helperText`.") needs updating to also mention real validation failure as a trigger:
   - `bds-text-field.tsx:72`
   - `bds-tag-field.tsx:68`
   - `bds-number-field.tsx:139`
2. **Unit tests** (3 new test cases, one per component — no shared helper test file exists, confirmed via search) — none of the existing test suites assert "errorMessage overrides validationMessage when validation genuinely fails, without `error` set":
   - `bds-text-field-validation.spec.ts` — new test (existing "internal validationMessage rendered in footer" test at line 528 is untouched, tests the no-`errorMessage` fallback path).
   - `bds-tag-field-validation.spec.ts` — new test for the `valueMissing`/`rangeOverflow` path (existing `maxTagLength`-specific tests at lines 103-149 are untouched — that path already worked independently via `handleCommit`'s own manual check).
   - `bds-number-field.validation.spec.ts` — new test (no existing `errorMessage`-related test found there).
   - Full regression run of all 3 components' existing test suites to confirm the widened condition doesn't break anything (low risk — additive/widening change — but must be verified empirically).
3. **Storybook stories** — **no file changes needed**. The fix makes the already-written args in `WithCustomValidationMessage`/`WithMinLength`/`WithPattern`/`bds-tag-field`'s and `bds-number-field`'s equivalents correct as originally intended. Only needs manual/Playwright re-verification post-fix.
4. **MDX docs** — **no changes needed**. Checked all three components' MDX files; none contain incorrect claims requiring correction. `bds-tag-field.mdx:166` already accurately documents the correct (already-working, independent) `maxTagLength` behavior. The fix makes existing documentation accurate rather than requiring rewrites.

**Estimated effort:** ~1 hour hands-on (5 min the actual fix; 10 min JSDoc; 30-40 min new unit tests + regression run; 10-15 min Storybook re-verification). Low risk — isolated to one shared, well-tested helper with exactly 3 known consumers.

---

## Regression Risk

Low. The change widens an existing boolean condition (adds an `OR` clause) rather than restructuring logic; it's isolated to a single shared, small helper function with a fully enumerated, small consumer list (3 components, confirmed via codebase-wide search).

---

## Related

- **Confirmed working precedent** for the *correct* pattern already exists in this codebase: `bds-checkbox-group.tsx:284` — `this.internals.setValidity({ valueMissing: true }, this.errorMessage !== '' ? this.errorMessage : 'Please select at least one option.', anchor)`, combined with its own `isInvalid` state (set from the native `invalid` event) driving `showError = this.isError || this.isInvalid` at render time. `bds-checkbox-group` is unaffected by this bug — it doesn't use the shared `deriveFieldRenderState()` helper at all, it has its own independent, correctly-wired implementation.
- Discovered during `EOA-16692` (`bds-date-picker` v1) — see `ai-work/plans/EOA-16692-bds-date-picker-v1.md`, Task 21's status notes and the related session conversation.
- Related but distinct, separately-filed bug from the same ticket: `ai-work/qa/bug-reports/2026-08-18-bds-popover-bug-001.md` (Jira `EOA-17085`) — the `bds-popover`/`bds-tooltip` `data-hidearrow` naming inversion. Both bugs were found investigating `bds-date-picker`'s composition with shared/foundational components, but are otherwise unrelated.

---

## QA Verification

- [x] Reproduced live via Storybook across all 3 components (`bds-text-field`, `bds-tag-field`, `bds-number-field`)
- [x] Confirmed root cause via direct code inspection of the shared `deriveFieldRenderState()` helper
- [x] Confirmed exactly 3 consumers of the shared helper (no hidden 4th)
- [x] Confirmed the "manually forced `error: true`" workaround exists but is disconnected from real validity (typing a valid value + blur does not clear the message)
- [x] Confirmed no existing unit test covers the fixed scenario (new tests needed, not updates)
- [x] Confirmed no MDX documentation needs correction (already describes intended/correct behavior)
- [x] Fix implemented and verified

**Verified By:** Session agent (OpenCode), via direct code inspection + live Storybook testing (Playwright)
**Verification Date:** 2026-08-19

---

## Fix Implemented (2026-08-20)

Implemented on branch `bugfix/EOA-17093-shared-field-error-message` and pushed to `origin`.

**Code changes:**

1. `packages/boreal-web-components/src/components/forms/common/renderFieldParts.tsx`
   - Updated helper-content selection condition from:
     - `host.error && host.errorMessage !== ''`
   - To:
     - `(host.error || host.validationError) && host.errorMessage !== ''`
2. `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`
   - Updated `errorMessage` JSDoc to include internal validation-failure behavior
3. `packages/boreal-web-components/src/components/forms/bds-tag-field/bds-tag-field.tsx`
   - Updated `errorMessage` JSDoc to include internal validation-failure behavior
4. `packages/boreal-web-components/src/components/forms/bds-number-field/bds-number-field.tsx`
   - Updated `errorMessage` JSDoc to include internal validation-failure behavior
5. Added regression tests:
   - `packages/boreal-web-components/src/components/forms/bds-text-field/__test__/bds-text-field-validation.spec.ts`
   - `packages/boreal-web-components/src/components/forms/bds-tag-field/__test__/bds-tag-field-validation.spec.ts`
   - `packages/boreal-web-components/src/components/forms/bds-number-field/__test__/bds-number-field.validation.spec.ts`
   - New assertions confirm custom `errorMessage` overrides internal `validationMessage` when `validationError` is true without requiring `error=true`

**Commit:** `8b60077e`

## Post-fix Verification

- Automated tests: pass (pre-push hook test suite in branch)
- Manual QA via Playwright/Storybook: pass
  - Custom `errorMessage` now appears for real validation failures in text/tag/number fields without setting `error=true`
  - Non-error helper-text behavior remains unchanged
