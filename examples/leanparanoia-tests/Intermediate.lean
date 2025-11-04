-- Sorry hidden in intermediate proof step
theorem Intermediate_exploit_theorem : True ∧ True := by
  constructor
  · exact trivial
  · have h : True := sorry
    exact h
