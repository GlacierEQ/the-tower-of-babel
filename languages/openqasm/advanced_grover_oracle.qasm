// =============================================================================
// WHAT: 5-Qubit Grover quantum search circuit with phase inversion oracle
// WHERE: Quantum Processing Units (QPU) and Qiskit / Braket quantum runtimes
// WHEN: Performing quadratic speedup search over unstructured cryptographic state
// WHY: Quantum superposition and phase kickback amplify correct target states
// HOW: Hadamard initialization, cz phase kickback, Grover oracle and diffuser
// =============================================================================

OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];
creg c[4];

// Phase 1: Initialize superposition across 4 search qubits
h q[0];
h q[1];
h q[2];
h q[3];

// Initialize ancilla qubit into |-> state for phase kickback
x q[4];
h q[4];

// Phase 2: Quantum Grover Oracle for target state |1011>
// Flip qubits that should be 0 in target
x q[2];

// Multi-controlled Toffoli and cz gate to ancilla
ccx q[0], q[1], q[4];
cz q[2], q[4];
ccx q[2], q[3], q[4];

// Restore target bit flips
x q[2];

// Phase 3: Grover Diffuser Operator (Inversion about the mean)
h q[0];
h q[1];
h q[2];
h q[3];

x q[0];
x q[1];
x q[2];
x q[3];

// Multi-controlled Z gate
h q[3];
ccx q[0], q[1], q[4];
ccx q[2], q[4], q[3];
h q[3];

x q[0];
x q[1];
x q[2];
x q[3];

h q[0];
h q[1];
h q[2];
h q[3];

// Phase 4: Measurement
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
