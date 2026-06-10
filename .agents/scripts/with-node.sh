#!/usr/bin/env bash
# with-node.sh — activate fnm + correct Node.js version, then exec the given command.
#
# Usage:
#   .agents/scripts/with-node.sh pnpm test
#   .agents/scripts/with-node.sh node --version
#
# Behaviour:
#   1. Locates the repo root via git so fnm can find .node-version.
#   2. Sources fnm into the current shell (handles common install locations).
#   3. Runs `fnm use` to activate the project's pinned version.
#   4. Execs the supplied command — if fnm is unavailable the command still runs
#      (warn-only; never blocks).

set -euo pipefail

# ── 1. Resolve repo root ──────────────────────────────────────────────────────
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
cd "$REPO_ROOT"

# ── 2. Source fnm (try common install locations) ──────────────────────────────
_source_fnm() {
  # Prefer the shell-init export path if fnm is already on PATH
  if command -v fnm &>/dev/null; then
    eval "$(fnm env --use-on-cd 2>/dev/null)" || true
    return 0
  fi

  # Try common fnm install locations
  local candidates=(
    "$HOME/.fnm/fnm"
    "$HOME/.local/share/fnm/fnm"
    "/opt/homebrew/bin/fnm"
    "/usr/local/bin/fnm"
  )
  for candidate in "${candidates[@]}"; do
    if [[ -x "$candidate" ]]; then
      eval "$("$candidate" env --use-on-cd 2>/dev/null)" || true
      return 0
    fi
  done

  # fnm not found — warn and continue without it
  echo "with-node.sh: warning: fnm not found; running command without Node.js version pinning" >&2
  return 1
}

fnm_available=true
_source_fnm || fnm_available=false

# ── 3. Activate the project's pinned Node.js version ─────────────────────────
if [[ "$fnm_available" == "true" ]]; then
  fnm use 2>/dev/null || true
fi

# ── 4. Exec the supplied command ──────────────────────────────────────────────
if [[ $# -eq 0 ]]; then
  echo "with-node.sh: error: no command supplied" >&2
  exit 1
fi

exec "$@"
