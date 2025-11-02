-- Simple test with custom axiom
axiom bad_axiom : False

theorem bad_theorem : False := bad_axiom

-- Good theorem
theorem good_theorem : True := trivial
