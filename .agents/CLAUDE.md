# Claude Code — Project Memory

## Memory

Non-obvious facts, discovered constraints, and verified patterns live in `.agents/memory/`.
Read the index before starting any component or infrastructure task: `.agents/memory/MEMORY.md`

---

## Tooling

- **Node.js**: run `fnm use` before any Node/pnpm command; reads `.node-version` at repo root.
- **Package manager**: pnpm 10+ only; install from workspace root with `pnpm add -D -w <pkg>@latest`.
- **npm versions**: always fetch `https://registry.npmjs.org/<pkg>/latest` before specifying any version in a plan, `package.json`, or install command. Fetch all packages in parallel. Never recall versions.
- **Docs before config**: before writing any config file or integration code, fetch current docs with Context7 MCP (`resolve-library-id` → `query-docs`). Never rely on recalled API shapes.
- **Commits**: `type(scope): TICKET-ID description` via `pnpm commit`.

---

## Non-Negotiable Rules

- **No `any`**: treat implicit `any` as an error regardless of `tsconfig.json` settings. All exported API surfaces must have explicit types.
- **No inline comments**: no `//` or `/* */` explaining what code does. JSDoc on exported public API only.
- **No Co-Authored-By**: never append `Co-Authored-By: ...` trailers to git commit messages.
- **No secrets**: never read, write, or modify `*.env` / `.env.*` files without explicit user permission.
- **Component tokens**: use `var(--boreal-*)` exclusively — no hard-coded colours, spacing, or radii.
- **Component prefix**: all web component tags use the `bds-[name]` prefix.

---

## Plan Execution

See `.claude/rules/plan-execution.md` for the full strategy (loaded every session).
