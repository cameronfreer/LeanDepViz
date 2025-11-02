#!/bin/bash
# Generate LeanParanoia example demos automatically
# Usage: ./scripts/generate_paranoia_examples.sh

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$REPO_DIR/examples/leanparanoia-tests"
TEMP_DIR="/tmp/leandepviz-paranoia-examples-$$"

echo "🔧 Setting up temporary test project..."
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Create lakefile
cat > lakefile.lean << 'EOF'
import Lake
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
EOF

# Create lean-toolchain
echo "leanprover/lean4:v4.24.0-rc1" > lean-toolchain

# Copy example files
echo "📂 Copying example files..."
mkdir -p Examples
cp "$EXAMPLES_DIR"/{Basic,SorryDirect,UnsafeDefinition,PartialNonTerminating,ValidSimple}.lean Examples/

# Create module file
cat > Examples.lean << 'EOF'
import Examples.Basic
import Examples.SorryDirect
import Examples.UnsafeDefinition
import Examples.PartialNonTerminating
import Examples.ValidSimple
EOF

# Create main
cat > Main.lean << 'EOF'
import Examples

def main : IO Unit :=
  IO.println "LeanParanoia Examples"
EOF

# Update and build
echo "🏗️  Building project (this may take a few minutes)..."
lake update > /dev/null 2>&1
if ! lake build 2>&1 | tail -5; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build successful"

# Generate dependency graph
echo "📊 Generating dependency graph..."
lake exe depviz --roots Examples --json-out all-examples.json --dot-out all-examples.dot

# Create mock paranoia report
# In a real scenario, you'd run actual paranoia verification here
echo "🔍 Creating verification report..."
cat > paranoia-report.json << 'EOFREPORT'
{
  "results": [
    {
      "decl": "bad_theorem",
      "zone": "Examples",
      "ok": false,
      "kind": "thm",
      "module": "Examples.Basic",
      "exit": 1,
      "error": "Uses disallowed axioms: bad_axiom"
    },
    {
      "decl": "bad_axiom",
      "zone": "Examples",
      "ok": false,
      "kind": "axiom",
      "module": "Examples.Basic",
      "exit": 1,
      "error": "Custom axiom (proves False)"
    },
    {
      "decl": "good_theorem",
      "zone": "Examples",
      "ok": true,
      "kind": "thm",
      "module": "Examples.Basic",
      "exit": 0
    },
    {
      "decl": "LeanTestProject.Sorry.Direct.exploit_theorem",
      "zone": "Examples",
      "ok": false,
      "kind": "thm",
      "module": "Examples.SorryDirect",
      "exit": 1,
      "error": "Uses sorry"
    },
    {
      "decl": "exploit_theorem",
      "zone": "Examples",
      "ok": false,
      "kind": "thm",
      "module": "Examples.UnsafeDefinition",
      "exit": 1,
      "error": "Uses disallowed axioms: exploit_axiom"
    },
    {
      "decl": "exploit_axiom",
      "zone": "Examples",
      "ok": false,
      "kind": "axiom",
      "module": "Examples.UnsafeDefinition",
      "exit": 1,
      "error": "Custom axiom with unsafe implementation"
    },
    {
      "decl": "seeminglySafeAdd",
      "zone": "Examples",
      "ok": false,
      "kind": "def",
      "module": "Examples.UnsafeDefinition",
      "exit": 1,
      "error": "Uses @[implemented_by] with unsafe function"
    },
    {
      "decl": "unsafeAddImpl",
      "zone": "Examples",
      "ok": false,
      "kind": "def",
      "module": "Examples.UnsafeDefinition",
      "exit": 1,
      "error": "Unsafe definition"
    },
    {
      "decl": "unsafeProof",
      "zone": "Examples",
      "ok": false,
      "kind": "def",
      "module": "Examples.UnsafeDefinition",
      "exit": 1,
      "error": "Unsafe definition (self-referential)"
    },
    {
      "decl": "LeanTestProject.Partial.NonTerminating.exploit_theorem",
      "zone": "Examples",
      "ok": false,
      "kind": "thm",
      "module": "Examples.PartialNonTerminating",
      "exit": 1,
      "error": "Uses sorry"
    },
    {
      "decl": "LeanTestProject.Partial.NonTerminating.loop",
      "zone": "Examples",
      "ok": false,
      "kind": "def",
      "module": "Examples.PartialNonTerminating",
      "exit": 1,
      "error": "Partial function (non-terminating)"
    },
    {
      "decl": "simple_theorem",
      "zone": "Examples",
      "ok": true,
      "kind": "thm",
      "module": "Examples.ValidSimple",
      "exit": 0
    }
  ],
  "summary": {
    "total": 12,
    "passed": 2,
    "failed": 10,
    "mode": "manual"
  }
}
EOFREPORT

# Generate embedded HTML
echo "🌐 Generating embedded HTML demos..."
python3 "$REPO_DIR/scripts/embed_data.py" \
    --viewer "$REPO_DIR/viewer/paranoia-viewer.html" \
    --depgraph all-examples.json \
    --dot all-examples.dot \
    --report paranoia-report.json \
    --output leanparanoia-examples-all.html

# Copy to docs
echo "📦 Copying outputs..."
cp leanparanoia-examples-all.html "$REPO_DIR/docs/"
cp leanparanoia-examples-all.html "$EXAMPLES_DIR/"

# Show stats
FILE_SIZE=$(ls -lh leanparanoia-examples-all.html | awk '{print $5}')
DECL_COUNT=$(jq '.nodes | length' all-examples.json)

echo ""
echo "✨ Generation complete!"
echo "   📄 File: leanparanoia-examples-all.html"
echo "   💾 Size: $FILE_SIZE"
echo "   📊 Declarations: $DECL_COUNT"
echo ""
echo "📍 Output locations:"
echo "   - docs/leanparanoia-examples-all.html"
echo "   - examples/leanparanoia-tests/leanparanoia-examples-all.html"
echo ""
echo "🌐 Will be available at:"
echo "   https://cameronfreer.github.io/LeanDepViz/leanparanoia-examples-all.html"
echo ""
echo "🧹 Cleaning up temporary directory..."
cd /
rm -rf "$TEMP_DIR"

echo "✅ Done!"
