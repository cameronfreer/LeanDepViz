-- Missing recursor manipulation
inductive MissingRecursor_Witness : Type

axiom missingRecCtor : MissingRecursor_Witness

noncomputable def MissingRecursor_exploit : MissingRecursor_Witness := missingRecCtor
