# Multi-Checker Verification Architecture

This branch implements a **defense-in-depth** verification system with multiple complementary checkers.

## Overview

Instead of relying on a single verification tool, LeanDepViz now supports a unified architecture where multiple checkers work together:

```
┌─────────────────────────────────────────────────────┐
│                  Lean Project                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │   leandepviz     │  Extract dependency graph
         │     extract      │  + zone assignment
         └────────┬─────────┘
                  │
                  ▼
          depgraph.json
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
│Paranoia│  │lean4check│  │SafeVerify│  │  FRO   │
│(Policy)│  │ (Kernel) │  │(Ref/Impl)│  │(Future)│
└───┬────┘  └────┬─────┘  └────┬─────┘  └───┬────┘
    │            │             │            │
    ▼            ▼             ▼            ▼
  JSON         JSON          JSON         JSON
    │            │             │            │
    └────────────┴─────────────┴────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  merge_reports  │  Combine all results
        └────────┬────────┘
                 │
                 ▼
        unified_report.json
                 │
                 ▼
        ┌─────────────────┐
        │  HTML Viewer    │  Interactive visualization
        └─────────────────┘
```

## Implemented Checkers

### 1. LeanParanoia (Policy Enforcement) ✅
**Script**: `scripts/paranoia_runner.py`

- **What**: Source-level policy enforcement
- **Checks**: sorry usage, axiom restrictions, unsafe/extern bans, partial functions
- **Speed**: Fast (parallelizable)
- **When**: Every commit, pre-merge
- **Catches**: Policy violations, intentional shortcuts

```bash
python scripts/paranoia_runner.py \
  --depgraph depgraph.json \
  --policy policy.yaml \
  --out paranoia_report.json
```

### 2. lean4checker (Kernel Replay) ✅ NEW
**Script**: `scripts/lean4checker_adapter.py`

- **What**: Replays declarations in the Lean kernel
- **Checks**: Environment validity, kernel-level correctness
- **Speed**: Fast (standard), Slow (--fresh)
- **When**: Changed modules (CI), nightly --fresh on core zones
- **Catches**: Environment hacking, kernel corruption

```bash
# Standard mode (fast)
python scripts/lean4checker_adapter.py \
  --depgraph depgraph.json \
  --out kernel_report.json

# Fresh mode (thorough, slower)
python scripts/lean4checker_adapter.py \
  --depgraph depgraph.json \
  --fresh \
  --out kernel_fresh_report.json
```

### 3. SafeVerify (Reference vs Implementation) ✅ NEW
**Script**: `scripts/safeverify_adapter.py`

- **What**: Compares target (.olean spec) vs submission (.olean impl)
- **Checks**: Statement equality, axiom restrictions, unsafe/partial bans
- **Speed**: Medium
- **When**: PRs modifying theorems, AI-generated code
- **Catches**: Statement changes, spec tampering

```bash
# Build baseline
git checkout main && lake build
mv .lake/build /tmp/target_build

# Build submission
git checkout pr-branch && lake build

# Compare
python scripts/safeverify_adapter.py \
  --depgraph depgraph.json \
  --target-dir /tmp/target_build \
  --submit-dir .lake/build \
  --out safeverify_report.json
```

### 4. FRO Reference Verifier 🔮 PLANNED
**Script**: `scripts/fro_adapter.py` (placeholder)

- **What**: High-assurance environment-level comparison
- **When**: Critical security reviews
- **Adapter ready**: Can be dropped in when available

## Unified Report Format

All adapters output the same JSON schema:

```json
{
  "tool": "paranoia" | "lean4checker" | "safeverify" | "fro",
  "version": "x.y.z",
  "timestamp": "2024-11-01T23:00:00+00:00",
  "declarations": [
    {
      "decl": "MyProject.Module.theorem_name",
      "module": "MyProject.Module",
      "zone": "Core",
      "kind": "theorem",
      "ok": true,
      "checks": ["policy-pass", "kernel-replay"],
      "error": null,
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

## Merging Reports

The `merge_reports.py` script combines results from multiple checkers:

```bash
python scripts/merge_reports.py \
  --reports paranoia_report.json kernel_report.json safeverify_report.json \
  --out unified_report.json
```

Output format:

```json
{
  "merged_report": true,
  "tools": ["paranoia", "lean4checker", "safeverify"],
  "summary": {
    "total_declarations": 100,
    "passed_all": 92,
    "failed_any": 8,
    "by_tool": {
      "paranoia": {"total": 100, "passed": 95, "failed": 5},
      "lean4checker": {"total": 100, "passed": 98, "failed": 2},
      "safeverify": {"total": 100, "passed": 97, "failed": 3}
    }
  },
  "declarations": [
    {
      "decl": "MyProject.theorem",
      "ok": false,  // false if ANY checker failed
      "tools": {
        "paranoia": {"ok": true, "checks": ["policy-pass"]},
        "lean4checker": {"ok": false, "error": "Kernel replay failed"},
        "safeverify": {"ok": true, "checks": ["ref-impl-match"]}
      },
      "summary": {
        "total_checks": 3,
        "passed_checks": 2,
        "failed_checks": 1
      }
    }
  ]
}
```

## Quick Start

### Local Testing

```bash
# 1. Extract graph
lake exe leandepviz extract MyProject -o depgraph.json

