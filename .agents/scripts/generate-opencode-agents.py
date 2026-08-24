#!/usr/bin/env python3
import re
import sys
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n(.*)\Z", re.DOTALL)
AGENT_CALL_RE = re.compile(r"Agent\(([^)]*)\)")
MEMORY_FALLBACK_NOTE = (
    "\n---\n\n"
    "**OpenCode memory note:** Claude Code auto-injects this agent's scoped "
    "memory (`.claude/agent-memory/<name>/MEMORY.md`) every invocation; "
    "OpenCode has no equivalent. Read and update the relevant topic files "
    "under `.agents/memory/` manually — see "
    "`.agents/memory/opencode-agent-memory-fallback.md`.\n"
)


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("file has no parseable frontmatter block")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return frontmatter, body


def build_opencode_frontmatter(frontmatter: dict) -> dict:
    out: dict = {"description": frontmatter["description"]}

    tools_line = frontmatter.get("tools", "")
    agent_match = AGENT_CALL_RE.search(tools_line)

    if agent_match:
        out["mode"] = "primary"
        names = [n.strip() for n in agent_match.group(1).split(",") if n.strip()]
        out["permission"] = {"task": {"*": "deny", **{name: "allow" for name in names}}}
    else:
        out["mode"] = "subagent"

    plain_tools = AGENT_CALL_RE.sub("", tools_line)
    plain_tools = [t.strip() for t in plain_tools.split(",") if t.strip()]
    if plain_tools and "Bash" not in plain_tools:
        out["tools"] = {"bash": False}

    return out


def generate(src: Path, out_dir: Path) -> Path:
    frontmatter, body = split_frontmatter(src.read_text())
    opencode_frontmatter = build_opencode_frontmatter(frontmatter)

    rendered = yaml.safe_dump(
        opencode_frontmatter, sort_keys=False, default_flow_style=False
    )
    out_path = out_dir / src.name
    out_path.write_text(f"---\n{rendered}---\n{body}{MEMORY_FALLBACK_NOTE}")
    return out_path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    src_dir = root / ".agents" / "agents"
    out_dir = root / ".opencode" / "agent"
    out_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for src in sorted(src_dir.glob("*.md")):
        out_path = generate(src, out_dir)
        generated.append(out_path.name)

    for existing in out_dir.glob("*.md"):
        if existing.name not in generated:
            existing.unlink()
            print(f"    removed:  {existing.name} (no matching source)")

    for name in generated:
        print(f"    generated: {name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
