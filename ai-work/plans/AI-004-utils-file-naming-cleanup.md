---
status: pending
component: utils
created: 2026-08-13
---

# `src/utils/` File Naming Cleanup

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Remove dead duplicate mock files and standardize the casing convention for function-exporting utility modules in `packages/boreal-web-components/src/utils/`, so the same file role is named the same way everywhere.

**Origin:** Surfaced during `bds-date-picker` (`EOA-16692`) implementation, Task 4/5 checkpoint — the user asked whether the package follows consistent file-naming standards. Audit found `src/components/` and `src/services/` are internally consistent (component `.tsx` files kebab-case matching their tag, interface files `IComponent.ts`, function modules PascalCase-for-classes / lowercase-for-functions), but `src/utils/` has two real, unrelated-to-this-ticket problems documented below. This is a standalone cleanup, out of scope for the date-picker plan.

## Findings

### 1. Dead duplicate mock file

`utils/testing/mocks/backdrop.ts` and `utils/testing/mocks/backdrop-mock.ts` are **byte-identical** (confirmed via `diff`) and **neither is imported anywhere in the repo** (confirmed via repo-wide grep). This is leftover from a rename to the `*-mock.ts` suffix convention that never deleted the original file.

### 2. Inconsistent casing for function-exporting utility modules

Files in the same `utils/` tree, exporting the same kind of thing (plain functions/constants, not a class or component), split roughly evenly between camelCase and kebab-case with no correlation to role:

| Casing | Files |
| --- | --- |
| camelCase | `utils/countries/countryFunctions.ts`, `utils/helpers/overlays/getOffset.ts`, `utils/helpers/validateProps.ts`, `utils/dom/sanitizer/html/sanitizerConfig.ts`, `utils/dom/sanitizer/html/sanitizerFactory.ts`, `utils/dom/sanitizer/url/sanitizerFactory.ts`, `utils/dom/sanitizer/url/urlSanitizer.ts`, `utils/testing/mocks/animationFrame.ts`, `utils/testing/mocks/dragDrop.ts`, `utils/testing/mocks/elementInternals.ts`, `utils/testing/mocks/pointerCapture.ts`, `utils/testing/mocks/fileMock.ts` |
| kebab-case | `utils/a11y/keyboard/focus/aria-activedescendant.ts`, `utils/a11y/keyboard/focus/resolve.ts` (single word, uninformative either way), `utils/a11y/keyboard/focus/roving-tabindex.ts`, `utils/a11y/keyboard/navigation/grid-navigation.ts`, `utils/a11y/keyboard/navigation/linear-navigation.ts`, `utils/dom/virtualScroll/virtual-scroll.ts`, `utils/form/field-form-association.ts`, `utils/testing/mocks/backdrop-mock.ts`, `utils/testing/mocks/popover-mock.ts` |

The `testing/mocks/` directory additionally has two competing suffix styles for the identical concept: `*-mock.ts` (`backdrop-mock.ts`, `popover-mock.ts`) vs. `*Mock.ts` (`fileMock.ts`).

**Recommendation: standardize on kebab-case.** It's the more common pattern in this specific tree (`utils/a11y/keyboard/` — the newest, most actively maintained subtree — is fully kebab-case), matches the `services/` sibling's function-module convention (`positioning.service.ts`), and matches `src/services/date-engine/`'s files added by the in-flight `EOA-16692` plan (`grid.ts`, `date-math.ts` — single-word, casing-neutral, but multi-word additions there would follow kebab-case). This is a recommendation, not yet confirmed — Task 2 below is a checkpoint to confirm before any renames happen.

**Out of scope:** `src/components/` (already consistent, confirmed by direct user judgment) and the broader `development-standards.md` §3.3 "No Barrel Files" documentation gap (the guideline forbids `index.ts` barrels; the codebase — `services/floating/index.ts`, `services/logger/index.ts`, most component `types/index.ts` files — doesn't follow that rule. Already resolved separately for `date-engine`'s own barrel file: codebase precedent wins, per explicit user decision on 2026-08-13. Not part of this cleanup unless the user asks for the guideline itself to be corrected.)

## Files to modify

| File | Notes |
| --- | --- |
| `packages/boreal-web-components/src/utils/testing/mocks/backdrop.ts` | Delete — dead duplicate |
| `packages/boreal-web-components/src/utils/countries/countryFunctions.ts` → `country-functions.ts` | Rename; 1 importer |
| `packages/boreal-web-components/src/utils/helpers/overlays/getOffset.ts` → `get-offset.ts` | Rename; 3 importers |
| `packages/boreal-web-components/src/utils/helpers/validateProps.ts` → `validate-props.ts` | Rename; 5 importers |
| `packages/boreal-web-components/src/utils/dom/sanitizer/html/sanitizerConfig.ts` → `sanitizer-config.ts` | Rename; 1 importer |
| `packages/boreal-web-components/src/utils/dom/sanitizer/html/sanitizerFactory.ts` → `sanitizer-factory.ts` | Rename; check importers (distinct from the `url/` sibling below) |
| `packages/boreal-web-components/src/utils/dom/sanitizer/url/sanitizerFactory.ts` → `sanitizer-factory.ts` | Rename; check importers (same target basename, different directory — not a collision) |
| `packages/boreal-web-components/src/utils/dom/sanitizer/url/urlSanitizer.ts` → `url-sanitizer.ts` | Rename; 3 importers |
| `packages/boreal-web-components/src/utils/testing/mocks/animationFrame.ts` → `animation-frame.ts` | Rename; 0 importers (verify still unused before renaming, otherwise flag as dead code instead) |
| `packages/boreal-web-components/src/utils/testing/mocks/dragDrop.ts` → `drag-drop.ts` | Rename; 2 importers |
| `packages/boreal-web-components/src/utils/testing/mocks/elementInternals.ts` → `element-internals.ts` | Rename; 1 importer |
| `packages/boreal-web-components/src/utils/testing/mocks/pointerCapture.ts` → `pointer-capture.ts` | Rename; 1 importer |
| `packages/boreal-web-components/src/utils/testing/mocks/fileMock.ts` → `file-mock.ts` | Rename; 1 importer — also aligns its suffix with `backdrop-mock.ts`/`popover-mock.ts` |

