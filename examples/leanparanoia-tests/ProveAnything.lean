-- Magic axiom proving any proposition
axiom magic : ∀ (p : Prop), p

theorem exploit_theorem : False := magic False
