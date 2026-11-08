// Dafny — Easy Example: Verified Absolute Value
//
// What:  A function with a machine-checked postcondition proving correctness.
// Where: Safety-critical arithmetic, financial calculations, sensor bounds.
// When:  Use when the compiler must mathematically guarantee the output
//        satisfies a specification before the program can even compile.
// Why:   Dafny's verifier (Boogie + Z3) proves postconditions at compile time.
//        If the proof fails, the program does not compile. Runtime bugs in
//        verified code are structurally impossible.
// How:   `ensures` clauses are logical assertions that the SMT solver must
//        discharge. The programmer writes the spec; the machine proves it.

method Abs(x: int) returns (result: int)
    ensures result >= 0
    ensures result == x || result == -x
{
    if x >= 0 {
        result := x;
    } else {
        result := -x;
    }
}

method Main() {
    var a := Abs(5);
    assert a == 5;

    var b := Abs(-3);
    assert b == 3;

    var c := Abs(0);
    assert c == 0;

    print "All verified at compile time. No runtime checks needed.\n";
}
