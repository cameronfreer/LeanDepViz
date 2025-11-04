-- Private extern bypasses checks if using Name.isInternal
@[extern "malicious_private_add"]
private def privateAdd (n m : Nat) : Nat := n + m

def publicAdd (n m : Nat) : Nat := privateAdd n m

axiom exploit_axiom : publicAdd 1 1 = 3

theorem exploit_theorem : 1 + 1 = 3 := exploit_axiom
