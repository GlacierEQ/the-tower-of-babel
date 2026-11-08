# Rego — Advanced Example: Tower Governance Policy Enforcer
#
# What:  An OPA policy that enforces the Tower's Architecture Law as executable
#        code. Validates technology placement proposals against ownership rules,
#        proof-class minimums, interface requirements, and anti-ambiguity law.
# Where: CI gates, agent admission, automated PR review, deployment pipelines.
# When:  Use when governance constraints must be machine-enforced without
#        human review bottlenecks, and when the same policy must apply across
#        CLI tools, CI systems, and agent orchestrators identically.
# Why:   Rego makes governance auditable: the policy IS the documentation.
#        Every decision produces an explanation trace. Every rule is testable.
# How:   The `placement_decision` rule evaluates a technology placement proposal
#        and returns a structured verdict with reasons, violations, and blockers.

package tower.governance

import rego.v1

# ── Constants ──────────────────────────────────────────────────────────────

proof_rank := {
    "illustrative": 0,
    "compile": 1,
    "behavioral": 2,
    "benchmark": 3,
    "hardware": 3,
    "integration": 4,
    "formal": 5,
}

gated_states := {"hardware_gated", "toolchain_gated", "service_gated"}

# ── Placement Decision ────────────────────────────────────────────────────

# Top-level verdict for a technology placement proposal.
placement_decision := {
    "allowed": count(violations) == 0,
    "violations": violations,
    "blockers": blockers,
    "proof_sufficient": proof_sufficient,
    "ownership_clear": ownership_clear,
    "receipt": {
        "proposal": input.proposal.technology_id,
        "lane": input.proposal.lane,
        "verdict": verdict_string,
    },
} if {
    verdict_string := "APPROVED" if { count(violations) == 0 }
    else := "REJECTED"
}

# ── Violation Rules ───────────────────────────────────────────────────────

# Every technology must declare exactly one lane.
violations contains msg if {
    not input.proposal.lane
    msg := "AMBIGUOUS_OWNERSHIP: technology must declare exactly one lane"
}

# Lane must not duplicate an existing owner without explicit migration.
violations contains msg if {
    existing := input.registry[_]
    existing.lane == input.proposal.lane
    existing.technology_id != input.proposal.technology_id
    not input.proposal.migration_from
    msg := sprintf("OWNERSHIP_CONFLICT: lane '%s' already owned by '%s'; declare migration_from to proceed", [input.proposal.lane, existing.technology_id])
}

# Proof class must meet the lane's minimum.
violations contains msg if {
    proposed_rank := proof_rank[input.proposal.proof_class]
    minimum_rank := proof_rank[input.lane_requirements[input.proposal.lane].minimum_proof_class]
    proposed_rank < minimum_rank
    msg := sprintf("INSUFFICIENT_PROOF: lane '%s' requires '%s' (rank %d) but proposal offers '%s' (rank %d)", [
        input.proposal.lane,
        input.lane_requirements[input.proposal.lane].minimum_proof_class,
        minimum_rank,
        input.proposal.proof_class,
        proposed_rank,
    ])
}

# Technology must not be in a gated state without an explicit blocker.
violations contains msg if {
    input.proposal.evidence_state in gated_states
    not input.proposal.explicit_blocker
    msg := sprintf("GATED_WITHOUT_BLOCKER: state '%s' requires an explicit_blocker field", [input.proposal.evidence_state])
}

# Interface contracts must be declared when the lane has adjacent lanes.
violations contains msg if {
    required_interfaces := input.lane_requirements[input.proposal.lane].required_interfaces
    count(required_interfaces) > 0
    provided := {iface | iface := input.proposal.interfaces[_]}
    missing := required_interfaces - provided
    count(missing) > 0
    msg := sprintf("MISSING_INTERFACES: lane '%s' requires interfaces %v", [input.proposal.lane, missing])
}

# ── Helper Rules ──────────────────────────────────────────────────────────

proof_sufficient if {
    proposed_rank := proof_rank[input.proposal.proof_class]
    minimum_rank := proof_rank[input.lane_requirements[input.proposal.lane].minimum_proof_class]
    proposed_rank >= minimum_rank
}

ownership_clear if {
    not ambiguous_lane
}

ambiguous_lane if {
    not input.proposal.lane
}

ambiguous_lane if {
    existing := input.registry[_]
    existing.lane == input.proposal.lane
    existing.technology_id != input.proposal.technology_id
    not input.proposal.migration_from
}

# Blockers: gated technologies that cannot proceed without external action.
blockers contains blocker if {
    input.proposal.evidence_state in gated_states
    blocker := {
        "technology": input.proposal.technology_id,
        "state": input.proposal.evidence_state,
        "blocker": input.proposal.explicit_blocker,
    }
}
