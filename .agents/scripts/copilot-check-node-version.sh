#!/usr/bin/env bash
# copilot-check-node-version.sh — preToolUse hook for GitHub Copilot agent.
#
# GitHub Copilot hook protocol:
#   - Reads tool input JSON from stdin.
#   - Exits 0 to approve the tool call.
#   - Exits non-zero to DENY the tool call; stdout/stderr is shown to the agent
#     so it can self-correct and retry with the right command.
#
# Behaviour:
#   - Denies any bash command that invokes pnpm/npm/node without the
#     .agents/scripts/with-node.sh wrapper, which activates the project's
#     pinned Node.js version via fnm.

set -euo pipefail

# ── Read stdin (required by hook protocol) ────────────────────────────────────
input="$(cat)"

# ── Extract the bash command from the JSON payload ────────────────────────────
# The `|| true` guard prevents set -e from aborting when grep finds no match
# (e.g. non-bash tool calls that contain no "command" key).
command_value="$(echo "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')" || true

# ── Deny if pnpm/npm/node is used without the wrapper ────────────────────────
if echo "$command_value" | grep -qE '\b(pnpm|npm|node)\b'; then
  if ! echo "$command_value" | grep -q 'with-node.sh'; then
    echo "ERROR: Do not call pnpm/npm/node directly. This repository pins its Node.js version via fnm and a .node-version file." >&2
    echo "Wrap the command with .agents/scripts/with-node.sh so the correct version is activated first." >&2
    echo "Example: .agents/scripts/with-node.sh pnpm install" >&2
    exit 1
  fi
fi

exit 0
