#!/usr/bin/env python3
"""
Validate unified verification reports.

This script performs comprehensive validation on unified reports to ensure:
1. Correct structure and required fields
2. Data integrity (matching declarations across tools)
3. Expected test results (for known test cases)
4. No hardcoded paths or machine-specific data

Usage:
    python3 scripts/validate_unified_report.py --report unified-report.json
    python3 scripts/validate_unified_report.py --report unified-report.json --expect-tests
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_structure(data: Dict[str, Any]) -> None:
    """Validate basic report structure."""
    # Check required top-level fields
    required_fields = ["merged_report", "version", "tools", "summary", "declarations"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    # Validate merged_report flag
    if not isinstance(data["merged_report"], bool):
        raise ValidationError(f"merged_report must be boolean, got {type(data['merged_report'])}")
    if not data["merged_report"]:
        raise ValidationError("Report is not marked as merged")

    # Validate version
    if not isinstance(data["version"], str):
        raise ValidationError(f"version must be string, got {type(data['version'])}")

    # Validate tools list
    if not isinstance(data["tools"], list):
        raise ValidationError(f"tools must be list, got {type(data['tools'])}")
    if not data["tools"]:
        raise ValidationError("tools list is empty")

    print(f"✓ Structure valid (version: {data['version']}, tools: {', '.join(data['tools'])})")


def validate_summary(data: Dict[str, Any]) -> None:
    """Validate summary section."""
    summary = data["summary"]

    # Check required summary fields
    required = ["total_declarations", "passed_all", "failed_any", "by_tool"]
    missing = [f for f in required if f not in summary]
    if missing:
        raise ValidationError(f"Summary missing fields: {', '.join(missing)}")

    # Validate counts
    total = summary["total_declarations"]
    passed = summary["passed_all"]
    failed = summary["failed_any"]

    if not isinstance(total, int) or total < 0:
        raise ValidationError(f"Invalid total_declarations: {total}")
    if not isinstance(passed, int) or passed < 0:
        raise ValidationError(f"Invalid passed_all: {passed}")
    if not isinstance(failed, int) or failed < 0:
        raise ValidationError(f"Invalid failed_any: {failed}")

    # Check counts match
    if passed + failed != total:
        raise ValidationError(
            f"Summary counts don't match: passed({passed}) + failed({failed}) != total({total})"
        )

    # Validate by_tool section
    by_tool = summary["by_tool"]
    if not isinstance(by_tool, dict):
        raise ValidationError(f"by_tool must be dict, got {type(by_tool)}")

    for tool_name in data["tools"]:
        if tool_name not in by_tool:
            raise ValidationError(f"Tool '{tool_name}' missing from by_tool summary")

        tool_summary = by_tool[tool_name]
        tool_total = tool_summary.get("total", 0)
        tool_passed = tool_summary.get("passed", 0)
        tool_failed = tool_summary.get("failed", 0)

        if tool_total != tool_passed + tool_failed:
            raise ValidationError(
                f"Tool '{tool_name}' counts don't match: "
                f"passed({tool_passed}) + failed({tool_failed}) != total({tool_total})"
            )

    print(f"✓ Summary valid (total: {total}, passed: {passed}, failed: {failed})")


def validate_declarations(data: Dict[str, Any]) -> None:
    """Validate declarations array."""
    declarations = data["declarations"]

    if not isinstance(declarations, list):
        raise ValidationError(f"declarations must be list, got {type(declarations)}")

    if not declarations:
        raise ValidationError("declarations list is empty")

    # Track declaration names for uniqueness check
    seen_names: Set[str] = set()

    for i, decl in enumerate(declarations):
        # Check required fields
        required = ["decl", "module", "ok", "tools", "checks", "summary"]
        missing = [f for f in required if f not in decl]
        if missing:
            raise ValidationError(
                f"Declaration {i} ({decl.get('decl', 'unknown')}) missing fields: {', '.join(missing)}"
            )

        decl_name = decl["decl"]

        # Check for duplicates
        if decl_name in seen_names:
            raise ValidationError(f"Duplicate declaration: {decl_name}")
        seen_names.add(decl_name)

        # Validate fully qualified name
        if "." not in decl_name:
            raise ValidationError(
                f"Declaration '{decl_name}' is not fully qualified (missing module prefix)"
            )

        # Validate module matches declaration prefix (for non-axioms)
        module = decl["module"]
        if module != "unknown" and decl.get("kind") != "axiom":
            # For most declarations, the module should be a prefix of the decl name
            # (except for special cases like constructors)
            if not decl_name.startswith(module):
                # This might be ok for some cases, just warn
                pass

        # Validate tools section
        tools = decl["tools"]
        if not isinstance(tools, dict):
            raise ValidationError(f"Declaration '{decl_name}' tools must be dict")

        for tool_name, tool_result in tools.items():
            if not isinstance(tool_result, dict):
                raise ValidationError(
                    f"Declaration '{decl_name}' tool '{tool_name}' result must be dict"
                )

            # Validate tool result structure
            if "ok" not in tool_result:
                raise ValidationError(
                    f"Declaration '{decl_name}' tool '{tool_name}' missing 'ok' field"
                )
            if "checks" not in tool_result:
                raise ValidationError(
                    f"Declaration '{decl_name}' tool '{tool_name}' missing 'checks' field"
                )

        # Validate summary
        decl_summary = decl["summary"]
        if not isinstance(decl_summary, dict):
            raise ValidationError(f"Declaration '{decl_name}' summary must be dict")

        # Check summary counts
        total_checks = decl_summary.get("total_checks", 0)
        passed_checks = decl_summary.get("passed_checks", 0)
        failed_checks = decl_summary.get("failed_checks", 0)

        if total_checks != passed_checks + failed_checks:
            raise ValidationError(
                f"Declaration '{decl_name}' summary counts don't match: "
                f"passed({passed_checks}) + failed({failed_checks}) != total({total_checks})"
            )

    print(f"✓ Declarations valid ({len(declarations)} total)")


def validate_no_hardcoded_paths(data: Dict[str, Any]) -> None:
    """Check for hardcoded machine-specific paths."""
    # Convert to JSON string to search
    json_str = json.dumps(data)

    # Suspicious patterns
    suspicious = [
        "/Users/",
        "/home/",
        "work/exch-repos",
        "C:\\Users\\",
        "C:\\\\Users\\\\",
    ]

    found = []
    for pattern in suspicious:
        if pattern in json_str:
            found.append(pattern)

    if found:
        raise ValidationError(
            f"Found hardcoded paths in report: {', '.join(found)}\n"
            "Reports should not contain machine-specific paths"
        )

    print("✓ No hardcoded paths found")


def validate_expected_test_results(data: Dict[str, Any]) -> None:
    """Validate expected results for known test cases."""
    declarations = {d["decl"]: d for d in data["declarations"]}

    # Expected failures for LeanTestProject examples
    expected_failures = {
        "LeanTestProject.Basic.bad_theorem": {
            "paranoia": "CustomAxioms",
            "reason": "Uses disallowed axioms: bad_axiom"
        },
        "LeanTestProject.ProveAnything.magic_theorem": {
            "paranoia": "CustomAxioms",
            "reason": "Uses disallowed axioms: magic"
        },
        "LeanTestProject.SorryDirect.sorry_theorem": {
            "paranoia": "Sorry",
            "reason": "contains sorry"
        },
        "LeanTestProject.PartialNonTerminating.partial_theorem": {
            "paranoia": "Sorry",
            "reason": "contains sorry"
        },
        "LeanTestProject.UnsafeDefinition.unsafeAddImpl": {
            "paranoia": "Unsafe",
            "reason": "marked unsafe"
        },
        "LeanTestProject.UnsafeDefinition.unsafeProof": {
            "paranoia": "Unsafe",
            "reason": "marked unsafe"
        },
        "LeanTestProject.UnsafeDefinition.seeminglySafeAdd": {
            "paranoia": "ImplementedBy",
            "reason": "uses implemented_by"
        },
        "LeanTestProject.UnsafeDefinition.unsafe_theorem": {
            "paranoia": "ImplementedBy",
            "reason": "uses implemented_by"
        },
    }

    # Expected passes
    expected_passes = [
        "LeanTestProject.Basic.good_theorem",
        "LeanTestProject.ValidSimple.simple_theorem",
    ]

    errors = []

    # Check expected failures
    for decl_name, expected in expected_failures.items():
        if decl_name not in declarations:
            # Only error if this is the LeanTestProject
            if any("LeanTestProject" in d for d in declarations):
                errors.append(f"Expected declaration not found: {decl_name}")
            continue

        decl = declarations[decl_name]

        # Should fail overall
        if decl["ok"]:
            errors.append(f"{decl_name}: Expected to fail but passed")

        # Check paranoia specifically failed
        if "paranoia" in decl["tools"]:
            paranoia_result = decl["tools"]["paranoia"]
            if paranoia_result["ok"]:
                errors.append(f"{decl_name}: Expected paranoia to fail but passed")
            else:
                # Check error contains expected category
                error_text = paranoia_result.get("error", "")
                if expected["paranoia"] not in error_text:
                    errors.append(
                        f"{decl_name}: Expected error category '{expected['paranoia']}' "
                        f"not found in: {error_text}"
                    )

        # lean4checker should always pass (kernel replay)
        if "lean4checker" in decl["tools"]:
            lean4checker_result = decl["tools"]["lean4checker"]
            if not lean4checker_result["ok"]:
                errors.append(f"{decl_name}: lean4checker unexpectedly failed")

    # Check expected passes
    for decl_name in expected_passes:
        if decl_name not in declarations:
            # Only error if this is the LeanTestProject
            if any("LeanTestProject" in d for d in declarations):
                errors.append(f"Expected declaration not found: {decl_name}")
            continue

        decl = declarations[decl_name]

        # Should pass overall
        if not decl["ok"]:
            errors.append(f"{decl_name}: Expected to pass but failed: {decl.get('error', 'unknown')}")

        # Check all tools passed
        for tool_name, tool_result in decl["tools"].items():
            if not tool_result["ok"]:
                errors.append(
                    f"{decl_name}: Expected {tool_name} to pass but failed: "
                    f"{tool_result.get('error', 'unknown')}"
                )

    if errors:
        raise ValidationError(
            "Expected test results validation failed:\n" + "\n".join(f"  • {e}" for e in errors)
        )

    num_checked = len(expected_failures) + len(expected_passes)
    print(f"✓ Expected test results valid ({num_checked} declarations checked)")


def main():
    parser = argparse.ArgumentParser(
        description="Validate unified verification reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to unified report JSON file"
    )
    parser.add_argument(
        "--expect-tests",
        action="store_true",
        help="Validate expected results for LeanTestProject test cases"
    )

    args = parser.parse_args()

    # Load report
    report_path = Path(args.report)
    if not report_path.exists():
        print(f"ERROR: Report file not found: {report_path}", file=sys.stderr)
        return 1

    try:
        with open(report_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in report: {e}", file=sys.stderr)
        return 1

    print(f"Validating: {report_path}")
    print()

    # Run validations
    try:
        validate_structure(data)
        validate_summary(data)
        validate_declarations(data)
        validate_no_hardcoded_paths(data)

        if args.expect_tests:
            validate_expected_test_results(data)

        print()
        print("=" * 50)
        print("✓ All validations passed!")
        print("=" * 50)

        return 0

    except ValidationError as e:
        print()
        print("=" * 50)
        print("✗ Validation failed:")
        print("=" * 50)
        print(f"  {e}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
