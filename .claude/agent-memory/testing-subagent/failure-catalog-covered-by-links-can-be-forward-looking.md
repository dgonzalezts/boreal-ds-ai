---
name: failure-catalog-covered-by-links-can-be-forward-looking
description: A failure-mode catalog's `Covered by:` links may name specs/tests that were planned but never written, or that exist only on another branch — verify each against the checkout before trusting it
metadata:
  type: feedback
---

When extending an existing `ai-work/testing/failure-modes/<component>.md`, never trust its `Covered by:` fields: `ai-work/` is untracked and authored across branches/sessions, so links can point at a plan's un-executed test names (bds-popover FM-09..FM-19 cited hyphenated `bds-popover-variants.spec.ts` files that never existed; the plan was `status: pending`) or at specs that live only on a sibling branch (`bds-popover.click-outside.spec.ts` + source fix `838b6600` exist only on `fix/EOA-19598-...`, so FM-20 is a live defect on `feature/EOA-19936-...`).

**Why:** a stale link makes a gap look covered; the catalog then misreports coverage and the real defect (missing `documentElement` click-outside exclusion) hides.

**How to apply:** for each row, `ls` the `__test__` dir, grep the quoted test name, and `git merge-base --is-ancestor <fix-commit> HEAD` for source claims; run the scoped coverage and map uncovered line numbers to rows; also scan existing tests for vacuous ones (name claims X, assertion proves Y) and record them in the catalog without editing them.
