#!/usr/bin/env bash
set -euo pipefail

# Bootstrap the Boreal DS AI scaffold.
# Idempotent — safe to run multiple times from any directory inside the repo.
# Usage: bash .agents/scripts/bootstrap.sh

root="$(git rev-parse --show-toplevel)"
git_common_dir="$(git rev-parse --git-common-dir)"

# ─── Scope 1: Machine ───────────────────────────────────────────────────────
printf "[machine] Checking aisync shell function...\n"

functions_file="$HOME/.functions"

aisync_present=false
if grep -q 'function aisync' "$functions_file" 2>/dev/null; then
  aisync_present=true
elif type aisync &>/dev/null; then
  aisync_present=true
fi

if [[ "$aisync_present" == true ]]; then
  printf "[machine] aisync already available — skipping\n"
else
  touch "$functions_file"
  cat >> "$functions_file" << 'AISYNC'

# Sync AI scaffold dirs to the ai-config branch and push to the ai remote.
# Usage: aisync [repo-path] [commit-message]
function aisync() {
  local root
  root=$(git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null)
  if [[ -z "$root" ]]; then
    printf "\033[31mERROR:\033[0m Not inside a git repository\n"
    return 1
  fi
  bash "$root/.agents/scripts/aisync.sh" "$root" "${2:-}"
}
AISYNC
  printf "[machine] aisync appended to %s\n" "$functions_file"
fi

if ! grep -qE 'source[[:space:]].*\.functions|\.[[:space:]].*\.functions' \
    "$HOME/.zshrc" "$HOME/.bashrc" 2>/dev/null; then
  printf "[machine] REMINDER: add 'source ~/.functions' to ~/.zshrc or ~/.bashrc to activate aisync in new shells\n"
fi

# ─── Scope 2: Repository ────────────────────────────────────────────────────
printf "[repo]    Checking repository-level setup...\n"

if git -C "$root" remote | grep -q '^ai$'; then
  printf "[repo]    ai remote already present — skipping\n"
else
  git -C "$root" remote add ai https://github.com/dgonzalezts/boreal-ds-ai.git
  printf "[repo]    ai remote added\n"
fi

if git config --file "$git_common_dir/config" alias.aiboot 2>/dev/null | grep -q 'bootstrap'; then
  printf "[repo]    git aiboot alias already present — skipping\n"
else
  git config --file "$git_common_dir/config" alias.aiboot \
    '!bash "$(git rev-parse --git-common-dir)/../.agents/scripts/bootstrap.sh"'
  printf "[repo]    git aiboot alias written to .git/config\n"
fi

exclude_file="$git_common_dir/info/exclude"
mkdir -p "$(dirname "$exclude_file")"
scaffold_dirs=(".agents/" "ai-docs/" "ai-work/" ".claude/" ".cursor/" ".github/" ".opencode/" "AGENTS.md" "/opencode.json")
for dir in "${scaffold_dirs[@]}"; do
  if grep -qF "$dir" "$exclude_file" 2>/dev/null; then
    printf "[repo]    %s already in .git/info/exclude — skipping\n" "$dir"
  else
    printf "%s\n" "$dir" >> "$exclude_file"
    printf "[repo]    %s added to .git/info/exclude\n" "$dir"
  fi
done

# ─── Scope 3: Worktree ──────────────────────────────────────────────────────
printf "[worktree] Checking AI scaffold in current directory...\n"

if [[ -d "$root/.agents" && -d "$root/.opencode" && -f "$root/AGENTS.md" ]]; then
  printf "[worktree] AI scaffold already present — skipping restore\n"
else
  printf "[worktree] AI scaffold incomplete or missing — restoring from ai/main...\n"
  git -C "$root" fetch ai
  git -C "$root" checkout ai/main -- .agents ai-docs ai-work .claude .cursor .github .opencode AGENTS.md opencode.json
  git -C "$root" rm --cached -r .agents ai-docs ai-work .claude .cursor .github .opencode AGENTS.md opencode.json
  printf "[worktree] Restore complete\n"
fi

printf "[worktree] Running sync-symlinks.sh...\n"
bash "$root/.agents/scripts/sync-symlinks.sh" "$root"

if [[ -f "$root/.opencode/package.json" ]] && command -v npm &>/dev/null; then
  printf "[worktree] Installing .opencode/ plugin dependencies (npm)...\n"
  (cd "$root/.opencode" && npm install --silent)
  printf "[worktree] .opencode/ dependencies installed\n"
fi

printf "\nBootstrap complete.\n"
