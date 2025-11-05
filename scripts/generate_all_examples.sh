#!/bin/bash
# Generate unified verification report for LeanParanoia test suite examples
# This script creates the data for docs/leanparanoia-examples-all.html
#
# Requirements:
#   - Lean 4.24.0-rc1 (elan)
#   - Python 3
#   - LeanDepViz built (lake build)
#
# Usage:
#   ./scripts/generate_all_examples.sh [--test-dir DIR]
#
# Options:
#   --test-dir DIR    Use specific test directory (default: /tmp/leanparanoia-test-TIMESTAMP)
#   --keep-temp       Don't delete temporary directory after completion
#   --help            Show this help message

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXAMPLES_SOURCE="$PROJECT_ROOT/examples/leanparanoia-tests"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TEST_DIR="${TEST_DIR:-/tmp/leanparanoia-test-$TIMESTAMP}"
KEEP_TEMP=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --test-dir)
      TEST_DIR="$2"
      shift 2
      ;;
    --keep-temp)
      KEEP_TEMP=true
      shift
      ;;
    --help)
      head -n 20 "$0" | grep "^#" | sed 's/^# //; s/^#//'
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "=========================================="
echo "Generate All Examples Unified Report"
echo "=========================================="
echo ""
echo "Project root: $PROJECT_ROOT"
echo "Test directory: $TEST_DIR"
echo ""

# Validate prerequisites
if ! command -v elan &> /dev/null; then
    echo "ERROR: elan not found. Install from https://github.com/leanprover/elan"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Clean up function
cleanup() {
    if [ "$KEEP_TEMP" = false ]; then
        echo "Cleaning up temporary directory..."
        rm -rf "$TEST_DIR"
    else
        echo "Keeping temporary directory: $TEST_DIR"
    fi
}

# Register cleanup on exit
trap cleanup EXIT

# Create test project
echo "Step 1: Creating test project..."
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create lakefile.lean
cat > lakefile.lean <<'EOF'
import Lake
open Lake DSL

package LeanTestProject where
  version := v!"0.1.0"

require LeanDepViz from git
  "https://github.com/CameronFreer/LeanDepViz.git" @ "main"

require paranoia from git
  "https://github.com/oOo0oOo/LeanParanoia.git" @ "main"

@[default_target]
lean_lib LeanTestProject where
EOF

# Create lean-toolchain
echo "leanprover/lean4:v4.24.0-rc1" > lean-toolchain

# Create root module with all 27 test files
cat > LeanTestProject.lean <<'EOF'
-- Basic & CustomAxioms
import LeanTestProject.Basic
import LeanTestProject.ProveAnything
import LeanTestProject.ProveFalse
import LeanTestProject.HiddenInMacro

-- Sorry variants
import LeanTestProject.SorryDirect
import LeanTestProject.Opaque
import LeanTestProject.Intermediate

-- Transitive dependencies
import LeanTestProject.DeepSorry_L0
import LeanTestProject.DeepSorry_L1
import LeanTestProject.DeepAxiom_L0
import LeanTestProject.DeepAxiom_L1

-- Unsafe & Partial
import LeanTestProject.UnsafeDefinition
import LeanTestProject.PartialNonTerminating

-- Extern/FFI
import LeanTestProject.ExportC
import LeanTestProject.PrivateExtern

-- ImplementedBy
import LeanTestProject.DirectReplacement

-- NativeComputation
import LeanTestProject.NativeDecide

-- SourcePatterns
import LeanTestProject.LocalMacroRules

-- KernelRejection
-- import LeanTestProject.NonPositive  -- Commented: doesn't compile by design

-- CSimp
import LeanTestProject.WithAxiom

-- ConstructorIntegrity
import LeanTestProject.ManualConstructor

-- RecursorIntegrity
import LeanTestProject.MissingRecursor

-- Metavariables
import LeanTestProject.Timeout

-- Valid cases
import LeanTestProject.ValidSimple
import LeanTestProject.Helper
import LeanTestProject.Dependencies
import LeanTestProject.WithAxioms
EOF

# Copy example files (27 files total, skip NonPositive as it doesn't compile)
mkdir -p LeanTestProject
EXAMPLE_FILES=(
  "Basic"
  "ProveAnything"
  "ProveFalse"
  "HiddenInMacro"
  "SorryDirect"
  "Opaque"
  "Intermediate"
  "DeepSorry_L0"
  "DeepSorry_L1"
  "DeepAxiom_L0"
  "DeepAxiom_L1"
  "UnsafeDefinition"
  "PartialNonTerminating"
  "ExportC"
  "PrivateExtern"
  "DirectReplacement"
  "NativeDecide"
  "LocalMacroRules"
  "WithAxiom"
  "ManualConstructor"
  "MissingRecursor"
  "Timeout"
  "ValidSimple"
  "Helper"
  "Dependencies"
  "WithAxioms"
)

for file in "${EXAMPLE_FILES[@]}"; do
    if [ ! -f "$EXAMPLES_SOURCE/${file}.lean" ]; then
        echo "ERROR: Missing example file: $EXAMPLES_SOURCE/${file}.lean"
        exit 1
    fi
    cp "$EXAMPLES_SOURCE/${file}.lean" "LeanTestProject/${file}.lean"
done

echo "✓ Copied ${#EXAMPLE_FILES[@]} test files"

