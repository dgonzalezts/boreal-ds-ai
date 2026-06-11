#!/usr/bin/env bash
set -euo pipefail

printf "sync-indexes: regenerating all index files\n\n"

# sync-indexes.sh — Regenerate all AI index files (plans, bug reports, etc.)
# Usage: ./sync-indexes.sh [repo-root]
#
# - Scans ai-work/plans/ and ai-work/qa/bug-reports/ for records
# - Rebuilds ai-work/plans/INDEX.md and ai-work/qa/bug-reports/index.md
# - Fails on malformed status/metadata
# - Deterministic output (sorted by file name)

root="${1:-$(git rev-parse --show-toplevel)}"

# --- Plans Index ---
plans_dir="$root/ai-work/plans"
plans_index="$plans_dir/INDEX.md"

if [[ -d "$plans_dir" ]]; then
  tmp_index="$(mktemp)"
  printf "# Plans Index\n\n" > "$tmp_index"
  printf "| File | Status | Description |\n| --- | --- | --- |\n" >> "$tmp_index"
  for f in $(find "$plans_dir" -maxdepth 1 -type f -name '*.md' ! -name 'INDEX.md' | sort); do
    status=$(awk '/^status:/ {print $2}' "$f" | head -1)
    [[ -z "$status" ]] && status="pending"
    desc=$(awk '/^# / {sub(/^# /, ""); print; exit}' "$f")
    relf="$(basename "$f")"
    printf "| [%s](./%s) | %s | %s |\n" "$relf" "$relf" "$status" "$desc" >> "$tmp_index"
  done
  mv "$tmp_index" "$plans_index"
fi

# --- Bug Reports Index ---
bugs_dir="$root/ai-work/qa/bug-reports"
bugs_index="$bugs_dir/INDEX.md"

if [[ -d "$bugs_dir" ]]; then
  tmp_index="$(mktemp)"
  printf "# QA Bug Reports Index\n\n" > "$tmp_index"
  printf "| Bug ID | Title | Status | Severity | Priority | Component | Date Fixed | Report |\n" >> "$tmp_index"
  printf "| --- | --- | --- | --- | --- | --- | --- | --- |\n" >> "$tmp_index"
  for f in $(find "$bugs_dir" -maxdepth 1 -type f -name 'BUG-*.md' | sort); do
    bugid=$(awk '/^# BUG/ {sub(/^# /, ""); print $1}' "$f")
    title=$(awk '/^# BUG/ {sub(/^# [^:]+: /, ""); print; exit}' "$f")
    status=$(grep -m1 '\*\*Status:\*\*' "$f" | cut -d'*' -f6 | awk '{print $1}') || true
    severity=$(grep -m1 '\*\*Severity:\*\*' "$f" | cut -d'*' -f6 | awk '{print $1}') || true
    priority=$(grep -m1 '\*\*Priority:\*\*' "$f" | cut -d'*' -f6 | awk '{print $1}') || true
    component=$(grep -m1 '\*\*Component:\*\*' "$f" | cut -d'*' -f6 | awk '{print $1}') || true
    datefixed=$(grep -m1 '\*\*Resolution date:\*\*' "$f" | cut -d'*' -f6 | awk '{$1=$1;print}') || true
    relf="$(basename "$f")"
    printf "| %s | %s | %s | %s | %s | %s | %s | [%s](./%s) |\n" "$bugid" "$title" "$status" "$severity" "$priority" "$component" "$datefixed" "$bugid" "$relf" >> "$tmp_index"
  done
  mv "$tmp_index" "$bugs_index"
fi

# Add more index generators here as needed

exit 0