Import counts above were measured via repo-wide grep on 2026-08-13; re-verify at execution time in case other tasks (e.g. the in-flight `EOA-16692` work) have added new references.

## Task 1: Remove the dead duplicate mock file

**Executor:** @frontend-subagent
**Files:**
- `packages/boreal-web-components/src/utils/testing/mocks/backdrop.ts` (delete)

**Acceptance criteria:**
- Confirm again at execution time (repo may have changed) that `backdrop.ts` and `backdrop-mock.ts` are still byte-identical and `backdrop.ts` still has zero importers repo-wide.
- Delete `backdrop.ts`. Do not touch `backdrop-mock.ts`.

**Manual test (required):**
Non-visual task — validate via `pnpm --filter boreal-web-components test` (full suite) passing with no new failures, and `pnpm --filter boreal-web-components exec tsc --noEmit` showing no new errors.

**Commit:**
```bash
git commit -m "chore(boreal-web-components): remove dead duplicate backdrop mock file"
```

---

## Task 2: Confirm the kebab-case convention before renaming

**Executor:** main thread (no executor — a decision checkpoint, not a code task)
**Files:** none

**Acceptance criteria:**
- Present the Findings section's recommendation (kebab-case) to the user for explicit confirmation before Task 3 renames anything, per this project's plan-execution rule on surfacing assumptions early.
- If the user prefers camelCase instead, invert Task 3's rename list (kebab-case files become the rename targets, not the camelCase ones) before proceeding.

**Manual test (required):** N/A — decision checkpoint only.

**Commit:** N/A — no files change in this task.

---

## Task 3: Rename camelCase utility files to kebab-case

**Executor:** @frontend-subagent
**Files:** all camelCase files listed in the Files table above (11 renames)

**Acceptance criteria:**
- Each file renamed via `git mv` (preserves history) to its kebab-case equivalent listed in the Files table.
- Every import statement referencing the old filename updated to the new one, repo-wide (`packages/boreal-web-components` and any cross-package references, e.g. from `apps/boreal-docs` if applicable — verify via grep before assuming none exist).
- No barrel `index.ts` re-export needs updating unless it explicitly names the old filename in an `export ... from './oldName'` statement (check each directory's `index.ts` before and after).
- `fileMock.ts` → `file-mock.ts` additionally aligns its suffix style with the two existing `*-mock.ts` files in the same directory (`backdrop-mock.ts`, `popover-mock.ts`) — confirm the directory now has one consistent mock-suffix convention, not three.

**Unit tests to cover:**
- No new tests required — this is a pure rename with no behavior change. Existing test suites must continue passing unmodified (aside from updated import paths inside spec files themselves, if any spec imports these files directly).

**Manual test (required):**
Non-visual task — validate via:
- `pnpm --filter boreal-web-components exec tsc --noEmit` passing with no new errors (a broken import path surfaces here immediately).
- `pnpm --filter boreal-web-components test` (full suite) passing with no new failures or a changed test count (a rename shouldn't add/remove any test).
- `pnpm --filter boreal-web-components lint` clean.

**Commit:**
```bash
git commit -m "chore(boreal-web-components): standardize utils/ function-module files to kebab-case"
```

---

## Task 4: Document the finalized convention

**Executor:** @documentation-subagent
**Files:**
- `ai-docs/guidelines/development-standards.md` (modify)

**Acceptance criteria:**
- Add a short, general file-naming subsection (not tied to this cleanup's ticket/history) under §3.3 or a new §3.4, stating the convention actually enforced going forward: component `.tsx` files kebab-case matching the tag (already documented in §1.2); component interface/enum/type files per the existing `IComponent.ts`/`enum.ts`/`types.ts` pattern (already documented); non-component modules exporting a class or singleton use PascalCase matching the export name; non-component modules exporting functions/constants use kebab-case.
- Do not reference this cleanup plan, ticket IDs, or "we found an inconsistency" framing — state the convention as a rule, the way the rest of the document does.

**Manual test (required):**
Read the updated section and confirm it's internally consistent with the rest of §3.3 and doesn't contradict anything in §1.2.

**Commit:**
```bash
git commit -m "docs(development-standards): document utils/ file naming convention"
```

## Verification

- **Automated:** `pnpm --filter boreal-web-components test` (full suite) and `pnpm --filter boreal-web-components exec tsc --noEmit` after every task, per this project's plan-execution convention.
- **Manual:** no visual/behavioral changes in this plan — no `pnpm dev:components`/`pnpm dev:docs` walkthrough needed, since renames and a doc update carry no runtime behavior change.
