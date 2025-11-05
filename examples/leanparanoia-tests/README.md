# LeanParanoia Test Examples

These examples demonstrate various exploits that LeanParanoia is designed to detect. They are adapted from the [LeanParanoia test suite](https://github.com/oOo0oOo/LeanParanoia/tree/main/tests/lean_exploit_files).

⚠️ **Warning**: These files contain intentionally unsound code! They demonstrate what LeanParanoia should catch, not safe coding practices.

## Live Demos

### 🎯 **Comprehensive Test Coverage** (Recommended)
**[View All Examples](https://cameronfreer.github.io/LeanDepViz/leanparanoia-examples-all.html)** - Complete test suite with real verification data

Shows **67 declarations** across **26 test files** with **2 verification tools**:
- ✅ **28 Pass**: Valid code passing all checks (42%)
- ❌ **39 Fail**: Various exploits caught by checkers (58%)

**Verification Tools**:
- **LeanParanoia**: Policy enforcement across all 15 exploit categories
- **lean4checker**: Kernel replay verification

**All 15 Categories Covered** (100% of official LeanParanoia test suite):
- 🔴 **Custom Axioms** (4 files): Proving False, arbitrary axioms, macro-hidden axioms
- 🟡 **Sorry Usage** (4 files): Direct sorry, transitive sorry, hidden sorry
- 🟠 **Unsafe Code** (1 file): Unsafe definitions bypassing type safety
- 🟣 **Partial Functions** (1 file): Non-terminating recursion
- 🔵 **Extern/FFI** (2 files): Foreign function interface exploits
- 🟢 **Transitive** (4 files): Hidden exploits in dependencies
- 🟤 **ImplementedBy** (1 file): Compiler replacement attacks
- ⚫ **Native Computation** (1 file): Native code execution
- 🟠 **Source Patterns** (1 file): Macro/notation hiding
- 🔴 **CSimp** (1 file): Compiler simplification exploits
- 🟡 **Constructor Integrity** (1 file): Type system bypasses
- 🟢 **Recursor Integrity** (1 file): Eliminator manipulation
- 🔵 **Metavariables** (1 file): Unsolved type inference
- 🟣 **Kernel Rejection** (1 file): Build/import failures
- ✅ **Valid** (4 files): Clean verified code

**Key Findings**:
- lean4checker **passes** on sorries & custom axioms ✓ (as expected)
- lean4checker **fails** on NativeComputation ✓ (rare but important!)
- LeanParanoia detects all 15 exploit categories ✓

### 📊 Other Demos

**[Multi-Checker UI Demo](https://cameronfreer.github.io/LeanDepViz/verification-demo.html)** - UI showcase with 3 tools (includes mock SafeVerify data)

**[Basic Demo](https://cameronfreer.github.io/LeanDepViz/leanparanoia-test-demo.html)** - Simple 3-declaration example

## Output Files

This directory includes complete output from the expanded test project:

### Source Code (26 files)
See [CATEGORIES.md](CATEGORIES.md) for complete list with descriptions.

### Dependency Graph Formats
- **all-examples-depgraph.json** (22KB) - Machine-readable dependency data for 67 declarations
- **all-examples-depgraph.dot** (17KB) - GraphViz DOT format
- **all-examples-depgraph.svg** (71KB) - Vector visualization (generated locally, gitignored)

### Verification Results  
- **all-examples-unified-report.json** (52KB) - Merged report from LeanParanoia + lean4checker
- **leanparanoia-examples-all.html** (230KB) - Interactive viewer with all data embedded

### Configuration
- **policy.yaml** - LeanParanoia policy defining zones, allowed axioms, forbidden items

### File Sizes Summary
| Format | Size | Purpose |
|--------|------|---------|
| Source | 26 files | Test exploits across 15 categories |
| JSON (graph) | 22KB | Dependency data (67 declarations) |
| JSON (report) | 52KB | Unified verification results |
| DOT | 17KB | Graph source |
| SVG | 71KB | Vector visualization (local) |
| HTML | 230KB | Complete interactive viewer with embedded data |
| Policy | ~1KB | Verification policy configuration |

**Total**: ~400KB for complete verification demo with all embedded data

## Example Files

### Custom Axioms

**ProveFalse.lean** - Custom axiom proving False:
```lean
axiom exploit_axiom : False
theorem exploit_theorem : False := exploit_axiom
```
**Detected**: Uses disallowed axiom `exploit_axiom`

**ProveAnything.lean** - Using False to prove anything:
```lean
axiom falseAxiom : False
theorem proveAnything (P : Prop) : P := False.elim falseAxiom
```
**Detected**: Uses disallowed axiom `falseAxiom`

### Sorry Usage

**SorryDirect.lean** - Direct sorry bypasses proof verification:
```lean
theorem exploit_theorem : False := sorry
```
**Detected**: Uses `sorry` (incomplete proof)

### Unsafe Declarations

**UnsafeDefinition.lean** - Unsafe code bypasses kernel verification:
```lean
unsafe def unsafeProof : 1 + 1 = 3 := unsafeProof
unsafe def unsafeAddImpl (n m : Nat) : Nat := n + m + 1

@[implemented_by unsafeAddImpl]
def seeminglySafeAdd (n m : Nat) : Nat := n + m

axiom exploit_axiom : seeminglySafeAdd 1 1 = 3
theorem exploit_theorem : 1 + 1 = 3 := exploit_axiom
```
**Detected**: Uses `unsafe` declarations and unsafe `@[implemented_by]`

### Partial Functions

**PartialNonTerminating.lean** - Non-terminating function:
```lean
partial def loop (n : Nat) : Nat := loop (n + 1)
theorem exploit_theorem : loop 0 = 42 := by sorry
```
**Detected**: Uses `partial` function (bypasses termination checker) and `sorry`

### Valid Code

**ValidSimple.lean** - Clean, verified code:
```lean
theorem simple_theorem : True := trivial
```
**Passes**: No exploits, standard axioms only

## Testing with LeanParanoia

### Prerequisites
- Lean 4 toolchain: v4.24.0-rc1 (required for LeanParanoia compatibility)
- LeanParanoia dependency in your lakefile.lean

### Setup a Test Project

1. Create a new Lean project:
```bash
mkdir paranoia-test && cd paranoia-test
```

2. Create `lakefile.lean`:
```lean
import Lake
open Lake DSL

package «test» where

require paranoia from git
  "https://github.com/oOo0oOo/LeanParanoia.git" @ "main"

lean_lib «Test» where
  roots := #[`Test]
```

3. Create `lean-toolchain`:
```
leanprover/lean4:v4.24.0-rc1
```

4. Copy test files:
```bash
mkdir Test
cp ProveFalse.lean Test/
```

5. Build and test:
```bash
lake build paranoia
lake build

# Test - should fail with custom axiom error
lake exe paranoia Test.ProveFalse.exploit_theorem
```

### Expected Output

**ProveFalse example**:
```json
{"failures":{"CustomAxioms":["Uses disallowed axioms: exploit_axiom"]},"success":false}
```

**ProveAnything example**:
```json
{"failures":{"CustomAxioms":["Uses disallowed axioms: falseAxiom"]},"success":false}
```

## Toolchain Compatibility

⚠️ **Important**: LeanParanoia currently only works with **Lean v4.24.0-rc1**

Newer toolchains (v4.24.0, v4.25.0+) have linker errors. If your project uses a newer toolchain:

1. **For testing only**: Temporarily downgrade to v4.24.0-rc1
2. **For production**: Wait for LeanParanoia to update toolchain compatibility

## More Examples

The full LeanParanoia test suite includes examples of:
- **CSimp exploits**: Compiler simplification issues
- **Constructor integrity**: Invalid inductive type constructors
- **Extern declarations**: FFI boundary violations
- **Implemented by**: @[implemented_by] attribute misuse
- **Metavariables**: Partially elaborated terms
- **Native computation**: Unsafe native code execution
- **Partial functions**: Non-terminating recursion
- **Recursor integrity**: Invalid eliminators

See: https://github.com/oOo0oOo/LeanParanoia/tree/main/tests/lean_exploit_files

## Regenerating the Demos

The embedded HTML demos are generated automatically. To regenerate after adding new examples:

```bash
# From repo root
./scripts/generate_all_examples.sh
```

This runs a complete 10-step pipeline:
1. **Create test project** with lakefile, toolchain, and all 26 test files
2. **Build project** using Lake (includes LeanParanoia dependency)
3. **Generate dependency graph** using LeanDepViz
4. **Run LeanParanoia** verification on 47 declarations
5. **Run lean4checker** verification on 67 declarations  
6. **Merge reports** into unified format
7. **Validate** unified report structure
8. **Copy outputs** to repository
9. **Generate SVG preview** from DOT file (requires Graphviz)
10. **Generate HTML viewer** with all data embedded

**Requirements**:
- Lean 4.24.0-rc1 toolchain
- Graphviz (`brew install graphviz` for SVG generation)
- Python 3 with PyYAML (`pip install pyyaml`)

**Output**: `docs/leanparanoia-examples-all.html` (230KB standalone file)

See `scripts/generate_all_examples.sh` for implementation details.

## Credits

Examples adapted from the LeanParanoia project by https://github.com/oOo0oOo

LeanParanoia itself builds on lean4checker by the Lean FRO.
