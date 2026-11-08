\* TLA+ — Easy Example: Simple Two-Phase Commit
\*
\* What:  A minimal TLA+ specification of a two-phase commit protocol.
\* Where: Distributed systems correctness verification.
\* When:  Use when you need mathematical certainty that a concurrent protocol
\*        cannot deadlock, livelock, or violate safety invariants.
\* Why:   TLA+ exhaustively explores every possible interleaving of actions.
\*        If a bug exists in the protocol, the model checker will find it.
\* How:   Define state variables, initial state, next-state transitions, and
\*        invariants. TLC explores the full state space.

---- MODULE SimpleCommit ----
EXTENDS Integers, FiniteSets

CONSTANTS Participants

VARIABLES
    participant_vote,   \* Function: participant -> {"working", "prepared", "committed", "aborted"}
    coordinator_decision \* "pending" | "commit" | "abort"

vars == <<participant_vote, coordinator_decision>>

Init ==
    /\ participant_vote = [p \in Participants |-> "working"]
    /\ coordinator_decision = "pending"

Prepare(p) ==
    /\ participant_vote[p] = "working"
    /\ participant_vote' = [participant_vote EXCEPT ![p] = "prepared"]
    /\ UNCHANGED coordinator_decision

DecideCommit ==
    /\ coordinator_decision = "pending"
    /\ \A p \in Participants : participant_vote[p] = "prepared"
    /\ coordinator_decision' = "commit"
    /\ UNCHANGED participant_vote

DecideAbort ==
    /\ coordinator_decision = "pending"
    /\ \E p \in Participants : participant_vote[p] = "working"
    /\ coordinator_decision' = "abort"
    /\ UNCHANGED participant_vote

Commit(p) ==
    /\ coordinator_decision = "commit"
    /\ participant_vote[p] = "prepared"
    /\ participant_vote' = [participant_vote EXCEPT ![p] = "committed"]
    /\ UNCHANGED coordinator_decision

Abort(p) ==
    /\ coordinator_decision = "abort"
    /\ participant_vote[p] \in {"working", "prepared"}
    /\ participant_vote' = [participant_vote EXCEPT ![p] = "aborted"]
    /\ UNCHANGED coordinator_decision

Next ==
    \/ \E p \in Participants : Prepare(p)
    \/ DecideCommit
    \/ DecideAbort
    \/ \E p \in Participants : Commit(p)
    \/ \E p \in Participants : Abort(p)

\* Safety: no participant commits while another aborts.
Consistency ==
    ~ \E p1, p2 \in Participants :
        /\ participant_vote[p1] = "committed"
        /\ participant_vote[p2] = "aborted"

Spec == Init /\ [][Next]_vars

====
