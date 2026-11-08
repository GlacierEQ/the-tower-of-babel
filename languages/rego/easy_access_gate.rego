# Rego — Easy Example: Simple Allow/Deny Policy Gate
#
# What:  A minimal OPA policy that gates access by role.
# Where: API gateways, Kubernetes admission control, CI pipelines.
# When:  Use when authorization logic must be decoupled from application code.
# Why:   Rego evaluates policies as pure data queries — no side effects,
#        deterministic, and testable independently of the systems they govern.
# How:   `allow` is true only when the input satisfies all conditions.

package tower.access

default allow := false

allow if {
    input.role == "operator"
    input.action == "verify"
}

allow if {
    input.role == "operator"
    input.action == "read"
}

allow if {
    input.role == "agent"
    input.action == "read"
}
