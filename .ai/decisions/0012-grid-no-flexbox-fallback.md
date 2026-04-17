# ADR 0012 — Grid browser support: CSS Grid only, no Flexbox fallback

**Date:** 2026-04-15
**Status:** Accepted

---

## Context

The ticket states: *"Use CSS Grid for the modern implementation, but provide a Flexbox fallback if the browser support matrix requires it (per PI 7 guidelines)."*

No PI 7 browser support matrix document was found in the repository or referenced explicitly in the ticket. The requirement to provide a Flexbox fallback is therefore conditional and currently unverifiable.

---

## Decision drivers

**CSS Grid browser support is effectively universal.** As of April 2026, CSS Grid (including `grid-template-columns`, `gap`, `grid-column: span N`) is supported by all modern browsers with global coverage exceeding 98% (Can I Use data). The only non-supporting browsers are IE 11 and legacy Edge (EdgeHTML), which reached end of life in 2022 and 2021 respectively.

**A Flexbox fallback doubles the SCSS surface area** for a component whose only job is position management. Every column-span calculation, gutter, and breakpoint override would need to be duplicated in a parallel Flexbox implementation. This creates a maintenance burden with no concrete user benefit.

**The "PI 7 guidelines" reference is unresolvable.** No document by that name exists in `.ai/`, the repository root, or any linked external resource. Without a concrete browser matrix specifying IE 11 or similar legacy targets, the fallback cannot be scoped or tested.

---

## Decision

`bds-grid` and `bds-grid-item` are implemented using **CSS Grid only**. No Flexbox fallback is provided.

Minimum supported browsers are:
- Chrome / Edge (Chromium) — last 2 major versions
- Firefox — last 2 major versions
- Safari — last 2 major versions

These should be documented in the component's JSDoc header.

---

## Consequences

**Positive:**
- SCSS stays lean — one implementation path per breakpoint
- No risk of Flexbox vs Grid behavioural divergence in edge cases
- Column-span math is semantically correct (CSS Grid `span` is purpose-built for this)

**Constraint introduced:**
- If PI 7 or a future PI defines a browser matrix that includes IE 11 or pre-Chromium Edge, this decision must be revisited and the ADR updated.
- The Storybook docs should note the minimum browser requirement so consuming teams can assess compatibility.

---

## References

- Ticket: `.ai/tickets/grid-system-&-component.md`
- Plan: `.ai/plans/EOA-12029_grid_foundational_system.md`
- Can I Use — CSS Grid: https://caniuse.com/css-grid
