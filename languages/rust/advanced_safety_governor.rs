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
    pub trusted_evidence_refs: BTreeSet<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Decision {
    Allowed { reason: String },
    Blocked { reason: String },
}

fn valid_sha256_ref(value: &str) -> bool {
    let Some(digest) = value.strip_prefix("sha256:") else {
        return false;
    };
    digest.len() == 64 && digest.bytes().all(|byte| byte.is_ascii_hexdigit())
}

impl AuthorityPolicy {
    pub fn evaluate(&self, mission: &Mission) -> Decision {
        if mission.mission_id.trim().is_empty() {
            return Decision::Blocked {
                reason: "mission_id is required".into(),
            };
        }
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
        if mission.action >= self.require_evidence_from {
            if mission.evidence_refs.is_empty() {
                return Decision::Blocked {
                    reason: "evidence is required for this action class".into(),
                };
            }
            let invalid: Vec<_> = mission
                .evidence_refs
                .iter()
                .filter(|reference| !valid_sha256_ref(reference))
                .cloned()
                .collect();
            if !invalid.is_empty() {
                return Decision::Blocked {
                    reason: "evidence references must be sha256:<64 hex>".into(),
                };
            }
            let untrusted: Vec<_> = mission
                .evidence_refs
                .iter()
                .filter(|reference| !self.trusted_evidence_refs.contains(*reference))
                .cloned()
                .collect();
            if !untrusted.is_empty() {
                return Decision::Blocked {
                    reason: "evidence is structurally valid but not trusted by this policy".into(),
                };
            }
        }
        Decision::Allowed {
            reason: "policy, capability, and trusted-evidence gates passed".into(),
        }
    }
}

fn main() {
    let evidence = format!("sha256:{}", "a".repeat(64));
    let policy = AuthorityPolicy {
        maximum_action: ActionClass::External,
        allowed_capabilities: ["github.read", "github.write"]
            .into_iter()
            .map(String::from)
            .collect(),
        require_evidence_from: ActionClass::WriteInternal,
        trusted_evidence_refs: [evidence.clone()].into_iter().collect(),
    };
    let mission = Mission {
        mission_id: "mission-001".into(),
        action: ActionClass::External,
        requested_capabilities: ["github.write"].into_iter().map(String::from).collect(),
        evidence_refs: vec![evidence],
    };
    println!("{:?}", policy.evaluate(&mission));
}

#[cfg(test)]
mod tests {
    use super::*;

    fn trusted() -> String {
        format!("sha256:{}", "a".repeat(64))
    }

    fn policy() -> AuthorityPolicy {
        AuthorityPolicy {
            maximum_action: ActionClass::External,
            allowed_capabilities: ["repo.read", "repo.write"]
                .into_iter()
                .map(String::from)
                .collect(),
            require_evidence_from: ActionClass::WriteInternal,
            trusted_evidence_refs: [trusted()].into_iter().collect(),
        }
    }

    #[test]
    fn permits_trusted_evidence_bound_write() {
        let mission = Mission {
            mission_id: "m1".into(),
            action: ActionClass::WriteInternal,
            requested_capabilities: ["repo.write"].into_iter().map(String::from).collect(),
            evidence_refs: vec![trusted()],
        };
        assert!(matches!(policy().evaluate(&mission), Decision::Allowed { .. }));
    }

    #[test]
    fn blocks_destructive_action() {
        let mission = Mission {
            mission_id: "m2".into(),
            action: ActionClass::Destructive,
            requested_capabilities: BTreeSet::new(),
            evidence_refs: vec![trusted()],
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

    #[test]
    fn blocks_malformed_evidence() {
        let mission = Mission {
            mission_id: "m4".into(),
            action: ActionClass::WriteInternal,
            requested_capabilities: ["repo.write"].into_iter().map(String::from).collect(),
            evidence_refs: vec!["sha256:abc".into()],
        };
        assert!(matches!(policy().evaluate(&mission), Decision::Blocked { .. }));
    }

    #[test]
    fn blocks_untrusted_evidence() {
        let mission = Mission {
            mission_id: "m5".into(),
            action: ActionClass::WriteInternal,
            requested_capabilities: ["repo.write"].into_iter().map(String::from).collect(),
            evidence_refs: vec![format!("sha256:{}", "b".repeat(64))],
        };
        assert!(matches!(policy().evaluate(&mission), Decision::Blocked { .. }));
    }
}
