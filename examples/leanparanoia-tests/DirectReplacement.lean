-- Implemented by attribute uses different runtime implementation
def wrongAddImpl (n m : Nat) : Nat := n + m + 1

@[implemented_by wrongAddImpl]
def seemsCorrectAdd (n m : Nat) : Nat := n + m

axiom DirectReplacement_exploit_axiom : seemsCorrectAdd 1 1 = 3

theorem DirectReplacement_exploit_theorem : 1 + 1 = 3 := DirectReplacement_exploit_axiom
