---
name: feedback_thirdparty_prop_string_literals
description: When one component's render() sets a prop on a nested third-party bds-* component, use a plain string literal, not an imported enum, unless the surrounding file already imports enums for that purpose
metadata:
  type: feedback
---

`bds-table.tsx` sets props on nested components (`variant="plain"` on `bds-button`, `variant="subheading"` on `bds-typography`, `orientation="vertical"` on `bds-divider`, `mode="search"` on `bds-search-bar`) using plain string literals, not the exporting component's enum constants (e.g. `bds-search-bar` exports `SEARCH_BAR_MODE.SEARCH` from its own `types/enum.ts`, but `bds-table.tsx` does not import it).

**Why:** the convention in this file is driven by what the *consuming* component already imports/uses elsewhere, not by what the target component exports. Importing every nested component's enum for a single literal prop value adds import noise without benefit — the target component's own `@Watch`-driven `validatePropValue` already guards against invalid strings at runtime.

**How to apply:** before adding an import like `SEARCH_BAR_MODE` (or any other component's enum) just to type one JSX prop value, check whether the file already uses string literals for similar nested third-party component props. If it does, match that pattern and skip the import. Only import an enum when the current component's own prop values are being validated/typed (e.g. its own `@Prop() readonly variant`), not to type a value passed one level down into a child element.
