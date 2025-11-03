/-!
# SafeVerify Demo - Reference Implementation

This is the REFERENCE version that will be compared against.
These theorems represent what was originally claimed/proven.
-/

namespace SafeVerifyDemo.Reference

/-! ## Arithmetic Theorems -/

/-- The sum of two even numbers is even -/
theorem sum_of_evens_is_even (a b : Nat) :
    Even a → Even b → Even (a + b) := by
  intro ⟨k, hk⟩ ⟨m, hm⟩
  exists k + m
  rw [hk, hm]
  ring

/-- Doubling a number produces an even number -/
theorem double_is_even (n : Nat) : Even (2 * n) := by
  exists n
  ring

/-! ## List Theorems -/

/-- The length of a reversed list equals the original length -/
theorem reverse_length {α : Type} (xs : List α) :
    xs.reverse.length = xs.length := by
  apply List.length_reverse

/-- Appending empty list doesn't change length -/
theorem append_nil_length {α : Type} (xs : List α) :
    (xs ++ []).length = xs.length := by
  simp

end SafeVerifyDemo.Reference
