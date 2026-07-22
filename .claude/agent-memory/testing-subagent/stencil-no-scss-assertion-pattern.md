---
name: stencil-no-scss-assertion-pattern
description: No codebase precedent for asserting on raw .scss content in Jest specs; CSS-only behaviors (animations, prefers-reduced-motion, keyframes) are not verifiable via newSpecPage and must be scoped out of the automated test with a documented reason.
metadata:
  type: project
---

Searched the whole `packages/boreal-web-components/src/components/` tree for any spec reading a `.scss` file's raw text (`readFileSync`, `require(...scss)`, `.scss'` + `toContain`) — zero hits. Confirmed during `bds-table` skeleton-loading testing (EOA-15507 Task 5, 2026-07-21): the plan asked for an automated check that `@media (prefers-reduced-motion: reduce)` disables the `.bds-skeleton` pulse animation.

**Why:** `newSpecPage`'s mock-doc/JSDOM environment does not load or evaluate stylesheets at all — `styleUrl` is never fetched, no CSSOM exists, and there is no `matchMedia` polyfill wired to Stencil's Jest preset by default. There is nothing in the DOM tree a Jest assertion could inspect to prove a `@keyframes`/`@media` rule exists or applies. This is a fundamental gap in `newSpecPage`, not a missing helper — no future utility function will make raw SCSS content assertable through it.

**How to apply:** When a plan's acceptance criteria includes a CSS-only behavior (animation states, reduced-motion overrides, hover-only styling, print styles, etc.), do not attempt to Jest-assert on the stylesheet. Instead:
1. Assert at the DOM level on whatever markup the CSS rule targets (e.g. confirm the `.bds-skeleton`/`.bds-skeleton--rect` class names the SCSS selectors key off are actually present in the rendered output).
2. Note the CSS-only criterion explicitly as *not covered by an automated assertion* in the task report, with this reasoning, so it doesn't silently look forgotten.
3. Route real visual/animation verification to the plan's manual-test checklist (e.g. via browser devtools' rendering panel to simulate `prefers-reduced-motion`), never to a fabricated Jest assertion that doesn't actually exercise the CSS.

This generalizes beyond `bds-table` — worth a `.agents/memory/` promotion if another component's plan hits the same "assert the reduced-motion CSS" acceptance criterion again.
