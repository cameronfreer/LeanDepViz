# Multi-Checker Integration Branch

**Status**: 🚧 Prototype/Testing

This branch implements a multi-checker verification architecture for defense-in-depth Lean code verification.

## What's New

### Three Verification Backends

1. **LeanParanoia** (existing) - Policy enforcement
2. **lean4checker** (new) - Kernel replay verification  
3. **SafeVerify** (new) - Reference vs implementation comparison

### Unified Architecture

All checkers output the same JSON format and can be combined via `merge_reports.py`.

## Quick Start

```bash
# 1. Extract dependency graph
lake exe leandepviz extract MyProject -o depgraph.json

# 2. Run checkers (run any/all)
python scripts/paranoia_runner.py --depgraph depgraph.json --policy policy.yaml --out paranoia_report.json
python scripts/lean4checker_adapter.py --depgraph depgraph.json --out kernel_report.json

# 3. Merge results
python scripts/merge_reports.py --reports paranoia_report.json kernel_report.json --out unified_report.json

# 4. Visualize
python scripts/embed_data.py \
  --viewer viewer/paranoia-viewer.html \
  --depgraph depgraph.json \
  --report unified_report.json \
  --output verification.html
```

## Documentation

- **[MULTI_CHECKER.md](MULTI_CHECKER.md)** - Complete architecture overview
- **[scripts/checkers/README.md](scripts/checkers/README.md)** - Detailed checker documentation
- **[.github/workflows/multi-checker-verify.yml.example](.github/workflows/multi-checker-verify.yml.example)** - CI template

## Testing

Try the example workflow:

```bash
./examples/multi-checker-example.sh
```

## Files Added

### Core Adapters
- `scripts/lean4checker_adapter.py` - lean4checker integration
- `scripts/safeverify_adapter.py` - SafeVerify integration  
- `scripts/merge_reports.py` - Report merger

### Documentation
- `MULTI_CHECKER.md` - Architecture overview
- `scripts/checkers/README.md` - Comprehensive guide
- This file

### Examples
- `examples/multi-checker-example.sh` - Demo workflow
- `.github/workflows/multi-checker-verify.yml.example` - CI template

### Modified
- `scripts/paranoia_runner.py` - Now outputs unified format

## Next Steps

- [ ] Test on real projects (Exchangeability)
- [ ] Enhance viewer for multi-tool display
- [ ] Performance benchmarks
- [ ] Integration tests
- [ ] Add FRO adapter when available

## Why Multiple Checkers?

Different checkers catch different issues:

| Issue | Paranoia | lean4checker | SafeVerify |
|-------|----------|--------------|------------|
| Sorry usage | ✅ | ❌ | ✅ |
| Disallowed axioms | ✅ | ❌ | ✅ |
| Unsafe/extern | ✅ | ❌ | ✅ |
| Kernel corruption | ❌ | ✅ | ❌ |
| Statement changes | ❌ | ❌ | ✅ |

**Together = Defense in Depth** 🛡️

## Questions?

See [MULTI_CHECKER.md](MULTI_CHECKER.md) for detailed documentation.

## Branch Merge Plan

Once tested and verified:
1. Merge to main
2. Tag as v0.3.0
3. Update main README
4. Blog post / announcement
