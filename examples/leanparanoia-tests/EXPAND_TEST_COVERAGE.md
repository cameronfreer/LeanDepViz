# Plan: Expand Test Coverage with More Categories

## Current Coverage

We currently have **7 test files** covering **5 categories**:

| Category | Current Files | Count |
|----------|--------------|-------|
| CustomAxioms | `ProveAnything.lean`, `ProveFalse.lean` | 2 |
| Sorry | `SorryDirect.lean` | 1 |
| Unsafe | `UnsafeDefinition.lean` | 1 |
| Partial | `PartialNonTerminating.lean` | 1 |
| Valid | `ValidSimple.lean` | 1 |
| Basic | `Basic.lean` | 1 |

## Official Test Suite

The official LeanParanoia test suite has **56 files** across **15 categories**.

## Proposed Expansion: Representative Samples

Add **1-2 files per category** for comprehensive coverage. This would bring us to **~25-30 files total**.

### Priority 1: Missing High-Impact Categories (Add These First)

#### 1. **Extern** - FFI/External Function Exploits
```bash
# Copy from official:
tests/lean_exploit_files/Extern/ExportC.lean        # @[export] FFI exploit
tests/lean_exploit_files/Extern/PrivateExtern.lean  # private + @[extern]

# Expected behavior:
LeanParanoia: 🛑 Extern + CustomAxioms
lean4checker: 🟢 (compiles successfully)
SafeVerify: 🛑 (custom axiom not in allowed set)
```

**Why important**: Shows FFI security concerns, common in real-world projects.

#### 2. **Transitive** - Dependency Chain Issues
```bash
tests/lean_exploit_files/Transitive/DeepSorry_L1.lean  # Sorry hidden in deps
tests/lean_exploit_files/Transitive/DeepAxiom_L1.lean  # Axiom hidden in deps

# Expected behavior:
LeanParanoia: 🛑 Detects through dependency analysis
lean4checker: 🟢 (valid kernel terms)
SafeVerify: 🛑 (sorryAx/axiom detected)
```

**Why important**: Real exploits often hide issues in dependencies!

#### 3. **ImplementedBy** - Compiler Replacement Attacks
```bash
tests/lean_exploit_files/ImplementedBy/DirectReplacement.lean

# Expected behavior:
LeanParanoia: 🛑 ImplementedBy + CustomAxioms
lean4checker: 🟢 (valid proof structure)
SafeVerify: 🛑 (axiom violation)
```

**Why important**: Shows compiler magic that can bypass proof requirements.

#### 4. **NativeComputation** - Native Code Exploits
```bash
tests/lean_exploit_files/NativeComputation/NativeDecide.lean

# Expected behavior:
LeanParanoia: 🛑 NativeComputation + CustomAxioms
lean4checker: 🛑 (kernel interpreter error!)
SafeVerify: 🛑 (kernel error)
```

**Why important**: One of the few things lean4checker catches!

#### 5. **SourcePatterns** - Notation & Macro Hiding
```bash
tests/lean_exploit_files/SourcePatterns/LocalMacroRules.lean

# Expected behavior:
LeanParanoia: 🛑 SourcePatterns + CustomAxioms
lean4checker: 🟢 (macros expand correctly)
SafeVerify: 🛑 (hidden axiom detected)
```

**Why important**: Shows how notation/macros can obscure exploits.

### Priority 2: Edge Cases & Kernel Issues

#### 6. **KernelRejection** - Build Failures
```bash
tests/lean_exploit_files/KernelRejection/NonPositive.lean

# Expected behavior:
LeanParanoia: 🛑 KernelRejection
lean4checker: 🛑 (no .olean files!)
SafeVerify: 🟡 N/A
```

**Why important**: Shows what happens when code doesn't even compile.

#### 7. **CSimp** - Compiler Simplification Exploits
```bash
tests/lean_exploit_files/CSimp/WithAxiom.lean

# Expected behavior:
LeanParanoia: 🛑 CSimp + CustomAxioms
lean4checker: 🟢
SafeVerify: 🛑
```

**Why important**: Demonstrates @[csimp] attribute attacks.

