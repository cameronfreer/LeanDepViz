# LeanParanoia Test Examples

These examples demonstrate various exploits that LeanParanoia is designed to detect. They are adapted from the [LeanParanoia test suite](https://github.com/oOo0oOo/LeanParanoia/tree/main/tests/lean_exploit_files).

⚠️ **Warning**: These files contain intentionally unsound code! They demonstrate what LeanParanoia should catch, not safe coding practices.

## Live Demos

### 🎯 **Comprehensive Verification Demo** (Recommended)
**[View Verification Demo](https://cameronfreer.github.io/LeanDepViz/verification-demo.html)** - All LeanParanoia examples with multi-checker UI

Shows **17 declarations** with **3 verification tool columns**:
- ✅ **2 Pass**: Valid code passing all checks
- ❌ **15 Fail**: Various exploits caught by checkers

**Verification Tools Demonstrated**:
- **LeanParanoia**: Policy enforcement (sorry, axioms, unsafe, partial)
- **lean4checker**: Kernel replay verification
- **SafeVerify**: Reference vs implementation comparison

> **⚠️ Important - Demonstration Data**: This demo showcases the multi-checker UI with **demonstration/mock data** to illustrate capabilities. The verification results are **manually crafted** based on known issues in the LeanParanoia test files. SafeVerify results are **entirely mock** because SafeVerify requires comparing two versions (baseline vs implementation), but these test files exist in only one version. The demo illustrates what a complete multi-tool verification workflow would look like when all tools are actually run.

**Categories Demonstrated**:
- 🔴 **Custom Axioms**: bad_axiom, custom_false
- 🟡 **Sorry Usage**: exploit_theorem, sorry_proof
- 🟠 **Unsafe Code**: exploit_value, unsafeCompute
- 🟣 **Partial Functions**: loop, partial_def
- 🟢 **Valid Code**: good_theorem, simple_theorem

### 📊 Legacy Single-Checker Demos

**[Basic Demo](https://cameronfreer.github.io/LeanDepViz/leanparanoia-test-demo.html)** - Simple 3-declaration example (LeanParanoia only)

**[All Examples (Single-Tool)](https://cameronfreer.github.io/LeanDepViz/leanparanoia-examples-all.html)** - 12 declarations (LeanParanoia only)

## Output Files

This directory includes complete output from the test project in all formats:

### Source Code
- **Basic.lean** - The test file with good and bad theorems

### Dependency Graph Formats
- **test-depgraph.json** (589B) - Machine-readable dependency data
- **test-graph.dot** (486B) - GraphViz DOT format
- **test-graph.svg** (2.2KB) - Scalable vector graphic
- **test-graph.png** (11KB) - Raster image

### Verification Results
- **paranoia-report.json** (694B) - LeanParanoia verification report
- **leanparanoia-test-demo.html** (27KB) - Interactive viewer with all data embedded

### File Sizes Summary
| Format | Size | Purpose |
|--------|------|---------|
| Source | N/A | Lean code |
| JSON | 589B | Dependency data |
| DOT | 486B | Graph source |
| SVG | 2.2KB | Vector visualization |
| PNG | 11KB | Raster visualization |
| Report | 694B | Verification results |
| HTML | 27KB | Complete interactive viewer |

**Total**: ~42KB for complete verification demo

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
python scripts/generate_paranoia_examples.py
```

This will:
1. Build a temporary test project with all example files
2. Generate dependency graphs
3. Create verification reports
4. Generate embedded HTML demos
5. Copy outputs to `docs/` for GitHub Pages

See `scripts/README.md` for details on adding new examples.

## Credits

Examples adapted from the LeanParanoia project by https://github.com/oOo0oOo

LeanParanoia itself builds on lean4checker by the Lean FRO.
