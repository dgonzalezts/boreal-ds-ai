# Stencil Best Practices vs Development Standards §1 — Dedup Audit

**Date:** 2026-06-15  
**Files read:**
- `ai-docs/guidelines/stencil-best-practices.md` (737 lines)
- `ai-docs/guidelines/development-standards.md` §1 (lines 14–598)

**Purpose:** Identify overlapping sections and produce a recommended action for each. No edits made in this task — user reviews and approves before any changes are applied.

---

## Dedup Map

| Section | In `stencil-best-practices.md` | In `development-standards.md` | Unique content? | Recommended action |
|---|---|---|---|---|
| Style Encapsulation (`scoped` vs `shadow` vs none) | Lines 1–101 | Not present | **Yes** — encapsulation comparison table, SSR behavior, CSS custom properties note | Keep in BP |
| Light DOM: direct tag selectors, not `:host` | Lines 104–136 | Brief mention in §1.2 naming table only ("Shadow Parts not applicable") | **Yes** — full `:host` gotcha explanation with code examples | Keep in BP |
| Global SCSS Utilities (`_commons.scss`, `_interactions.scss`, `@use` rules) | Lines 139–238 | Not present | **Yes** — `%flex-center`, interaction mixin table, three `@use` constraint rules | Keep in BP |
| `@Prop()` type declaration — constant default rule | Lines 241–254 | §1.4 lines 332–354 | **Partial** — DS has the rule; BP additionally has "when/when NOT to use defaults" rationale table and the Stencil+wrapper note about `reflect: true` + false/undefined | Delegate rule to DS; keep "when/when not" and wrapper note only in BP |
| Boolean prop naming | Lines 292–308 | §1.2 lines 140–155 | **No** — same content, different table format | Delegate to DS; replace BP section with one-line pointer |
| Custom event naming | Lines 310–327 | §1.2 naming table (one row) + §1.5 reserved `valueChange` note | **Partial** — DS has the format rule; BP has the three-failure explanation for native DOM event name collisions (type-contract violation, duplicate dispatch, framework binding collision) | Delegate naming format to DS; keep the three-failure explanation in BP |
| FACE components (`@AttachInternals`, `@Method` wrappers, constraint validation) | Lines 337–408 | §1.1 mixin section (decorator placement), §1.4 disabled mirror | **Partial** — DS covers `@AttachInternals` placement and `disabled` mirror; BP has unique gotchas: `formDisabledCallback` trigger conditions (`<fieldset disabled>` only, not `form.disabled`), `HTMLButtonElement.prototype.checkValidity` collision with test harness functions, doubled validation events via `required` on inner `<input>`, focus delegation steps | Delegate `@AttachInternals` and disabled mirror to DS; keep FACE gotchas section in BP |
| Component class member ordering (15-section table) | Lines 411–482 | §1.3 lines 172–297 | **Partial** — both have the 15-section table; DS has a Mermaid lifecycle diagram + reference skeleton + enforcement notes; BP has three separate lifecycle tables (initial / update / disconnect) that are slightly more detailed than the Mermaid diagram | ✅ **Applied** — lifecycle tables collapsed to one-line pointer to DS §1.3 Mermaid diagram |
| Alphabetical ordering within sections | Lines 467–482 | §1.3 line 196 (one sentence) | **Partial** — DS mentions it; BP has a code example | Merge BP example into DS; remove duplicate from BP |
| Guarding reflected `@Prop` writes inside `@Watch` cycles | Lines 486–517 | Not present | **Yes** — equality guard pattern + Stencil warning explanation + test-environment `suppressConsoleWarn()` note | Keep in BP |
| Event listener placement (vDOM vs `@Listen` vs `addEventListener`) | Lines 521–582 | Not present | **Yes** — decision table with 6 dimensions, code examples for all three approaches | Keep in BP |
| Composite light DOM event boundary | Lines 586–606 | Not present | **Yes** — `stopPropagation()` rule for composite components + duplicate event detection via Storybook Actions panel | Keep in BP |
| DOM API: `setAttribute` requires kebab-case for ARIA | Lines 610–624 | Not present (in memory + now in code-review-checklist.md) | **Yes** — explanation of camelCase property vs attribute distinction | Keep in BP |
| Accessor naming (no `get` prefix) + `\|\| false` redundancy | Lines 628–654 | Not present | **Yes** — both conventions with examples | Keep in BP |
| Mixin architecture table + when to add a mixin + anti-patterns | Lines 658–683 | §1.1 lines 18–115 | **Partial** — DS is the more complete source (has Mermaid diagram, form component code example, "Why Mixins Instead of Base Classes" explanation); BP has the same table and rules but no unique content | Delegate to DS; replace BP section with one-line pointer |
| `IComponent.ts` interface contract | Lines 687–713 | §1.4 lines 429–454 | **No** — nearly identical content and code examples | Delegate to DS; replace BP section with one-line pointer |
| `IFormControl<T>` interface layering | Lines 716–736 | §1.6 lines 577–595 | **No** — same interface table and code example | Delegate to DS; replace BP section with one-line pointer |

