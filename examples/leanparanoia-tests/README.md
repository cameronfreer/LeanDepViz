# LeanParanoia Test Examples

These examples demonstrate various exploits that LeanParanoia is designed to detect. They are adapted from the [LeanParanoia test suite](https://github.com/oOo0oOo/LeanParanoia/tree/main/tests/lean_exploit_files).

⚠️ **Warning**: These files contain intentionally unsound code! They demonstrate what LeanParanoia should catch, not safe coding practices.

## Examples

### ProveFalse.lean
Demonstrates a custom axiom that directly proves `False`:
```lean
axiom exploit_axiom : False
theorem exploit_theorem : False := exploit_axiom
```

**What LeanParanoia detects**: Uses disallowed axiom `exploit_axiom`

### ProveAnything.lean
Shows how an axiom proving False can prove any statement:
```lean
axiom falseAxiom : False
theorem proveAnything (P : Prop) : P := False.elim falseAxiom
```

**What LeanParanoia detects**: Uses disallowed axiom `falseAxiom`

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

## Credits

Examples adapted from the LeanParanoia project by https://github.com/oOo0oOo

LeanParanoia itself builds on lean4checker by the Lean FRO.
