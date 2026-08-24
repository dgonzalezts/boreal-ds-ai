---
ticket: AI-005
status: done
created: 2026-08-24
---

# OpenCode Facade — AI Scaffold Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Add OpenCode as a fourth supported AI tool surface for the Boreal DS AI scaffold, following the existing per-entry symlink facade pattern already used for Claude Code, Cursor, and GitHub Copilot.

**Architecture:** `.agents/` stays the canonical source of truth. A new `.opencode/` mirror directory is added to `sync-symlinks.sh` for the two surfaces OpenCode does *not* natively read from `.agents/` (agents, commands) — OpenCode's skill loader already searches `.agents/skills/*/SKILL.md` natively, per its documented fallback paths, so skills need no new facade (Task 1 confirms this live before we treat it as settled). `.agents/CLAUDE.md` is renamed to `.agents/AGENTS.md` and promoted to the single canonical instructions file both tools read — Claude Code via a repointed `.claude/CLAUDE.md` symlink (its `CLAUDE.md`-only file recognition and `@`-import support were both verified live against Claude Code's own docs before adopting this approach), OpenCode via a new root-level `AGENTS.md` symlink. Two OpenCode-only artifacts with no Claude Code equivalent are introduced: a plugin (`.opencode/plugins/check-node-version.ts`) that ports the `PreToolUse` Bash hook, and `opencode.json` carrying skill permissions and plugin registration. Every existing agent file gets a frontmatter translation pass (model string, mode/permission.task in place of `tools:`/`Agent(...)`, dropped fields with no OpenCode equivalent). One capability — Claude's auto-injected per-subagent memory — has no OpenCode equivalent at all; this plan documents a fallback convention rather than silently dropping it.

**Tech Stack:** bash (`sync-symlinks.sh`), Markdown + YAML frontmatter (agent/command files), TypeScript (OpenCode plugin), JSON (`opencode.json`), OpenCode CLI (`opencode` — confirmed installed locally, v1.18.22) for live verification.

---

## Files to create / modify

| File | Notes |
| --- | --- |
| `.agents/scripts/sync-symlinks.sh` | Modify — add `.opencode/agent` and `.opencode/command` facade rows |
| `.agents/CLAUDE.md` → `.agents/AGENTS.md` | Rename — becomes the new canonical file (see Task 3) |
| `AGENTS.md` (repo root) | New — symlink facade → `.agents/AGENTS.md`, serves OpenCode |
| `.claude/CLAUDE.md` | Modify — repointed symlink → `.agents/AGENTS.md` instead of `.agents/CLAUDE.md`; still serves Claude Code at the exact same path |
| `.agents/agents/*.md` (8 files) | Unchanged — Claude's canonical format; confirmed OpenCode's frontmatter schema cannot share this file (see Task 4 finding) |
| `.agents/scripts/generate-opencode-agents.py` | New — derives `.opencode/agent/*.md` from the canonical files with OpenCode-shaped frontmatter |
| `.opencode/agent/*.md` (8 files) | Generated — real files, not symlinks; excluded from origin tracking with the rest of `.opencode/` |
| `.opencode/plugins/check-node-version.ts` | New — `tool.execute.before` hook porting the Bash `PreToolUse` node-version gate |
| `opencode.json` (repo root) | New — `permission.skill`, plugin registration, `agent.frontend-developer.permission.task` allowlist |
| `.agents/memory/opencode-agent-memory-fallback.md` | New — documents the per-agent memory gap and the fallback convention |
| `.agents/README.md` | Modify — document OpenCode facade rows and the memory-gap fallback |
| `.agents/SETUP.md` | Modify — add OpenCode to the facade table |

---

## Task 1: Confirm OpenCode's native skill discovery live

**Executor:** main thread (no executor)
**Files:** none (verification only)

**Acceptance criteria:**

- Run a real OpenCode session (not a docs lookup) against this repo and confirm at least one skill from `.agents/skills/` (e.g. `brainstorming`) is discoverable without any `.opencode/skills/` facade existing.
- Record the actual command/output used to confirm this in the task's manual test log — not just "docs say so."
- If OpenCode does *not* pick up `.agents/skills/` in practice (docs vs. behavior mismatch), stop and flag it — this changes Task 2's scope (a `.opencode/skills` facade row would need to be added).