#### 8. **ConstructorIntegrity** - Type System Bypasses
```bash
tests/lean_exploit_files/ConstructorIntegrity/ManualConstructor.lean

# Expected behavior:
LeanParanoia: 🛑 ConstructorIntegrity + CustomAxioms
lean4checker: 🟢
SafeVerify: 🟡 (type mismatch)
```

#### 9. **RecursorIntegrity** - Recursor Manipulation
```bash
tests/lean_exploit_files/RecursorIntegrity/MissingRecursor.lean

# Expected behavior:
LeanParanoia: 🛑 RecursorIntegrity + CustomAxioms
lean4checker: 🟢
SafeVerify: 🟡 (type mismatch)
```

#### 10. **Metavariables** - Unsolved Type Inference
```bash
tests/lean_exploit_files/Metavariables/Timeout.lean

# Expected behavior:
LeanParanoia: 🛑 CustomAxioms + Sorry + Unsafe
lean4checker: 🟢
SafeVerify: 🟡 (type mismatch)
```

### Priority 3: More Examples from Existing Categories

#### 11. **More Sorry Variants**
```bash
tests/lean_exploit_files/Sorry/Opaque.lean       # Opaque sorry hiding
tests/lean_exploit_files/Sorry/Intermediate.lean # Indirect sorry
```

#### 12. **More CustomAxioms Examples**
```bash
tests/lean_exploit_files/CustomAxioms/HiddenInMacro.lean
tests/lean_exploit_files/CustomAxioms/ForgeRunCmd.lean  # IO exploit
```

#### 13. **More Valid Cases**
```bash
tests/lean_exploit_files/Valid/Dependencies.lean   # With helper theorems
tests/lean_exploit_files/Valid/WithAxioms.lean    # Using allowed axioms
```

## Implementation Plan

### Step 1: Copy Files (Batch 1 - High Impact)

```bash
cd /tmp/leanparanoia/tests/lean_exploit_files

# Copy to our repo
cp Extern/{ExportC,PrivateExtern}.lean \
   Transitive/{DeepSorry_L1,DeepAxiom_L1}.lean \
   ImplementedBy/DirectReplacement.lean \
   NativeComputation/NativeDecide.lean \
   SourcePatterns/LocalMacroRules.lean \
   ~/work/exch-repos/LeanDepViz/examples/leanparanoia-tests/
```

### Step 2: Copy Dependencies

Some test files depend on helper modules:

```bash
# Transitive tests need base modules
cp Transitive/Level0*.lean ~/work/.../leanparanoia-tests/

# SourcePatterns might need shared definitions
cp SourcePatterns/Shared.lean ~/work/.../leanparanoia-tests/ 2>/dev/null
```

### Step 3: Update Generation Script

Edit `scripts/generate_all_examples.sh`:

```bash
# Add new files to copy list
EXAMPLE_FILES=(
  "Basic.lean"
  "ProveAnything.lean"
  "ProveFalse.lean"
  "SorryDirect.lean"
  "PartialNonTerminating.lean"
  "UnsafeDefinition.lean"
  "ValidSimple.lean"
  # NEW FILES:
  "ExportC.lean"
  "PrivateExtern.lean"
  "DeepSorry_L1.lean"
  "DeepAxiom_L1.lean"
  "DirectReplacement.lean"
  "NativeDecide.lean"
  "LocalMacroRules.lean"
  # ... more as needed
)
```

### Step 4: Update Validation

Edit `scripts/validate_unified_report.py`:

```python
# Update expected counts
EXPECTED_TOTAL = 25  # Was 14

# Add new expected failures
EXPECTED_FAILURES = {
    "exploit_axiom": ["custom-axiom"],
    "sorry_theorem": ["sorry"],
    # NEW:
    "export_c_exploit": ["extern", "custom-axiom"],
    "deep_sorry_l1": ["sorry"],  # Via transitive
    "native_decide_exploit": ["native-computation"],
    # ...
}
```

### Step 5: Run Generation

```bash
./scripts/generate_all_examples.sh
```

This will:
1. Create test project with all files
2. Build project
3. Run LeanParanoia → detects all exploit categories
4. Run lean4checker → passes most, fails on NativeComputation & KernelRejection
5. Merge reports
6. Validate expected results
7. Generate HTML with embedded data

### Step 6: Update Documentation

