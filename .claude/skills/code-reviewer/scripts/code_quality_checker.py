#!/usr/bin/env python3
"""
Code Quality Checker for Boreal DS monorepo.
Scans TypeScript/TSX source files for violations of Boreal DS coding standards:
Stencil prop/event/FACE rules, TypeScript safety, and general code quality.
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Rule definitions
# ---------------------------------------------------------------------------

NATIVE_EVENT_NAMES = {
    "click", "change", "input", "focus", "blur", "keydown", "keyup",
    "keypress", "mousedown", "mouseup", "mouseover", "mouseout",
    "mousemove", "submit", "reset", "scroll", "resize", "load",
    "unload", "error", "select", "touchstart", "touchend", "touchmove",
}

# Matches: @Prop(...) someField  (with optional readonly)
RE_PROP_DECL = re.compile(r"@Prop\([^)]*\)\s*(readonly\s+)?(\w+)")
# Matches JSDoc block ending just before the prop line
RE_JSDOC_BEFORE_PROP = re.compile(r"/\*\*[\s\S]*?\*/\s*$")
# Matches: @Prop({ ... }) propName  — without readonly keyword
RE_PROP_NOT_READONLY = re.compile(r"@Prop\([^)]*\)\s+(?!readonly\s)(\w+)")
# Matches mutable prop with broad `as any` cast
RE_MUTABLE_ANY_CAST = re.compile(r"this\.\w+\s*=\s*.*as\s+any")
# Matches: @Event() name  or @Event({ ... }) name
RE_EVENT_DECL = re.compile(r"@Event\([^)]*\)\s+(\w+)")
# Matches @Event() without explicit bubbles/composed/cancelable options
RE_EVENT_NO_OPTIONS = re.compile(r"@Event\(\s*\)")
# Matches class-level JSDoc containing @internal
RE_CLASS_INTERNAL = re.compile(r"/\*\*[\s\S]*?@internal[\s\S]*?\*/\s*@Component")
# Matches @fileoverview (should be @file)
RE_FILEOVERVIEW = re.compile(r"@fileoverview")
# Matches nodeType property access
RE_NODE_TYPE = re.compile(r"\.nodeType\b")
# Matches unsafe `any` usage (not in comments)
RE_ANY_USAGE = re.compile(r":\s*any\b|as\s+any\b|<any>")
# Matches @AttachInternals inside a function/mixin factory
RE_ATTACH_INTERNALS_IN_FUNC = re.compile(
    r"(function|=>)\s*\{[^}]*@AttachInternals\(\)"
)
# Matches formDisabledCallback test using form.disabled
RE_FORM_DISABLED_WRONG = re.compile(r"form\.disabled\s*=")
# Matches waitForChanges missing in spec files after prop/attr assignment
RE_PROP_SET_WITHOUT_WAIT = re.compile(
    r'(\.setProperty|setAttribute|\.(\w+)\s*=\s*[^=])[^\n]*\n(?!\s*await\s+page\.waitForChanges)'
)
# Matches @element or @method in class-level JSDoc
RE_CLASS_JSDOC_ELEMENT_METHOD = re.compile(
    r"/\*\*[\s\S]*?(@element|@method)[\s\S]*?\*/\s*@Component"
)
# Matches event name in @Event declaration that collides with native events
RE_EVENT_NAME_EXTRACT = re.compile(r"@Event\([^)]*\)\s+(\w+)!")


class Finding:
    def __init__(self, rule: str, severity: str, message: str, file: str, line: Optional[int] = None):
        self.rule = rule
        self.severity = severity
        self.message = message
        self.file = file
        self.line = line

    def to_dict(self) -> Dict:
        d = {"rule": self.rule, "severity": self.severity, "message": self.message, "file": self.file}
        if self.line is not None:
            d["line"] = self.line
        return d

    def __str__(self) -> str:
        loc = f":{self.line}" if self.line else ""
        icon = {"error": "✖", "warning": "⚠", "info": "ℹ"}.get(self.severity, "·")
        return f"  {icon} {self.file}{loc}  [{self.rule}] {self.message}"


# ---------------------------------------------------------------------------
# Source preprocessing
# ---------------------------------------------------------------------------

def _strip_jsdoc_bodies(source: str) -> str:
    """Replace JSDoc comment bodies with blank lines, preserving line numbers."""
    def blank_out(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")
    return re.sub(r"/\*\*[\s\S]*?\*/", blank_out, source)


# ---------------------------------------------------------------------------
# Per-file checkers
# ---------------------------------------------------------------------------

def check_tsx_component(path: Path, source: str) -> List[Finding]:
    findings: List[Finding] = []
    rel = str(path)

    is_stencil = "@Component(" in source
    is_spec = "__test__" in str(path) or ".spec." in str(path)

    # Strip JSDoc bodies so decorator patterns inside @example blocks are invisible
    # to per-line checks. Line numbers are preserved (bodies become blank lines).
    code_only = _strip_jsdoc_bodies(source)
    lines = code_only.splitlines()

    if not is_stencil and not is_spec:
        findings += _check_typescript_safety(rel, lines)
        return findings

    if is_spec:
        findings += _check_spec_file(rel, lines, source)
        return findings

    # Stencil component checks
    # prop-jsdoc uses original lines — JSDoc blocks must be visible for the look-behind
    findings += _check_prop_jsdoc(rel, source.splitlines())
    # remaining line-based checks use JSDoc-stripped lines to avoid false positives
    findings += _check_prop_readonly(rel, lines)
    findings += _check_mutable_any_cast(rel, lines)
    findings += _check_event_naming(rel, lines)
    findings += _check_event_options(rel, lines)
    findings += _check_class_jsdoc_tags(rel, source)   # uses full source — anchored to @Component
    findings += _check_fileoverview(rel, lines)
    findings += _check_nodetype(rel, lines)
    findings += _check_typescript_safety(rel, lines)
    findings += _check_face_patterns(rel, source, code_only)

    return findings


def _check_prop_jsdoc(rel: str, lines: List[str]) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines):
        if re.search(r"@Prop\(", line) and not line.strip().startswith("*"):
            preceding = "\n".join(lines[max(0, i - 4):i])
            if "/**" not in preceding:
                findings.append(Finding(
                    rule="prop-missing-jsdoc",
                    severity="error",
                    message="@Prop() declaration is missing a JSDoc block directly above it.",
                    file=rel,
                    line=i + 1,
                ))
    return findings


def _check_prop_readonly(rel: str, lines: List[str]) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines):
        m = re.search(r"@Prop\(([^)]*)\)\s+(?!readonly\s)(\w+)", line)
        if m:
            options = m.group(1)
            if "mutable: true" not in options and "mutable:true" not in options:
                findings.append(Finding(
                    rule="prop-not-readonly",
                    severity="error",
                    message=f"@Prop() '{m.group(2)}' must be declared `readonly` (or explicitly `mutable: true`).",
                    file=rel,
                    line=i + 1,
                ))
    return findings


def _check_mutable_any_cast(rel: str, lines: List[str]) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines):
        if RE_MUTABLE_ANY_CAST.search(line) and "//" not in line.split("as any")[0]:
            findings.append(Finding(
                rule="mutable-prop-any-cast",
                severity="warning",
                message="Mutable prop assignment uses `as any` cast; use a narrow type cast instead.",
                file=rel,
                line=i + 1,
            ))
    return findings


def _check_event_naming(rel: str, lines: List[str]) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines):
        m = RE_EVENT_NAME_EXTRACT.search(line)
        if m:
            name = m.group(1)
            if name.lower() in NATIVE_EVENT_NAMES:
                findings.append(Finding(
                    rule="event-native-collision",
                    severity="error",
                    message=f"@Event() name '{name}' collides with a native DOM event. Use the `bds{{Component}}{{Action}}` prefix pattern.",
                    file=rel,
                    line=i + 1,
                ))
    return findings


def _check_event_options(_rel: str, _lines: List[str]) -> List[Finding]:
    # Boreal DS aligns with Aqua DS and BEEQ: bare @Event() is the accepted convention.
    # All consumers attach listeners directly to the component element, so bubbles/composed
    # are not needed. See ADR .ai/decisions/0003-event-options-convention.md.
    return []


def _check_class_jsdoc_tags(rel: str, source: str) -> List[Finding]:
    findings = []
    if RE_CLASS_INTERNAL.search(source):
        findings.append(Finding(
            rule="class-jsdoc-internal",
            severity="error",
            message="Component class JSDoc contains `@internal`, which removes the component from the CEM. Remove it.",
            file=rel,
        ))
    if RE_CLASS_JSDOC_ELEMENT_METHOD.search(source):
        findings.append(Finding(
            rule="class-jsdoc-invalid-tags",
            severity="warning",
            message="Component class JSDoc uses `@element` or `@method` tags — ignored by the CEM analyzer. Use method-level JSDoc instead.",
            file=rel,
        ))
    return findings


def _check_fileoverview(rel: str, lines: List[str]) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines):
        if RE_FILEOVERVIEW.search(line):
            findings.append(Finding(
                rule="fileoverview-tag",
                severity="error",
                message="Use `@file` for module-level JSDoc, not `@fileoverview` (fails lint rules).",
                file=rel,
                line=i + 1,
            ))
    return findings


def _check_nodetype(rel: str, lines: List[str]) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines):
        if RE_NODE_TYPE.search(line) and not line.strip().startswith("//"):
            findings.append(Finding(
                rule="nodetype-check",
                severity="warning",
                message=".nodeType does not narrow TypeScript types. Use `instanceof Element` instead.",
                file=rel,
                line=i + 1,
            ))
    return findings


def _check_typescript_safety(rel: str, lines: List[str]) -> List[Finding]:
    findings = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        prev_line = lines[i - 1].strip() if i > 0 else ""
        if "eslint-disable" in prev_line and "any" in prev_line:
            continue
        if RE_ANY_USAGE.search(line):
            findings.append(Finding(
                rule="unsafe-any",
                severity="warning",
                message="Broad `any` usage detected. Use a specific type or narrow cast with justification.",
                file=rel,
                line=i + 1,
            ))
    return findings


def _check_face_patterns(rel: str, source: str, code_only: str) -> List[Finding]:
    findings = []

    if "@AttachInternals()" not in source and "formAssociated: true" in source:
        findings.append(Finding(
            rule="face-missing-attach-internals",
            severity="error",
            message="Component has `formAssociated: true` but no `@AttachInternals()` found on the class body.",
            file=rel,
        ))

    has_reset_body = bool(re.search(r"formResetCallback\s*\([^)]*\)\s*:\s*\w+\s*\{", code_only))
    if has_reset_body and "updateValidity" not in code_only and "setValidity" not in code_only:
        findings.append(Finding(
            rule="face-reset-no-validity",
            severity="warning",
            message="`formResetCallback` is defined but `updateValidity()` or `setValidity()` is not called — validity state may be stale after reset.",
            file=rel,
        ))

    has_restore_body = bool(re.search(r"formStateRestoreCallback\s*\([^)]*\)\s*:\s*\w+\s*\{", code_only))
    if has_restore_body and "updateValidity" not in code_only and "syncFormValue" not in code_only:
        findings.append(Finding(
            rule="face-restore-no-validity",
            severity="warning",
            message="`formStateRestoreCallback` is defined but validity is not re-synced — state may be inconsistent after restore.",
            file=rel,
        ))

    native_constraint_attrs = ["required", "minlength", "maxlength", "min", "max", "pattern"]
    for attr in native_constraint_attrs:
        if re.search(rf'<input[^>]+{attr}=', source):
            findings.append(Finding(
                rule="face-native-constraint-on-input",
                severity="error",
                message=f"Inner <input> carries native constraint attribute `{attr}`. Ownership of validity must stay with `ElementInternals.setValidity()`.",
                file=rel,
            ))
            break

    return findings


def _check_spec_file(rel: str, lines: List[str], source: str) -> List[Finding]:
    findings = []

    if RE_FORM_DISABLED_WRONG.search(source):
        findings.append(Finding(
            rule="spec-form-disabled-wrong",
            severity="error",
            message="Test sets `form.disabled` directly — this does NOT trigger `formDisabledCallback`. Use `<fieldset disabled>` instead.",
            file=rel,
        ))

    prop_set_lines = []
    for i, line in enumerate(lines):
        if re.search(r"\.\w+\s*=\s*[^=;{]", line) and "await" not in line:
            prop_set_lines.append(i)

    for idx in prop_set_lines:
        remaining = lines[idx + 1:idx + 3]
        has_wait = any("waitForChanges" in l for l in remaining)
        if not has_wait and idx + 1 < len(lines) and re.search(r"expect\(|getBy|query", lines[idx + 1]):
            findings.append(Finding(
                rule="spec-missing-wait-for-changes",
                severity="warning",
                message="DOM assertion follows a prop/attr assignment without `await page.waitForChanges()`. Stencil renders asynchronously.",
                file=rel,
                line=idx + 2,
            ))

    return findings


# ---------------------------------------------------------------------------
# Directory walker
# ---------------------------------------------------------------------------

class CodeQualityChecker:
    def __init__(self, target_path: str, verbose: bool = False):
        self.target_path = Path(target_path)
        self.verbose = verbose
        self.findings: List[Finding] = []

    def run(self, print_report: bool = True) -> Dict:
        if print_report:
            print(f"Scanning: {self.target_path}\n")

        if not self.target_path.exists():
            print(f"Error: Path does not exist: {self.target_path}", file=sys.stderr)
            sys.exit(1)

        files = self._collect_files()
        for f in files:
            self._analyze_file(f)

        if print_report:
            self._print_report()

        return {
            "target": str(self.target_path),
            "files_scanned": len(files),
            "findings": [f.to_dict() for f in self.findings],
            "summary": self._summary(),
        }

    def _collect_files(self) -> List[Path]:
        if self.target_path.is_file():
            return [self.target_path]
        exts = {".tsx", ".ts"}
        skip_dirs = {"node_modules", "dist", ".stencil", "storybook-static"}
        result = []
        for p in self.target_path.rglob("*"):
            if any(s in p.parts for s in skip_dirs):
                continue
            if p.suffix in exts and p.is_file():
                result.append(p)
        return result

    def _analyze_file(self, path: Path):
        try:
            source = path.read_text(encoding="utf-8")
        except Exception as e:
            if self.verbose:
                print(f"  Could not read {path}: {e}", file=sys.stderr)
            return

        new_findings = check_tsx_component(path, source)
        if self.verbose and new_findings:
            print(f"  {path.name}: {len(new_findings)} finding(s)")
        self.findings.extend(new_findings)

    def _summary(self) -> Dict:
        counts: Dict[str, int] = {"error": 0, "warning": 0, "info": 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _print_report(self):
        summary = self._summary()
        print("=" * 60)
        print("CODE QUALITY REPORT")
        print("=" * 60)

        if self.findings:
            by_file: Dict[str, List[Finding]] = {}
            for f in self.findings:
                by_file.setdefault(f.file, []).append(f)
            for file_path, file_findings in sorted(by_file.items()):
                print(f"\n{file_path}")
                for f in file_findings:
                    print(str(f))
        else:
            print("\n  No findings — all checks passed.")

        print(f"\nSummary: {summary.get('error', 0)} error(s), "
              f"{summary.get('warning', 0)} warning(s), "
              f"{summary.get('info', 0)} info(s)")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Boreal DS Code Quality Checker")
    parser.add_argument("target", nargs="?", default=".", help="File or directory to scan")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-file progress")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--output", "-o", help="Write JSON output to file")
    args = parser.parse_args()

    checker = CodeQualityChecker(args.target, verbose=args.verbose)
    results = checker.run(print_report=not args.json)

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
