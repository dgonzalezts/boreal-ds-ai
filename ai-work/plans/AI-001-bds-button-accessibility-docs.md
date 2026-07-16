---
ticket: AI-001
component: bds-button
status: done
created: 2026-07-15
---

# bds-button Accessibility & Documentation Improvements

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Add development-time accessibility diagnostics and clarify `label` prop documentation to prevent inaccessible icon-only button usage.

**Ticket brief:** [`ai-work/tickets/AI-001-bds-button-accessibility-docs.md`](../tickets/AI-001-bds-button-accessibility-docs.md)

**Architecture:** Add unconditional `console.info`/`console.warn` diagnostics in `componentDidLoad`, using the existing (previously unused) `hasSlotContent` utility to detect accessible-name gaps. Update JSDoc on `label` prop. Add a Storybook story and MDX docs section for the icon-only button pattern.

**Tech Stack:** Stencil, TypeScript, SCSS, Storybook, MDX, Jest

**Corrected from an earlier draft:** this version fixes factual errors verified against the real codebase — the test directory is `__test__` (singular, not `__tests__`), Storybook/MDX files live in `apps/boreal-docs/src/stories/actions/bds-button/` (not inside the component package), `label` has no `reflect` option, and there is no `process.env.NODE_ENV` dev-gating convention anywhere in `packages/boreal-web-components/src` — confirmed by exhaustive grep. Warnings are unconditional, matching the only real precedent in this file (`processFormClick`'s warning).

---

## Files to create / modify

| File | Notes |
| --- | --- |
| `packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx` | Modify — add `checkAccessibleName()` diagnostic in `componentDidLoad`, update JSDoc on `label` prop |
| `packages/boreal-web-components/src/components/actions/bds-button/__test__/bds-button-a11y.spec.ts` | Modify — extend with diagnostic warning/info test cases |
| `apps/boreal-docs/src/stories/actions/bds-button/bds-button.stories.ts` | Modify — add `IconOnlyButton` story, sync `label` argType description |
| `apps/boreal-docs/src/stories/actions/bds-button/bds-button.mdx` | Modify — add icon-only accessibility guidance to existing Accessibility section |

---

### Task 1: Update JSDoc on `label` prop and sync Storybook description

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx` (modify)
- `apps/boreal-docs/src/stories/actions/bds-button/bds-button.stories.ts` (modify)

**Acceptance criteria:**

- Update the `label` prop's JSDoc (currently `/** The accessible name for the button, used for screen readers. It should be provided by the user for accessibility purposes. */`) to:
  ```ts
  /**
   * The accessible name for the button, used for screen readers.
   * For accessibility only - does not render visible text. Use the default slot for visible button content.
   */
  ```
- Do NOT add a `reflect` option — the prop has none today and none should be introduced.
- Find and update the duplicated `label` description string in `bds-button.stories.ts`'s `argTypes` (Storybook descriptions are manually duplicated in this codebase, not derived from JSDoc) so both stay in sync.

**Unit tests to cover:** None (documentation only).

**Manual test:**

- Run `pnpm build` (or the package's build script) and confirm it compiles without errors.
- Confirm the updated JSDoc appears on hover in an IDE / in generated `.d.ts` output.

Validation checklist:
- [ ] Build compiles cleanly
- [ ] JSDoc text matches exactly

---

### Task 2: Add `checkAccessibleName()` diagnostic wired into `componentDidLoad`

**Executor:** @frontend-subagent
**Files:**

- `packages/boreal-web-components/src/components/actions/bds-button/bds-button.tsx` (modify)

**Acceptance criteria:**

- Extend the existing `@/utils` barrel import to include `hasSlotContent` (from `packages/boreal-web-components/src/utils/dom/elements.ts` — this is its first real consumer in the codebase; no other component uses it yet).
- Add a private method:
  ```ts
  private checkAccessibleName() {
    const hasDefaultSlotContent = hasSlotContent(this.el);
    const iconEl = this.el.querySelector('[slot="icon"]');
    const iconHasOwnAccessibleName = Boolean(
      iconEl?.hasAttribute('aria-label') || iconEl?.hasAttribute('aria-labelledby'),
    );

    if (this.label && !hasDefaultSlotContent && iconEl !== null) {
      console.info(
        '[BorealDS Button] Icon-only button detected: the "label" prop provides the accessible name and no visible text will render.',
      );
      return;
    }

    const hasAccessibleName = Boolean(this.label) || hasDefaultSlotContent || iconHasOwnAccessibleName;
    if (!hasAccessibleName) {
      console.warn(
        '[BorealDS Button] No accessible name found. Provide a "label" prop, visible text in the default slot, or an aria-label/aria-labelledby on the icon slot content.',
      );
    }
  }
  ```
- Call `this.checkAccessibleName()` from the existing `componentDidLoad()`, alongside `setupFormAssociation()` and `setupKeyboard()`.
- No `NODE_ENV` gating — warnings/info fire unconditionally, matching the existing `processFormClick` precedent in this same file.
- No new `@State` property — this is a one-time diagnostic side effect, not something that drives re-render.
- Use `console.info` (not `console.warn`) for the icon-only confirmation case — it signals expected, valid usage, not a defect. Reserve `console.warn` for the genuine "no accessible name at all" failure.

**Unit tests to cover** _(see Task 3 — do not write tests in this task)_

**Manual test:**

Run `pnpm dev:docs` from the monorepo root, open the browser console, and verify against these four scenarios:
- `label` set + icon slot + no default slot content → `console.info` fires with the icon-only message
- No `label`, no default slot content, no icon slot → `console.warn` fires with the no-accessible-name message
- No `label`, icon slot present with its own `aria-label` → no console output
- `label` set + default slot has visible text → no console output

Validation checklist:
- [ ] All four scenarios behave as specified
- [ ] No warnings/info fire for any other existing bds-button story (spot check the Storybook gallery)

---

### Task 3: Add unit tests for accessible-name diagnostics

**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/src/components/actions/bds-button/__test__/bds-button-a11y.spec.ts` (modify)

**Acceptance criteria:**

- Add a `describe('accessible name diagnostics', ...)` block to the existing file.
- Use manual `jest.spyOn(console, 'info').mockImplementation(() => {})` / `jest.spyOn(console, 'warn').mockImplementation(() => {})` (not the `suppressConsoleWarn()` helper from `utils/testing/mocks/console.ts`, since these tests assert on exact call arguments).
- Cover all 7 cases:
  1. `label` set, no default slot content, icon slot present → `console.info` called with the icon-only message; `console.warn` NOT called.
  2. No `label`, no default slot content, no icon slot → `console.warn` called with the no-accessible-name message.
  3. No `label`, no default slot content, icon slot present without `aria-label`/`aria-labelledby` → `console.warn` called.
  4. No `label`, no default slot content, icon slot present **with** `aria-label` → no warning, no info.
  5. `label` set, default slot has visible text → no warning, no info.
  6. No `label`, default slot has visible text → no warning, no info.
  7. `label` set, no default slot, no icon slot at all → no warning (label alone satisfies accessible name), no info (icon-only branch requires an icon element to be present).
- Follow the existing `newSpecPage` HTML-string pattern used in this file / `bds-button-slots.spec.ts`.
- Meet the project's two-phase quality gate: ≥90% coverage and ≥90% mutation score for the new branches (per `.claude/skills/mutations-testing` / `testing-knowledge` conventions).

**Manual test:**

- Run the component's Jest suite scoped to `bds-button` and confirm all cases pass.
- Confirm coverage/mutation thresholds hold.

Validation checklist:
- [ ] All 7 cases pass
- [ ] Coverage ≥90%
- [ ] Mutation score ≥90% for new branches

---

### Task 4: Add Storybook story for icon-only button

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/actions/bds-button/bds-button.stories.ts` (modify)

**Acceptance criteria:**

- Add a new export after the existing `ButtonWithIcon` story, following the file's existing `Story` pattern exactly (no `name:` override — confirmed decision, let Storybook auto-format the title from the export name):
  ```ts
  export const IconOnlyButton: Story = {
    args: {
      label: 'Delete item',
      slotIcon: true,
      slotDefault: '',
    },
    render: renderButton,
  };
  ```

**Manual test:**

- Run `pnpm dev:docs`, navigate to the bds-button stories, confirm `IconOnlyButton` renders correctly, controls work, and `console.info` fires as expected (per Task 2).

Validation checklist:
- [ ] Story appears and renders
- [ ] Controls function correctly
- [ ] Expected console output confirmed

---

### Task 5: Update MDX documentation with icon-only accessibility guidance

**Executor:** @documentation-subagent
**Files:**

- `apps/boreal-docs/src/stories/actions/bds-button/bds-button.mdx` (modify)

**Acceptance criteria:**

- Do NOT add a new top-level section — the file already has a `<Subtitle>Accessibility</Subtitle>` section. Add content inside it.
- Add a bullet subsection covering:
  - `label` is for accessibility only and never renders visible text
  - Pair `label` with the `icon` slot and leave the default slot empty for icon-only buttons
  - The component logs `console.info`/`console.warn` diagnostics in development to help catch missing accessible names
  - A short code example showing the correct icon-only pattern
- Add the new story to the component preview gallery (near the existing `### With Icon` section):
  ```mdx
  ### Icon-only button
  <Description of={BdsButtonStories.IconOnlyButton} />
  <Canvas of={BdsButtonStories.IconOnlyButton} />
  ```
- Follow existing MDX formatting/tone in the file.

**Manual test:**

- Run `pnpm dev:docs`, navigate to the bds-button docs page, confirm the new subsection and Canvas render without MDX errors.

Validation checklist:
- [ ] Accessibility subsection renders correctly
- [ ] Code example renders correctly
- [ ] New story Canvas renders without errors

---

## Execution Handoff

Executing in-session via `executing-plans` skill, dispatching each task to its declared `**Executor:**` subagent, in an isolated worktree at `.worktrees/ai-001-bds-button-a11y` (branch `feature/AI-001-bds-button-accessibility-docs`). Commits are left for the user to review and create manually — no automatic commits per task.
