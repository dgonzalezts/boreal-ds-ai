---
name: nested-template-literal-double-backslash-escaping
description: Inline <script> content inside a story's render:-function Lit html`` template must double-escape backslashes (\\n, \\t, etc.) — single-escaped versions silently become real control characters and can break regex literals mid-source.
metadata:
  type: project
---

`bds-table.stories.ts` (and any other `.stories.ts` using the `render: args => html\`...<script>...</script>\`` pattern) nests a second "virtual" JS source — the inline `<script>` tag's text content — inside the outer TypeScript template literal that Lit's `html` tag processes. Any `\n`, `\t`, etc. written literally in that inner script (intending it to appear as a two-character escape sequence in the *emitted* script text) is instead consumed by the **outer** JS parser at TypeScript-compile time and turned into a real control character before Storybook ever sees the string.

This is invisible in code review — the source looks correct — and does not throw at build time. It only breaks when the story actually mounts, with an opaque runtime error, e.g.:

```
SyntaxError: Failed to execute 'appendChild' on 'Node': Invalid regular expression: missing /
```

That specific error came from `/[",\n]/.test(str)` inside a CSV-escaping helper (`WithExport` story, EOA-16000 Task 14) — the real newline produced by `\n` split the regex literal across two lines, which is illegal (an unescaped raw newline inside `/.../ ` terminates the literal without a closing `/`).

**Fix:** inside a `render:`-function's inline `<script>` block, always write `\\n` (and other escapes doubled) to get a literal `\n` in the emitted script. The `parameters.docs.source.code` string (the separate "Show code" snippet, also a template literal at the same nesting level) needs the same double-escaping — it's easy to get right there by copy/analogy and then forget to mirror it into the actual `render:` script, which is what happened here.

**Verification:** a source diff or `tsc` pass will not catch this — the story must actually be mounted in a running Storybook (or headless browser hitting `/iframe.html?id=...`) and its console checked for a `SyntaxError` before the task is considered done. Data silently failing to render (e.g. "No data to display" when rows were assigned) is the visible symptom if the break happens before the data-assignment line executes.
