/-!
# SafeVerify Demo - Modified Implementation

This is the MODIFIED version with CHANGED STATEMENTS.
SafeVerify will detect these changes even though the code still compiles
and passes LeanParanoia/lean4checker.

## Changes from Reference:
1. `sum_of_evens_is_even`: WEAKENED - removed the requirement that both inputs are even
2. `double_is_even`: STRENGTHENED - now claims result is divisible by 4
3. `reverse_length`: CHANGED - now claims reverse is always shorter (FALSE)
4. `append_nil_length`: UNCHANGED - control to show SafeVerify works correctly
-/

namespace SafeVerifyDemo.Modified

/-! ## Arithmetic Theorems -/

/-- The sum of two numbers is even (WEAKENED: removed even requirement on inputs) -/
theorem sum_of_evens_is_even (a b : Nat) :
    Even (a + b) := by
  -- This is now PROVABLY FALSE in general, so we use sorry
  -- SafeVerify will catch that the statement changed
  sorry

/-- Doubling a number produces a number divisible by 4 (STRENGTHENED: false claim) -/
theorem double_is_even (n : Nat) : ∃ k, 2 * n = 4 * k := by
  -- This is FALSE (e.g., 2 * 1 = 2, not divisible by 4)
  -- But SafeVerify will catch the statement change
  sorry

/-! ## List Theorems -/

/-- The reverse of a list is shorter than the original (CHANGED: false claim) -/
theorem reverse_length {α : Type} (xs : List α) :
    xs.reverse.length < xs.length := by
  -- This is FALSE (reverse preserves length)
  -- SafeVerify will catch this statement change
  sorry

/-- Appending empty list doesn't change length (UNCHANGED) -/
theorem append_nil_length {α : Type} (xs : List α) :
    (xs ++ []).length = xs.length := by
  simp

end SafeVerifyDemo.Modified
