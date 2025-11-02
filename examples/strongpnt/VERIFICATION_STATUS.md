# StrongPNT Verification Status

## Current Status: Dependency Graph Only ✓

We have successfully extracted the dependency graph for StrongPNT:
- **1,129 declarations** from the StrongPNT module
- **2,449 dependency edges**
- Interactive visualization available

## Multi-Checker Verification: Not Yet Compatible ❌

### Version Incompatibility Summary

**StrongPNT**: Lean v4.21.0 (October 2024)  
**LeanParanoia**: Lean v4.24.0 (requires API not in v4.21.0) ❌  
**lean4checker**: Lean v4.25.0-rc2 (incompatible .olean format) ❌  
**SafeVerify**: Requires baseline + implementation (N/A for single version) ⚠️

### Technical Details

#### LeanParanoia
Attempted to add LeanParanoia but encountered compilation errors:
```
error: LeanParanoia/Helpers.lean:174:2: invalid field 'foldl', 
the environment does not contain 'Lean.NameSet.foldl'
```
LeanParanoia uses APIs from Lean v4.24.0 that don't exist in v4.21.0.

#### lean4checker  
Built successfully but cannot replay StrongPNT modules:
```
uncaught exception: failed to read file '.../PNT5_Strong.olean', 
incompatible header
```
The lean4checker bundled with LeanParanoia uses Lean v4.25.0-rc2, which produces incompatible `.olean` files with v4.21.0.

#### SafeVerify
SafeVerify requires two versions to compare (baseline reference vs implementation). Since we only have one version of StrongPNT, this tool isn't applicable without creating a baseline fork or using git history.

### Options to Enable Multi-Checker Verification

1. **Update StrongPNT to Lean v4.24.0**
   - Update `lean-toolchain` to `leanprover/lean4:v4.24.0`
   - Update Mathlib to v4.24.0
   - Rebuild and test all proofs
   - This is the recommended long-term solution

2. **Wait for LeanParanoia backport**
   - LeanParanoia could add compatibility with older Lean versions
   - Would require maintaining multiple code paths

3. **Use lean4checker standalone**
   - The lean4checker component might work independently
   - Would only provide kernel replay verification (no policy checks)

## What Works Now

✅ **Dependency Graph Visualization**
- Full module dependency graph
- Interactive exploration at: https://cameronfreer.github.io/LeanDepViz/strongpnt-example.html
- Shows axiom usage, unsafe declarations, and sorry/admit occurrences

## Future Work

When StrongPNT updates to Lean v4.24.0+, we can:
1. Add LeanParanoia for policy-driven verification
2. Run lean4checker for kernel replay
3. Run SafeVerify for reference comparison
4. Generate unified multi-checker reports

For now, the dependency graph provides valuable insights into the project structure and potential verification concerns.
