#!/usr/bin/env python3
"""
Merge verification reports from multiple checkers into a unified format.

Supports:
- LeanParanoia (paranoia_report.json)
- lean4checker (kernel_report.json)
- SafeVerify (safeverify_report.json)
- Future checkers following the same schema

Usage:
    python merge_reports.py --reports paranoia_report.json kernel_report.json safeverify_report.json --out unified_report.json
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

def load_report(path: Path) -> Dict[str, Any]:
    """Load a verification report JSON file."""
    with open(path) as f:
        return json.load(f)

def normalize_paranoia_report(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize LeanParanoia report to unified format.
    
    Expected input format (from paranoia_runner.py):
    {
        "declarations": [
            {"decl": "name", "ok": bool, "kind": "...", "module": "...", "zone": "...", "exit": int, "error": "..."}
        ]
    }
    """
    normalized = []
    for decl in report.get("declarations", []):
        checks = []
        if not decl.get("ok"):
            # Infer check types from error message
            error = decl.get("error", "").lower()
            if "sorry" in error:
                checks.append("sorry")
            if "axiom" in error:
                checks.append("disallowed-axioms")
            if "unsafe" in error:
                checks.append("unsafe")
            if "partial" in error:
                checks.append("partial")
            if "extern" in error:
                checks.append("extern")
            if not checks:
                checks.append("policy-violation")
        else:
            checks.append("policy-pass")
        
        normalized.append({
            "decl": decl["decl"],
            "module": decl.get("module", ""),
            "tool": "paranoia",
            "zone": decl.get("zone", "unknown"),
            "ok": decl.get("ok", False),
            "checks": checks,
            "error": decl.get("error") if not decl.get("ok") else None,
            "notes": decl.get("notes"),
            "kind": decl.get("kind"),
            "exit": decl.get("exit", 0)
        })
    
    return normalized

def normalize_checker_report(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normalize lean4checker/SafeVerify reports (already in unified format).
    
    Expected input format:
    {
        "tool": "lean4checker" | "safeverify" | ...,
        "declarations": [
            {"decl": "name", "ok": bool, "checks": [...], "error": "...", ...}
        ]
    }
    """
    # Already in unified format, just extract declarations
    return report.get("declarations", [])

def merge_declaration_reports(reports_by_decl: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge multiple reports for the same declaration.
    
    Returns a single merged report per declaration with all checker results.
    """
    merged = []
    
    for decl_name, decl_reports in sorted(reports_by_decl.items()):
        # Use first report as base
        base = decl_reports[0].copy()
        
        # Collect all tools and their results
        tools = {}
        all_checks = []
        all_errors = []
        overall_ok = True
        
        for rep in decl_reports:
            tool = rep["tool"]
            tools[tool] = {
                "ok": rep["ok"],
                "checks": rep.get("checks", []),
                "error": rep.get("error"),
                "notes": rep.get("notes")
            }
            
            all_checks.extend(rep.get("checks", []))
            if rep.get("error"):
                all_errors.append(f"[{tool}] {rep['error']}")
            
            if not rep["ok"]:
                overall_ok = False
        
        # Build merged report
        merged.append({
            "decl": decl_name,
            "module": base.get("module", ""),
            "zone": base.get("zone", "unknown"),
            "kind": base.get("kind"),
            "ok": overall_ok,
            "tools": tools,
            "checks": list(set(all_checks)),  # unique checks
            "error": "; ".join(all_errors) if all_errors else None,
            "summary": {
                "total_checks": len(decl_reports),
                "passed_checks": sum(1 for r in decl_reports if r["ok"]),
                "failed_checks": sum(1 for r in decl_reports if not r["ok"]),
            }
        })
    
    return merged

def main():
    parser = argparse.ArgumentParser(description="Merge verification reports from multiple checkers")
    parser.add_argument("--reports", nargs="+", required=True, help="Verification report JSON files")
    parser.add_argument("--out", required=True, help="Output unified report JSON")
    parser.add_argument("--summary-only", action="store_true", help="Only output summary, not full declarations")
    
    args = parser.parse_args()
    
    print(f"Merging {len(args.reports)} verification reports...")
    
    # Load and normalize all reports
    all_declarations = []
    tool_summaries = {}
    
    for report_path in args.reports:
        path = Path(report_path)
        if not path.exists():
            print(f"  ⚠ Skipping missing report: {path}")
            continue
        
        print(f"  Loading {path.name}...", end=" ")
        report = load_report(path)
        tool_name = report.get("tool", path.stem)
        
        # Normalize based on tool
        if tool_name.startswith("paranoia") or "paranoia" in path.stem:
            normalized = normalize_paranoia_report(report)
        else:
            normalized = normalize_checker_report(report)
        
        all_declarations.extend(normalized)
        
        # Store tool summary
        tool_summaries[tool_name] = report.get("summary", {})
        print(f"✓ ({len(normalized)} declarations)")
    
    # Group by declaration name
    by_decl = defaultdict(list)
    for decl in all_declarations:
        by_decl[decl["decl"]].append(decl)
    
    print(f"\nMerging reports for {len(by_decl)} unique declarations...")
    
    # Merge declarations
    merged_declarations = merge_declaration_reports(by_decl)
    
    # Compute overall summary
    summary = {
        "total_declarations": len(merged_declarations),
        "passed_all": sum(1 for d in merged_declarations if d["ok"]),
        "failed_any": sum(1 for d in merged_declarations if not d["ok"]),
        "by_tool": tool_summaries
    }
    
    # Build output
    output = {
        "merged_report": True,
        "version": "1.0.0",
        "tools": list(tool_summaries.keys()),
        "summary": summary,
    }
    
    if not args.summary_only:
        output["declarations"] = merged_declarations
    
    # Write output
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Unified report written to {args.out}")
    print(f"  Declarations: {summary['passed_all']}/{summary['total_declarations']} passed all checks")
    print(f"  Failed any check: {summary['failed_any']}")
    print(f"  Tools included: {', '.join(output['tools'])}")
    
    # Exit with failure if any declarations failed
    if summary['failed_any'] > 0:
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
