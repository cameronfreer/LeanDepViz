-- Export attribute exposes declaration to C ABI like extern
@[export lean_test_exported_add]
def exportedAdd (x y : Nat) : Nat := x + y

axiom exploit_axiom : exportedAdd 1 1 = 3

theorem exploit_theorem : 1 + 1 = 3 := exploit_axiom