**Manual test _(required — not waiveable)_:**

- [x] Given this repo root, when running `opencode run "list your available skills" --print-logs` (or the closest equivalent non-interactive invocation), then `brainstorming` (or another known `.agents/skills/` entry) appears in the result. Pass: skill is listed without any `.opencode/` directory existing yet.
- [x] Given the same session, when asking OpenCode which file backs that skill, then it resolves to `.agents/skills/brainstorming/SKILL.md`. Pass: path confirms the native fallback path claimed in OpenCode's docs, not a cached/hallucinated answer.

**Commit:** N/A — verification-only task.

---

## Task 2: Extend `sync-symlinks.sh` with the `.opencode/command` facade (`.opencode/agent` deferred to Task 4)

**Executor:** main thread (no executor)
**Files:**

- `.agents/scripts/sync-symlinks.sh` (modify)

**Acceptance criteria:**

- Two new `sync_surface` calls added, following the exact pattern already used for `.cursor/agents` and `.cursor/commands`:
  - `.opencode/agent` → `.agents/agents` (prefix `../../.agents/agents`)
  - `.opencode/command` → `.agents/commands` (prefix `../../.agents/commands`)
- Directory names match OpenCode's documented singular form (`agent/`, `command/`) — confirmed against the docs snippet noting OpenCode supports singular directory names for backwards compatibility, but the plural form is primary; use `agent`/`command` only if Task 1's live check (or a quick doc re-check) confirms OpenCode reads the singular names, otherwise use `agents`/`commands` to match its plural primary form.
- No changes to any existing `sync_surface` call for Claude/Cursor/Copilot.
- Script still exits non-zero on conflicts, per existing behavior.

**Manual test _(required — not waiveable)_:**

- [x] Given the modified script, when running `bash .agents/scripts/sync-symlinks.sh`, then it reports `added:` lines for every file under `.agents/agents/` and `.agents/commands/` under the new `.opencode/agent` and `.opencode/command` sections, with zero conflicts. Pass: script exits 0 and `ls -la .opencode/agent .opencode/command` shows valid relative symlinks resolving back into `.agents/`.
- [x] Given a second run immediately after, when running the script again, then every line reports `linked:` (already correct) rather than `added:`/`fixed:`. Pass: script is idempotent.

**Commit:**

```bash
git commit -m "chore(agents): AI-005 add opencode agent and command symlink facades"
```

---

## Task 3: Promote `AGENTS.md` to canonical and repoint the Claude Code facade

**Decision confirmed:** promote to canonical (was "Option B" in earlier drafts of this plan). Verified live via `claude-code-guide`: Claude Code has no native recognition of a file named `AGENTS.md` — it only ever reads `CLAUDE.md` at whatever path it's configured to look (here, `.claude/CLAUDE.md`). That file can be a symlink to anything, so renaming the canonical source to `.agents/AGENTS.md` and repointing `.claude/CLAUDE.md` at it is a pure rename + relink with zero behavior change for Claude Code — it opens the same path it always has and gets identical content. Also verified: `.claude/CLAUDE.md` supports `@path/to/file` imports resolved relative to the file's own location (not the symlink target, not the working directory), with a four-hop recursion limit — this matters for the plan-execution reference rewritten below.

**Executor:** main thread (no executor)
**Files:**

- `.agents/CLAUDE.md` → `.agents/AGENTS.md` (rename)
- `AGENTS.md` (repo root, create — symlink)
- `.claude/CLAUDE.md` (modify — repoint symlink target)
- `.agents/scripts/sync-symlinks.sh` (modify — repoint the existing `.claude/CLAUDE.md` row, add the new root `AGENTS.md` row)

**Acceptance criteria:**