Update `examples/leanparanoia-tests/README.md`:

```markdown
## Categories Demonstrated

**All 15 LeanParanoia Categories:**
- 🔴 **Custom Axioms** (2): bad_axiom, custom_false
- 🟡 **Sorry Usage** (3): exploit_theorem, sorry_proof, deep_sorry
- 🟠 **Unsafe Code** (5): exploit_value, unsafeCompute, ...
- 🟣 **Partial Functions** (1): loop
- 🔵 **Extern/FFI** (2): export_c, private_extern
- 🟢 **Transitive Issues** (2): deep_sorry, deep_axiom
- 🟤 **ImplementedBy** (1): direct_replacement
- ⚫ **NativeComputation** (1): native_decide
- 🟦 **SourcePatterns** (1): local_macro_rules
- ... (all 15 categories covered)
- ✅ **Valid Code** (3): good_theorem, simple_theorem, with_axioms
```

## Expected Output

### Final Demo Stats

With expanded coverage:

```
Total Declarations: ~25-30
Categories: 15 (all from official test suite)

By Tool:
- LeanParanoia: ~22 fail, ~5 pass
- lean4checker: ~3 fail, ~24 pass
- SafeVerify: ~18 fail, ~7 N/A/edge cases

Pass All Tools: ~2-3
Fail Any Tool: ~22-25
```

### HTML Demo Improvements

The viewer will show:
- **Category diversity**: All exploit types represented
- **Tool specialization**: Clear patterns of what each tool catches
- **Edge cases**: N/A cases, build failures, kernel errors
- **Real-world relevance**: FFI, dependencies, compiler magic

## File Structure After Expansion

```
examples/leanparanoia-tests/
├── Basic.lean
├── ProveAnything.lean
├── ProveFalse.lean
├── SorryDirect.lean
├── SorryOpaque.lean
├── PartialNonTerminating.lean
├── UnsafeDefinition.lean
├── ValidSimple.lean
├── ValidWithAxioms.lean
├── ExportC.lean                    # NEW: Extern
├── PrivateExtern.lean              # NEW: Extern
├── DeepSorry_L1.lean              # NEW: Transitive
├── Level0_HasSorry.lean           # NEW: Transitive dependency
├── DeepAxiom_L1.lean              # NEW: Transitive
├── DirectReplacement.lean          # NEW: ImplementedBy
├── NativeDecide.lean              # NEW: NativeComputation
├── LocalMacroRules.lean           # NEW: SourcePatterns
├── ManualConstructor.lean         # NEW: ConstructorIntegrity
├── NonPositive.lean               # NEW: KernelRejection
├── MissingRecursor.lean           # NEW: RecursorIntegrity
├── WithAxiom.lean                 # NEW: CSimp
├── Timeout.lean                   # NEW: Metavariables
├── policy.yaml
├── README.md
├── all-examples-unified-report.json  # Now with 25+ declarations
└── all-examples.{json,dot}
```

## Benefits

### Comprehensive Coverage ✅
- Demonstrates full breadth of LeanParanoia's detection capabilities
- Shows all 15 exploit categories from official test suite
- Matches real-world security concerns

### Better Tool Comparison 📊
- Clear patterns: what each tool catches vs. misses
- Shows lean4checker's niche (NativeComputation, build failures)
- Demonstrates SafeVerify's edge cases

### Educational Value 📚
- Real examples of each exploit type
- Shows why multi-checker verification matters
- Helps users understand their security posture

### Credibility 🎯
- Based on official LeanParanoia test suite
- Not cherry-picked examples
- Shows tool limitations honestly

## Timeline Estimate

- **Phase 1** (2-3 hours): Copy 7-10 priority files + dependencies
- **Phase 2** (1 hour): Update scripts and validation
- **Phase 3** (30 min): Run generation & fix any issues
- **Phase 4** (1 hour): Update documentation & commit

**Total: ~5 hours** for comprehensive expansion

## Alternative: Incremental Approach

Instead of all at once, add categories progressively:

**Week 1**: Extern + Transitive (most impactful)
**Week 2**: ImplementedBy + NativeComputation  
**Week 3**: SourcePatterns + remaining categories

This allows testing and refinement between additions.
