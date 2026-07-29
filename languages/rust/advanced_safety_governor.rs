//! Advanced Rust exhibit: authority gate with explicit evidence and tests.
//! Evidence class: tested. No external crates are required.

use std::collections::BTreeSet;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum ActionClass {
    Read,
    Plan,
    WriteInternal,
    External,
    Destructive,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Mission {
    pub mission_id: String,
    pub action: ActionClass,
    pub requested_capabilities: BTreeSet<String>,
    pub evidence_refs: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuthorityPolicy {
    pub maximum_action: ActionClass,
    pub allowed_capabilities: BTreeSet<String>,
    pub require_evidence_from: ActionClass,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Decision {
    Allowed { reason: String },
    Blocked { reason: String },
}

impl AuthorityPolicy {
    pub fn evaluate(&self, mission: &Mission) -> Decision {
        if mission.action > self.maximum_action {
            return Decision::Blocked {
                reason: format!(
                    "action {:?} exceeds maximum {:?}",
                    mission.action, self.maximum_action
                ),
            };
        }
        let denied: Vec<_> = mission
            .requested_capabilities
            .difference(&self.allowed_capabilities)
            .cloned()
            .collect();
        if !denied.is_empty() {
            return Decision::Blocked {
                reason: format!("capabilities are not allowed: {}", denied.join(",")),
            };
        }
        if mission.action >= self.require_evidence_from && mission.evidence_refs.is_empty() {
            return Decision::Blocked {
                reason: "evidence is required for this action class".into(),
            };
        }
        Decision::Allowed {
            reason: "policy, capability, and evidence gates passed".into(),
        }
    }
}

fn main() {
    let policy = AuthorityPolicy {
        maximum_action: ActionClass::External,
        allowed_capabilities: ["github.read", "github.write"]
            .into_iter()
            .map(String::from)
            .collect(),
        require_evidence_from: ActionClass::WriteInternal,
    };
    let mission = Mission {
        mission_id: "mission-001".into(),
        action: ActionClass::External,
        requested_capabilities: ["github.write"].into_iter().map(String::from).collect(),
        evidence_refs: vec!["sha256:example".into()],
    };
    println!("{:?}", policy.evaluate(&mission));
}

#[cfg(test)]
mod tests {
    use super::*;

    fn policy() -> AuthorityPolicy {
        AuthorityPolicy {
            maximum_action: ActionClass::External,
            allowed_capabilities: ["repo.read", "repo.write"]
                .into_iter()
                .map(String::from)
                .collect(),
            require_evidence_from: ActionClass::WriteInternal,
        }
    }

    #[test]
    fn permits_evidence_bound_write() {
        let mission = Mission {
            mission_id: "m1".into(),
            action: ActionClass::WriteInternal,
            requested_capabilities: ["repo.write"].into_iter().map(String::from).collect(),
            evidence_refs: vec!["sha256:abc".into()],
        };
        assert!(matches!(policy().evaluate(&mission), Decision::Allowed { .. }));
    }

    #[test]
    fn blocks_destructive_action() {
        let mission = Mission {
            mission_id: "m2".into(),
            action: ActionClass::Destructive,
            requested_capabilities: BTreeSet::new(),
            evidence_refs: vec!["sha256:def".into()],
        };
        assert!(matches!(policy().evaluate(&mission), Decision::Blocked { .. }));
    }

    #[test]
    fn blocks_unapproved_capability() {
        let mission = Mission {
            mission_id: "m3".into(),
            action: ActionClass::Read,
            requested_capabilities: ["shell.root"].into_iter().map(String::from).collect(),
            evidence_refs: vec![],
        };
        assert!(matches!(policy().evaluate(&mission), Decision::Blocked { .. }));
    }
}
