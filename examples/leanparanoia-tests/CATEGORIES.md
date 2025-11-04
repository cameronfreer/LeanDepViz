# Test File Categories - Complete Coverage

## Overview

**27 test files** covering **all 15 exploit categories** from the official LeanParanoia test suite.

## Files by Category

### 🔴 Custom Axioms (3 files)
- `ProveFalse.lean` - Basic axiom proving False
- `ProveAnything.lean` - Axiom that proves anything
- `HiddenInMacro.lean` - Axiom hidden in macro definition

**Expected behavior**:
- LeanParanoia: 🛑 CustomAxioms
- lean4checker: 🟢 (axioms are valid kernel constructs)
- SafeVerify: 🛑 (axiom not in allowed set)

### 🟡 Sorry Usage (4 files)
- `SorryDirect.lean` - Direct sorry usage
- `Opaque.lean` - Sorry in opaque definition
- `Intermediate.lean` - Sorry through intermediate step
- `DeepSorry_L0.lean` + `DeepSorry_L1.lean` - Sorry in transitive dependency

**Expected behavior**:
- LeanParanoia: 🛑 Sorry
- lean4checker: 🟢 (sorryAx is valid kernel axiom)
- SafeVerify: 🛑 (sorryAx not in allowed set)

### 🟠 Unsafe Code (1 file)
- `UnsafeDefinition.lean` - Unsafe definition with axiom

**Expected behavior**:
- LeanParanoia: 🛑 Unsafe
- lean4checker: 🟢 (compiles successfully)
- SafeVerify: 🛑 (unsafe + axiom violation)

### 🟣 Partial Functions (1 file)
- `PartialNonTerminating.lean` - Non-terminating partial function

**Expected behavior**:
- LeanParanoia: 🛑 Partial
- lean4checker: 🟢 (partial is allowed)
- SafeVerify: 🟡 N/A (verification error)

### 🔵 Extern/FFI (2 files)
- `ExportC.lean` - @[export] FFI exploit
- `PrivateExtern.lean` - private + @[extern] combination

**Expected behavior**:
- LeanParanoia: 🛑 Extern + CustomAxioms
- lean4checker: 🟢 (valid declarations)
- SafeVerify: 🛑 (axiom violation)

### 🟢 Transitive Dependencies (4 files)
- `DeepSorry_L0.lean` - Base level with sorry
- `DeepSorry_L1.lean` - Uses sorry from L0
- `DeepAxiom_L0.lean` - Base level with axiom
- `DeepAxiom_L1.lean` - Uses axiom from L0

**Expected behavior**:
- LeanParanoia: 🛑 Detects through transitive analysis
- lean4checker: 🟢 (valid kernel terms)
- SafeVerify: 🛑 (detects hidden sorry/axiom)

**Why critical**: Shows how exploits hide in dependency chains!

### 🟤 ImplementedBy (1 file)
- `DirectReplacement.lean` - @[implemented_by] compiler replacement

**Expected behavior**:
- LeanParanoia: 🛑 ImplementedBy + CustomAxioms
- lean4checker: 🟢 (valid structure)
- SafeVerify: 🛑 (axiom violation)

### ⚫ NativeComputation (1 file)
- `NativeDecide.lean` - Native decide exploit

**Expected behavior**:
- LeanParanoia: 🛑 NativeComputation + CustomAxioms
- lean4checker: 🛑 **FAILS** - kernel interpreter error!
- SafeVerify: 🛑 kernel error

**Special**: One of the few things lean4checker actually catches!

### 🟦 SourcePatterns (1 file)
- `LocalMacroRules.lean` - Hidden axiom in macro

**Expected behavior**:
- LeanParanoia: 🛑 SourcePatterns + CustomAxioms
- lean4checker: 🟢 (macros expand correctly)
- SafeVerify: 🛑 (axiom detected)

### 🟧 KernelRejection (1 file)
- `NonPositive.lean` - Code that kernel rejects (doesn't compile)

**Expected behavior**:
- LeanParanoia: 🛑 KernelRejection
- lean4checker: 🛑 **FAILS** - no .olean files!
- SafeVerify: 🟡 N/A (can't verify)

**Special**: Shows build failures

### 🟪 CSimp (1 file)
- `WithAxiom.lean` - @[csimp] compiler simplification exploit

**Expected behavior**:
- LeanParanoia: 🛑 CSimp + CustomAxioms
- lean4checker: 🟢
- SafeVerify: 🛑 (axiom violation)

### 🟨 ConstructorIntegrity (1 file)
- `ManualConstructor.lean` - Manual constructor bypassing type checks

**Expected behavior**:
- LeanParanoia: 🛑 ConstructorIntegrity + CustomAxioms
- lean4checker: 🟢
- SafeVerify: 🟡 (type mismatch)

### 🟩 RecursorIntegrity (1 file)
- `MissingRecursor.lean` - Recursor manipulation

**Expected behavior**:
- LeanParanoia: 🛑 RecursorIntegrity + CustomAxioms
- lean4checker: 🟢
- SafeVerify: 🟡 (type mismatch)

### ⬛ Metavariables (1 file)
- `Timeout.lean` - Unsolved metavariables

**Expected behavior**:
- LeanParanoia: 🛑 CustomAxioms + Sorry + Unsafe
- lean4checker: 🟢
- SafeVerify: 🟡 (type mismatch)

### ✅ Valid Code (4 files)
- `ValidSimple.lean` - Simple valid theorem
- `Helper.lean` - Helper definition
- `Dependencies.lean` - Valid theorem using helper
- `WithAxioms.lean` - Valid code using allowed axioms

**Expected behavior**:
- LeanParanoia: 🟢 PASS
- lean4checker: 🟢 PASS
- SafeVerify: 🟢 PASS (or 🟡 type mismatch for some)

### 🔧 Basic/Mixed (1 file)
- `Basic.lean` - Combined test cases

## Tool Behavior Summary

### LeanParanoia
**Role**: Policy enforcement
- Detects: All 15 categories ✓
- Expected: ~23 fail, ~4 pass

### lean4checker
**Role**: Kernel replay verification
- Detects: NativeComputation, KernelRejection
- Misses: Sorry, axioms, most exploits
- Expected: ~2-3 fail, ~24 pass

### SafeVerify
**Role**: Reference vs implementation comparison
- Detects: Most exploits via axiom/sorry checking
- Has edge cases: Type mismatches, verification errors
- Expected: ~18 fail, ~7 N/A/edge, ~2 pass

## Coverage Statistics

| Metric | Value |
|--------|-------|
| **Total Files** | 27 |
| **Categories** | 15 (100% of official suite) |
| **Exploits** | 23 |
| **Valid Cases** | 4 |
| **With Dependencies** | 4 (transitive tests) |

## Notable Patterns

1. **lean4checker passes on sorries and axioms** ✓ Confirmed
2. **lean4checker only fails on**:
   - NativeComputation (interpreter errors)
   - KernelRejection (build failures)
3. **Transitive analysis**: LeanParanoia catches hidden issues in deps
4. **SafeVerify edge cases**: Many 🟡 N/A due to type mismatches

## Source

All files copied from official LeanParanoia test suite:
https://github.com/oOo0oOo/LeanParanoia/tree/main/tests/lean_exploit_files

Imports adjusted for flat structure in examples directory.

## Next Steps

1. Generate demo with `./scripts/generate_all_examples.sh`
2. Validate output with expected behaviors
3. Update documentation to reflect expanded coverage
4. Deploy updated demo to GitHub Pages
