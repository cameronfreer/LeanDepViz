# Multi-Checker Verification Architecture

LeanDepViz supports multiple verification backends to provide defense-in-depth for Lean code:

## Available Checkers

### 1. **LeanParanoia** (Policy Enforcement)
- **What**: Enforces source-level policies (no sorry, allowed axioms, unsafe/extern bans)
- **When**: Every commit, pre-merge checks
- **Catches**: Policy violations, intentional shortcuts, risky constructs
- **Adapter**: `paranoia_runner.py` (existing)

### 2. **lean4checker** (Kernel Replay)
- **What**: Replays declarations in the Lean kernel
- **When**: Changed modules (fast), nightly on core zones (--fresh)
- **Catches**: Environment hacking, kernel-level corruption
- **Adapter**: `lean4checker_adapter.py` (new)
- **Modes**:
  - Standard: Fast replay of changed modules
  - `--fresh`: Thorough re-check including imports (slower)

### 3. **SafeVerify** (Reference vs Implementation)
- **What**: Compares target (spec/reference) vs submission (impl) .olean files
- **When**: PRs that modify statements, AI-generated code
- **Catches**: Statement changes, extra axioms, unsafe/partial in impl
- **Adapter**: `safeverify_adapter.py` (new)

### 4. **FRO Reference Verifier** (Planned)
- **What**: Higher-assurance environment-level comparison
- **When**: Critical security reviews, formal verification contexts
- **Adapter**: `fro_adapter.py` (placeholder for future)

## Unified Report Format

All adapters output JSON in this schema:

```json
{
  "tool": "lean4checker" | "paranoia" | "safeverify" | ...,
  "version": "x.y.z",
  "timestamp": "ISO-8601",
  "declarations": [
    {
      "decl": "My.Module.theorem_name",
      "module": "My.Module",
      "zone": "Core" | "Trusted" | ...,
      "ok": true | false,
      "checks": ["kernel-replay", "policy-pass", ...],
      "error": "Error message if ok=false",
      "notes": "Additional context",
      "cmd": "Command that was run",
      "exit": 0
    }
  ],
  "summary": {
    "total": 100,
    "passed": 95,
    "failed": 5
  }
}
```

## Workflow

### 1. Extract Dependency Graph
```bash
lake exe leandepviz extract MyProject -o depgraph.json --zones zones.yaml
```

### 2. Run Individual Checkers

**LeanParanoia (policy)**:
```bash
python scripts/paranoia_runner.py \
  --depgraph depgraph.json \
  --policy policy.yaml \
  --out paranoia_report.json
```

**lean4checker (kernel)**:
```bash
python scripts/lean4checker_adapter.py \
  --depgraph depgraph.json \
  --out kernel_report.json
  
# For thorough check (slower):
python scripts/lean4checker_adapter.py \
  --depgraph depgraph.json \
  --out kernel_fresh_report.json \
  --fresh
```

**SafeVerify (ref vs impl)**:
```bash
# First build both versions
git checkout main
lake build
mv .lake/build /tmp/target_build

git checkout pr-branch
lake build

# Then compare
python scripts/safeverify_adapter.py \
  --depgraph depgraph.json \
  --target-dir /tmp/target_build \
  --submit-dir .lake/build \
  --out safeverify_report.json
```

### 3. Merge Reports
```bash
python scripts/merge_reports.py \
  --reports paranoia_report.json kernel_report.json safeverify_report.json \
  --out unified_report.json
```

### 4. Visualize
```bash
python scripts/embed_data.py \
  --viewer viewer/paranoia-viewer.html \
  --depgraph depgraph.json \
  --report unified_report.json \
  --output review.html
  
# Open in browser
open review.html
```

## CI Integration

### Example GitHub Actions Workflow

