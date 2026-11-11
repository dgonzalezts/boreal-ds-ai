---
name: docs-app-gates-and-html-pragma-indent
description: The docs app has no working tsc gate (`ignoreDeprecations: "6.0"` is invalid for TS 5.9); gate story/MDX changes with eslint + prettier + `pnpm --filter @pxglobal/boreal-docs build`. Also — Prettier's `/* HTML */` pragma indents a snippet that contains a `<script>` block.
metadata:
  type: project
---

Two verified facts for finishing any story/MDX task in `apps/boreal-docs` (measured 2026-10-26,
EOA-19597 T16).

**1. There is no usable TypeScript gate for the docs package.**

`apps/boreal-docs/package.json` has no `typecheck` script, and a bare
`pnpm --filter @pxglobal/boreal-docs exec tsc --noEmit` fails before checking anything:

```
tsconfig.json(4,27): error TS5103: Invalid value for '--ignoreDeprecations'.
```

`apps/boreal-docs/tsconfig.json` sets `"ignoreDeprecations": "6.0"`, which TS 5.9 rejects (it
accepts `"5.0"`). Passing `--ignoreDeprecations 5.0` on the CLI overrides the config value and gives
a real typecheck:

```bash
.agents/scripts/with-node.sh pnpm --filter @pxglobal/boreal-docs exec tsc --noEmit --ignoreDeprecations 5.0
```

As of 2026-10-26 that run reports exactly one pre-existing error, unrelated to any new work:
`src/stories/feedback/bds-progress-bar/bds-progress-bar.stories.ts(140,11): error TS6133: 'args' is
declared but its value is never read.` Treat "no new errors beyond that one" as the pass condition,
or fix the tsconfig in a dedicated task rather than inside a docs task.

Full gate actually used, all green:

```bash
.agents/scripts/with-node.sh pnpm --filter @pxglobal/boreal-docs exec prettier --check <files>
.agents/scripts/with-node.sh pnpm --filter @pxglobal/boreal-docs exec eslint <files>
.agents/scripts/with-node.sh pnpm --filter @pxglobal/boreal-docs build   # storybook build, ~1-2 min
```

`prettier --check`/`--write` ignores `*.mdx` (`apps/boreal-docs/.prettierignore`), so MDX formatting
is never enforced — `storybook build` compiling the MDX is the only automated check on it.

**2. `/* HTML */` + a `<script>` block changes how Prettier indents the snippet.**

`storybook-patterns.md` says hoisting the pragma-tagged string to a top-level `const` keeps the
embedded HTML flush-left. That holds only for script-free snippets. If the string contains a
`<script>` element, Prettier formats the whole embedded HTML with a 2-space base indent (attributes
at 4, script body at 4):

```ts
const docsSource = /* HTML */ `<bds-search-bar
    id="x"
    placeholder="Search item..."
  ></bds-search-bar>

  <script>
    document.querySelector('#x').items = [];
  </script>`;
```

This is the same shape already committed in `bds-table.stories.ts`
(`rowClickSelectionDocsSource`) and `bds-flag.stories.ts`, so treat it as the project's accepted
format rather than fighting it — and do NOT inline the string inside `parameters.docs.source.code`
to "avoid" it (that reintroduces the deep-indent problem the guideline warns about). In the rendered
Docs panel the snippet still reads flush-left.

**How to apply:** run the three commands above before reporting a docs task done; quote the tsc
command with `--ignoreDeprecations 5.0` (and the one known pre-existing error) rather than running a
bare `tsc` and reporting it as a failure of your change.
