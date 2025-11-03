#!/usr/bin/env python3
"""
Adapter for lean4checker - kernel replay verification

lean4checker replays declarations in the Lean kernel to ensure they're valid.
It can catch environment hacking and other kernel-level issues.

Usage:
    python lean4checker_adapter.py --depgraph depgraph.json --out kernel_report.json [--fresh]
"""

import json
import subprocess
import shlex
import argparse
from pathlib import Path
from typing import List, Dict, Any

def run_module_check(module: str, fresh: bool = False, cwd: Path = Path.cwd()) -> Dict[str, Any]:
    """Run lean4checker on a module."""
    cmd = ["lake", "exe", "lean4checker"]
    if fresh:
        cmd.append("--fresh")
    cmd.append(module)
    
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=cwd
        )
        
        ok = (p.returncode == 0)
        
        return {
            "module": module,
            "ok": ok,
            "cmd": " ".join(shlex.quote(c) for c in cmd),
            "stdout": p.stdout[-8000:] if p.stdout else "",
            "stderr": p.stderr[-8000:] if p.stderr else "",
            "returncode": p.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "module": module,
            "ok": False,
            "cmd": " ".join(shlex.quote(c) for c in cmd),
            "stdout": "",
            "stderr": "TIMEOUT: lean4checker took longer than 5 minutes",
            "returncode": -1
        }
    except Exception as e:
        return {
            "module": module,
            "ok": False,
            "cmd": " ".join(shlex.quote(c) for c in cmd),
            "stdout": "",
            "stderr": f"ERROR: {str(e)}",
            "returncode": -1
        }

def attach_to_declarations(depgraph: Dict[str, Any], module_results: List[Dict[str, Any]], fresh: bool) -> List[Dict[str, Any]]:
    """
    Map module-level results to declaration-level reports.
    
    Returns list of verification records in unified format.
    """
    by_module = {r["module"]: r for r in module_results}
    
    reports = []
    for node in depgraph.get("nodes", []):
        module = node.get("module")
        decl_name = node.get("fullName", node.get("name"))
        
        result = by_module.get(module)
        if not result:
            continue
        
        tool_name = "lean4checker" + ("-fresh" if fresh else "")
        
        if result["ok"]:
            # Module passed - all declarations pass
            reports.append({
                "decl": decl_name,
                "module": module,
                "tool": tool_name,
                "zone": node.get("zone", "unknown"),
                "ok": True,
                "checks": ["kernel-replay"],
                "notes": "Kernel replay successful",
                "cmd": result["cmd"],
                "exit": 0
            })
        else:
            # Module failed - check if this specific decl is mentioned in output
            output = result["stdout"] + result["stderr"]
            decl_mentioned = decl_name in output
            
            reports.append({
                "decl": decl_name,
                "module": module,
                "tool": tool_name,
                "zone": node.get("zone", "unknown"),
                "ok": False,
                "checks": ["kernel-replay"],
                "error": result["stderr"] if decl_mentioned else f"Module {module} kernel replay failed",
                "notes": result["stdout"][:500] if result["stdout"] else "",
                "cmd": result["cmd"],
                "exit": result["returncode"]
            })
    
    return reports

def main():
    parser = argparse.ArgumentParser(description="Run lean4checker on modules from depgraph")
    parser.add_argument("--depgraph", required=True, help="Path to dependency graph JSON")
    parser.add_argument("--out", required=True, help="Output report JSON path")
    parser.add_argument("--fresh", action="store_true", help="Use --fresh mode (thorough, slower)")
    parser.add_argument("--cwd", help="Working directory for lake commands", default=".")
    parser.add_argument("--modules", nargs="+", help="Specific modules to check (default: all from depgraph)")
    
    args = parser.parse_args()
    
    # Load dependency graph
    with open(args.depgraph) as f:
        depgraph = json.load(f)
    
    # Determine which modules to check
    if args.modules:
        modules = args.modules
    else:
        # Extract unique modules from depgraph
        modules = sorted(set(node["module"] for node in depgraph.get("nodes", []) if node.get("module")))
    
    print(f"Running lean4checker{' --fresh' if args.fresh else ''} on {len(modules)} modules...")
    
    # Run checker on each module
    module_results = []
    for i, module in enumerate(modules, 1):
        print(f"  [{i}/{len(modules)}] Checking {module}...", end=" ", flush=True)
        result = run_module_check(module, fresh=args.fresh, cwd=Path(args.cwd))
        module_results.append(result)
        
        status = "✓" if result["ok"] else "✗"
        print(status)
    
    # Map to declaration-level reports
    print("Mapping results to declarations...")
    reports = attach_to_declarations(depgraph, module_results, args.fresh)
    
    # Write output
    output = {
        "tool": "lean4checker" + ("-fresh" if args.fresh else ""),
        "version": "0.1.0",
        "timestamp": subprocess.run(["date", "-Iseconds"], capture_output=True, text=True).stdout.strip(),
        "modules_checked": len(modules),
        "modules_passed": sum(1 for r in module_results if r["ok"]),
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
    print(f"  Modules: {output['modules_passed']}/{output['modules_checked']} passed")
    print(f"  Declarations: {output['summary']['passed']}/{output['summary']['total']} passed")
    
    # Exit with failure if any checks failed
    if output['summary']['failed'] > 0:
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
