#!/usr/bin/env python3
"""
PR Analyzer for Boreal DS monorepo.
Inspects git diff to determine which packages are affected, classify the change
type, and surface checklist sections that reviewers must apply.
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Set


PACKAGE_RULES: Dict[str, Dict] = {
    "packages/boreal-web-components": {
        "label": "boreal-web-components (Stencil)",
        "checklist_sections": ["A"],
    },
    "packages/boreal-react": {
        "label": "boreal-react (React wrapper)",
        "checklist_sections": ["B"],
    },
    "packages/boreal-vue": {
        "label": "boreal-vue (Vue wrapper)",
        "checklist_sections": ["B"],
    },
    "packages/boreal-style-guidelines": {
        "label": "boreal-style-guidelines (tokens)",
        "checklist_sections": ["C"],
    },
    "apps/boreal-docs": {
        "label": "boreal-docs (Storybook)",
        "checklist_sections": ["D"],
    },
    "scripts-boreal": {
        "label": "scripts-boreal (release pipeline)",
        "checklist_sections": ["E"],
    },
}

NATIVE_EVENT_NAMES: Set[str] = {
    "click", "change", "input", "focus", "blur", "keydown", "keyup",
    "keypress", "mousedown", "mouseup", "mouseover", "mouseout",
    "mousemove", "submit", "reset", "scroll", "resize", "load",
    "unload", "error", "select", "touchstart", "touchend", "touchmove",
}


class PrAnalyzer:
    def __init__(self, repo_path: str, base_ref: str = "release/current", verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.base_ref = base_ref
        self.verbose = verbose
        self.results: Dict = {}

    def run(self, print_report: bool = True) -> Dict:
        if print_report:
            print(f"Analyzing PR diff against '{self.base_ref}'...")
            print(f"Repo: {self.repo_path}\n")

        changed_files = self._get_changed_files()
        if not changed_files:
            if print_report:
                print("No changed files detected.")
            self.results = {"changed_files": [], "affected_packages": [], "checklist_sections": [], "findings": []}
            return self.results

        affected_packages = self._detect_affected_packages(changed_files)
        checklist_sections = self._collect_checklist_sections(affected_packages)
        findings = self._check_pr_hygiene(changed_files)

        self.results = {
            "changed_files": changed_files,
            "affected_packages": affected_packages,
            "checklist_sections": sorted(checklist_sections),
            "findings": findings,
        }

        if print_report:
            self._print_report()
        return self.results

    def _run_git(self, args: List[str]) -> str:
        result = subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 and self.verbose:
            print(f"  git warning: {result.stderr.strip()}", file=sys.stderr)
        return result.stdout.strip()

    def _get_changed_files(self) -> List[str]:
        output = self._run_git(["diff", "--name-only", f"{self.base_ref}...HEAD"])
        if not output:
            output = self._run_git(["diff", "--name-only", "HEAD~1", "HEAD"])
        return [f for f in output.splitlines() if f]

    def _detect_affected_packages(self, files: List[str]) -> List[Dict]:
        seen: Set[str] = set()
        affected = []
        for file in files:
            for pkg_prefix, meta in PACKAGE_RULES.items():
                if file.startswith(pkg_prefix) and pkg_prefix not in seen:
                    seen.add(pkg_prefix)
                    affected.append({"path": pkg_prefix, **meta})
        return affected

    def _collect_checklist_sections(self, packages: List[Dict]) -> Set[str]:
        sections: Set[str] = set()
        for pkg in packages:
            sections.update(pkg.get("checklist_sections", []))
        return sections

    def _check_pr_hygiene(self, files: List[str]) -> List[Dict]:
        findings = []

        tsx_files = [f for f in files if f.endswith(".tsx") and "/components/" in f]
        test_files = [f for f in files if "__test__" in f or ".spec." in f]
        story_files = [f for f in files if ".stories." in f or ".mdx" in f.lower()]

        if tsx_files and not test_files:
            findings.append({
                "severity": "warning",
                "rule": "missing-tests",
                "message": "Component TSX files changed but no test files found in the diff.",
                "files": tsx_files,
            })

        if tsx_files and not story_files:
            findings.append({
                "severity": "info",
                "rule": "missing-stories",
                "message": "Component TSX files changed but no Storybook stories found in the diff.",
                "files": tsx_files,
            })

        changelog_files = [f for f in files if "CHANGELOG" in f.upper() or "changeset" in f.lower()]
        if not changelog_files and any(
            f.startswith(tuple(PACKAGE_RULES.keys())) for f in files
        ):
            findings.append({
                "severity": "info",
                "rule": "missing-changeset",
                "message": "No changeset or CHANGELOG entry detected for package-level changes.",
                "files": [],
            })

        return findings

    def _print_report(self):
        r = self.results
        print("=" * 60)
        print("PR ANALYSIS REPORT")
        print("=" * 60)

        print(f"\nChanged files: {len(r['changed_files'])}")
        if self.verbose:
            for f in r["changed_files"]:
                print(f"  {f}")

        print(f"\nAffected packages ({len(r['affected_packages'])}):")
        for pkg in r["affected_packages"]:
            sections = ", ".join(pkg["checklist_sections"])
            print(f"  [{sections}] {pkg['label']}")

        print(f"\nRequired checklist sections: {', '.join(r['checklist_sections']) or 'Universal only'}")

        print(f"\nFindings ({len(r['findings'])}):")
        if r["findings"]:
            for f in r["findings"]:
                icon = "⚠" if f["severity"] == "warning" else "ℹ"
                print(f"  {icon} [{f['rule']}] {f['message']}")
        else:
            print("  No hygiene issues found.")

        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Boreal DS PR Analyzer")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the git repository root")
    parser.add_argument("--base", default="release/current", help="Base branch/ref to diff against (default: release/current)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all changed file paths")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--output", "-o", help="Write JSON output to file")
    args = parser.parse_args()

    analyzer = PrAnalyzer(args.repo_path, base_ref=args.base, verbose=args.verbose)
    results = analyzer.run(print_report=not args.json)

    if args.json:
        output = json.dumps(results, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
