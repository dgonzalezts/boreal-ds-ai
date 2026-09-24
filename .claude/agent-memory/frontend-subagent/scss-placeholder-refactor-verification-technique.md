---
name: scss-placeholder-refactor-verification-technique
description: How to prove a %placeholder/@extend SCSS dedup produced zero computed-CSS change, since raw diff of compiled output is misleading
metadata:
  type: project
---

When deduplicating SCSS via `%placeholder` + `@extend` (EOA-17662 Task 36a, `bds-date-picker.scss`), a raw line-by-line `diff` of the before/after compiled CSS is NOT a valid equivalence check — `@extend` merges selectors into shared comma-grouped rules and moves declaration blocks to new source positions, so the diff shows large chunks of churn even when every selector's final computed styles are byte-identical.

**Verification technique that actually works:**
1. `git stash` the SCSS change, run `pnpm --filter @telesign/boreal-web-components build`, copy `dist/collection/components/.../<component>.css` to a scratch "before" file.
2. `git stash pop`, rebuild, copy the compiled CSS to a scratch "after" file.
3. Parse both CSS files with a small script that expands comma-separated selectors and computes an *effective declarations map per individual selector* (last-write-wins per property, matching cascade order) — then compare those maps as unordered dicts, not the raw text.
4. Only if every shared selector's effective-declarations dict is equal (regardless of declaration order or how selectors were grouped in the rule) is the refactor visually/behaviorally equivalent.

A Python script doing this (regex-split top-level `{...}` rules, no nested at-rules) lives in this task's scratch dir as a reusable pattern — recreate it rather than trusting `diff`.

Also useful: the Stencil dev server's hashed `www/build/p-*.entry.js` chunk (find via `grep -rl "<a selector fragment>" www/build/`) reflects a live `--watch` rebuild immediately — grepping the compiled selector text out of that chunk and checking its mtime is a fast live-freshness proxy when a full browser-driven visual check isn't available.

See also [[stencil-sass-inject-global-paths-constraint]] for why component SCSS never has its own `@use` of the token package (tokens arrive pre-injected as `var(--boreal-*)`), which is why the compiled CSS shows `var(--boreal-*)` rather than resolved literals.
