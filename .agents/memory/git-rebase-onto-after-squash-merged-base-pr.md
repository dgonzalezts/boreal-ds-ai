# Continuing a branch after its base PR was squash-merged: `git rebase --onto`

Verified in a simulation in EOA-20193 (2026-11-13): 0 conflicts.

## The Problem

A branch stacked on a PR branch cannot simply be merged or rebased after the base PR is squash-merged: the squash commit is a different commit from the base branch's commits, and a merge conflicts in every manifest and in the lockfile that both PRs edited.

## The Fix

Replay only the commits made after the old base tip:

```bash
git rebase --onto origin/release/current <base-branch-tip-before-the-squash> <branch>
git push --force-with-lease=<branch>:<old-tip-sha>
```

- Pass the branch name as the third argument. Without it (`git rebase --onto <base> <old-tip> HEAD`) the result is a DETACHED HEAD and the branch name keeps pointing at the old commits. If that happened, run `git checkout -B <branch>`.
- Record the old base tip and the old branch tip SHA before the squash merge; the lease pins the push to that SHA.
- After the rebase, delete the stale generated file if the build fails: [[stale-generated-components-dts-after-rebase]].

## How to verify

`git log --oneline origin/release/current..<branch>` lists only the branch's own commits; `git status` shows a branch, not a detached HEAD.
