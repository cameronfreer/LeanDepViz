## SafeVerify Demo: Detecting Statement Changes

This example demonstrates **SafeVerify's** ability to detect when theorem statements change between a reference implementation and a submission, even when both compile successfully.

### Scenario

You're reviewing a pull request that claims to have "cleaned up" some theorems. The code compiles and all tests pass. But did the theorem statements actually change?

**SafeVerify** compares the reference implementation against the modified version and detects statement changes.

### The Files

- **`Reference.lean`**: Original version with correct theorem statements
- **`Modified.lean`**: "Cleaned up" version with subtly changed statements

### What Changed?

| Theorem | Reference Statement | Modified Statement | Type of Change |
|---------|-------------------|-------------------|----------------|
| `sum_of_evens_is_even` | `Even a → Even b → Even (a + b)` | `Even (a + b)` | **WEAKENED** - removed preconditions |
| `double_is_even` | `Even (2 * n)` | `∃ k, 2 * n = 4 * k` | **STRENGTHENED** - false stronger claim |
| `reverse_length` | `xs.reverse.length = xs.length` | `xs.reverse.length < xs.length` | **CHANGED** - completely different claim |
| `append_nil_length` | `(xs ++ []).length = xs.length` | `(xs ++ []).length = xs.length` | **UNCHANGED** - control |

### Defense-in-Depth Analysis

Let's see how each verification tool handles these changes:

#### LeanParanoia ✓ (Passes)
- Checks: No sorry, no custom axioms, no unsafe code
- **Result**: All modified theorems use `sorry`, so LeanParanoia will **FAIL** on the sorry check
- **Catches**: The use of sorry, but not the statement changes

#### lean4checker ✓ (Passes)
- Checks: Kernel replay integrity
- **Result**: Will **PASS** - the sorry axiom is valid in the kernel
- **Misses**: Both sorry usage and statement changes

#### SafeVerify ✗ (Fails - Detects Changes!)
- Checks: Statement equivalence between reference and submission
- **Result**: **FAILS** on 3 theorems with statement changes
- **Catches**: The changed statements even though code compiles

### Why This Matters

Imagine these scenarios:

1. **Weakened Theorem** (`sum_of_evens_is_even`):
   - Original: Guarantees sum is even if both inputs are even
   - Modified: Claims ANY two numbers sum to even (false!)
   - **Impact**: Other code relying on this theorem gets weaker guarantees

2. **Strengthened Theorem** (`double_is_even`):
   - Original: `2 * n` is even
   - Modified: `2 * n` is divisible by 4 (false!)
   - **Impact**: Theorem is now unprovable without sorry

3. **Changed Theorem** (`reverse_length`):
   - Original: Reverse preserves length
   - Modified: Reverse makes list shorter (nonsense!)
   - **Impact**: Completely changes the meaning

### Running the Demo

```bash
# 1. Build reference version
mkdir -p /tmp/safeverify-demo-reference
cd /tmp/safeverify-demo-reference
# ... setup and build reference ...

# 2. Build modified version
mkdir -p /tmp/safeverify-demo-modified
cd /tmp/safeverify-demo-modified
# ... setup and build modified ...

# 3. Run SafeVerify comparison
python3 scripts/safeverify_adapter.py \
  --depgraph modified-depgraph.json \
  --target-dir /tmp/safeverify-demo-reference/.lake/build \
  --submit-dir /tmp/safeverify-demo-modified/.lake/build \
  --out safeverify-report.json

# 4. Merge with other verification tools
python3 scripts/merge_reports.py \
  --reports paranoia-report.json lean4checker-report.json safeverify-report.json \
  --out unified-report.json
```

### Expected Results

**SafeVerify Report:**
```json
{
  "sum_of_evens_is_even": {
    "ok": false,
    "error": "Statement mismatch: reference and submission have different types"
  },
  "double_is_even": {
    "ok": false,
    "error": "Statement mismatch: reference and submission have different types"
  },
  "reverse_length": {
    "ok": false,
    "error": "Statement mismatch: reference and submission have different types"
  },
  "append_nil_length": {
    "ok": true,
    "notes": "Statements match exactly"
  }
}
```

### Key Takeaway

**Defense-in-depth verification requires multiple independent checkers:**

- **LeanParanoia**: Catches policy violations (sorry, axioms, unsafe)
- **lean4checker**: Catches kernel corruption
- **SafeVerify**: Catches statement changes

Together, they provide comprehensive assurance that your code is:
1. ✅ Policy-compliant (no sorry/axioms)
2. ✅ Kernel-valid (environment integrity)
3. ✅ Statement-preserving (claims unchanged)
