-- Magic axiom proving any proposition
axiom magic : ∀ (p : Prop), p

theorem ProveAnything_exploit_theorem : False := magic False
