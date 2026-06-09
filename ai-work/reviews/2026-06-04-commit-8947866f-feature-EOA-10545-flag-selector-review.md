# Boreal DS — Code Review Report

**Generated:** 2026-06-04
**Branch:** `feature/EOA-10545-flag-selector-component`
**Head commit:** `bd05758d`
**Base ref:** `main`
**Repository:** `.`

---

## Scope Note

This review is scoped to the flag-selector feature introduced in `bds-select` as part of EOA-10545. The feature adds a `variant="flag"` prop that embeds a `bds-flag` element inside `bds-text-field` and updates it dynamically as the user selects a country.

Four commits are in scope:

1. `5dfa1ffc` — Added flag variant support with country utilities and flag loading logic
2. `fa400ee4` — Fixed clear behavior for flag reset on `bdsClear`
3. `8947866f` — Resolved import issues
4. `bd05758d` — Added variant tests and moved to a new file

Files reviewed:

- `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`
- `packages/boreal-web-components/src/components/forms/bds-select/types/ISelect.ts`
- `packages/boreal-web-components/src/utils/countries/countryFunctions.ts`
- `packages/boreal-web-components/src/utils/countries/countries.ts`
- `packages/boreal-web-components/src/components/forms/bds-select/__test__/bds-select.variants.spec.ts`

---

## Affected Packages

- **boreal-web-components (Stencil)** — checklist sections: A, Tests, Docs

---

## Manual Review Findings

### Bug — `loadFlag()` guard condition is logically incorrect ❌

**File:** `bds-select.tsx:206`

```ts
private loadFlag() {
  if (this.variant !== 'flag' && this.bdsFlag !== null) return;
  ...
  updateElementProp(this.bdsFlag, 'country', countrySelected.country);
}
```

The guard uses `&&` (both conditions must be true), but the `bdsFlag` getter **always returns `null`** when `variant !== 'flag'`:

```ts
private get bdsFlag(): HTMLBdsFlagElement | null {
  if (this.variant === 'flag' && this.bdsField !== null) {
    return (this.bdsField as HTMLElement).querySelector('bds-flag');
  }
  return null;
}
```

Truth table:

| `variant` | `bdsFlag` | Guard evaluates to | Actual result |
|---|---|---|---|
| `'default'` | `null` | `true && false` → **does NOT return** | Proceeds, calls `updateElementProp(null, ...)` |
| `'flag'`, no `<bds-flag>` in slot | `null` | `false && false` → **does NOT return** | Proceeds, calls `updateElementProp(null, ...)` |
| `'flag'`, `<bds-flag>` present | element | `false && true` → **does NOT return** | Works correctly ✓ |

The guard never fires. The correct condition is:

```ts
if (this.variant !== 'flag' || this.bdsFlag === null) return;
```

---

### Interface gap — `ISelect` is missing the `variant` prop ❌

**File:** `types/ISelect.ts`

```ts
export interface ISelect {
  value: string;
  searchable: boolean;
  name: string;
  // variant is absent
}
```

`variant: 'default' | 'flag'` is a public `@Prop()` on `BdsSelect` but not declared in the interface. The class correctly declares `implements ISelect`, so the interface is the enforced contract. Add:

```ts
variant: 'default' | 'flag';
```

---

### Tests for `variant="flag"` — added with gaps ⚠️

**File:** `__test__/bds-select.variants.spec.ts` _(added in `bd05758d`)_

Five tests were added in `describe('bds-select - variants')`. Coverage against the originally identified behaviours:

| Behaviour | Covered? |
|---|---|
| `loadFlag()` sets the correct country prop on load when `variant="flag"` and value is empty | ✅ Test 1 |
| `loadFlag()` sets the correct country prop on load when `variant="flag"` and value is pre-set | ✅ Test 2 |
| `loadFlag()` updates the flag when the value changes programmatically | ✅ Test 5 |
| `listenClearInput` resets the flag to the global entry on clear | ✅ Test 4 |
| `bdsFlag` getter returns `null` for `variant="default"` (validates the `&&` vs `\|\|` guard) | ❌ |
| Component renders without errors when `variant="flag"` but no `<bds-flag>` in slot | ❌ |

**Critical gap — Test 3 never asserts the flag country after a user click:**

Test 3 ("Should select a country when variant is flag") clicks a list item and correctly
verifies the `bdsChange` / `valueChange` events, the `selected` attribute, the text field
value, and the hidden input — but never checks `flag.getAttribute('country')`. This is
the core dynamic behaviour of the feature (flag updating on user selection) and it has no
assertion. Add:

```ts
expect(flag.getAttribute('country')).toBe('55');
```

after the second `waitForChanges()`.

**Minor issues in the test file:**