- `.agents/CLAUDE.md` is renamed to `.agents/AGENTS.md` (`git mv`, preserving history).
- `sync-symlinks.sh`'s `sync_surface` helper only supports suffix changes on a shared basename, not a full rename (canonical `AGENTS.md` → link named `CLAUDE.md`) — do not force the generic helper to cover this one case. Write two explicit `ln -s` lines by hand instead, next to (not replacing) the existing `sync_surface` calls: one for `.claude/CLAUDE.md` → `../.agents/AGENTS.md`, one for root `AGENTS.md` → `.agents/AGENTS.md`.
- Content-neutralizing edits applied once to `.agents/AGENTS.md` (shared by both tools, not duplicated per-tool):
  1. Header changed from `# Claude Code — Project Memory` to a tool-neutral title, e.g. `# Boreal DS — Agent Instructions`.
  2. The plan-execution line rewritten to use an `@`-import: replace `See .claude/rules/plan-execution.md for the full strategy (loaded every session)` with an `@.agents/rules/plan-execution.md` reference. For Claude Code this now behaves as a real import (confirmed above). For OpenCode, add the short "External File Loading" preamble pattern from OpenCode's own `AGENTS.md` docs (a `CRITICAL:` instruction telling the agent to `Read` `@`-referenced files on demand and treat loaded content as mandatory) — without that preamble, OpenCode has no built-in reason to fetch the file, since it doesn't auto-scan a rules directory the way Claude Code does.
  3. Add a one-clause caveat to the Context7 MCP tooling line — e.g. "if the `context7` MCP server is registered in your session" — since that server is configured at the user's global level, not per-repo, for either tool.
- `.claude/CLAUDE.md` resolves to identical content post-rename (diff against the pre-rename file content, minus the three neutralizing edits above, is empty).
- Every other reference to `.agents/CLAUDE.md` by path — across `.agents/README.md`, `.agents/SETUP.md`, and any agent/skill file — is updated to `.agents/AGENTS.md`. Grep for `CLAUDE.md` under `.agents/` before finishing this task; do not rely on memory of which files reference it.

**Manual test _(required — not waiveable)_:**

- [x] Given the rename and both new symlinks, when running `bash .agents/scripts/sync-symlinks.sh`, then it reports no conflicts and the two hand-written `ln -s` lines execute cleanly (idempotent on a second run — no error if links already correct).
- [ ] Given a real Claude Code session (fresh, not this one) started in this repo, when it initializes, then it reads `.claude/CLAUDE.md` and the content matches `.agents/AGENTS.md` exactly, including the `@.agents/rules/plan-execution.md` import actually resolving (confirm by asking the session to state a specific rule from `plan-execution.md`, e.g. "confirm before continuing between tasks").
- [x] Given a real OpenCode session in this repo, when it initializes, then it loads `AGENTS.md` from the repo root and, given its lazy-load preamble, actually reads `.agents/rules/plan-execution.md` when asked a question that requires it (not just when asked to recite the raw instruction file).
- [ ] Given both sessions, when comparing their stated understanding of the non-negotiable rules (no `any`, no inline comments, `bds-` prefix, etc.), then both give identical answers. Pass: no content drift between the two tools reading the same canonical file.

**Commit:**

```bash
git commit -m "chore(agents): AI-005 promote AGENTS.md to canonical, repoint claude facade"
```

---

## Task 4: Generate OpenCode-compatible agent files (resolved — see finding below)

