# TODO: Replace Mock Data with Actual LeanParanoia Test Results

## Current Status

The `all-examples-unified-report.json` currently contains **demonstration/mock data** that was manually crafted to showcase the multi-checker UI.

## What We Need

**Actual test output** from running LeanParanoia, lean4checker, and SafeVerify on the LeanParanoia test files.

### Example of Desired Format

```json
{
  "Sorry": [{
    "exploit_file": "Sorry/Direct",
    "leanparanoia": {
      "detected": "yes",
      "message": "CustomAxioms; Sorry; Unsafe",
      "time_ms": 1314.74,
      "time_failfast_ms": 803.55
    },
    "lean4checker": {
      "detected": "no",
      "message": "",
      "time_ms": 2433.46
    },
    "safeverify": {
      "detected": "yes",
      "message": "sorryAx is not in the allowed set of standard axioms",
      "time_ms": 2128.05
    }
  }]
}
```

## How to Generate Real Data

### Option 1: Use LeanParanoia's Comparison Script (if it exists)

```bash
cd /path/to/leanparanoia
# Run comparison script that tests all three tools
# Output should be in JSON format
```

### Option 2: Run Tools Separately and Merge

1. **Build test project**:
```bash
cd /path/to/leanparanoia/tests/project_template
lake build
```

2. **Run LeanParanoia**:
```bash
uv run pytest tests/exploits/ -v --json-report
```

3. **Run lean4checker** (via our adapter):
```bash
python ~/LeanDepViz/scripts/lean4checker_adapter.py \
  --depgraph depgraph.json \
  --out lean4checker-results.json
```

4. **Run SafeVerify** (requires baseline):
```bash
# Create baseline
git checkout baseline-commit
lake build
mv .lake/build /tmp/baseline

# Build current
git checkout current
lake build

python ~/LeanDepViz/scripts/safeverify_adapter.py \
  --depgraph depgraph.json \
  --target-dir /tmp/baseline \
  --submit-dir .lake/build \
  --out safeverify-results.json
```

5. **Merge results**:
```bash
python ~/LeanDepViz/scripts/merge_reports.py \
  --reports paranoia.json lean4checker-results.json safeverify-results.json \
  --out unified-real-data.json
```

## Test Files to Include

From `tests/lean_exploit_files/`:

### Sorry Category
- `Sorry/Direct.lean`
- `Sorry/Admit.lean`  
- `Sorry/ProofAsSorry.lean`

### Axiom Category
- `CustomAxioms/ProveFalse.lean`
- `CustomAxioms/ProveAnything.lean`

### Unsafe Category
- `Unsafe/Definition.lean`

### Partial Category
- `Partial/NonTerminating.lean`

### Valid Category  
- `Valid/Simple.lean`
- `Valid/Dependencies.lean`

## Benefits of Real Data

1. **Accuracy**: Shows actual tool behavior, not assumptions
2. **Credibility**: Demonstrates tools actually work as described
3. **Documentation**: Real timing data shows performance characteristics
4. **Discovery**: May reveal unexpected tool behaviors or edge cases

## Current Workaround

Until we have real data, the mock data has been:
1. Corrected to match known tool behavior (lean4checker passes on sorry-only)
2. Clearly labeled as demonstration data throughout documentation
3. Based on plausible scenarios from test file analysis

## Next Steps

- [ ] Locate or create comparison script that runs all three tools
- [ ] Generate real test results in standardized JSON format
- [ ] Convert to unified report format
- [ ] Replace mock data
- [ ] Update documentation to say "Based on actual LeanParanoia v0.X test results"
- [ ] Add attribution and version info
