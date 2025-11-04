-- Unsafe code bypasses kernel verification through computation
unsafe def unsafeProof : 1 + 1 = 3 := unsafeProof

unsafe def unsafeAddImpl (n m : Nat) : Nat := n + m + 1

@[implemented_by unsafeAddImpl]
def seeminglySafeAdd (n m : Nat) : Nat := n + m

axiom UnsafeDefinition_exploit_axiom : seeminglySafeAdd 1 1 = 3

theorem UnsafeDefinition_exploit_theorem : 1 + 1 = 3 := UnsafeDefinition_exploit_axiom
