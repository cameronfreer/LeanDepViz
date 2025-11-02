-- Unsafe code bypasses kernel verification through computation
unsafe def unsafeProof : 1 + 1 = 3 := unsafeProof

unsafe def unsafeAddImpl (n m : Nat) : Nat := n + m + 1

@[implemented_by unsafeAddImpl]
def seeminglySafeAdd (n m : Nat) : Nat := n + m

axiom exploit_axiom : seeminglySafeAdd 1 1 = 3

theorem exploit_theorem : 1 + 1 = 3 := exploit_axiom
