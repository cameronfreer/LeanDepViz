namespace LeanTestProject.KernelRejection

-- Kernel rejects: non-positive inductive type

inductive Bad where
  | mk : (Bad → False) → Bad

def exploit : Bad → False
  | .mk f => f (.mk f)

theorem exploit_theorem : False :=
  exploit (.mk exploit)

end LeanTestProject.KernelRejection
