import Lean
def is_truthful (c : Float) : Bool := c >= 0.99
theorem truth_soundness (c : Float) (h : c >= 0.99) : is_truthful c = true := by rfl
