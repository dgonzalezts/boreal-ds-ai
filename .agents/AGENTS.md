# Boreal DS — Agent Instructions

## Memory

Non-obvious facts, discovered constraints, and verified patterns live in `.agents/memory/`.
Read the index before starting any component or infrastructure task: `.agents/memory/MEMORY.md`

---

## Tooling

- **Node.js**: run `fnm use` before any Node/pnpm command; reads `.node-version` at repo root.
- **Package manager**: pnpm 10+ only; install from workspace root with `pnpm add -D -w <pkg>@latest`.
- **npm versions**: always fetch `https://registry.npmjs.org/<pkg>/latest` before specifying any version in a plan, `package.json`, or install command. Fetch all packages in parallel. Never recall versions.
- **Docs before config**: before writing any config file or integration code, fetch current docs with Context7 MCP (`resolve-library-id` → `query-docs`) if the `context7` MCP server is registered in your session. Never rely on recalled API shapes.
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

CRITICAL: When you encounter an `@`-referenced file below, load it with your Read tool if you have not already — for Claude Code this resolves as an automatic import; for other tools, treat this line as an explicit instruction to fetch it now, on first need. Once loaded, treat its content as mandatory.

For the full plan-execution strategy: @.agents/rules/plan-execution.md