**Finding (superseded the plan's original two-branch approach):** live-tested against a real OpenCode session (v1.18.22). OpenCode's agent-frontmatter loader is a strict schema validator, not a lenient one — confirmed by an actual config error the user hit: `tools:` must be an object (`{tool: boolean}`), not Claude's comma-string with embedded `Agent(a, b, c)` syntax; `color:` must be a `#rrggbb` hex or one of five fixed enum values, not a named color. All 8 agent files had a `color:` value that fails this (`cyan`, `green`, `purple`, `teal`, `orange`, `yellow`, `blue`), and 3 (`frontend-developer`, `knowledge-keeper`, `technical-writer`) also had `tools:` in Claude's shape. This is not an "unrecognized field" situation (that's the lenient behavior confirmed for `SKILL.md` in Task 1) — `tools` and `color` are field names OpenCode *does* recognize, just with incompatible shapes and, for `tools`, incompatible semantics (Claude's `tools:` conflates built-in-tool access and subagent-dispatch permission into one field; OpenCode splits these into `tools` and `permission.task`). No single frontmatter block can satisfy both schemas for these two keys. Symlinking `.opencode/agent/` broke every OpenCode session in the repo until reverted (see this task's implementation log).

**Resolved approach:** stop trying to share one physical file for agent frontmatter. `.agents/agents/*.md` remains Claude's canonical, untouched format (Claude Code keeps reading it via `.claude/agents/` exactly as today). A generator script derives a **separate real file** per agent under `.opencode/agent/` with OpenCode-shaped frontmatter and the identical prose body — prose stays single-sourced (still DRY), only the frontmatter genuinely forks, because it has to.

**Executor:** main thread (no executor)
**Files:**

- `.agents/scripts/generate-opencode-agents.py` (create)
- `.agents/scripts/sync-symlinks.sh` (modify — replace the disabled `.opencode/agent` placeholder with a call to the generator)
- `.opencode/agent/*.md` (generated output — 8 files, not committed to `.agents/` since they're derived; excluded from origin same as the rest of `.opencode/`)

**Acceptance criteria:**

- Generator reads each `.agents/agents/*.md`, splits frontmatter from prose body at the second `---` fence, and emits `.opencode/agent/<name>.md` with:
  - `description:` — passthrough, unchanged.
  - `mode:` — `primary` only for `frontend-developer.md` (the sole file whose `tools:` line contains `Agent(...)`); `subagent` for the other 7.
  - `permission.task:` — only on `frontend-developer.md`, built from the `Agent(a, b, c, ...)` contents: `{"*": "deny", "a": "allow", "b": "allow", ...}`.
  - `tools:` — only emitted when the source `tools:` line (after removing the `Agent(...)` segment) excludes a tool OpenCode grants by default; concretely, only `knowledge-keeper.md` and `technical-writer.md` currently omit `Bash` from an otherwise-explicit list, so those two get `tools: {bash: false}`. The 5 agents with no `tools:` line at all in Claude's frontmatter (full access by omission) get no `tools:` key either.
  - No `color:` key — dropped, not translated (OpenCode's format has no equivalent named palette; not worth mapping to hex for a cosmetic field).
  - No `model:` key — dropped, not hardcoded. Do not guess a provider string: this OpenCode installation has no Anthropic credential configured (`opencode providers list` shows `github-copilot`, `google`, `opencode-go` only), so a hardcoded `anthropic/claude-sonnet-4-5` would fail to resolve at runtime. Per OpenCode's own docs, an agent with no `model:` uses the globally configured model (primary agents) or its invoking primary agent's model (subagents) — the correct default here, not a guess.
  - No `effort`, `skills`, `memory`, `hooks`, `name` keys — dropped; `skills` access moves to `opencode.json`'s `permission.skill` (Task 6), `memory` gets the fallback-convention pointer added to the prose body (see below), `hooks` is superseded by the Task 5 plugin.
  - Prose body — byte-identical to the source file's body (everything after the second `---`).
- A one-line pointer to `.agents/memory/opencode-agent-memory-fallback.md` (Task 7) is appended to each generated file's body — since the generator can't selectively edit the canonical prose without diverging it from Claude's copy, add this as a generation-time appendix rather than editing the shared source body.
- Generator is idempotent — running it twice with no source changes produces byte-identical output.
- `sync-symlinks.sh`'s `.opencode/agent` section calls the generator instead of `sync_surface` (no symlinks for this facade — the output is real, derived content, and per-entry symlinking doesn't apply to a transform).
- `.agents/agents/*.md` files themselves are **not modified** by this task — confirmed by diffing them against their state before Task 4 started.

**Manual test _(required — not waiveable)_:**

- [x] Given the generator runs via `bash .agents/scripts/sync-symlinks.sh`, when checking `.opencode/agent/*.md`, then all 8 files exist, none contain `color:` or a Claude-shaped `tools:` string, and `knowledge-keeper.md`/`technical-writer.md` contain `tools: {bash: false}` (or equivalent JSON-in-YAML form OpenCode accepts).
- [x] Given the generated files, when starting a real OpenCode session in this repo, then it starts with **no** configuration-invalid error (this is the regression this task exists to fix — confirm by reproducing the original failure mode first against the pre-fix state, then confirming it's gone).
- [x] Given a real OpenCode session, when running `opencode agent list` (or asking the session which subagents it has), then `frontend-subagent`, `testing-subagent`, `documentation-subagent`, `qa-subagent`, `release-subagent`, `knowledge-keeper`, and `technical-writer` all appear as `subagent` mode, and `frontend-developer` appears as `primary`.
- [x] Given the `frontend-developer` agent's `permission.task` allowlist, when asking an OpenCode session running as `frontend-developer` to invoke a subagent *not* on the list (e.g. `knowledge-keeper`), then it is denied per the deny-by-default rule.
- [ ] Given a real Claude Code session (fresh), when dispatching `knowledge-keeper` or `technical-writer` as a subagent, then it behaves identically to before this task — confirms `.agents/agents/*.md` truly went untouched.

**Commit:** handled by the end-of-plan `aisync` (per user's earlier decision — no per-task `git commit` for this scaffold-only plan).

---

## Task 5: Port the Node-version `PreToolUse` hook to an OpenCode plugin

**Executor:** main thread (no executor)
**Files:**

- `.opencode/plugins/check-node-version.ts` (create)

**Finding (corrects the plan's original assumption):** re-read `.agents/scripts/check-node-version.sh` before implementing, per plan-execution rule 5. It is **warn-only** — always exits 0, never blocks — and only emits a warning when the command contains `pnpm`/`npm`/`node` as a whole word *and* lacks `with-node.sh`; every other Bash call (including Node-unrelated ones) passes through silently with no warning. The Claude-side matcher (`"Bash"`) fires the hook for every Bash call, but the hook's own internal logic — not the matcher — is what scopes it to Node commands. The plugin must reproduce this exactly: a non-blocking warning, not a thrown error.

**Acceptance criteria:**

- Plugin exports a function implementing `tool.execute.before`, matching OpenCode's documented plugin shape.
- When `input.tool === "bash"`, the plugin shells out to the existing `.agents/scripts/check-node-version.sh` (reused, not reimplemented) and writes its stderr warning through — via `console.warn`/stderr, not a thrown error — so the Bash call proceeds exactly as it does today under Claude Code.
- Plugin does not duplicate the version-check logic itself — it is a thin adapter, consistent with `frontend-subagent.md`'s existing instruction to always route through `.agents/scripts/with-node.sh` rather than reimplementing Node version handling per tool.
- No `any` types (per repo-wide non-negotiable rule) — type the plugin context/hook signature from `@opencode-ai/plugin`.

**Manual test _(required — not waiveable)_:**

- [x] Given the plugin file exists, when starting a real OpenCode session in this repo and running a `bash` tool call for `pnpm --version` (deliberately not through `with-node.sh`), then the command still executes (not blocked) and a warning is visible (stderr/logs). Pass: matches Claude Code's actual warn-only behavior, not a blocking one.
- [x] Given a `bash` tool call for a non-Node command (e.g. `ls`), when it runs, then no warning appears and it is otherwise unaffected. Pass: hook only warns on Node/pnpm-relevant commands missing the wrapper, matching the shell script's actual scoping logic.

**Commit:**

```bash
git commit -m "feat(agents): AI-005 add opencode plugin for node version gate"
```

---

## Task 6: Write `opencode.json`

**Executor:** main thread (no executor)
**Files:**

- `opencode.json` (repo root, create)

**Scope reduced (finding):** every substantive thing this task originally planned to configure turned out to already be handled elsewhere or to already be the default: `permission.task` lives in the Task 4 generator's output, not here; local plugins auto-load from `.opencode/plugins/` with no `plugin` array entry needed; `permission.skill`'s default is already `allow` with no restriction requested, so writing `{"*": "allow"}` would only restate the default. Per YAGNI, `opencode.json` stays minimal rather than encoding no-op policy.

**Acceptance criteria:**

- `$schema: "https://opencode.ai/config.json"` present — the only content. No `permission`, `plugin`, `agent`, or `mcp` blocks unless a real, requested need surfaces during implementation.
- The MCP-config finding (no repo-level MCP config exists; `context7`/`figma`/`playwright`/`atlassian` are configured at the user's global Claude Code level in `~/.claude.json`, not per-repo) is documented in `.agents/README.md` instead (Task 9) — not fabricated here.

**Manual test _(required — not waiveable)_:**

- [x] Given `opencode.json` exists, when running `opencode` in this repo, then it starts without a config parse error.

**Commit:** handled by the end-of-plan `aisync`.

---

## Task 7: Document the per-agent memory gap and its fallback convention

**Executor:** main thread (no executor)
**Files:**

- `.agents/memory/opencode-agent-memory-fallback.md` (create)
- `.agents/memory/MEMORY.md` (modify — add index row)

**Acceptance criteria:**

- New memory file states plainly: OpenCode has no equivalent to Claude Code's `memory: project` auto-injected per-subagent memory (`.claude/agent-memory/<name>/MEMORY.md`, auto-created, first 200 lines auto-injected every invocation) — this is a genuine capability loss, not a config translation.
- Documents the fallback convention decided for OpenCode agents: point each OpenCode agent's prompt body (added in Task 4) at `.agents/memory/` and instruct it to explicitly read the relevant topic files at the start of a task and append new learnings at the end, rather than relying on auto-injection.
- Explicitly notes the ergonomic cost of the fallback (no automatic injection, agent must remember to read/write) so future sessions don't mistake the workaround for parity.
- Follows this repo's memory-file frontmatter convention (`name`, `description`, `metadata.type: reference` or `project` as appropriate) — read `.agents/memory/MEMORY.md`'s existing entries for the exact format before writing.
- `MEMORY.md` gets one new index row under an appropriate existing section (or a new "OpenCode" section if none fits), per its "index, not a memory" rule — one line, under ~150 characters.

**Manual test _(required — not waiveable)_:**

- [x] Given the new memory file, when reading it back, then it accurately describes the current state of Task 4's implementation (the prose-pointer approach) — not a stale plan-time description if the approach changed during implementation.
- [x] N/A for live OpenCode verification — this is a documentation-only task.

**Commit:**

```bash
git commit -m "docs(agents): AI-005 document opencode per-agent memory gap and fallback"
```

---

## Task 8: Verify command portability

**Executor:** main thread (no executor)
**Files:** `.agents/commands/*.md` (verify only; modify only if a real problem is found)

**Acceptance criteria:**

- Confirm live (not from docs alone) that OpenCode's command loader tolerates the `argument-hint` frontmatter field present in commands like `sync-plans.md` without erroring — OpenCode's own docs only document `description`, `agent`, and `model` as recognized command frontmatter fields; "unrecognized fields are ignored" was confirmed for skills specifically, not commands, so this needs its own check rather than assuming the same rule applies.
- Confirm `$ARGUMENTS` and positional (`$1`, `$2`) placeholders in existing commands behave identically under OpenCode — spot-check `sync-plans.md` (uses `$ARGUMENTS`) via the `.opencode/command` facade from Task 2.
- If `argument-hint` does cause a problem, this task's scope expands to stripping/renaming that field across affected command files — but only do this if the live check actually shows a failure, not preemptively.

**Manual test _(required — not waiveable)_ — finding noted:** a `/command-name` prefix inside a plain `opencode run "..."` message is **not** reliably routed to the command file — the model may just treat it as literal text (confirmed: it responded conversationally instead of loading the file). The correct non-interactive invocation is the dedicated `opencode run --command <name> <args>` flag.

- [x] Given `.opencode/command/zzverify-cmd-test.md` (throwaway probe, an unambiguous name with no risk of matching an agent by substring — the earlier Task 2 probe's apparent success was a false positive: `/probe-singular-cmd` got routed to the `probe-singular` *agent* via ordinary Task-tool dispatch, not genuine command-file loading, because the names overlapped), when invoked via `opencode run --command zzverify-cmd-test "hello123"`, then the command's body (containing a unique marker) loads as the prompt and `$ARGUMENTS` substitutes to `hello123` correctly, with no error from the `argument-hint`-bearing frontmatter shape. Pass: confirmed live, probe file removed after.

**Commit:** N/A unless a fix was needed — if so:

```bash
git commit -m "fix(agents): AI-005 fix opencode command frontmatter compatibility"
```

---

## Task 9: Update `.agents/README.md` and `.agents/SETUP.md`

**Executor:** main thread (no executor)
**Files:**

- `.agents/README.md` (modify)
- `.agents/SETUP.md` (modify)

**Acceptance criteria:**

- `SETUP.md`'s facade table gets three new/changed rows: `.opencode/agent/` → `.agents/agents/`, `.opencode/command/` → `.agents/commands/`, `AGENTS.md` → `.agents/AGENTS.md`; the existing `.claude/CLAUDE.md` row's target column is updated from `.agents/CLAUDE.md` to `.agents/AGENTS.md`.
- `SETUP.md`'s "twelve entries" prose count is updated to reflect the new total (fifteen, pending Task 2's final row count).
- `README.md`'s "Folder Reference" / participant tables are extended only if OpenCode changes how any existing folder is used (it doesn't — this task is primarily `SETUP.md`'s facade table plus a short OpenCode section if the existing structure warrants one).
- The MCP-config finding from Task 6 (no repo-level MCP config exists; it's user-global) is documented here if it wasn't already captured as a JSONC comment in `opencode.json`.
- The memory-gap fallback (Task 7) gets a one-line pointer from `README.md` to `.agents/memory/opencode-agent-memory-fallback.md`, consistent with how other cross-cutting concerns are referenced rather than duplicated.

**Manual test _(required — not waiveable)_:**

- [x] Given the updated docs, when a new contributor reads `SETUP.md` top to bottom, then the facade table and setup steps are sufficient to explain the OpenCode surface without needing to read this plan. Pass: self-reviewed for completeness — no live tooling test applicable to documentation-only content.

**Commit:**

```bash
git commit -m "docs(agents): AI-005 document opencode facade in README and SETUP"
```

---

## Task 10: End-to-end verification with a real OpenCode session

**Executor:** main thread (no executor)
**Files:** none (verification only)

**Acceptance criteria:**

- All prior tasks' individual manual tests passed.
- This task performs one combined, realistic session rather than re-testing each piece in isolation.

**Manual test _(required — not waiveable)_:**

- [x] Given a clean `bash .agents/scripts/sync-symlinks.sh` run reports zero conflicts, when starting a fresh `opencode` session in this repo, then `AGENTS.md` loads as project instructions, `frontend-subagent` and at least two other subagents appear in `opencode agent list`, at least one skill (e.g. `brainstorming`) is invokable, and at least one command (e.g. `/sync-plans`) runs successfully.
- [x] Given the session, when triggering a `bash` tool call for a pnpm command not routed through `with-node.sh`, then the Task 5 plugin warns (not blocks — corrected wording, see Task 5's finding). Pass: full loop confirmed — agents, skills, commands, rules, and the hook all function together in one live session, not just individually.

**Commit:** N/A — verification-only task; no code changes expected unless a regression is found (log as a new task if so).

---

## Open Questions Requiring Confirmation Before Execution

- **Task 3:** Resolved — `AGENTS.md` is promoted to canonical (`.agents/AGENTS.md`), with `.claude/CLAUDE.md` repointed to it. Confirmed live: Claude Code has no native `AGENTS.md` recognition (only ever reads `CLAUDE.md`), but does support `@path` imports resolved relative to the importing file's location, four-hop max — both facts checked against Claude Code's own docs before this plan was updated.
- **Task 4:** Resolved — confirmed live (the hard way: it broke the user's OpenCode session on first symlink). OpenCode's frontmatter parser is strict on recognized-but-differently-shaped fields (`tools`, `color`); a generator script producing separate real files is required. See Task 4's finding write-up for full detail.

## Genuinely Unverified Items (honest gaps, not just unchecked bookkeeping)

Three manual-test lines remain unchecked because they specifically require a **fresh Claude Code session** — something this session cannot spawn on itself:

- Line 113 (Task 3): whether `@.agents/rules/plan-execution.md` actually auto-imports for Claude Code the way its own docs claim. Confirmed via `claude-code-guide` research that the feature exists and behaves that way per documentation, and confirmed the *content* is correct through the symlink — but never watched it fire in a live session, unlike the OpenCode side (line 114), which was directly observed.
- Line 115 (Task 3): depends on the above — only OpenCode's half of the comparison was actually run.
- Line 160 (Task 4): confirmed `.agents/agents/*.md` are byte-unchanged (proves Claude Code's *input* is identical to before), but never literally re-dispatched `knowledge-keeper`/`technical-writer` as subagents in a fresh Claude Code session to observe the *output* is unaffected.

If this matters before treating the plan as fully closed, open a new Claude Code session in this repo and: (1) ask it to state a specific rule from `plan-execution.md` without having read the file yet in that session, and (2) dispatch `knowledge-keeper` or `technical-writer` and confirm normal behavior.
