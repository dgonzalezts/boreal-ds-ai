# Agent shell: zsh does not split variables, and `grep` pipelines can print nothing

Observed while running the EOA-20193 procedures from an agent tool shell on macOS (2026-11-13).

## The Problem

- In zsh an unquoted variable holding several words is not split: `for x in $VAR` runs once with the whole string, and `env $cfg cmd` fails because `$cfg` is one argument.
- `grep` pipelines inside the tool shell can silently print nothing, so an empty result is not evidence of zero matches.

## The Fix

- Use arrays (`for x in "${arr[@]}"`), or `${=VAR}` to force splitting, or write the words literally.
- When counting matches or checking absence, use Python (`python3 -I -c ...`) or a quoted glob, and confirm the tool works on a known positive first.

## How to verify

`for x in $VAR; do echo "[$x]"; done` with `VAR="a b"` prints one line in zsh.

Related: [[kill-sandbox-boundary-for-background-tasks]] (the same word-splitting trap for PID lists).
