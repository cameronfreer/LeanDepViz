-- Incomplete calc proof with sorry in chain
theorem exploit_theorem (a b c : Nat) (h1 : a = b) (h2 : b = c) : a = c := by
  calc a = b := h1
       _ = c := sorry
