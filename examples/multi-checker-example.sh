#!/bin/bash
# Example workflow demonstrating multi-checker verification

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Multi-Checker Verification Example"
echo "=========================================="
echo ""

# 1. Extract dependency graph
echo "Step 1: Extracting dependency graph..."
lake exe leandepviz extract MyProject -o examples/multi-checker/depgraph.json

# 2. Run LeanParanoia (policy enforcement)
echo ""
echo "Step 2: Running LeanParanoia (policy check)..."
python scripts/paranoia_runner.py \
  --depgraph examples/multi-checker/depgraph.json \
  --policy examples/multi-checker/policy.yaml \
  --out examples/multi-checker/paranoia_report.json

# 3. Run lean4checker (kernel replay)
echo ""
echo "Step 3: Running lean4checker (kernel replay)..."
python scripts/lean4checker_adapter.py \
  --depgraph examples/multi-checker/depgraph.json \
  --out examples/multi-checker/kernel_report.json

# Optional: Run with --fresh for thorough check (slower)
# python scripts/lean4checker_adapter.py \
#   --depgraph examples/multi-checker/depgraph.json \
#   --out examples/multi-checker/kernel_fresh_report.json \
#   --fresh

# 4. Run SafeVerify (reference vs implementation)
# This requires two builds: target and submission
echo ""
echo "Step 4: Running SafeVerify (reference check)..."
echo "  (Skipping - requires baseline build)"
echo "  To run SafeVerify:"
echo "    1. Build baseline: git checkout main && lake build"
echo "    2. Save build: mv .lake/build /tmp/target_build"
echo "    3. Build current: git checkout your-branch && lake build"
echo "    4. Compare:"
echo "       python scripts/safeverify_adapter.py \\"
echo "         --depgraph depgraph.json \\"
echo "         --target-dir /tmp/target_build \\"
echo "         --submit-dir .lake/build \\"
echo "         --out safeverify_report.json"

# 5. Merge reports
echo ""
echo "Step 5: Merging verification reports..."
python scripts/merge_reports.py \
  --reports examples/multi-checker/paranoia_report.json \
            examples/multi-checker/kernel_report.json \
  --out examples/multi-checker/unified_report.json

# 6. Generate HTML viewer
echo ""
echo "Step 6: Generating interactive HTML viewer..."
python scripts/embed_data.py \
  --viewer viewer/paranoia-viewer.html \
  --depgraph examples/multi-checker/depgraph.json \
  --report examples/multi-checker/unified_report.json \
  --output examples/multi-checker/verification_report.html

echo ""
echo "=========================================="
echo "✓ Multi-checker verification complete!"
echo "=========================================="
echo ""
echo "View results:"
echo "  • HTML viewer: open examples/multi-checker/verification_report.html"
echo "  • Unified report: cat examples/multi-checker/unified_report.json | jq '.summary'"
echo ""
echo "Individual reports:"
echo "  • Paranoia: examples/multi-checker/paranoia_report.json"
echo "  • Kernel: examples/multi-checker/kernel_report.json"
echo ""
