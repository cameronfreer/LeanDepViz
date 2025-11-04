-- Manual constructor manipulation without exposing generated constructors
inductive ManualConstructor_Witness : Type

axiom manualCtor : ManualConstructor_Witness

noncomputable def ManualConstructor_exploit : ManualConstructor_Witness := manualCtor
