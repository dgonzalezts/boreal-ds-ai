> **Jira ID not yet assigned** — file naming convention in this folder is `EOA-#####-slug.md`; replace `EOA-XXXXX` once this is created in Jira. No project/epic convention is defined in this repo (checked `.claude/commands/create-ticket.md` and `CLAUDE.md`); recent commits in this repo use the `EOA` project key.

### Metadata

| Field        | Value                                                                                                  |
| ------------ | ------------------------------------------------------------------------------------------------------ |
| **Type**     | Task                                                                                                   |
| **Priority** | P2 — Medium                                                                                            |
| **Effort**   | L (3–5 d) — spans 5 concerns across 4 components; consider splitting (see Scope risk below)            |
| **Domain**   | Frontend                                                                                               |
| **Labels**   | design-system, boreal-web-components, bds-button, bds-popover, bds-list-menu, bds-badge, documentation |

---

### Title

` : icon state, spacing, list-menu-item alignment, and docs`

---

### Description

#### Background & Motivation

An exploratory session prototyped wiring `bds-button`'s `disclosure` prop to a `bds-popover` + `bds-list-menu` dropdown (single-select and multi-select with a `bds-badge`), to validate whether the existing components support this composition. The approach works — `bds-popover` already auto-discovers `bds-button` as its trigger with no changes needed to `bds-button.tsx` — but the exploration surfaced four concrete gaps that need to be closed before this pattern is production-ready and discoverable.

#### Current Behaviour

1. `bds-button`'s `disclosure` chevron has no visual state change when a slotted dropdown opens/closes, even though `aria-expanded`/`aria-haspopup`/`aria-describedby` are already correctly applied to the button by `bds-popover`.
2. `bds-button`'s default (label) slot and badge slot have no inline padding. A bare `<slot>` can't reliably carry its own spacing since it may project text nodes or multiple elements. Separately, a `bds-badge` slotted into the badge slot (e.g. a multi-select count) has no stable width by default — it shrinks/grows with digit count, which reflows the button as the count changes.
3. Slotting an icon into `bds-list-menu-item`'s `left-content` slot (e.g. a checkmark) previously misaligned against the item's text and, in the `checkable` variant, the checkbox. Exploration validated a fix: switching `left-content`'s icon/text from an `inline-block` + `vertical-align: middle` + `padding-right` model to an `inline-flex` + `gap` + `align-items: center` model resolves the misalignment. The icon font-size was also reduced (from `md` to `sm`), but that rule is scoped to the whole list item via `[class*='bds-icon-']`, not just `left-content` — needs verification it doesn't regress `right-content` icon sizing elsewhere.
4. The button + popover + list-menu dropdown composition (including single-select-closes-on-pick and multi-select-with-badge) has no documented home. `bds-popover.mdx`'s "How to use it" section already documents generic trigger+content composition and is the natural place for this recipe; `bds-button.mdx` currently has no cross-link to it.

**Environment**: Boreal DS `boreal-web-components` package, Storybook docs app (`boreal-docs`).

#### Expected Behaviour / Desired Outcome

