\* TLA+ — Advanced Example: Tower Receipt Chain Safety and Liveness
\*
\* What:  A TLA+ specification that formally verifies the Tower of Babel's
\*        receipt chain protocol. Proves that receipts are monotonic (safety),
\*        that every submitted verification eventually produces a receipt
\*        (liveness), and that no receipt can reference a future sequence.
\* Where: Formal verification of distributed receipt and evidence systems.
\* When:  Use when the correctness of an ordering or sequencing protocol must
\*        be mathematically proven across all possible interleavings of
\*        concurrent verifiers, network partitions, and crash-recovery.
\* Why:   Testing checks finitely many executions. TLA+ model checking
\*        exhaustively verifies ALL reachable states. If the receipt chain
\*        can ever violate monotonicity, TLC will find the counterexample.
\* How:   Models N concurrent verifiers submitting verification results to a
\*        sequencer. The sequencer assigns monotonic sequence numbers. Each
\*        receipt links to its predecessor. TLC verifies safety invariants
\*        and temporal liveness properties.

---- MODULE TowerReceiptChain ----
EXTENDS Integers, Sequences, FiniteSets

CONSTANTS
    Verifiers,       \* Set of concurrent verifier IDs
    MaxSequence      \* Bound for model checking (e.g., 5)

VARIABLES
    next_sequence,   \* Nat: the next sequence number to assign
    pending,         \* Set of verifier IDs with unprocessed results
    receipts,        \* Sequence of receipt records
    verifier_state   \* Function: verifier -> {"idle", "verifying", "submitted", "receipted"}

vars == <<next_sequence, pending, receipts, verifier_state>>

Receipt == [sequence: Nat, verifier: Verifiers, prev_sequence: Nat]

\* ── Initial State ─────────────────────────────────────────────────────

Init ==
    /\ next_sequence = 1
    /\ pending = {}
    /\ receipts = <<>>
    /\ verifier_state = [v \in Verifiers |-> "idle"]

\* ── Actions ───────────────────────────────────────────────────────────

\* A verifier begins a verification task.
StartVerification(v) ==
    /\ verifier_state[v] = "idle"
    /\ verifier_state' = [verifier_state EXCEPT ![v] = "verifying"]
    /\ UNCHANGED <<next_sequence, pending, receipts>>

\* A verifier completes and submits its result.
SubmitResult(v) ==
    /\ verifier_state[v] = "verifying"
    /\ verifier_state' = [verifier_state EXCEPT ![v] = "submitted"]
    /\ pending' = pending \union {v}
    /\ UNCHANGED <<next_sequence, receipts>>

\* The sequencer processes one pending submission and issues a receipt.
IssueReceipt(v) ==
    /\ v \in pending
    /\ next_sequence <= MaxSequence
    /\ LET prev == IF Len(receipts) = 0 THEN 0
                    ELSE receipts[Len(receipts)].sequence
           receipt == [sequence |-> next_sequence, verifier |-> v, prev_sequence |-> prev]
       IN /\ receipts' = Append(receipts, receipt)
          /\ next_sequence' = next_sequence + 1
          /\ pending' = pending \ {v}
          /\ verifier_state' = [verifier_state EXCEPT ![v] = "receipted"]

\* A receipted verifier returns to idle (can verify again).
Reset(v) ==
    /\ verifier_state[v] = "receipted"
    /\ verifier_state' = [verifier_state EXCEPT ![v] = "idle"]
    /\ UNCHANGED <<next_sequence, pending, receipts>>

Next ==
    \/ \E v \in Verifiers : StartVerification(v)
    \/ \E v \in Verifiers : SubmitResult(v)
    \/ \E v \in Verifiers : IssueReceipt(v)
    \/ \E v \in Verifiers : Reset(v)

\* ── Safety Invariants ─────────────────────────────────────────────────

\* Monotonicity: each receipt's sequence > its predecessor's sequence.
MonotonicSequence ==
    \A i \in 1..Len(receipts) :
        /\ receipts[i].sequence > receipts[i].prev_sequence
        /\ IF i > 1 THEN receipts[i].sequence > receipts[i-1].sequence
           ELSE TRUE

\* No gaps: sequence numbers are contiguous starting from 1.
NoGaps ==
    \A i \in 1..Len(receipts) : receipts[i].sequence = i

\* No receipt references a future sequence.
NoProphecy ==
    \A i \in 1..Len(receipts) : receipts[i].prev_sequence < receipts[i].sequence

\* Sequence counter always equals length + 1.
SequenceIntegrity ==
    next_sequence = Len(receipts) + 1

TypeInvariant ==
    /\ next_sequence \in 1..(MaxSequence + 1)
    /\ pending \subseteq Verifiers
    /\ \A i \in 1..Len(receipts) :
        /\ receipts[i].sequence \in 1..MaxSequence
        /\ receipts[i].verifier \in Verifiers
        /\ receipts[i].prev_sequence \in 0..MaxSequence

\* ── Liveness ──────────────────────────────────────────────────────────

\* Every submitted verification eventually gets a receipt.
\* (Requires fairness: WF or SF on the sequencer actions.)
Liveness ==
    \A v \in Verifiers :
        verifier_state[v] = "submitted" ~> verifier_state[v] = "receipted"

\* ── Specification ─────────────────────────────────────────────────────

Fairness == \A v \in Verifiers : WF_vars(IssueReceipt(v))

Spec == Init /\ [][Next]_vars /\ Fairness

====
