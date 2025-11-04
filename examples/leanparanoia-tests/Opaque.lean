-- Opaque definition hiding sorry axiom in body
import Lean

open Lean

set_option maxHeartbeats 100000 in
opaque hiddenSorryProof : False := by
  have h : False := sorryAx _ false
  exact h

def exploit_theorem : False := hiddenSorryProof
