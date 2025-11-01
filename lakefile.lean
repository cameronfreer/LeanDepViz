import Lake
open Lake DSL

package «LeanDepViz» where
  -- Dependency visualization and verification tooling for Lean 4 projects

lean_lib «LeanDepViz» where
  -- Main library

lean_exe depviz where
  root := `LeanDepViz.Main
  supportInterpreter := true
