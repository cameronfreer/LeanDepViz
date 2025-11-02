#!/usr/bin/env python3
"""
Generate LeanParanoia example demos automatically

This script:
1. Creates a temporary Lean project with all example files
2. Builds the project
3. Generates dependency graph (JSON + DOT)
4. Creates mock paranoia verification report
5. Generates embedded HTML demos

Usage:
    python scripts/generate_paranoia_examples.py
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

# Configuration: Example files to include
EXAMPLE_FILES = [
    "Basic.lean",
    "SorryDirect.lean",
    "UnsafeDefinition.lean",
    "PartialNonTerminating.lean",
    "ValidSimple.lean",
]

# Mock verification results (in real usage, run actual paranoia)
VERIFICATION_RESULTS = [
    {"decl": "bad_theorem", "zone": "Examples", "ok": False, "kind": "thm", 
     "module": "Examples.Basic", "exit": 1, 
     "error": "Uses disallowed axioms: bad_axiom"},
    
    {"decl": "bad_axiom", "zone": "Examples", "ok": False, "kind": "axiom",
     "module": "Examples.Basic", "exit": 1,
     "error": "Custom axiom (proves False)"},
    
    {"decl": "good_theorem", "zone": "Examples", "ok": True, "kind": "thm",
     "module": "Examples.Basic", "exit": 0},
    
    {"decl": "LeanTestProject.Sorry.Direct.exploit_theorem", "zone": "Examples", 
     "ok": False, "kind": "thm", "module": "Examples.SorryDirect", "exit": 1,
     "error": "Uses sorry"},
    
    {"decl": "exploit_theorem", "zone": "Examples", "ok": False, "kind": "thm",
     "module": "Examples.UnsafeDefinition", "exit": 1,
     "error": "Uses disallowed axioms: exploit_axiom"},
    
    {"decl": "exploit_axiom", "zone": "Examples", "ok": False, "kind": "axiom",
     "module": "Examples.UnsafeDefinition", "exit": 1,
     "error": "Custom axiom with unsafe implementation"},
    
    {"decl": "seeminglySafeAdd", "zone": "Examples", "ok": False, "kind": "def",
     "module": "Examples.UnsafeDefinition", "exit": 1,
     "error": "Uses @[implemented_by] with unsafe function"},
    
    {"decl": "unsafeAddImpl", "zone": "Examples", "ok": False, "kind": "def",
     "module": "Examples.UnsafeDefinition", "exit": 1,
     "error": "Unsafe definition"},
    
    {"decl": "unsafeProof", "zone": "Examples", "ok": False, "kind": "def",
     "module": "Examples.UnsafeDefinition", "exit": 1,
     "error": "Unsafe definition (self-referential)"},
    
    {"decl": "LeanTestProject.Partial.NonTerminating.exploit_theorem", "zone": "Examples",
     "ok": False, "kind": "thm", "module": "Examples.PartialNonTerminating", "exit": 1,
     "error": "Uses sorry"},
    
    {"decl": "LeanTestProject.Partial.NonTerminating.loop", "zone": "Examples",
     "ok": False, "kind": "def", "module": "Examples.PartialNonTerminating", "exit": 1,
     "error": "Partial function (non-terminating)"},
    
    {"decl": "simple_theorem", "zone": "Examples", "ok": True, "kind": "thm",
     "module": "Examples.ValidSimple", "exit": 0},
]


def main():
    script_dir = Path(__file__).parent.absolute()
    repo_dir = script_dir.parent
    examples_dir = repo_dir / "examples" / "leanparanoia-tests"
    
    print("🔧 Setting up temporary test project...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create lakefile
        lakefile = temp_path / "lakefile.lean"
        lakefile.write_text('''import Lake
open Lake DSL

package «examples» where

require paranoia from git
  "https://github.com/oOo0oOo/LeanParanoia.git" @ "main"

require LeanDepViz from git
  "https://github.com/cameronfreer/LeanDepViz.git" @ "main"

lean_lib «Examples» where
  roots := #[`Examples]

@[default_target]
lean_exe «examples» where
  root := `Main
''')
        
        # Create lean-toolchain
        (temp_path / "lean-toolchain").write_text("leanprover/lean4:v4.24.0-rc1\n")
        
        # Copy example files
        print("📂 Copying example files...")
        examples_lib = temp_path / "Examples"
        examples_lib.mkdir()
        
        modules = []
        for example_file in EXAMPLE_FILES:
            src = examples_dir / example_file
            dst = examples_lib / example_file
            shutil.copy(src, dst)
            module_name = example_file.replace(".lean", "")
            modules.append(f"import Examples.{module_name}")
        
        # Create Examples.lean
        (temp_path / "Examples.lean").write_text("\n".join(modules) + "\n")
        
        # Create Main.lean
        (temp_path / "Main.lean").write_text('''import Examples

def main : IO Unit :=
  IO.println "LeanParanoia Examples"
''')
        
        # Build project
        print("🏗️  Building project (this may take a few minutes)...")
        try:
            subprocess.run(["lake", "update"], cwd=temp_path, check=True,
                          capture_output=True, text=True)
            result = subprocess.run(["lake", "build"], cwd=temp_path, check=True,
                                   capture_output=True, text=True)
            # Show last few lines of output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:
                    print(f"  {line}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print(e.stderr)
            return 1
        
        print("✅ Build successful")
        
        # Generate dependency graph
        print("📊 Generating dependency graph...")
        subprocess.run([
            "lake", "exe", "depviz",
            "--roots", "Examples",
            "--json-out", "all-examples.json",
            "--dot-out", "all-examples.dot"
        ], cwd=temp_path, check=True)
        
        # Create paranoia report
        print("🔍 Creating verification report...")
        report = {
            "results": VERIFICATION_RESULTS,
            "summary": {
                "total": len(VERIFICATION_RESULTS),
                "passed": sum(1 for r in VERIFICATION_RESULTS if r["ok"]),
                "failed": sum(1 for r in VERIFICATION_RESULTS if not r["ok"]),
                "mode": "manual"
            }
        }
        
        report_file = temp_path / "paranoia-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate embedded HTML
        print("🌐 Generating embedded HTML demo...")
        subprocess.run([
            "python3",
            str(script_dir / "embed_data.py"),
            "--viewer", str(repo_dir / "viewer" / "paranoia-viewer.html"),
            "--depgraph", "all-examples.json",
            "--dot", "all-examples.dot",
            "--report", "paranoia-report.json",
            "--output", "leanparanoia-examples-all.html"
        ], cwd=temp_path, check=True)
        
        # Copy outputs
        print("📦 Copying outputs...")
        output_file = temp_path / "leanparanoia-examples-all.html"
        shutil.copy(output_file, repo_dir / "docs" / "leanparanoia-examples-all.html")
        shutil.copy(output_file, examples_dir / "leanparanoia-examples-all.html")
        
        # Show stats
        file_size = output_file.stat().st_size
        with open(temp_path / "all-examples.json") as f:
            decl_count = len(json.load(f)["nodes"])
        
        print()
        print("✨ Generation complete!")
        print(f"   📄 File: leanparanoia-examples-all.html")
        print(f"   💾 Size: {file_size / 1024:.1f}KB")
        print(f"   📊 Declarations: {decl_count}")
        print()
        print("📍 Output locations:")
        print("   - docs/leanparanoia-examples-all.html")
        print("   - examples/leanparanoia-tests/leanparanoia-examples-all.html")
        print()
        print("🌐 Will be available at:")
        print("   https://cameronfreer.github.io/LeanDepViz/leanparanoia-examples-all.html")
        print()
    
    print("✅ Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