---

## Summary

**Sections that are duplicated and should delegate to `development-standards.md`:**

| Section | Delegate to |
|---|---|
| Boolean prop naming | DS §1.2 |
| Mixin architecture (basic table + anti-patterns) | DS §1.1 |
| `IComponent.ts` interface contract | DS §1.4 |
| `IFormControl<T>` interface layering | DS §1.6 |
| `@Prop()` constant-default rule (the rule itself) | DS §1.4 |
| Custom event naming format | DS §1.2 + §1.5 |
| `@AttachInternals()` placement rule | DS §1.1 |
| `disabled` `@State()` mirror pattern | DS §1.4 |

**Sections that are unique to `stencil-best-practices.md` and must stay:**

| Section | Why it stays |
|---|---|
| Style encapsulation (scoped/shadow/none) | Not in DS; architectural reference |
| Light DOM `:host` gotcha | Not in DS; non-obvious compilation behavior |
| Global SCSS utilities + `@use` constraint rules | Not in DS; project-specific SCSS setup |
| `@Prop()` "when / when NOT to use defaults" | DS has the rule; BP has the rationale table |
| Native event collision three-failure explanation | Not in DS; only naming format is there |
| FACE gotchas (formDisabledCallback, doubled validation, `@Method` wrappers) | Not fully in DS; critical runtime bugs |
| Guarding reflected `@Prop` writes in `@Watch` | Not in DS |
| Event listener placement decision table | Not in DS |
| Composite light DOM event boundary | Not in DS |
| DOM API ARIA `setAttribute` gotcha | Not in DS |
| Accessor naming + `\|\| false` conventions | Not in DS |

---

## Proposed edit scope (pending user approval)

If approved, the edits to `stencil-best-practices.md` would be:

1. **Delete** the Boolean prop naming section → replace with: _"See [`development-standards.md §1.2`](./development-standards.md#12-component-naming-conventions)."_
2. **Delete** the Mixin architecture section → replace with: _"See [`development-standards.md §1.1`](./development-standards.md#11-component-architecture--inheritance)."_
3. **Delete** the `IComponent.ts` section → replace with: _"See [`development-standards.md §1.4`](./development-standards.md#14-properties--attributes)."_
4. **Delete** the `IFormControl<T>` section → replace with: _"See [`development-standards.md §1.6`](./development-standards.md#16-developing-for-output-targets)."_
5. **Trim** the `@Prop()` type declaration section → keep "when/when not to use defaults" rationale and the wrapper note; remove the constant-default rule (pointer to DS §1.4).
6. **Trim** the custom event naming section → keep the three-failure native-event explanation; remove the `bds{Action}` format table (pointer to DS §1.2).
7. **Trim** the FACE section → keep `@Method` wrappers, doubled validation, `formDisabledCallback` trigger quirks; remove `@AttachInternals` placement rule and `disabled` mirror (pointer to DS §1.1 / §1.4).
8. **Member ordering section** — decision needed: keep BP's three lifecycle tables (more detailed) alongside a pointer to DS, or collapse to pointer only.

**No file changes are made until the user approves this map.**
