-- Uses sorry from L0 transitively (1 level deep)
import LeanTestProject.DeepSorry_L0

theorem uses_sorry_from_l0 : True := by
  have : False := has_sorry
  exact True.intro