- The disclosure chevron rotates 180° (0.3s ease transition) when its slotted `bds-popover` opens, and reverts when it closes.
- Label and badge slot content both receive the same inline padding (validated: `$boreal-spatial-padding-3xs`).
- A `bds-badge` slotted into the badge slot has a stable minimum width (validated: `--bds-badge-min-width: 20px`, set from `bds-button`'s own stylesheet, not inline on the consumer) so the button doesn't visibly reflow as the count's digit count changes.
- Icons in `left-content` align correctly against text and checkbox across all list-menu-item variants, using the validated flex/gap-based alignment model.
- The dropdown composition pattern (single- and multi-select) is documented in `bds-popover.mdx` with a cross-link from `bds-button.mdx`.

#### Constraints & Assumptions

- No changes to `bds-popover`'s or `bds-list-menu`'s public API are in scope — single-select-closes-on-pick already has a correct, precedented implementation pattern (mirrors `bds-select.tsx`'s internal `listenListMenu` handler) and only needs to be documented, not built.
- All spacing/sizing changes must use existing design tokens — no hard-coded values.
- Icon rotation, slot padding, and the list-item alignment model below were validated during exploration; no outstanding design confirmation needed for those values.

---

### Acceptance Criteria

- [ ] `bds-button`'s disclosure chevron rotates 180° with a smooth transition when its slotted `bds-popover` opens, and reverts when it closes.
- [ ] `bds-button`'s default (label) slot and badge slot both have consistent inline padding.
- [ ] A `bds-badge` slotted into `bds-button`'s badge slot has a stable minimum width and doesn't reflow the button as its digit count changes.
- [ ] Icons slotted into `bds-list-menu-item`'s `left-content` align correctly with item text and (in `checkable` variant) the checkbox, using the validated flex/gap-based alignment model, without regressing `right-content` icon sizing.
- [ ] `bds-popover.mdx` includes a dropdown-menu recipe (single-select auto-close, multi-select with badge) under "How to use it".
- [ ] `bds-button.mdx` links to the new `bds-popover.mdx` recipe from its `disclosure` prop documentation.

---

### Non-Functional Requirements

- **Performance**: N/A
- **Security**: N/A
- **Accessibility**: AA — verify `aria-expanded`/`aria-haspopup`/`aria-describedby` remain correct through the full open/close lifecycle (click, keyboard, click-outside), and that icon changes don't introduce new accessible-name issues.
- **Observability**: N/A
- **Scalability**: N/A
- **i18n / l10n**: N/A
- **Backward compatibility**: N/A — additive visual/spacing fixes and documentation only; no prop or event API changes.

---

### Definition of Done

- [ ] Code reviewed and approved by at least one peer
- [ ] All acceptance criteria verified and checked off
- [ ] Automated tests written and passing
- [ ] No new lint, type-check, or build errors introduced
- [ ] Documentation updated where applicable
- [ ] Deployed to the target environment and smoke-tested
- [ ] Relevant stakeholders notified of the change

---

### Out of Scope

- Any new prop/event API on `bds-popover` or `bds-list-menu` for auto-close behaviour — the existing consumer-side `bdsChange` → `closePopover()` pattern is confirmed correct and sufficient.
- A dedicated Storybook story demonstrating the full dropdown composition — `ButtonWithDisclosure` stays a single-prop showcase per existing story conventions; the composition itself lives only in `bds-popover.mdx`.

---

### Dependencies

| Type           | Ticket / Resource | Notes |
| -------------- | ----------------- | ----- |
| **Blocks**     | —                 | —     |
| **Blocked by** | —                 | —     |
| **External**   | —                 | —     |

---

### Testing Guidance

- **Test environment**: local (`pnpm dev:docs`) and Storybook (`boreal-docs`)
- **Test data requirements**: none — static component examples
- **Key scenarios to cover**: full open/close lifecycle via click, keyboard (Enter/Escape), and click-outside; icon alignment across `checkable` × `left-content` × selection-mode combinations; single-select auto-close vs. multi-select stays-open
- **Regression areas**: existing `bds-list-menu-item` icon usage in `right-content`; other components consuming `bds-button`'s default/badge slots

---

### Technical Notes

- `bds-popover` auto-discovers `bds-button` as its trigger via light-DOM `parentElement` traversal against `ANCHORED_TRIGGERS` — no wiring changes needed in `bds-button.tsx` for trigger discovery itself.
- The single-select-closes-on-pick pattern should mirror `bds-select.tsx`'s internal `listenListMenu` handler (listens to `bdsChange`, calls `closePopover()` only for single-select) — treat this as the reference implementation for the documentation recipe, not something to re-derive.
- The `left-content` icon alignment fix should follow the validated model: `inline-flex` + `gap` on `.bds-list-item__content-left` + `align-items: center` on the icon wrapper, replacing the old `inline-block` + `vertical-align: middle` + `padding-right` approach.
- `bds-badge` exposes `--bds-badge-min-width` (default `auto`) as a CSS custom property, following this codebase's established pattern for optional dimension overrides (e.g. `--bds-list-menu-max-width`, `--bds-text-field-width`). `bds-button` should set it from its own stylesheet, scoped to `.bds-button__content-badge bds-badge`, rather than requiring consumers to inline-style it.

---

### Links & References

| Type                 | URL / Reference                                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Design / Figma       | [TO BE DEFINED]                                                                                                                       |
| Related ticket       | —                                                                                                                                     |
| API / spec / schema  | `apps/boreal-docs/src/stories/overlays/bds-popover/bds-popover.mdx`, `apps/boreal-docs/src/stories/actions/bds-button/bds-button.mdx` |
| Runbook / playbook   | —                                                                                                                                     |
| Monitoring dashboard | N/A                                                                                                                                   |

---

### Comments & Notes

> 📝 **Scope risk**: This ticket bundles five independent fixes across four components plus documentation. Consider splitting into: (1) disclosure icon rotation, (2) button slot spacing and badge min-width, (3) list-menu-item icon alignment, (4) popover dropdown-recipe documentation — each is independently shippable and testable.
