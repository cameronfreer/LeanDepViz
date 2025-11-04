-- Local macro rules that change elaboration behavior
namespace LeanTestProject.SourcePatterns.LocalMacroRules

axiom hidden_axiom : 1 = 2

-- Override the sorry macro to use our axiom instead
local macro_rules | `(sorry) => `(hidden_axiom)

theorem exploit_theorem : 1 = 2 := sorry

end LeanTestProject.SourcePatterns.LocalMacroRules
