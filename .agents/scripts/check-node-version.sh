#!/usr/bin/env bash
# check-node-version.sh — PreToolUse hook for Bash tool calls in subagent definitions.
#
# Claude Code hook protocol:
#   - Reads tool input JSON from stdin (required — must consume stdin).
#   - Prints a one-line warning to stderr when pnpm/npm/node are called without
#     the with-node.sh wrapper.
#   - Always exits 0 (warn-only; never blocks execution).
#
# Usage in subagent frontmatter:
#   hooks:
#     PreToolUse:
#       - matcher: "Bash"
#         hooks:
#           - type: command
#             command: ".agents/scripts/check-node-version.sh"

set -euo pipefail

# ── Read and discard stdin (required by Claude Code hook protocol) ────────────
input="$(cat)"

# ── Extract command from JSON input ──────────────────────────────────────────
# The tool input is a JSON object: {"tool_input": {"command": "..."}}
# Use a simple grep rather than requiring jq.
# The `|| true` guard prevents `set -e` + `pipefail` from exiting when grep
# finds no "command" key (e.g. non-bash tools like read_file or edit).
command_value="$(echo "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')" || true

# ── Warn if pnpm/npm/node runs without the wrapper ───────────────────────────
if echo "$command_value" | grep -qE '\b(pnpm|npm|node)\b'; then
  if ! echo "$command_value" | grep -q 'with-node.sh'; then
    echo "check-node-version: warning: command uses pnpm/npm/node without .agents/scripts/with-node.sh; Node.js version may not match .node-version" >&2
  fi
fi

# Always exit 0 — warn only, never block
exit 0
