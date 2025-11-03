#!/bin/bash
# Build SafeVerify demo: Reference vs Modified comparison
#
# This script:
# 1. Builds reference version
# 2. Builds modified version
# 3. Runs all three verification tools (LeanParanoia, lean4checker, SafeVerify)
# 4. Generates unified report
# 5. Creates interactive HTML viewer
#
# Requirements:
#   - Lean 4.24.0-rc1 (elan)
#   - Python 3
#   - LeanDepViz repository

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
WORK_DIR="/tmp/safeverify-demo-$TIMESTAMP"

echo "=========================================="
echo "SafeVerify Demo Builder"
echo "=========================================="
echo ""
echo "Repository: $REPO_ROOT"
echo "Work directory: $WORK_DIR"
echo ""

# Create work directories
mkdir -p "$WORK_DIR"/{reference,modified}

echo "Step 1: Building Reference Version"
echo "======================================"
cd "$WORK_DIR/reference"

# Create lakefile
cat > lakefile.lean <<'EOF'
import Lake
open Lake DSL

package SafeVerifyDemoRef where
  version := v!"0.1.0"

require LeanDepViz from git
  "https://github.com/CameronFreer/LeanDepViz.git" @ "main"

@[default_target]
lean_lib SafeVerifyDemo where
  roots := #[`SafeVerifyDemo.Reference]
EOF

# Create lean-toolchain
echo "leanprover/lean4:v4.24.0-rc1" > lean-toolchain

# Create module structure
mkdir -p SafeVerifyDemo
cat > SafeVerifyDemo.lean <<'EOF'
import SafeVerifyDemo.Reference
EOF

# Copy reference file
cp "$SCRIPT_DIR/Reference.lean" SafeVerifyDemo/

# Build
echo "Building reference..."
lake update
lake build

# Generate dependency graph
echo "Generating dependency graph..."
lake exe depviz --roots SafeVerifyDemo.Reference \
  --json-out depgraph.json \
  --dot-out depgraph.dot

echo "✓ Reference build complete"
echo ""

echo "Step 2: Building Modified Version"
echo "======================================"
cd "$WORK_DIR/modified"

# Create lakefile (same as reference)
cat > lakefile.lean <<'EOF'
import Lake
open Lake DSL

package SafeVerifyDemoMod where
  version := v!"0.1.0"

require LeanDepViz from git
  "https://github.com/CameronFreer/LeanDepViz.git" @ "main"

@[default_target]
lean_lib SafeVerifyDemo where
  roots := #[`SafeVerifyDemo.Modified]
EOF

# Create lean-toolchain
echo "leanprover/lean4:v4.24.0-rc1" > lean-toolchain

# Create module structure
mkdir -p SafeVerifyDemo
cat > SafeVerifyDemo.lean <<'EOF'
import SafeVerifyDemo.Modified
EOF

# Copy modified file
cp "$SCRIPT_DIR/Modified.lean" SafeVerifyDemo/

# Build
echo "Building modified..."
lake update
lake build

# Generate dependency graph
echo "Generating dependency graph..."
lake exe depviz --roots SafeVerifyDemo.Modified \
  --json-out depgraph.json \
  --dot-out depgraph.dot

echo "✓ Modified build complete"
echo ""

echo "Step 3: Running Verification Tools"
echo "======================================"

# Run LeanParanoia on modified version
echo "Running LeanParanoia..."
# Create simple policy that forbids sorry
cat > "$WORK_DIR/modified/policy.yaml" <<'EOF'
zones:
  - name: "Demo"
    include:
      - "SafeVerifyDemo.**"
    exclude: []
    allowed_axioms:
      - "propext"
      - "Classical.choice"
      - "Quot.sound"
    forbid:
      - "sorry"
      - "metavariables"
    trust_modules:
      - "Init"
      - "Std"
EOF

python3 "$REPO_ROOT/scripts/paranoia_runner.py" \
  --depgraph "$WORK_DIR/modified/depgraph.json" \
  --policy "$WORK_DIR/modified/policy.yaml" \
  --out "$WORK_DIR/paranoia-report.json"

echo "✓ LeanParanoia complete"

# Run lean4checker on modified version
echo "Running lean4checker..."
python3 "$REPO_ROOT/scripts/lean4checker_adapter.py" \
  --depgraph "$WORK_DIR/modified/depgraph.json" \
  --out "$WORK_DIR/lean4checker-report.json"

echo "✓ lean4checker complete"

# Run SafeVerify comparison
echo "Running SafeVerify..."
python3 "$REPO_ROOT/scripts/safeverify_adapter.py" \
  --depgraph "$WORK_DIR/modified/depgraph.json" \
  --target-dir "$WORK_DIR/reference/.lake/build" \
  --submit-dir "$WORK_DIR/modified/.lake/build" \
  --out "$WORK_DIR/safeverify-report.json"

echo "✓ SafeVerify complete"
echo ""

echo "Step 4: Merging Reports"
echo "======================================"
python3 "$REPO_ROOT/scripts/merge_reports.py" \
  --reports "$WORK_DIR/paranoia-report.json" \
           "$WORK_DIR/lean4checker-report.json" \
           "$WORK_DIR/safeverify-report.json" \
  --out "$WORK_DIR/unified-report.json"

echo "✓ Reports merged"
echo ""

echo "Step 5: Generating HTML Viewer"
echo "======================================"
python3 "$REPO_ROOT/scripts/embed_data.py" \
  --viewer "$REPO_ROOT/viewer/paranoia-viewer.html" \
  --depgraph "$WORK_DIR/modified/depgraph.json" \
  --dot "$WORK_DIR/modified/depgraph.dot" \
  --report "$WORK_DIR/unified-report.json" \
  --output "$SCRIPT_DIR/safeverify-demo.html"

echo "✓ HTML viewer generated"
echo ""

# Copy outputs to repository
cp "$WORK_DIR/unified-report.json" "$SCRIPT_DIR/unified-report.json"
cp "$WORK_DIR/modified/depgraph.json" "$SCRIPT_DIR/depgraph.json"
cp "$WORK_DIR/modified/depgraph.dot" "$SCRIPT_DIR/depgraph.dot"

echo "=========================================="
echo "✓ SafeVerify Demo Complete!"
echo "=========================================="
echo ""
echo "Outputs:"
echo "  • HTML viewer: $SCRIPT_DIR/safeverify-demo.html"
echo "  • Unified report: $SCRIPT_DIR/unified-report.json"
echo "  • Dependency graph: $SCRIPT_DIR/depgraph.json"
echo ""
echo "View the demo:"
echo "  open $SCRIPT_DIR/safeverify-demo.html"
echo ""
echo "Key findings (expected):"
echo "  • LeanParanoia: 3 failures (sorry usage)"
echo "  • lean4checker: 4 passes (sorry is valid axiom)"
echo "  • SafeVerify: 3 failures (statement changes detected)"
echo "  • Only 'append_nil_length' passes all checks"
echo ""
echo "Work directory preserved at: $WORK_DIR"
echo ""
