#!/usr/bin/env python3
"""
Review Report Generator for Boreal DS monorepo.
Orchestrates pr_analyzer and code_quality_checker, then renders a unified
Markdown review report aligned to the Boreal DS code review checklist.
"""

import re
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Checklist section metadata
# ---------------------------------------------------------------------------

CHECKLIST_SECTIONS = {
    "Universal": [
        ("single-responsibility", "Change has a clear purpose with minimal unrelated edits"),
        ("type-safety", "No `any` usage without justification"),
        ("edge-cases", "Error paths and invalid inputs handled explicitly"),
        ("test-coverage", "New logic is covered by tests"),
        ("async-correctness", "Tests use `waitForChanges()` before DOM assertions"),
        ("docs-updated", "Storybook/MDX/README updated when behavior or APIs change"),
        ("naming-consistent", "Public APIs, events, and props follow naming conventions"),
    ],
    "A — Stencil (boreal-web-components)": [
        ("prop-jsdoc", "Every @Prop() has `readonly` and an adjacent JSDoc block"),
        ("prop-validation", "`validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props"),
        ("event-naming", "Custom events use the `bds{Component}{Action}` prefix pattern"),
        ("no-native-events", "Event names do not reuse native DOM events"),
        ("face-attach-internals", "@AttachInternals() is on the class body, not in a mixin"),
        ("face-method-wrappers", "`checkValidity()` and `reportValidity()` exposed via @Method()"),
        ("face-validity-ownership", "Only ElementInternals.setValidity() manages validity"),
        ("face-reset-restore", "`formResetCallback` and `formStateRestoreCallback` call updateValidity()"),
        ("cem-integrity", "JSDoc changes preserve custom-elements.json generation accuracy"),
    ],
    "B — React/Vue Wrappers": [
        ("wrapper-outputs", "Generated outputs/types rebuilt when web components change"),
        ("internal-dep-location", "@telesign/boreal-web-components stays in `dependencies`"),
        ("release-it-config", "Uses `publishPackageManager: pnpm` with `publishArgs`"),
    ],
    "C — Style Guidelines": [
        ("token-generation", "`generate` and `validate` pass after token changes"),
        ("export-map", "dist/css, dist/scss, and token exports match package.json exports"),
        ("breaking-tokens", "Breaking token changes documented with migration guidance"),
    ],
    "D — Docs (Storybook)": [
        ("stories-updated", "Component behavior changes reflected in stories and MDX"),
        ("vite-css-aliasing", "Storybook aliasing intact for @telesign/boreal-web-components/css/*"),
        ("chromatic-workflow", "Uses `dotenv --` and `--storybook-build-dir`"),
    ],
    "E — Scripts / Release Pipeline": [
        ("build-guarantee", "Pack/validate scripts rely on Turbo `dependsOn`"),
        ("suffix-convention", "Per-framework scripts use :react, :vue, :angular consistently"),
    ],
}

SECTION_LETTER_MAP = {
    "A": "A — Stencil (boreal-web-components)",
    "B": "B — React/Vue Wrappers",
    "C": "C — Style Guidelines",
    "D": "D — Docs (Storybook)",
    "E": "E — Scripts / Release Pipeline",
}

RULE_TO_CHECKLIST: Dict[str, str] = {
    "prop-missing-jsdoc": "prop-jsdoc",
    "prop-not-readonly": "prop-jsdoc",
    "event-native-collision": "no-native-events",
    "class-jsdoc-internal": "cem-integrity",
    "class-jsdoc-invalid-tags": "cem-integrity",
    "fileoverview-tag": "prop-jsdoc",
    "nodetype-check": "type-safety",
    "unsafe-any": "type-safety",
    "mutable-prop-any-cast": "type-safety",
    "face-missing-attach-internals": "face-attach-internals",
    "face-reset-no-validity": "face-reset-restore",
    "face-restore-no-validity": "face-reset-restore",
    "face-native-constraint-on-input": "face-validity-ownership",
    "spec-form-disabled-wrong": "async-correctness",
    "spec-missing-wait-for-changes": "async-correctness",
    "missing-tests": "test-coverage",
    "missing-stories": "docs-updated",
    "missing-changeset": "docs-updated",
}


# ---------------------------------------------------------------------------
# Runner helpers
# ---------------------------------------------------------------------------

def _run_script(script: Path, args: List[str]) -> Optional[Dict]:
    cmd = [sys.executable, str(script)] + args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Warning: {script.name} exited {result.returncode}", file=sys.stderr)
        if result.stderr:
            print(f"  {result.stderr.strip()}", file=sys.stderr)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

