# Stencil light-DOM components: unscoped top-level SCSS selectors leak globally

Stencil compiles a component's SCSS straight into that component's global stylesheet — there is no shadow boundary to contain it. A selector left at the top level of a component's SCSS file, outside the root tag block (e.g. `bds-table { }`), is not scoped to that component at all: it becomes a page-wide rule matching any element anywhere in the document, including another component's own markup, from the moment the stylesheet loads.

**Real incident:** `bds-table.scss` and `bds-calendar-grid.scss` (used by `bds-date-picker`) both shipped bare top-level `table { }` / `thead th { }` / `td { }` rules sitting outside their `bds-table { }` / `bds-calendar-grid { }` blocks. Once both components' stylesheets loaded in the same session (trivially reproducible by navigating between their Storybook docs pages, or by rendering both on the same page in a consumer app), each leaked its header-cell padding/width/text-alignment onto the other's `<table>`. Symptom: `bds-calendar-grid`'s weekday header row ("Sun Mon Tue…") wrapped into single letters per line because it was silently using `bds-table`'s header padding instead of its own.

This is **not Storybook-specific** — no navigation, SPA session, or timing is required. Any production page rendering both components at once, on first paint, is affected. It looked timing-dependent at first only because reproducing it required both stylesheets to have loaded at least once in the page's lifetime.

## Fix pattern

Nest every selector in the file under the root tag block, including any separate BEM-class block that may exist alongside it:

```scss
bds-table {
  display: flex;

  table {
    width: 100%;
  }

  thead th {
    padding-inline: $boreal-spatial-padding-m;
  }

  .bds-table {
    &__wrapper { /* ... */ }
  }
}
```

This compiles every previously-bare selector to a real descendant combinator (`bds-table table`, `bds-table thead th`, `bds-table .bds-table__wrapper`), which can only ever match inside an actual `<bds-table>` element.

## How to verify a fix is behavior-preserving

Diff the **compiled** CSS output before/after, not just the source — confirm identical rule-block and declaration counts (only the selector text should change, nothing should be added, removed, or altered in value):

```bash
git stash push -m "pre-fix" -- path/to/component.scss
cd packages/boreal-web-components && eval "$(fnm env --shell bash)" && fnm use && pnpm build
# copy dist/collection/components/.../*.css aside
git stash pop
pnpm build
# diff the two compiled CSS files; grep -c '{' for rule count, grep -cE '^\s+[a-z-]+:' for declaration count
```

## Why this class of bug is hard to catch

- **Unit tests can't see it.** `newSpecPage()` never loads real component CSS into a real DOM — coverage and mutation-testing gates (see `mutation-testing-workflow-decisions.md`) are structurally blind to this failure mode regardless of score.
- **Single-component QA can't see it either** — the bug only manifests when two (or more) components sharing a native-element selector are mounted in the same page/session. Testing either component in isolation looks completely correct.
- **Static review of `.tsx`/`.ts` misses it** — the defect lives entirely in `.scss`, which the `code-reviewer` skill's checker did not scan as of this writing (see `stencil-scss-selector-scoping-review-rule.md` if a check was later added).

## Prevention checklist (apply proactively, not just when debugging a report)

1. Before finishing any component SCSS edit, re-read the file and confirm every selector is indented under the root tag block — a selector at column 0 (not nested) is a scoping bug regardless of how correct its declarations are.
2. If the component renders a common native element also used elsewhere (`table`, `input`, `button`, `dialog`, etc.), proactively test it side-by-side with any other component known to render the same element, in one browser session — don't wait for a bug report.
3. See `ai-docs/guidelines/stencil-best-practices.md` §"Every selector must nest inside the root tag block" for the canonical positive/negative example.
