# PR Title

feat(web-components): EOA-12342 implement bds-checkbox-button component

---

# PR Body

Adds `bds-checkbox-button`, a pill-shaped checkbox that toggles independently using `role="checkbox"` semantics, matching the visual language of `bds-radio-button` while supporting multi-select behaviour.

The `bds-radio-button` SCSS was already duplicating the full selectable-button pattern. Rather than copy it a second time, this PR extracts that shared visual language into `forms/_shared/_selectable-button.scss` and replaces the `bds-radio-button` stylesheet with a single `@use` of the mixin. `bds-checkbox-button` then builds on the same foundation, adding its own checked/error state overrides. This keeps both components in sync visually without duplicated token references.

A standalone approach (`@Prop({ mutable: true }) checked`) was considered alongside a controlled approach (`@Prop() checked` + emitted event only). Mutable was chosen to allow the button to function as a fully self-contained standalone element — a future `bds-checkbox-group` can take over group coordination when it exists, at which point checked state will be driven by the parent.

The `bds-radio-group` also picks up a new `joined` prop and test corrections as foundational work aligned with EOA-12342's group-level scope. These are included here because the shared mixin refactor touched `bds-radio-button.scss`, and the group tests were already inconsistent with the component's actual behaviour.

Refs EOA-12342
