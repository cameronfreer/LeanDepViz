# StrongPNT Example

Verification demo for the [StrongPNT project](https://github.com/math-inc/strongpnt) - a formalization of the strong form of the Prime Number Theorem.

## Project Details

- **Repository**: https://github.com/math-inc/strongpnt
- **Lean Version**: v4.21.0
- **Mathlib**: v4.21.0
- **Declarations**: 1129 declarations from the StrongPNT module
- **Dependencies**: 2449 edges in the dependency graph

## About StrongPNT

The StrongPNT project provides a complete formalization of the strong form of the Prime Number Theorem, including:
- Complex analysis foundations
- Logarithmic derivative properties
- Riemann zeta function analysis
- Zero-free regions
- The final strong PNT proof

## Files

- `strongpnt.json` - Dependency graph in JSON format
- `strongpnt.dot` - Dependency graph in DOT format  
- `strongpnt-embedded.html` - Interactive viewer with embedded data

## How to Generate

To extract the dependency graph from your own StrongPNT checkout:

```bash
# Clone StrongPNT
git clone https://github.com/math-inc/strongpnt.git
cd strongpnt

# Add LeanDepViz and build
# (Add LeanDepViz to lakefile.toml or use a local copy)
lake build depviz

# Generate dependency graph
lake exe depviz --roots StrongPNT --json-out strongpnt.json --dot-out strongpnt.dot
```

## Multi-Checker Verification Status

**Currently**: Dependency graph visualization only ✓  
**LeanParanoia**: ❌ Incompatible (requires Lean v4.24.0, StrongPNT uses v4.21.0)  
**lean4checker**: ❌ Incompatible (.olean format mismatch with v4.25.0-rc2)  
**SafeVerify**: ⚠️  N/A (requires baseline + implementation versions)  

**Root Cause**: StrongPNT uses Lean v4.21.0 (October 2024), but all current verification tools require v4.24.0+ (December 2024+).

See [VERIFICATION_STATUS.md](VERIFICATION_STATUS.md) for detailed technical analysis and options.

## Note

The StrongPNT source code is NOT included in the LeanDepViz repository. 
This directory only contains the extracted dependency graph data and configuration.
Clone StrongPNT separately at: https://github.com/math-inc/strongpnt
