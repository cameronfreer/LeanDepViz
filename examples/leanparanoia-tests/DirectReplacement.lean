-- Implemented by attribute uses different runtime implementation
def wrongAddImpl (n m : Nat) : Nat := n + m + 1

@[implemented_by wrongAddImpl]
def seemsCorrectAdd (n m : Nat) : Nat := n + m

axiom exploit_axiom : seemsCorrectAdd 1 1 = 3

theorem exploit_theorem : 1 + 1 = 3 := exploit_axiom