```yaml
name: Multi-Checker Verification

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Need history for SafeVerify
      
      # Build submission
      - name: Build project
        run: lake build
      
      # Extract dependency graph
      - name: Extract dependency graph
        run: |
          lake exe leandepviz extract MyProject -o depgraph.json
      
      # Run LeanParanoia
      - name: Policy check (LeanParanoia)
        run: |
          python scripts/paranoia_runner.py \
            --depgraph depgraph.json \
            --policy policy.yaml \
            --out paranoia_report.json
      
      # Run lean4checker
      - name: Kernel replay (lean4checker)
        run: |
          python scripts/lean4checker_adapter.py \
            --depgraph depgraph.json \
            --out kernel_report.json
      
      # Run SafeVerify (PR only)
      - name: Reference check (SafeVerify)
        if: github.event_name == 'pull_request'
        run: |
          # Build target
          git checkout ${{ github.base_ref }}
          lake build
          mv .lake/build /tmp/target_build
          
          # Build submission
          git checkout ${{ github.head_ref }}
          lake build
          
          # Compare
          python scripts/safeverify_adapter.py \
            --depgraph depgraph.json \
            --target-dir /tmp/target_build \
            --submit-dir .lake/build \
            --out safeverify_report.json
      
      # Merge reports
      - name: Merge verification reports
        run: |
          python scripts/merge_reports.py \
            --reports paranoia_report.json kernel_report.json safeverify_report.json \
            --out unified_report.json
      
      # Generate review page
      - name: Generate verification report
        run: |
          python scripts/embed_data.py \
            --viewer viewer/paranoia-viewer.html \
            --depgraph depgraph.json \
            --report unified_report.json \
            --output verification_report.html
      
      # Upload artifact
      - name: Upload verification report
        uses: actions/upload-artifact@v3
        with:
          name: verification-report
          path: |
            unified_report.json
            verification_report.html
      
      # Fail if any checker failed
      - name: Check verification results
        run: |
          if [ $(jq '.summary.failed_any' unified_report.json) -gt 0 ]; then
            echo "❌ Verification failed"
            exit 1
          fi
          echo "✅ All verifications passed"
```

## Policy Configuration

Create `zones.yaml` for zone assignment:

```yaml
zones:
  Core:
    patterns:
      - "MyProject.Core.*"
    policy:
      allowed_axioms: []
      disallow: [sorry, unsafe, extern, partial]
      source_blacklist: ["@[csimp]", "implemented_by"]
  
  Trusted:
    patterns:
      - "MyProject.Stdlib.*"
    policy:
      allowed_axioms: ["propext", "Classical.choice", "Quot.sound"]
      disallow: [sorry, metavariables]
  
  Experimental:
    patterns:
      - "MyProject.Experiments.*"
    policy:
      allowed_axioms: ["propext", "Classical.choice", "Quot.sound"]
      disallow: [metavariables]
```

## Checker Comparison

| Checker | Speed | Coverage | Use Case |
|---------|-------|----------|----------|
| **LeanParanoia** | Fast | Source-level | Daily development, policy enforcement |
| **lean4checker** | Fast (standard)<br>Slow (--fresh) | Kernel-level | Changed modules (CI)<br>Full validation (nightly) |
| **SafeVerify** | Medium | Statement equality | PRs, AI-generated code |
| **FRO** (future) | Slow | Environment-level | Critical security reviews |

## Benefits of Multi-Checker Approach

1. **Defense in Depth**: Multiple layers catch different issue types
2. **Complementary**: LeanParanoia (policy) + lean4checker (kernel) + SafeVerify (ref-impl)
3. **Flexible**: Choose checkers based on context (CI vs nightly vs PR)
4. **Unified View**: Merge reports for single verification status per declaration
5. **Extensible**: Easy to add new checkers following the adapter pattern

## Adding a New Checker

1. **Create adapter script**: `scripts/your_checker_adapter.py`
2. **Implement standard interface**:
   - Input: `--depgraph depgraph.json`
   - Output: `--out report.json` (unified schema)
   - Returns: exit code 0 (pass) or 1 (fail)
3. **Output unified format**: See schema above
4. **Document**: Add to this README
5. **Update merge_reports.py**: Handle tool-specific normalization if needed
6. **Test**: Run on example projects

## Troubleshooting

**lean4checker fails on .olean cache**:
- Solution: `lake clean && lake build` before running

**SafeVerify can't find .olean files**:
- Check: `--target-dir` and `--submit-dir` point to `.lake/build`
- Try: Absolute paths instead of relative

**Timeout on large projects**:
- Increase timeout in adapter (default: 5min for lean4checker, 1min for SafeVerify)
- Run on specific modules: `--modules MyProject.Core MyProject.Main`

**Merge reports shows wrong tool**:
- Check: Report JSON has `"tool": "correct_name"` field
- Fix: Normalize in `merge_reports.py` if needed
