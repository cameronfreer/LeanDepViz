namespace LeanTestProject.Valid.WithAxioms

-- Valid theorem using whitelisted Classical axioms
open Classical

theorem uses_choice : True := by
  have h := em (∃ n : Nat, n = n)
  trivial

end LeanTestProject.Valid.WithAxioms
