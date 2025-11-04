-- Native decide introduces compiler axioms to trusted codebase
theorem exploit_theorem : (List.range 100).length = 100 := by
  native_decide
