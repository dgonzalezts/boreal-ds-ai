---
name: feedback_pure_reorder_verification_technique
description: How to safely execute a large pure class-member-reorder task and prove zero behavior change without hand-retyping code
metadata:
  type: feedback
---

For a "reorder class members, no logic changes" task on a large Stencil component (bds-table.tsx, ~1230 lines, ~70 members), hand-retyping each block via Edit risks silent transcription errors (dropped lines, altered whitespace inside long JSDoc rationale blocks). The reliable approach:

1. Read the full file once, note exact 1-indexed line ranges for every member (including its JSDoc).
2. Write a Python script that reads the file into a line list, extracts each member by `lines[start-1:end]` with an `assert`-backed substring check (`chk()` helper) confirming the expected signature text is inside that range — this fails loudly if a line range is off by one instead of silently mis-copying.
3. Reassemble in the target order, write once.
4. Verify with `sort file_before | diff - <(sort file_after)` — a reorder-only change produces zero diff on sorted lines; any output means content was lost, duplicated, or altered, not just moved.
5. For final confidence beyond static diffing, reconstruct the pre-change file (from `git show HEAD:<path>` plus any pre-existing uncommitted edits) and run the real Jest suite against both the reconstructed original and the reordered version — identical pass/fail counts and coverage numbers is the actual proof of "no behavior change," since a pure line-sorted diff can't catch reordering that changes runtime meaning (e.g. accidentally moving a method outside the class body, or splitting a decorator from its target).

This technique caught nothing wrong in this session (bds-table reorder was clean), but the discipline is what made it safe to certify "zero behavior change" instead of just asserting it.

**AST-based refinement (2026-10-26, `bds-search-bar.tsx`, 134 members, T53).** Line-range extraction still needs a human to map every range. Faster and stronger: parse both the `git show HEAD:<path>` version and the working copy with the repo's own `typescript` (`require('typescript')` with `NODE_PATH=./node_modules` from the package dir), walk `ClassDeclaration.members`, and compare per member name: (a) sorted name multiset, (b) normalised member text (`m.getFullStart()`..`m.getEnd()`, blank lines and `// ` banner lines stripped, whitespace collapsed), (c) decorator text (`ts.getDecorators(m)`) + declared type text — note `m.getText()` **excludes decorators**, so decorator args must be compared separately or a dropped `@Watch('mode')` goes unnoticed. Then `sort | uniq -c` the whole file's non-banner non-blank lines: identical multisets prove a pure reorder including indentation. Zero-diff on all four + the unchanged Jest suite is a complete proof, and the same script doubles as the before/after member inventory the task's report needs.

**Alphabetical means case-insensitive.** For section ordering, `localeCompare` order (dictionary) is the one to use, not codepoint order: `cancelDebounce` sorts *before* `canShowClear`, and `@typescript-eslint/member-ordering` (the rule `development-standards.md` §1.3 may adopt) compares the same way. Existing components (e.g. `bds-table.tsx` section 2) mix both conventions, so they are not a reliable oracle — only case-pairs like `canShow*`/`cancel*` are affected.

See also: [[feedback_stale_baseline_numbers_in_task_prompts]].
