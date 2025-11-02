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

## Generation

Generated from StrongPNT project at commit: (see git log)

```bash
cd ~/work/exch-repos/strongpnt
lake exe depviz --roots StrongPNT --json-out strongpnt.json --dot-out strongpnt.dot
```

## Multi-Checker Verification Status

**Currently**: Dependency graph visualization only ✓  
**LeanParanoia**: ❌ Incompatible (requires Lean v4.24.0, StrongPNT uses v4.21.0)  
**lean4checker**: Not tested yet  
**SafeVerify**: Not tested yet  

See [VERIFICATION_STATUS.md](VERIFICATION_STATUS.md) for details on version compatibility and future plans.

## Note

The StrongPNT source code is NOT included in the LeanDepViz repository. 
This directory only contains the extracted dependency graph data and configuration.
Clone StrongPNT separately at: https://github.com/math-inc/strongpnt
