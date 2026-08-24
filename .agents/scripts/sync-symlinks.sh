#!/usr/bin/env bash
set -euo pipefail

# Reconcile per-entry symlinks across all mirror surfaces.
# For each mirror dir, every canonical entry must have a valid relative symlink;
# orphaned or broken symlinks are removed or recreated; real files are never touched.
#
# Usage: sync-symlinks.sh [repo-root]

root="${1:-$(git rev-parse --show-toplevel)}"

if [[ -z "$root" ]]; then
  printf "\033[31mERROR:\033[0m Not inside a git repository\n" >&2
  exit 1
fi

added=0
fixed=0
removed=0
conflicts=0

# sync_surface <mirror_rel> <canonical_rel> <symlink_prefix> [glob] [link_suffix]
#   mirror_rel     — mirror dir path relative to repo root (e.g. .claude/agents)
#   canonical_rel  — canonical dir path relative to repo root (e.g. .agents/agents)
#   symlink_prefix — relative path written into the symlink target (e.g. ../../.agents/agents)
#   glob           — optional filename pattern to restrict which canonical entries are managed
#                    (default: *); entries NOT matching the pattern are treated as external
#   link_suffix    — optional suffix appended to the symlink name but NOT the target
#                    (e.g. ".prompt.md" → link "foo.prompt.md" points to "prefix/foo.md")
sync_surface() {
  local mirror_rel="$1"
  local canonical_rel="$2"
  local prefix="$3"
  local glob="${4:-*}"
  local link_suffix="${5:-}"

  local mirror="$root/$mirror_rel"
  local canonical="$root/$canonical_rel"

  mkdir -p "$mirror"

  # --- Pass 1: ensure every canonical entry has a valid symlink in the mirror ---
  local found_any=false
  for src in "$canonical"/$glob; do
    [[ -e "$src" ]] || continue
    found_any=true
    local name
    name=$(basename "$src")
    local link_name
    if [[ -n "$link_suffix" ]]; then
      link_name="${name%.md}${link_suffix}"
    else
      link_name="$name"
    fi
    local link="$mirror/$link_name"
    local target="$prefix/$name"

    if [[ -L "$link" ]]; then
      local actual
      actual=$(readlink "$link")
      if [[ "$actual" == "$target" && -e "$link" ]]; then
        printf "    linked:   %s\n" "$link_name"
      else
        rm -f "$link"
        ln -s "$target" "$link"
        printf "    fixed:    %s\n" "$link_name"
        added=$((added + 1))
        fixed=$((fixed + 1))
      fi
    elif [[ -e "$link" ]]; then
      printf "    \033[33mCONFLICT:\033[0m %s — real %s exists; skipping (manual review needed)\n" \
        "$link_name" "$([[ -d "$link" ]] && echo dir || echo file)"
      conflicts=$((conflicts + 1))
    else
      ln -s "$target" "$link"
      printf "    added:    %s\n" "$link_name"
      added=$((added + 1))
    fi
  done

  if [[ "$found_any" == false ]]; then
    printf "    (canonical dir empty or no entries match '%s')\n" "$glob"
  fi

  # --- Pass 2: remove orphaned symlinks (broken link + no canonical counterpart) ---
  for link in "$mirror"/*; do
    # skip if glob expansion produced no matches
    [[ -e "$link" || -L "$link" ]] || continue

    local link_name
    link_name=$(basename "$link")

    # Derive canonical name by stripping link_suffix and restoring .md (if any)
    local canon_name="$link_name"
    if [[ -n "$link_suffix" && "$link_name" == *"$link_suffix" ]]; then
      canon_name="${link_name%"$link_suffix"}.md"
    fi

    # Only manage entries whose canonical name matches the pattern
    case "$canon_name" in
      $glob) ;;
      *) continue ;;
    esac

    [[ -L "$link" ]] || continue   # real files are external — leave alone
    [[ ! -e "$link" ]] || continue # valid symlink — already handled in pass 1

    # Broken symlink. Check if the canonical entry still exists.
    if [[ ! -e "$canonical/$canon_name" ]]; then
      rm -f "$link"
      printf "    removed:  %s (orphaned symlink)\n" "$link_name"
      removed=$((removed + 1))
    fi
  done
}

# sync_single_link <link_rel> <target_rel>
#   For the one case a renamed canonical file needs a differently-named link
#   (.agents/AGENTS.md → .claude/CLAUDE.md and → root AGENTS.md) — sync_surface
#   only handles suffix changes on a shared basename, not a full rename.
sync_single_link() {
  local link_rel="$1"
  local target_rel="$2"
  local link="$root/$link_rel"

  mkdir -p "$(dirname "$link")"

  if [[ -L "$link" ]]; then
    local actual
    actual=$(readlink "$link")
    if [[ "$actual" == "$target_rel" && -e "$link" ]]; then
      printf "    linked:   %s\n" "$link_rel"
    else
      rm -f "$link"
      ln -s "$target_rel" "$link"
      printf "    fixed:    %s\n" "$link_rel"
      added=$((added + 1))
      fixed=$((fixed + 1))
    fi
  elif [[ -e "$link" ]]; then
    printf "    \033[33mCONFLICT:\033[0m %s — real %s exists; skipping (manual review needed)\n" \
      "$link_rel" "$([[ -d "$link" ]] && echo dir || echo file)"
    conflicts=$((conflicts + 1))
  else
    ln -s "$target_rel" "$link"
    printf "    added:    %s\n" "$link_rel"
    added=$((added + 1))
  fi
}

printf "sync-symlinks: reconciling mirror surfaces\n\n"

printf "── .claude/agents → .agents/agents\n"
sync_surface ".claude/agents" ".agents/agents" "../../.agents/agents"

printf "── .claude/CLAUDE.md → .agents/AGENTS.md\n"
sync_single_link ".claude/CLAUDE.md" "../.agents/AGENTS.md"

printf "── AGENTS.md → .agents/AGENTS.md\n"
sync_single_link "AGENTS.md" ".agents/AGENTS.md"

printf "── .claude/commands → .agents/commands\n"
sync_surface ".claude/commands" ".agents/commands" "../../.agents/commands"

printf "── .claude/memory → .agents/memory\n"
sync_surface ".claude/memory" ".agents/memory" "../../.agents/memory"

printf "── .claude/rules → .agents/rules\n"
sync_surface ".claude/rules" ".agents/rules" "../../.agents/rules"

printf "── .claude/skills → .agents/skills\n"
sync_surface ".claude/skills" ".agents/skills" "../../.agents/skills"

printf "── .cursor/agents → .agents/agents\n"
sync_surface ".cursor/agents" ".agents/agents" "../../.agents/agents"

printf "── .cursor/commands → .agents/commands\n"
sync_surface ".cursor/commands" ".agents/commands" "../../.agents/commands"

printf "── .cursor/rules → .agents/rules (*.mdc)\n"
sync_surface ".cursor/rules" ".agents/rules" "../../.agents/rules" "*.md" ".mdc"

printf "── .cursor/skills → .agents/skills\n"
sync_surface ".cursor/skills" ".agents/skills" "../../.agents/skills"

# .opencode/agent is generated, not symlinked: OpenCode's agent frontmatter
# schema hard-errors on Claude's `tools:` (string) and `color:` (named color)
# shapes, so a plain per-entry symlink would ship broken config. The
# generator derives OpenCode-shaped frontmatter with the same prose body.
printf "── .opencode/agent → .agents/agents (generated)\n"
python3 "$root/.agents/scripts/generate-opencode-agents.py" "$root" | sed 's/^/    /'

printf "── .opencode/command → .agents/commands\n"
sync_surface ".opencode/command" ".agents/commands" "../../.agents/commands"

printf "── .github/prompts → .agents/commands (*.prompt.md)\n"
sync_surface ".github/prompts" ".agents/commands" "../../.agents/commands" "*.md" ".prompt.md"

printf "── .github/copilot-instructions.md → .agents/copilot-instructions.md\n"
sync_surface ".github" ".agents" "../.agents" "copilot-instructions.md"

printf "\nsync-symlinks: done  added=%d  fixed=%d  removed=%d  conflicts=%d\n" \
  "$added" "$fixed" "$removed" "$conflicts"

if (( conflicts > 0 )); then
  printf "\033[33mWARNING:\033[0m %d conflict(s) require manual review (see CONFLICT lines above)\n" \
    "$conflicts" >&2
  exit 1
fi