- Test 2 description has a typo: `'Sould preselect country...'` → `'Should preselect country...'`
- Test 3 calls `assertExists(option, ...)` after clicking the element, which is redundant — the option cannot have disappeared between the click and the assertion.

---

### No Storybook story for `variant="flag"` ❌

**File:** `apps/boreal-docs/src/stories/forms/bds-select/bds-select.stories.ts`

Eight stories are present and none demonstrate the flag variant. The feature has no visual documentation, no interactive demo, and no usage example that developers can reference. A `FlagSelector` story should be added:

```html
<bds-select variant="flag" name="country">
  <bds-text-field slot="field" label="Country" placeholder="Select a country">
    <bds-flag slot="prefix" country="00" identifier="code"></bds-flag>
  </bds-text-field>
  <bds-list-menu slot="list" menu-role="listbox">
    <bds-list-menu-item value="br">Brazil</bds-list-menu-item>
    <bds-list-menu-item value="us">United States</bds-list-menu-item>
    <bds-list-menu-item value="gb">United Kingdom</bds-list-menu-item>
  </bds-list-menu>
</bds-select>
```

The flag should update as each option is selected, and reset to the global flag when cleared.

---

### Minor — Redundant ternary in `loadFlag()` ⚠️

**File:** `bds-select.tsx:208`

```ts
const countrySelected = searchCountry(this.value === '' ? 'global' : this.value);
```

`searchCountry` already handles empty input:

```ts
export function searchCountry(query: string): ICountry {
  if (query === null || query.trim() === '') {
    return allCountries[0]; // GLOBAL is allCountries[0]
  }
  ...
}
```

Passing `'global'` when `this.value === ''` and letting `searchCountry` fall through its empty-guard to reach the same `allCountries[0]` result is identical. Simplify:

```ts
const countrySelected = searchCountry(this.value);
```

---

### Minor — Inaccurate JSDoc in `searchCountry` ⚠️

**File:** `utils/countries/countryFunctions.ts:15–16`

The docstring states:

> "If the query is empty or consists only of whitespace, the function returns the original list of countries."

The function returns `allCountries[0]` (a single `ICountry` object), not a list. This is a copy-paste artefact from a list-based predecessor. Update:

```
If the query is empty or consists only of whitespace, the function returns the first country in the list.
```

---

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage
- ⚠️ New logic is covered by tests — flag variant tests added (`bd05758d`), but Test 3 is missing the flag country assertion after a user click; `variant="default"` guard and flag-less slot still uncovered
- ❌ Storybook/MDX updated when behaviour or APIs change — no story for `variant="flag"`
- ✅ Public API naming conventions followed (`variant`, `bdsFlag`, `loadFlag`)

### A — Stencil (boreal-web-components)

- ❌ Interface file reflects all public `@Prop()` declarations — `variant` missing from `ISelect`
- ✅ Getter accessors carry no `get` prefix — `bdsFlag` passes
- ✅ Boolean `@Prop()` names use no `is`/`has`/`show` prefix
- ✅ ARIA attribute names are kebab-case — no new `setAttribute` calls introduced
- ✅ `searchCountry` fallback behaviour is consistent with GLOBAL entry

---

## Summary

| Severity | Finding | Location |
|---|---|---|
| **Bug** | `loadFlag()` guard uses `&&` — never fires; always proceeds to `updateElementProp(null, ...)` | `bds-select.tsx:206` |
| **Interface** | `ISelect` missing `variant: 'default' \| 'flag'` | `types/ISelect.ts` |
| **Tests** | Tests added (`bd05758d`) — Test 3 missing flag assertion after user click; `variant="default"` guard and flag-less slot still uncovered | `bds-select.variants.spec.ts` |
| **Docs** | No Storybook story for `variant="flag"` | `bds-select.stories.ts` |
| **Minor** | Redundant ternary in `loadFlag()` | `bds-select.tsx:208` |
| **Minor** | Inaccurate JSDoc in `searchCountry` | `countryFunctions.ts:15` |

**Blocking before merge:**

1. Fix `loadFlag()` guard: `&&` → `||` (`bds-select.tsx:206`)
2. Add `variant` to `ISelect` (`types/ISelect.ts`)
3. ~~Add flag variant tests~~ — added in `bd05758d`; add missing `flag.getAttribute('country')` assertion to Test 3; cover `variant="default"` guard behaviour and flag-less slot in flag mode
4. Add `FlagSelector` story to `bds-select.stories.ts`

**Recommended (non-blocking):**

5. Remove redundant ternary in `loadFlag()` — use `searchCountry(this.value)` directly
6. Fix `searchCountry` JSDoc — "returns the first country in the list", not "the original list"
