namespace LeanTestProject.Partial.NonTerminating

-- Non-terminating function marked as partial to bypass termination checker
partial def loop (n : Nat) : Nat :=
  loop (n + 1)

theorem exploit_theorem : loop 0 = 42 := by
  -- This would never terminate, but we "prove" it anyway
  sorry

end LeanTestProject.Partial.NonTerminating
