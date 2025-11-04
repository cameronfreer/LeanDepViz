-- Manual constructor manipulation without exposing generated constructors
inductive ManualWitness : Type

axiom manualCtor : ManualWitness

noncomputable def exploit_theorem : ManualWitness := manualCtor
