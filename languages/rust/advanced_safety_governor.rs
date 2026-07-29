pub struct SafetyGovernor { pub max_depth: usize }
impl SafetyGovernor { pub fn check(&self, d: usize) -> bool { d <= self.max_depth } }
