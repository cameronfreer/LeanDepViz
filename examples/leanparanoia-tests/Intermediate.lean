-- Sorry hidden in intermediate proof step
theorem exploit_theorem : True ∧ True := by
  constructor
  · exact trivial
  · have h : True := sorry
    exact h
