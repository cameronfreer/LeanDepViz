# Comparison: Our Demo vs Official LeanParanoia VERIFIER_COMPARISON.md

## Official Data Source

https://github.com/oOo0oOo/LeanParanoia/blob/main/VERIFIER_COMPARISON.md

This contains **REAL verification data** from running:
- LeanParanoia
- lean4checker  
- SafeVerify

On **56 exploit test files** across multiple categories.

## Key Findings from Official Data

### 1. **lean4checker Behavior Confirmed** ✅

Our fix was **CORRECT**! From the official data:

#### Sorry Examples (lean4checker PASSES):
- `Sorry/Direct`: 🛑 LeanParanoia | 🟢 lean4checker | 🛑 SafeVerify
- `Sorry/Admit`: 🛑 LeanParanoia | 🟢 lean4checker | 🛑 SafeVerify
- `Sorry/ByAsSorry`: 🛑 LeanParanoia | 🟢 lean4checker | 🛑 SafeVerify
- `Sorry/ProofAsSorry`: 🛑 LeanParanoia | 🟢 lean4checker | 🛑 SafeVerify
- ALL 8 sorry-only examples: lean4checker shows 🟢 **PASSED**

**Confirmation**: lean4checker performs kernel replay and **does NOT detect sorries**.

#### Axiom Examples (lean4checker PASSES):
- `CustomAxioms/ProveFalse`: 🛑 LeanParanoia | 🟢 lean4checker | 🛑 SafeVerify
- `CustomAxioms/ProveAnything`: 🛑 LeanParanoia | 🟢 lean4checker | 🛑 SafeVerify
- ALL custom axiom examples: lean4checker shows 🟢 **PASSED**

**Surprise**: lean4checker even **passes on custom axioms** if they compile!

#### What lean4checker FAILS On:
- `KernelRejection/NonPositive`: 🛑 lean4checker - "Could not find any oleans"
- `KernelRejection/UnsafeCast`: 🛑 lean4checker - "Could not find any oleans"
- `NativeComputation/NativeDecide`: 🛑 lean4checker - "(kernel) unknown declaration"
- `NativeComputation/OfReduce`: 🛑 lean4checker - "(kernel) unknown declaration"

**Pattern**: lean4checker only fails when:
1. Files don't compile (no .olean files)
2. Kernel interpreter errors
3. Missing declarations

### 2. **SafeVerify Behavior**

From the official data, SafeVerify:
- ✅ **Detects sorries**: All sorry examples show 🛑 "sorryAx is not in the allowed set"
- ✅ **Detects custom axioms**: All custom axiom examples show 🛑  
- 🟡 **Has limitations**: Many 🟡 N/A or "does not match requirement" errors
- ✅ **Passes valid code**: `Valid/Simple`, `Valid/WithAxioms` show 🟢

### 3. **Coverage Comparison**

| Category | Official Data | Our Mock Data |
|----------|--------------|---------------|
| **Total Test Files** | 56 | 17 |
| **Sorry Examples** | 8 | 2 |
| **Axiom Examples** | 18 | ~5 |
| **Unsafe Examples** | 1 direct + many combined | ~5 |
| **Valid Examples** | 6 | 2 |
| **Partial Examples** | 1 | 1-3 |

**Our mock data** is a **subset** and **simplification** of the real test suite.

## What We Got WRONG in Mock Data

### ❌ lean4checker Behavior (FIXED)
- **Was**: Failing on sorries
- **Actually**: Passes on sorries
- **Status**: ✅ **CORRECTED** in commit 1e66f40

### ❌ lean4checker on Axioms
- **Mock**: Shows failing on custom axioms
- **Actually**: PASSES on custom axioms (they compile successfully!)
- **Status**: ⚠️ **STILL WRONG** - needs fixing

### ❌ SafeVerify Accuracy
- **Mock**: Artificially perfect alignment
- **Actually**: Has many 🟡 N/A cases and edge cases
- **Status**: ⚠️ **OVERSIMPLIFIED**

### ❌ Missing Test Categories
Our mock data doesn't include:
- CSimp attacks
- ConstructorIntegrity issues
- Extern/FFI exploits
- ImplementedBy replacements
- Kernel rejection cases
- Metavariables
- NativeComputation issues
- RecursorIntegrity
- SourcePatterns
- Transitive dependency issues

## Timing Data from Official

**LeanParanoia**: ~1.3-1.7s per test (fail-fast ~0.8s)
**lean4checker**: ~2.4s per test (consistent)
**SafeVerify**: ~1.3s per test (consistent)

## Recommendations

### Immediate Actions

1. **Use Official Data** ✅
   - The VERIFIER_COMPARISON.md contains REAL data
   - We should convert this to our unified format
   - Replace mock data entirely

2. **Fix Remaining Inaccuracies**
   - lean4checker should PASS on custom axioms
   - Update mock data for this behavior

3. **Add More Test Categories**
   - Include at least representatives from each category
   - Show the breadth of exploit types

### Long-term

1. **Automated Sync**
   - Script to fetch VERIFIER_COMPARISON.md
   - Convert to our unified JSON format
   - Keep in sync with LeanParanoia updates

2. **Full Test Suite**
   - Include all 56 test cases
   - Show comprehensive coverage
   - Link to specific test files

## Action Items

- [ ] Convert VERIFIER_COMPARISON.md to unified JSON format
- [ ] Fix lean4checker behavior on axioms in mock data
- [ ] Replace all-examples-unified-report.json with real data
- [ ] Update documentation to reference official source
- [ ] Add conversion script for future updates
- [ ] Include more exploit categories
- [ ] Add timing benchmarks section

## Conclusion

The official VERIFIER_COMPARISON.md is **exactly what we need**! It contains:
- ✅ Real verification data from all 3 tools
- ✅ Comprehensive test coverage (56 files)
- ✅ Timing information
- ✅ Proper tool behavior documentation

**Our mock data was a placeholder** - we should now replace it with the real thing!