# 2. Run checkers
python scripts/paranoia_runner.py --depgraph depgraph.json --policy policy.yaml --out paranoia_report.json
python scripts/lean4checker_adapter.py --depgraph depgraph.json --out kernel_report.json

# 3. Merge
python scripts/merge_reports.py --reports *.json --out unified_report.json

# 4. View
python scripts/embed_data.py \
  --viewer viewer/paranoia-viewer.html \
  --depgraph depgraph.json \
  --report unified_report.json \
  --output review.html
```

### CI Integration

See `.github/workflows/multi-checker-verify.yml.example` for a complete CI workflow.

Key features:
- ✅ Runs all checkers in parallel where possible
- ✅ SafeVerify only on PRs (compares against base branch)
- ✅ Deep kernel check (--fresh) on nightly schedule
- ✅ Posts summary to PR comments
- ✅ Uploads HTML report as artifact
- ✅ Fails CI if any checker fails

## Why Multiple Checkers?

| Issue Type | Paranoia | lean4checker | SafeVerify | FRO |
|------------|----------|--------------|------------|-----|
| **Sorry usage** | ✅ | ❌ | ✅ | ❌ |
| **Disallowed axioms** | ✅ | ❌ | ✅ | ✅ |
| **Unsafe/extern** | ✅ | ❌ | ✅ | ❌ |
| **Partial functions** | ✅ | ❌ | ✅ | ❌ |
| **Kernel corruption** | ❌ | ✅ | ❌ | ✅ |
| **Env hacking** | ❌ | ✅ | ❌ | ✅ |
| **Statement changes** | ❌ | ❌ | ✅ | ✅ |
| **Spec tampering** | ❌ | ❌ | ✅ | ✅ |

**Together they provide defense-in-depth**: Multiple independent checks catch different classes of issues.

## Policy Configuration

Example `zones.yaml`:

```yaml
zones:
  Core:
    patterns: ["MyProject.Core.*"]
    policy:
      allowed_axioms: []
      disallow: [sorry, unsafe, extern, partial, metavariables]
      source_blacklist: ["@[csimp]", "implemented_by"]
  
  Trusted:
    patterns: ["MyProject.Stdlib.*"]
    policy:
      allowed_axioms: ["propext", "Classical.choice", "Quot.sound"]
      disallow: [sorry, metavariables]
  
  Experimental:
    patterns: ["MyProject.Experiments.*"]
    policy:
      allowed_axioms: ["propext", "Classical.choice", "Quot.sound"]
      disallow: [metavariables]
```

## Viewer Enhancements (TODO)

The HTML viewer will be enhanced to show multi-checker results:

- [ ] Toggle badges for each checker (Kernel, Policy, Ref-Impl)
- [ ] Color nodes: red ring if ANY checker fails
- [ ] Tooltip shows which checker(s) failed
- [ ] Table column: "Which checks failed"
- [ ] Support loading unified_report.json with multiple tools

## Files Added

### Adapters
- `scripts/lean4checker_adapter.py` - lean4checker integration
- `scripts/safeverify_adapter.py` - SafeVerify integration
- `scripts/merge_reports.py` - Report merging utility

### Documentation
- `scripts/checkers/README.md` - Comprehensive checker docs
- `MULTI_CHECKER.md` - This file
- `.github/workflows/multi-checker-verify.yml.example` - CI template

### Examples
- `examples/multi-checker-example.sh` - Complete workflow demo

### Modified
- `scripts/paranoia_runner.py` - Updated to output unified format

## Next Steps

1. **Test with real projects**: Run on Exchangeability and LeanParanoia test suite
2. **Enhance viewer**: Add multi-tool visualization support
3. **Performance tuning**: Optimize parallel execution
4. **Add FRO adapter**: When FRO verifier is ready
5. **Documentation**: Tutorial videos, blog post

## References

- [lean4checker](https://github.com/leanprover/lean4checker) - Kernel replay tool
- [SafeVerify](https://github.com/Timeroot/SafeVerify) - Reference vs implementation checker
- [LeanParanoia](https://github.com/oOo0oOo/LeanParanoia) - Policy enforcement tool
- [FRO Verifier Discussion](https://leanprover.zulipchat.com/#narrow/...) - Future high-assurance checker

---

**Branch Status**: 🚧 Prototype/MVP - ready for testing and feedback

**Maintainer**: Cameron Freer (@cameronfreer)
