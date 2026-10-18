//! Rust — Advanced Example: Typed Action Safety Governor
//!
//! What: A deterministic policy kernel for tool execution decisions.
//! Where: MCP gateways, evidence pipelines, privileged CLIs, agent runtimes.
//! When: Untrusted requests must be constrained before any side effect occurs.
//! Why: Rust's enums, ownership, and exhaustive matching make policy gaps visible.
//! How: Canonicalized paths, bounded inputs, explicit mutation approval, structured
//!      decisions, and tests that exercise denial paths as first-class behavior.

use std::fmt;
use std::path::{Component, Path, PathBuf};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ActionKind {
    Read,
    Write,
    Delete,
    Execute,
    Publish,
}

impl ActionKind {
    pub fn is_mutating(self) -> bool {
        !matches!(self, Self::Read)
    }

    pub fn requires_elevated_approval(self) -> bool {
        matches!(self, Self::Delete | Self::Execute | Self::Publish)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ActionRequest {
    pub actor: String,
    pub action: ActionKind,
    pub target: PathBuf,
    pub payload_bytes: usize,
    pub recursion_depth: usize,
    pub approved_mutation: bool,
    pub approved_elevated_action: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GovernorConfig {
    pub allowed_roots: Vec<PathBuf>,
    pub max_payload_bytes: usize,
    pub max_recursion_depth: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DenialReason {
    MissingActor,
    NoAllowedRoots,
    PathTraversal,
    SymlinkPath,
    TargetOutsideAllowedRoots,
    PayloadTooLarge { actual: usize, maximum: usize },
    RecursionTooDeep { actual: usize, maximum: usize },
    MutationApprovalRequired,
    ElevatedApprovalRequired,
}

impl fmt::Display for DenialReason {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::MissingActor => write!(f, "authenticated actor is required"),
            Self::NoAllowedRoots => write!(f, "no allowed roots are configured"),
            Self::PathTraversal => write!(f, "target contains a parent traversal component"),
            Self::SymlinkPath => write!(f, "target traverses a symbolic link beneath an allowed root"),
            Self::TargetOutsideAllowedRoots => write!(f, "target is outside every allowed root"),
            Self::PayloadTooLarge { actual, maximum } => {
                write!(f, "payload size {actual} exceeds maximum {maximum}")
            }
            Self::RecursionTooDeep { actual, maximum } => {
                write!(f, "recursion depth {actual} exceeds maximum {maximum}")
            }
            Self::MutationApprovalRequired => write!(f, "mutation approval is required"),
            Self::ElevatedApprovalRequired => write!(f, "elevated action approval is required"),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PolicyDecision {
    pub allowed: bool,
    pub normalized_target: Option<PathBuf>,
    pub reason: Option<DenialReason>,
    pub policy_version: &'static str,
}

impl PolicyDecision {
    fn allow(target: PathBuf) -> Self {
        Self {
            allowed: true,
            normalized_target: Some(target),
            reason: None,
            policy_version: "safety-governor/1",
        }
    }

    fn deny(reason: DenialReason) -> Self {
        Self {
            allowed: false,
            normalized_target: None,
            reason: Some(reason),
            policy_version: "safety-governor/1",
        }
    }
}

#[derive(Debug, Clone)]
pub struct SafetyGovernor {
    config: GovernorConfig,
}

impl SafetyGovernor {
    pub fn new(config: GovernorConfig) -> Result<Self, DenialReason> {
        if config.allowed_roots.is_empty() {
            return Err(DenialReason::NoAllowedRoots);
        }
        let allowed_roots = config
            .allowed_roots
            .into_iter()
            .map(|root| normalize_without_io(&root))
            .collect::<Result<Vec<_>, _>>()?;
        Ok(Self {
            config: GovernorConfig {
                allowed_roots,
                ..config
            },
        })
    }

    pub fn evaluate(&self, request: &ActionRequest) -> PolicyDecision {
        if request.actor.trim().is_empty() {
            return PolicyDecision::deny(DenialReason::MissingActor);
        }
        if request.payload_bytes > self.config.max_payload_bytes {
            return PolicyDecision::deny(DenialReason::PayloadTooLarge {
                actual: request.payload_bytes,
                maximum: self.config.max_payload_bytes,
            });
        }
        if request.recursion_depth > self.config.max_recursion_depth {
            return PolicyDecision::deny(DenialReason::RecursionTooDeep {
                actual: request.recursion_depth,
                maximum: self.config.max_recursion_depth,
            });
        }
        if request.action.is_mutating() && !request.approved_mutation {
            return PolicyDecision::deny(DenialReason::MutationApprovalRequired);
        }
        if request.action.requires_elevated_approval() && !request.approved_elevated_action {
            return PolicyDecision::deny(DenialReason::ElevatedApprovalRequired);
        }

        let normalized = match normalize_without_io(&request.target) {
            Ok(path) => path,
            Err(reason) => return PolicyDecision::deny(reason),
        };
        let matching_roots: Vec<&PathBuf> = self
            .config
            .allowed_roots
            .iter()
            .filter(|root| normalized == **root || normalized.starts_with(root))
            .collect();
        if matching_roots.is_empty() {
            return PolicyDecision::deny(DenialReason::TargetOutsideAllowedRoots);
        }
        // Select the deepest declared owner for overlapping roots.
        let root = matching_roots.into_iter().max_by_key(|r| r.components().count()).unwrap();
        if crosses_symlink_boundary(root, &normalized) {
            return PolicyDecision::deny(DenialReason::SymlinkPath);
        }

        PolicyDecision::allow(normalized)
    }
}


// The governor is a preflight decision, not an openat2/dirfd filesystem
// capability or authorization token. Every caller must still bind the actual
// file descriptor and revalidate its real owner at the effect boundary.
fn crosses_symlink_boundary(root: &Path, target: &Path) -> bool {
    let Ok(relative) = target.strip_prefix(root) else {
        return false;
    };
    let mut candidate = root.to_path_buf();
    for component in relative.components() {
        candidate.push(component.as_os_str());
        if let Ok(metadata) = std::fs::symlink_metadata(&candidate) {
            if metadata.file_type().is_symlink() {
                let (Ok(real_root), Ok(real_candidate)) = (
                    std::fs::canonicalize(root),
                    std::fs::canonicalize(&candidate),
                ) else {
                    // Dangling links and unverifiable resolution cannot pass.
                    return true;
                };
                if !real_candidate.starts_with(&real_root) {
                    return true;
                }
            }
        }
    }
    false
}

fn normalize_without_io(path: &Path) -> Result<PathBuf, DenialReason> {
    let mut normalized = PathBuf::new();
    for component in path.components() {
        match component {
            Component::ParentDir => return Err(DenialReason::PathTraversal),
            Component::CurDir => {}
            other => normalized.push(other.as_os_str()),
        }
    }
    Ok(normalized)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn governor() -> SafetyGovernor {
        SafetyGovernor::new(GovernorConfig {
            allowed_roots: vec![PathBuf::from("/srv/evidence")],
            max_payload_bytes: 1024,
            max_recursion_depth: 4,
        })
        .expect("valid governor")
    }

    fn request(action: ActionKind, target: &str) -> ActionRequest {
        ActionRequest {
            actor: "operator.casey".to_string(),
            action,
            target: PathBuf::from(target),
            payload_bytes: 64,
            recursion_depth: 1,
            approved_mutation: false,
            approved_elevated_action: false,
        }
    }

    #[test]
    fn allows_read_inside_root() {
        let decision = governor().evaluate(&request(
            ActionKind::Read,
            "/srv/evidence/case-1009/index.json",
        ));
        assert!(decision.allowed);
        assert_eq!(
            decision.normalized_target,
            Some(PathBuf::from("/srv/evidence/case-1009/index.json"))
        );
    }

    #[test]
    fn denies_parent_traversal_before_root_evaluation() {
        let decision = governor().evaluate(&request(
            ActionKind::Read,
            "/srv/evidence/../secrets/token.txt",
        ));
        assert_eq!(decision.reason, Some(DenialReason::PathTraversal));
    }

    #[test]
    fn denies_write_without_mutation_approval() {
        let decision = governor().evaluate(&request(
            ActionKind::Write,
            "/srv/evidence/case-1009/manifest.json",
        ));
        assert_eq!(
            decision.reason,
            Some(DenialReason::MutationApprovalRequired)
        );
    }

    #[test]
    fn delete_requires_both_approval_levels() {
        let mut candidate = request(ActionKind::Delete, "/srv/evidence/quarantine/item");
        candidate.approved_mutation = true;
        let denied = governor().evaluate(&candidate);
        assert_eq!(denied.reason, Some(DenialReason::ElevatedApprovalRequired));

        candidate.approved_elevated_action = true;
        assert!(governor().evaluate(&candidate).allowed);
    }


    #[cfg(unix)]
    #[test]
    fn denies_symlink_escape_from_allowed_evidence_root() {
        use std::os::unix::fs::symlink;
        use std::time::{SystemTime, UNIX_EPOCH};
        let nonce = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos();
        let sandbox = std::env::temp_dir().join(format!("tower-rust-symlink-{}-{nonce}", std::process::id()));
        let root = sandbox.join("evidence");
        let outside = sandbox.join("outside");
        std::fs::create_dir_all(&root).unwrap();
        std::fs::create_dir_all(&outside).unwrap();
        std::fs::write(outside.join("secret.txt"), b"outside-root").unwrap();
        symlink(&outside, root.join("alias")).unwrap();
        let governor = SafetyGovernor::new(GovernorConfig {
            allowed_roots: vec![root.clone()],
            max_payload_bytes: 1024,
            max_recursion_depth: 4,
        }).unwrap();
        let candidate = ActionRequest {
            actor: "authenticated-operator".into(),
            action: ActionKind::Read,
            target: root.join("alias").join("secret.txt"),
            payload_bytes: 0,
            recursion_depth: 1,
            approved_mutation: false,
            approved_elevated_action: false,
        };
        let decision = governor.evaluate(&candidate);
        assert!(!decision.allowed, "a symlink cannot escape the allowlisted root");
        assert_eq!(decision.reason, Some(DenialReason::SymlinkPath));
        std::fs::remove_dir_all(&sandbox).unwrap();
    }


    #[cfg(unix)]
    #[test]
    fn permits_symlink_resolving_within_the_same_evidence_root() {
        use std::os::unix::fs::symlink;
        use std::time::{SystemTime, UNIX_EPOCH};
        let nonce = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos();
        let sandbox = std::env::temp_dir().join(format!("tower-rust-internal-{}-{nonce}", std::process::id()));
        let root = sandbox.join("evidence");
        std::fs::create_dir_all(root.join("internal")).unwrap();
        std::fs::write(root.join("internal").join("record.txt"), b"internal-record").unwrap();
        symlink(root.join("internal"), root.join("alias")).unwrap();
        let governor = SafetyGovernor::new(GovernorConfig {
            allowed_roots: vec![root.clone()],
            max_payload_bytes: 1024,
            max_recursion_depth: 4,
        }).unwrap();
        let candidate = ActionRequest {
            actor: "authenticated-operator".into(),
            action: ActionKind::Read,
            target: root.join("alias").join("record.txt"),
            payload_bytes: 0,
            recursion_depth: 1,
            approved_mutation: false,
            approved_elevated_action: false,
        };
        assert!(governor.evaluate(&candidate).allowed);
        std::fs::remove_dir_all(&sandbox).unwrap();
    }

    #[cfg(unix)]
    #[test]
    fn denies_dangling_symlink_within_evidence_root() {
        use std::os::unix::fs::symlink;
        use std::time::{SystemTime, UNIX_EPOCH};
        let nonce = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos();
        let sandbox = std::env::temp_dir().join(format!("tower-rust-dangling-{}-{nonce}", std::process::id()));
        let root = sandbox.join("evidence");
        std::fs::create_dir_all(&root).unwrap();
        symlink(sandbox.join("missing"), root.join("alias")).unwrap();
        let governor = SafetyGovernor::new(GovernorConfig {
            allowed_roots: vec![root.clone()],
            max_payload_bytes: 1024,
            max_recursion_depth: 4,
        }).unwrap();
        let candidate = ActionRequest {
            actor: "authenticated-operator".into(),
            action: ActionKind::Read,
            target: root.join("alias"),
            payload_bytes: 0,
            recursion_depth: 1,
            approved_mutation: false,
            approved_elevated_action: false,
        };
        assert_eq!(governor.evaluate(&candidate).reason, Some(DenialReason::SymlinkPath));
        std::fs::remove_dir_all(&sandbox).unwrap();
    }

    #[test]
    fn bounded_inputs_fail_closed() {
        let mut candidate = request(ActionKind::Read, "/srv/evidence/item");
        candidate.payload_bytes = 1025;
        assert!(matches!(
            governor().evaluate(&candidate).reason,
            Some(DenialReason::PayloadTooLarge { .. })
        ));

        candidate.payload_bytes = 1;
        candidate.recursion_depth = 5;
        assert!(matches!(
            governor().evaluate(&candidate).reason,
            Some(DenialReason::RecursionTooDeep { .. })
        ));
    }
}
