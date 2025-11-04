-- CSimp attribute with axiom replaces function at runtime
def wrongAdd (n m : Nat) : Nat := n + m + 1

def correctAdd (n m : Nat) : Nat := n + m

@[csimp] axiom correctAdd_eq_wrongAdd : @correctAdd = @wrongAdd

axiom exploit_axiom : correctAdd 1 1 = 3

theorem exploit_theorem : 1 + 1 = 3 := exploit_axiom
