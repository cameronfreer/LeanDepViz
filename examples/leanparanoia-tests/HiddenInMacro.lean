namespace LeanTestProject.CustomAxioms.HiddenInMacro

-- Axiom hidden behind macro expansion

axiom hidden_axiom : False

macro "prove_false" : term => `(hidden_axiom)

theorem exploit_theorem : False :=
  prove_false

end LeanTestProject.CustomAxioms.HiddenInMacro
