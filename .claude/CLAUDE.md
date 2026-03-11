# Claude Code — Project Memory

## Codebase Memory

Non-obvious facts, discovered constraints, and verified patterns that have surfaced during implementation sessions are stored as topic files under `.claude/memory/`. Always read the index before starting work on a new component or infrastructure area:

```
.claude/memory/MEMORY.md
```

Key topic files currently available:

- `.claude/memory/stencil-face-attach-internals.md` — `@AttachInternals()` must be on the component class body, never in a mixin factory
- `.claude/memory/stencil-face-element-proxy-limits.md` — Stencil's element proxy blocks native FACE prototype members; use `@Method()` wrappers
- `.claude/memory/stencil-face-constraint-validation-pattern.md` — how to avoid doubled validation events; `IFormValidator` / `customValidators` pattern
- `.claude/memory/stencil-async-rendering-gotchas.md` — async DOM reflection, `formDisabledCallback` trigger conditions, naming collision gotcha

---

## General Instructions

### Always verify npm package versions before specifying them

Before writing any version number for an npm dependency into a plan, `package.json`, or installation command, **always fetch the latest version from the official npm registry**:

```
https://registry.npmjs.org/<package-name>/latest
```

Fetch all required packages **in parallel** using WebFetch, extract the `"version"` field from each response, and use those verified values. Never guess or use recalled version numbers — they will be stale.

Apply this rule to:

- Plan documents (`.ai/plans/`)
- `package.json` files (root and per-package)
- Installation command instructions given to the user
- Any `pnpm add`, `npm install`, or `yarn add` commands

The recommended installation pattern at the workspace root is:

```bash
pnpm add -D -w <package>@latest ...
```

Using `@latest` at install time ensures pnpm resolves the true latest and pins the exact resolved version in `pnpm-lock.yaml`.

### Always use the correct Node.js version via fnm

This project uses **fnm** (Fast Node Manager) to manage Node.js versions. Before executing any shell command that invokes Node.js, pnpm, or project scripts, always run:

```bash
fnm use
```

This reads the project's `.node-version` file at the workspace root and activates the correct version. Never rely on the system default Node.js version — it will be stale and cause `WARN Unsupported engine` errors or runtime failures.

### Always offer the user a choice for running commands

When a task involves running shell commands (installs, builds, scripts, deletions, etc.), **always present the user with two options before proceeding**:

1. **Run it yourself** — provide the exact command(s) for the user to copy-paste and run manually in their terminal
2. **Let Claude run it** — offer to execute the command(s) directly using the Bash tool

Use AskUserQuestion to present this choice when the command is non-trivial or has side effects (e.g. installs, deletions, file generation). For clearly safe read-only commands (e.g. `ls`, `cat`, `git log`), Claude may run them directly without asking.

### Always verify technology docs before writing configuration or code

Before writing configuration files, schemas, or integration code for any specific technology (e.g. Turborepo, Vite, Stencil, ESLint, pnpm, Changesets), **always fetch the official documentation** for that technology to confirm:

- The correct schema, field names, and API surface for the current version
- Whether any fields are deprecated or renamed between versions
- The official recommended patterns and gotchas

Use WebFetch to retrieve the relevant documentation page(s) in parallel with other research. Never rely on recalled configuration examples — they may be from an older version of the tool.

Apply this rule to:

- Configuration files (`turbo.json`, `vite.config.ts`, `eslint.config.ts`, `.stencil/`, etc.)
- Integration guides and setup steps in plan documents
- Any field, option, or schema value that is version-sensitive

### Always use Context7 MCP for library and API documentation

When a task involves library usage, API documentation, code generation, or setup and configuration steps, always use the **Context7 MCP** tools (`resolve-library-id` then `query-docs`) to retrieve accurate, up-to-date documentation — without waiting for the user to ask.

Apply this rule to:

- Any library or framework integration (e.g. Stencil, Vite, Storybook, Changesets)
- Code generation that depends on a library's API surface
- Setup or configuration steps for tools already present in the workspace

Do not rely on recalled API shapes or examples — they may be stale. Context7 provides versioned, source-accurate documentation that prevents subtle breakage from API drift.

---

## Plan Implementation Strategy

These rules apply whenever an agent is executing a plan (a `.ai/plans/` document or any multi-step task).

Before executing a plan, check its frontmatter `status` field:

- `pending` — safe to start; update it to `in progress` and move its row in `.ai/plans/INDEX.md` before writing any code.
- `in progress` — confirm with the user before resuming.
- `done` — do not re-execute; inform the user the plan has already been completed.

### 1. Establish a TODO list before starting

Before writing a single line of code, create a concrete, ordered task list using the `TaskCreate` tool.

- Each task must map to **one discrete, testable unit of work** from the plan.
- Include a task for manual testing after each implementation step.
- Include a task for requesting human input whenever a design decision has multiple valid approaches (error handling strategy, data shape, API surface, etc.).
- Do not begin implementation until the list is visible and reviewed.

### 2. Work one task at a time — no rushing ahead

- Mark a task `in_progress` before starting it, and `completed` only when it is fully done and verified.
- **Never start the next task until the current one is complete and validated.**
- If a task reveals unexpected complexity or a blocker, create a new task to track the blocker rather than silently working around it.
- Prefer small, focused commits per task rather than one large commit at the end.

### 3. Ask for validation before moving on

After completing each task, **pause and ask the user to confirm** before continuing to the next one. Use `AskUserQuestion` with a clear summary of what was just done and what comes next.

Do not proceed automatically through multiple tasks in one shot — sequential validation prevents compounding errors that are costly to undo.

### 4. Manual testing checkpoint after each task

Every completed implementation task must include a manual testing step scoped to what was just built. The testing checklist should be:

- **Minimal** — only cover the surface area changed in that task.
- **Explicit** — list the exact steps the user should take (e.g. "Run `pnpm dev` in `apps/boreal-docs`, open the browser, and verify the Button renders without console errors").
- **Pass/fail criteria** — state what a passing result looks like.

Do not mark a task `completed` until the manual test has been performed or explicitly waived by the user.

### 5. Prefer reading before writing

Never propose or apply changes to a file that has not been read in the current session. Always use the `Read` tool first to understand existing structure, naming conventions, and surrounding context before editing.

### 6. Surface assumptions early

If a plan step is ambiguous or relies on an assumption (e.g. "assume the component uses CSS Modules"), state the assumption explicitly and ask the user to confirm it **before** acting on it. Do not silently assume and proceed.

### 8. No inline code comments unless asked

Do not add inline comments (`//` or `/* */`) to explain what code does. Code should be self-explanatory through clear naming and structure.

**Allowed:**

- JSDoc blocks (`/** */`) on exported functions, types, components, and public API surfaces — for documentation purposes only.

**Not allowed:**

- Inline comments explaining implementation details (e.g. `// loop through items`, `// convert to string`).
- Section divider comments (e.g. `// --- helpers ---`).
- `TODO`, `FIXME`, or `NOTE` comments added during implementation (track these as tasks instead).

If a piece of logic genuinely requires explanation, that is a signal to simplify the logic — not to add a comment. Only add inline comments when the user explicitly requests them.

### 9. No Co-Authored-By trailer in commit messages

Do not append `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>` (or any Claude authorship trailer) to git commit messages. Use only the commit message itself — no trailers, footers, or attribution lines.

### 7. Keep scope tight

Only implement what is described in the current task. Do not refactor surrounding code, rename things for style reasons, or add features outside the task scope — even if they seem helpful. Log any observations as new tasks instead.
