# PR Title

docs(boreal-docs): EOA-10057 add bds-text-field Storybook documentation

---

# PR Body

Adds the Storybook MDX documentation page and interactive stories for
`bds-text-field`, completing the three-branch delivery of the text field
component (implementation → unit tests → docs).

The stories file covers all major prop combinations — variants, sizes,
validation states, helper text, char counter, clearable, readonly, and
disabled — as well as a dedicated `FormIntegration` story that exercises
native form participation via FACE. The MDX page documents every prop,
event, slot, and CSS part with usage guidelines and accessibility notes.
Two minor Storybook fixes are also included: a global variable mismatch
in `preview.ts` and missing brand themes in the main navigation sidebar.

This branch was built on top of
`feature/EOA-10057_add_text_field_component_testing_DG`, so all
implementation code and unit tests for the component are already included
through the merge history.

Refs EOA-10057