class ReviewReportGenerator:
    def __init__(self, repo_path: str, base_ref: str = "release/current", verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.base_ref = base_ref
        self.verbose = verbose
        self.scripts_dir = Path(__file__).parent
        self.results: Dict = {}

    def run(self) -> Dict:
        print(f"Generating review report for: {self.repo_path}\n")

        pr_data = self._run_pr_analyzer()
        quality_data = self._run_quality_checker()

        failed_rules = self._collect_failed_rules(pr_data, quality_data)
        required_sections = self._get_required_sections(pr_data)
        checklist = self._build_checklist(required_sections, failed_rules)

        self.results = {
            "repo": str(self.repo_path),
            "base_ref": self.base_ref,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "affected_packages": pr_data.get("affected_packages", []) if pr_data else [],
            "required_sections": sorted(required_sections),
            "quality_findings": quality_data.get("findings", []) if quality_data else [],
            "pr_findings": pr_data.get("findings", []) if pr_data else [],
            "checklist": checklist,
        }

        report_md = self._render_markdown()
        self._print_report(report_md)
        return self.results

    def _run_pr_analyzer(self) -> Optional[Dict]:
        script = self.scripts_dir / "pr_analyzer.py"
        if not script.exists():
            print("  pr_analyzer.py not found — skipping PR analysis", file=sys.stderr)
            return None
        args = [str(self.repo_path), "--base", self.base_ref]
        if self.verbose:
            args.append("--verbose")
        return _run_script(script, args)

    def _run_quality_checker(self) -> Optional[Dict]:
        script = self.scripts_dir / "code_quality_checker.py"
        if not script.exists():
            print("  code_quality_checker.py not found — skipping quality checks", file=sys.stderr)
            return None

        pr_script = self.scripts_dir / "pr_analyzer.py"
        changed_files: List[str] = []
        if pr_script.exists():
            pr_data = _run_script(pr_script, [str(self.repo_path), "--base", self.base_ref])
            if pr_data:
                changed_files = pr_data.get("changed_files", [])

        if changed_files:
            findings: List[Dict] = []
            for rel_file in changed_files:
                abs_file = self.repo_path / rel_file
                if abs_file.suffix in {".tsx", ".ts"} and abs_file.exists():
                    file_data = _run_script(script, [str(abs_file)])
                    if file_data:
                        findings.extend(file_data.get("findings", []))
            return {"findings": findings}

        return _run_script(script, [str(self.repo_path)])

    def _collect_failed_rules(self, pr_data: Optional[Dict], quality_data: Optional[Dict]) -> set:
        failed = set()
        for source in (pr_data, quality_data):
            if not source:
                continue
            for f in source.get("findings", []):
                checklist_key = RULE_TO_CHECKLIST.get(f.get("rule", ""))
                if checklist_key:
                    failed.add(checklist_key)
        return failed

    def _get_required_sections(self, pr_data: Optional[Dict]) -> set:
        sections = {"Universal"}
        if not pr_data:
            return sections
        for letter in pr_data.get("checklist_sections", []):
            full_name = SECTION_LETTER_MAP.get(letter)
            if full_name:
                sections.add(full_name)
        return sections

    def _build_checklist(self, required_sections: set, failed_rules: set) -> Dict[str, List[Dict]]:
        result = {}
        for section, items in CHECKLIST_SECTIONS.items():
            if section not in required_sections:
                continue
            result[section] = []
            for rule_key, description in items:
                status = "fail" if rule_key in failed_rules else "pass"
                result[section].append({"rule": rule_key, "description": description, "status": status})
        return result

    def _render_markdown(self) -> str:
        r = self.results
        lines = [
            "# Boreal DS — Code Review Report",
            "",
            f"**Generated:** {r['generated_at']}  ",
            f"**Base ref:** `{r['base_ref']}`  ",
            f"**Repository:** `{r['repo']}`",
            "",
        ]

        if r["affected_packages"]:
            lines += ["## Affected Packages", ""]
            for pkg in r["affected_packages"]:
                sections = ", ".join(pkg.get("checklist_sections", []))
                lines.append(f"- **{pkg['label']}** — checklist section(s): {sections}")
            lines.append("")

        all_findings = r["quality_findings"] + r["pr_findings"]
        if all_findings:
            lines += ["## Automated Findings", ""]
            for f in all_findings:
                icon = "🔴" if f.get("severity") == "error" else "🟡" if f.get("severity") == "warning" else "🔵"
                loc = f":{f['line']}" if f.get("line") else ""
                file_ref = f"`{f.get('file', '')}{loc}`" if f.get("file") else ""
                lines.append(f"- {icon} **[{f['rule']}]** {f['message']} {file_ref}".strip())
            lines.append("")

        lines += ["## Review Checklist", ""]
        total_pass = total_fail = 0
        for section, items in r["checklist"].items():
            lines.append(f"### {section}")
            lines.append("")
            for item in items:
                mark = "✅" if item["status"] == "pass" else "❌"
                lines.append(f"- {mark} {item['description']}")
                if item["status"] == "pass":
                    total_pass += 1
                else:
                    total_fail += 1
            lines.append("")

        lines += [
            "---",
            "",
            f"**Result: {total_pass} passed · {total_fail} failed**",
            "",
            "_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_",
        ]

        return "\n".join(lines)

    def _derive_output_path(self) -> Path:
        date_str = datetime.now().strftime("%Y-%m-%d")

        short_sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=self.repo_path, capture_output=True, text=True,
        ).stdout.strip() or "unknown"

        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_path, capture_output=True, text=True,
        ).stdout.strip() or "unknown"

        slug = re.sub(r"[^a-z0-9]+", "-", branch.lower()).strip("-")
        slug = re.sub(r"-+", "-", slug)

        filename = f"{date_str}-commit-{short_sha}-{slug}-review.md"
        reviews_dir = self.repo_path / ".ai" / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)
        return reviews_dir / filename

    def _print_report(self, report_md: str):
        print(report_md)

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        report_md = self._render_markdown()
        path = output_path or self._derive_output_path()
        path.write_text(report_md, encoding="utf-8")
        return path


def main():
    parser = argparse.ArgumentParser(description="Boreal DS Review Report Generator")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to the git repository root")
    parser.add_argument("--base", default="release/current", help="Base branch/ref to diff against (default: release/current)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose mode")
    parser.add_argument("--no-save", action="store_true", help="Skip saving to .ai/reviews/")
    parser.add_argument("--output", "-o", help="Override output file path (implies save)")
    parser.add_argument("--json", action="store_true", help="Output structured results as JSON")
    args = parser.parse_args()

    generator = ReviewReportGenerator(args.repo_path, base_ref=args.base, verbose=args.verbose)
    results = generator.run()

    if not args.no_save:
        output_path = Path(args.output) if args.output else None
        saved_path = generator.save_report(output_path)
        print(f"\nReport saved to {saved_path}")

    if args.json:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
