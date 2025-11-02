#!/usr/bin/env python3
"""
Adapter for SafeVerify - reference vs implementation verification

SafeVerify compares two .olean files (target/spec and submission/impl) to ensure:
- Type signatures match
- No statement changes
- Allowed axioms only
- No unsafe/partial declarations

Usage:
    python safeverify_adapter.py --depgraph depgraph.json --target-dir target/.lake/build --submit-dir .lake/build --out safeverify_report.json
"""

import json
import subprocess
import shlex
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

def find_olean_file(module: str, build_dir: Path) -> Optional[Path]:
    """Find .olean file for a module in build directory."""
    # Convert module name to path: My.Module -> My/Module.olean
    relative_path = Path(*module.split(".")).with_suffix(".olean")
    
    # Common locations
    candidates = [
        build_dir / "lib" / relative_path,
        build_dir / relative_path,
        build_dir.parent / "lib" / relative_path,
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    return None

def run_safeverify(target_olean: Path, submit_olean: Path, cwd: Path = Path.cwd()) -> Dict[str, Any]:
    """Run SafeVerify on a pair of .olean files."""
    cmd = ["lake", "exe", "safe_verify", str(target_olean), str(submit_olean)]
    
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=cwd
        )
        
        ok = (p.returncode == 0)
        
        # Parse SafeVerify output for specific failures
        checks_failed = []
        stdout = p.stdout.lower()
        stderr = p.stderr.lower()
        output = stdout + stderr
        
        if "statement" in output and "changed" in output:
            checks_failed.append("statement-changed")
        if "axiom" in output or "axioms" in output:
            checks_failed.append("extra-axioms")
        if "unsafe" in output:
            checks_failed.append("unsafe")
        if "partial" in output:
            checks_failed.append("partial")
        if "sorry" in output:
            checks_failed.append("sorry")
        
        return {
            "ok": ok,
            "checks_failed": checks_failed,
            "cmd": " ".join(shlex.quote(c) for c in cmd),
            "stdout": p.stdout[-8000:] if p.stdout else "",
            "stderr": p.stderr[-8000:] if p.stderr else "",
            "returncode": p.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "checks_failed": ["timeout"],
            "cmd": " ".join(shlex.quote(c) for c in cmd),
            "stdout": "",
            "stderr": "TIMEOUT: SafeVerify took longer than 60 seconds",
            "returncode": -1
        }
    except Exception as e:
        return {
            "ok": False,
            "checks_failed": ["error"],
            "cmd": " ".join(shlex.quote(c) for c in cmd),
            "stdout": "",
            "stderr": f"ERROR: {str(e)}",
            "returncode": -1
        }

def process_changed_modules(
    depgraph: Dict[str, Any],
    target_build_dir: Path,
    submit_build_dir: Path,
    cwd: Path
) -> List[Dict[str, Any]]:
    """
    Process modules and run SafeVerify for each.
    
    Returns list of declaration-level verification reports.
    """
    # Group declarations by module
    by_module = {}
    for node in depgraph.get("nodes", []):
        module = node.get("module")
        if module:
            by_module.setdefault(module, []).append(node)
    
    reports = []
    modules_checked = 0
    modules_passed = 0
    
    for module, nodes in sorted(by_module.items()):
        print(f"  Checking {module}...", end=" ", flush=True)
        
        # Find .olean files
        target_olean = find_olean_file(module, target_build_dir)
        submit_olean = find_olean_file(module, submit_build_dir)
        
        if not target_olean:
            print(f"⚠ target .olean not found")
            for node in nodes:
                reports.append({
                    "decl": node["name"],
                    "module": module,
                    "tool": "safeverify",
                    "zone": node.get("zone", "unknown"),
                    "ok": False,
                    "checks": ["missing-target"],
                    "error": f"Target .olean not found in {target_build_dir}",
                    "cmd": "",
                    "exit": -1
                })
            continue
        
        if not submit_olean:
            print(f"⚠ submission .olean not found")
            for node in nodes:
                reports.append({
                    "decl": node["name"],
                    "module": module,
                    "tool": "safeverify",
                    "zone": node.get("zone", "unknown"),
                    "ok": False,
                    "checks": ["missing-submission"],
                    "error": f"Submission .olean not found in {submit_build_dir}",
                    "cmd": "",
                    "exit": -1
                })
            continue
        
        # Run SafeVerify
        result = run_safeverify(target_olean, submit_olean, cwd)
        modules_checked += 1
        
        if result["ok"]:
            modules_passed += 1
            print("✓")
            # All declarations in module pass
            for node in nodes:
                reports.append({
                    "decl": node["name"],
                    "module": module,
                    "tool": "safeverify",
                    "zone": node.get("zone", "unknown"),
                    "ok": True,
                    "checks": ["ref-impl-match"],
                    "notes": "Reference and implementation match",
                    "cmd": result["cmd"],
                    "exit": 0
                })
        else:
            print("✗")
            # Module failed - apply to all declarations
            error_msg = result["stderr"] or "SafeVerify verification failed"
            checks = result["checks_failed"] or ["unknown-failure"]
            
            for node in nodes:
                # Check if this specific declaration is mentioned in output
                output = result["stdout"] + result["stderr"]
                decl_mentioned = node["name"] in output
                
                reports.append({
                    "decl": node["name"],
                    "module": module,
                    "tool": "safeverify",
                    "zone": node.get("zone", "unknown"),
                    "ok": False,
                    "checks": checks,
                    "error": error_msg if decl_mentioned else f"Module {module} verification failed: {', '.join(checks)}",
                    "notes": result["stdout"][:500] if result["stdout"] else "",
                    "cmd": result["cmd"],
                    "exit": result["returncode"]
                })
    
    return reports

def main():
    parser = argparse.ArgumentParser(description="Run SafeVerify on changed modules")
    parser.add_argument("--depgraph", required=True, help="Path to dependency graph JSON")
    parser.add_argument("--target-dir", required=True, help="Build directory for target/reference (.lake/build)")
    parser.add_argument("--submit-dir", required=True, help="Build directory for submission/implementation (.lake/build)")
    parser.add_argument("--out", required=True, help="Output report JSON path")
    parser.add_argument("--cwd", help="Working directory for lake commands", default=".")
    
    args = parser.parse_args()
    
    target_build = Path(args.target_dir)
    submit_build = Path(args.submit_dir)
    cwd = Path(args.cwd)
    
    if not target_build.exists():
        print(f"ERROR: Target build directory not found: {target_build}")
        return 1
    
    if not submit_build.exists():
        print(f"ERROR: Submission build directory not found: {submit_build}")
        return 1
    
    # Load dependency graph
    with open(args.depgraph) as f:
        depgraph = json.load(f)
    
    print(f"Running SafeVerify on modules...")
    print(f"  Target: {target_build}")
    print(f"  Submit: {submit_build}")
    
    # Process modules
    reports = process_changed_modules(depgraph, target_build, submit_build, cwd)
    
    # Write output
    output = {
        "tool": "safeverify",
        "version": "0.1.0",
        "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
        "target_dir": str(target_build),
        "submit_dir": str(submit_build),
        "declarations": reports,
        "summary": {
            "total": len(reports),
            "passed": sum(1 for r in reports if r["ok"]),
            "failed": sum(1 for r in reports if not r["ok"])
        }
    }
    
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Report written to {args.out}")
    print(f"  Declarations: {output['summary']['passed']}/{output['summary']['total']} passed")
    
    # Exit with failure if any checks failed
    if output['summary']['failed'] > 0:
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
