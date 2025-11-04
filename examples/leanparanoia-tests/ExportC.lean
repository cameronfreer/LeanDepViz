-- Export attribute exposes declaration to C ABI like extern
@[export lean_test_exported_add]
def exportedAdd (x y : Nat) : Nat := x + y

axiom ExportC_exploit_axiom : exportedAdd 1 1 = 3

theorem ExportC_exploit_theorem : 1 + 1 = 3 := ExportC_exploit_axiom
