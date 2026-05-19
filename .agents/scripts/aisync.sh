#!/usr/bin/env bash
set -euo pipefail

# Sync AI scaffold directories to the ai-config branch on the ai remote.
# Uses a git worktree so the working directory is never modified.
#
# Usage: aisync.sh [repo-root] [commit-message]
#   repo-root       Path to the repository root (defaults to the root of the
#                   current git repository).
#   commit-message  Optional. Defaults to "sync: update AI configuration <timestamp>".

root="${1:-$(git rev-parse --show-toplevel)}"
commit_msg="${2:-"sync: update AI configuration $(date '+%Y-%m-%d %H:%M')"}"

if [[ -z "$root" ]]; then
  printf "\033[31mERROR:\033[0m Not inside a git repository\n" >&2
  exit 1
fi

wt="$root/../ai-sync-worktree"
trap 'git -C "$root" worktree remove --force "$wt" 2>/dev/null || true' EXIT

git -C "$root" worktree add "$wt" ai-config

for d in .claude .github .agents .cursor ai-docs ai-work; do
  if [[ -e "$root/$d" ]]; then
    rsync -a --delete --links "$root/$d" "$wt/"
  else
    rm -rf "$wt/$d"
  fi
done

git -C "$wt" add -f .claude .github .agents .cursor ai-docs ai-work

if git -C "$wt" diff --cached --quiet; then
  printf "aisync: nothing changed, skipping commit and push\n"
else
  git -C "$wt" commit -m "$commit_msg"
  git -C "$wt" push ai ai-config:main
  printf "aisync: pushed to ai/main\n"

  if [[ -x "$root/.agents/scripts/sync-symlinks.sh" ]]; then
    bash "$root/.agents/scripts/sync-symlinks.sh" "$root"
  fi
fi