# Copy policy
if [ ! -f "$EXAMPLES_SOURCE/policy.yaml" ]; then
    echo "ERROR: Missing policy file: $EXAMPLES_SOURCE/policy.yaml"
    exit 1
fi
cp "$EXAMPLES_SOURCE/policy.yaml" policy.yaml

echo "✓ Test project created"

# Build project
echo ""
echo "Step 2: Building test project..."
lake update
lake build
echo "✓ Build complete"

# Generate dependency graph
echo ""
echo "Step 3: Generating dependency graph..."
lake exe depviz --roots LeanTestProject --json-out depgraph.json --dot-out depgraph.dot
echo "✓ Dependency graph generated"

# Run LeanParanoia
echo ""
echo "Step 4: Running LeanParanoia verification..."
python3 "$PROJECT_ROOT/scripts/paranoia_runner.py" \
  --depgraph depgraph.json \
  --policy policy.yaml \
  --out paranoia-report.json || {
    echo "Note: LeanParanoia found failures (expected for test exploit files)"
    # Check if report was generated
    if [ ! -f "paranoia-report.json" ]; then
        echo "ERROR: paranoia-report.json was not generated"
        exit 1
    fi
}

echo "✓ LeanParanoia complete"

# Run lean4checker
echo ""
echo "Step 5: Running lean4checker verification..."
python3 "$PROJECT_ROOT/scripts/lean4checker_adapter.py" \
  --depgraph depgraph.json \
  --out lean4checker-report.json || {
    echo "Note: lean4checker found failures (expected for some test files)"
    # Check if report was generated
    if [ ! -f "lean4checker-report.json" ]; then
        echo "ERROR: lean4checker-report.json was not generated"
        exit 1
    fi
}

echo "✓ lean4checker complete"

# Merge reports
echo ""
echo "Step 6: Merging verification reports..."
python3 "$PROJECT_ROOT/scripts/merge_reports.py" \
  --reports paranoia-report.json lean4checker-report.json \
  --out unified-report.json || {
    # merge_reports.py exits with code 1 if any declarations failed
    # This is expected for test exploit files
    if [ ! -f "unified-report.json" ]; then
        echo "ERROR: unified-report.json was not generated"
        exit 1
    fi
    echo "Note: Some declarations failed verification (expected for test exploits)"
}

echo "✓ Reports merged"

# Validate the unified report
echo ""
echo "Step 7: Validating unified report..."
python3 "$PROJECT_ROOT/scripts/validate_unified_report.py" \
  --report unified-report.json || {
    echo "Note: Validation warnings/errors (may be expected for test data)"
}

echo "✓ Validation complete"

# Copy outputs to repo
echo ""
echo "Step 8: Copying outputs to repository..."
cp unified-report.json "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-unified-report.json"
cp depgraph.json "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.json"
cp depgraph.dot "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.dot"

echo "✓ Outputs copied"

# Generate SVG preview from DOT file
echo ""
echo "Step 9: Generating SVG preview..."
if command -v dot >/dev/null 2>&1; then
    dot -Tsvg depgraph.dot -o depgraph.svg
    cp depgraph.svg "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.svg"
    echo "✓ SVG preview generated"
else
    echo "⚠ Warning: Graphviz 'dot' command not found, skipping SVG generation"
    echo "  Install with: brew install graphviz"
fi

# Generate HTML viewer
echo ""
echo "Step 10: Generating HTML viewer..."
if [ -f "depgraph.svg" ]; then
    python3 "$PROJECT_ROOT/scripts/embed_data.py" \
      --viewer "$PROJECT_ROOT/viewer/paranoia-viewer.html" \
      --depgraph "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.json" \
      --dot "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.dot" \
      --svg "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.svg" \
      --report "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-unified-report.json" \
      --output "$PROJECT_ROOT/docs/leanparanoia-examples-all.html"
else
    python3 "$PROJECT_ROOT/scripts/embed_data.py" \
      --viewer "$PROJECT_ROOT/viewer/paranoia-viewer.html" \
      --depgraph "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.json" \
      --dot "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-depgraph.dot" \
      --report "$PROJECT_ROOT/examples/leanparanoia-tests/all-examples-unified-report.json" \
      --output "$PROJECT_ROOT/docs/leanparanoia-examples-all.html"
fi

# Also copy to examples directory
cp "$PROJECT_ROOT/docs/leanparanoia-examples-all.html" \
   "$PROJECT_ROOT/examples/leanparanoia-tests/leanparanoia-examples-all.html"

echo "✓ HTML viewer generated"

echo ""
echo "=============================================="
echo "✓ All examples unified report generated!"
echo "=============================================="
echo ""
echo "Outputs:"
echo "  • HTML: docs/leanparanoia-examples-all.html"
echo "  • Unified report: examples/leanparanoia-tests/all-examples-unified-report.json"
echo "  • Dependency graph: examples/leanparanoia-tests/all-examples-depgraph.json"
echo ""
echo "Next steps:"
echo "  1. Review the outputs"
echo "  2. Test the HTML viewer: open docs/leanparanoia-examples-all.html"
echo "  3. Commit the changes:"
echo "     git add docs/leanparanoia-examples-all.html examples/leanparanoia-tests/"
echo "     git commit -m 'Regenerate all-examples unified report'"
echo ""
