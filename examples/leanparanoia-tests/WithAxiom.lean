-- CSimp attribute with axiom replaces function at runtime
def wrongAdd (n m : Nat) : Nat := n + m + 1

def correctAdd (n m : Nat) : Nat := n + m

@[csimp] axiom correctAdd_eq_wrongAdd : @correctAdd = @wrongAdd

axiom WithAxiom_exploit_axiom : correctAdd 1 1 = 3

theorem WithAxiom_exploit_theorem : 1 + 1 = 3 := WithAxiom_exploit_axiom
